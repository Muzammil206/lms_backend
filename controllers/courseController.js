const { supabase } = require('../config');
const winston = require('winston');

// @desc    Get all courses
// @route   GET /api/v1/courses
// @access  Public
exports.getCourses = async (req, res, next) => {
  try {
    const { difficulty, isPublished, category, duration } = req.query;
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 25;
    const offset = (page - 1) * limit;

    // Build Supabase query
    let query = supabase
      .from('courses')
      .select(`
        *,
        category:course_categories (name, slug)
      `, { count: 'exact' })
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);

    // Add filters
    if (difficulty) query = query.eq('level', difficulty);
    if (isPublished) query = query.eq('is_published', isPublished === 'true');
    if (category) query = query.eq('category_id', category);
    if (duration) {
      const [min, max] = duration.split('-');
      if (min) query = query.gte('duration', min);
      if (max) query = query.lte('duration', max);
    }

    // Execute query
    const { data: courses, count: totalCount, error } = await query;

    if (error) throw error;

    // Pagination
    const pagination = {
      total: totalCount,
      pages: Math.ceil(totalCount / limit),
      current: page
    };

    if (offset + limit < totalCount) {
      pagination.next = { page: page + 1, limit };
    }
    if (offset > 0) {
      pagination.prev = { page: page - 1, limit };
    }

    res.status(200).json({
      success: true,
      count: courses.length,
      pagination,
      data: courses
    });
  } catch (err) {
    winston.error('Error getting courses:', err);
    next(err);
  }
};

// @desc    Get single course with modules and content
// @route   GET /api/v1/courses/:id
// @access  Public
exports.getCourse = async (req, res, next) => {
  try {
    // Get course basic info
    const { data: course, error: courseError } = await supabase
      .from('courses')
      .select(`
        *,
        category:course_categories (name, slug)
      `)
      .eq('id', req.params.id)
      .single();

    if (courseError) throw courseError;
    if (!course) {
      return res.status(404).json({
        success: false,
        message: 'Course not found'
      });
    }

    // Get course modules with their content
    const { data: modules, error: modulesError } = await supabase
      .from('modules')
      .select(`
        *,
        contents:module_contents (
          *,
          video:content_videos (*),
          quiz:content_quizzes (*),
          assignment:content_assignments (*)
        )
      `)
      .eq('course_id', req.params.id)
      .order('position', { ascending: true });

    if (modulesError) throw modulesError;

    // Structure the response
    const response = {
      ...course,
      modules: modules.map(module => ({
        ...module,
        contents: module.contents.map(content => {
          let contentDetails = {};
          if (content.content_type === 'video' && content.video) {
            contentDetails = content.video;
          } else if (content.content_type === 'quiz' && content.quiz) {
            contentDetails = content.quiz;
          } else if (content.content_type === 'assignment' && content.assignment) {
            contentDetails = content.assignment;
          }
          return {
            ...content,
            ...contentDetails
          };
        })
      }))
    };

    res.status(200).json({
      success: true,
      data: response
    });
  } catch (err) {
    winston.error('Error getting course:', err);
    next(err);
  }
};

// @desc    Create course
// @route   POST /api/v1/courses
// @access  Private (Admin)
exports.createCourse = async (req, res, next) => {
  try {
    // Check if user is an admin
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('role')
      .eq('id', req.user.id)
      .single();

    if (userError) throw userError;
    if (user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to create courses'
      });
    }

    // Validate request body
    const { title, description, category_id } = req.body;
    if (!title || !description || !category_id) {
      return res.status(400).json({
        success: false,
        message: 'Title, description and category are required'
      });
    }

    // Create course
    const { data: course, error } = await supabase
      .from('courses')
      .insert({
        ...req.body,
        instructor_name: req.body.instructor_name || 'LMS Instructor'
      })
      .select(`
        *,
        category:course_categories (name, slug)
      `)
      .single();

    if (error) throw error;

    res.status(201).json({
      success: true,
      data: course
    });
  } catch (err) {
    winston.error('Error creating course:', err);
    next(err);
  }
};

// @desc    Update course
// @route   PUT /api/v1/courses/:id
// @access  Private (Admin)
exports.updateCourse = async (req, res, next) => {
  try {
    // Check if user is an admin
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('role')
      .eq('id', req.user.id)
      .single();

    if (userError) throw userError;
    if (user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to update courses'
      });
    }

    // Update course
    const { data: updatedCourse, error } = await supabase
      .from('courses')
      .update(req.body)
      .eq('id', req.params.id)
      .select(`
        *,
        category:course_categories (name, slug)
      `)
      .single();

    if (error) throw error;
    if (!updatedCourse) {
      return res.status(404).json({
        success: false,
        message: 'Course not found'
      });
    }

    res.status(200).json({
      success: true,
      data: updatedCourse
    });
  } catch (err) {
    winston.error('Error updating course:', err);
    next(err);
  }
};

// @desc    Delete course
// @route   DELETE /api/v1/courses/:id
// @access  Private (Admin)
exports.deleteCourse = async (req, res, next) => {
  try {
    // Check if user is an admin
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('role')
      .eq('id', req.user.id)
      .single();

    if (userError) throw userError;
    if (user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to delete courses'
      });
    }

    // First delete all related modules and content
    // Get all modules for this course
    const { data: modules, error: modulesError } = await supabase
      .from('modules')
      .select('id')
      .eq('course_id', req.params.id);

    if (modulesError) throw modulesError;

    if (modules && modules.length > 0) {
      const moduleIds = modules.map(m => m.id);
      
      // Delete all module contents
      await supabase
        .from('module_contents')
        .delete()
        .in('module_id', moduleIds);

      // Delete all modules
      await supabase
        .from('modules')
        .delete()
        .eq('course_id', req.params.id);
    }

    // Delete enrollments
    await supabase
      .from('enrollments')
      .delete()
      .eq('course_id', req.params.id);

    // Finally delete the course
    const { error } = await supabase
      .from('courses')
      .delete()
      .eq('id', req.params.id);

    if (error) throw error;

    res.status(200).json({
      success: true,
      data: {}
    });
  } catch (err) {
    winston.error('Error deleting course:', err);
    next(err);
  }
};

// @desc    Publish/unpublish course
// @route   PATCH /api/v1/courses/:id/publish
// @access  Private (Admin)
exports.publishCourse = async (req, res, next) => {
  try {
    // Check if user is an admin
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('role')
      .eq('id', req.user.id)
      .single();

    if (userError) throw userError;
    if (user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to publish courses'
      });
    }

    const { publish } = req.body;
    if (typeof publish !== 'boolean') {
      return res.status(400).json({
        success: false,
        message: 'Publish status is required'
      });
    }

    const updateData = {
      is_published: publish,
      published_at: publish ? new Date().toISOString() : null
    };

    const { data: updatedCourse, error } = await supabase
      .from('courses')
      .update(updateData)
      .eq('id', req.params.id)
      .select()
      .single();

    if (error) throw error;
    if (!updatedCourse) {
      return res.status(404).json({
        success: false,
        message: 'Course not found'
      });
    }

    res.status(200).json({
      success: true,
      data: updatedCourse
    });
  } catch (err) {
    winston.error('Error publishing course:', err);
    next(err);
  }
};

// @desc    Add material to course
// @route   POST /api/v1/courses/:id/materials
// @access  Private (Instructor)
exports.addMaterial = async (req, res, next) => {
  try {
    const { title, description, content, type } = req.body;
    const courseId = req.params.id;

    // Validate required fields
    if (!title || !description || !content || !type) {
      return res.status(400).json({
        success: false,
        message: 'Title, description, content and type are required'
      });
    }

    // Validate material type
    const validTypes = ['document', 'video', 'link', 'presentation'];
    if (!validTypes.includes(type)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid material type'
      });
    }

    // Create material
    const { data: material, error } = await supabase
      .from('materials')
      .insert({
        title,
        description,
        content,
        type,
        course_id: courseId,
        created_by: req.user.id
      })
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({
      success: true,
      data: material
    });
  } catch (err) {
    winston.error('Error adding material:', err);
    next(err);
  }
};

// @desc    Add quiz to course
// @route   POST /api/v1/courses/:id/quizzes
// @access  Private (Instructor)
exports.addQuiz = async (req, res, next) => {
  try {
    const { title, description, questions, passing_score } = req.body;
    const courseId = req.params.id;

    // Validate required fields
    if (!title || !description || !questions || !passing_score) {
      return res.status(400).json({
        success: false,
        message: 'Title, description, questions and passing_score are required'
      });
    }

    // Validate questions array
    if (!Array.isArray(questions) || questions.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Questions must be a non-empty array'
      });
    }

    // Create quiz
    const { data: quiz, error } = await supabase
      .from('quizzes')
      .insert({
        title,
        description,
        questions,
        passing_score,
        course_id: courseId,
        created_by: req.user.id
      })
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({
      success: true,
      data: quiz
    });
  } catch (err) {
    winston.error('Error adding quiz:', err);
    next(err);
  }
};