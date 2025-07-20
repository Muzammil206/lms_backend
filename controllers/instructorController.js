const { supabase } = require('../config');
const winston = require('winston');

// @desc    Get instructor profile
// @route   GET /api/v1/instructors/me
// @access  Private (Instructor)
exports.getProfile = async (req, res, next) => {
  try {
    // Get instructor profile with user details and courses
    const { data: instructor, error } = await supabase
      .from('instructors')
      .select(`
        *,
        user:users(username, email),
        courses:courses(title, description, duration, difficulty),
        expertise:skills(name, category)
      `)
      .eq('user_id', req.user.id)
      .single();

    if (error) throw error;
    if (!instructor) {
      return res.status(404).json({
        success: false,
        message: 'Instructor profile not found'
      });
    }

    res.status(200).json({
      success: true,
      data: instructor
    });
  } catch (err) {
    winston.error('Error getting instructor profile:', err);
    next(err);
  }
};

// @desc    Update instructor profile
// @route   PUT /api/v1/instructors/me
// @access  Private (Instructor)
exports.updateProfile = async (req, res, next) => {
  try {
    // First get current instructor to verify existence
    const { data: existingInstructor, error: fetchError } = await supabase
      .from('instructors')
      .select('*')
      .eq('user_id', req.user.id)
      .single();

    if (fetchError) throw fetchError;
    if (!existingInstructor) {
      return res.status(404).json({
        success: false,
        message: 'Instructor profile not found'
      });
    }

    // Update instructor profile
    const { data: instructor, error } = await supabase
      .from('instructors')
      .update(req.body)
      .eq('user_id', req.user.id)
      .select(`
        *,
        user:users(username, email),
        courses:courses(title, description, duration, difficulty),
        expertise:skills(name, category)
      `)
      .single();

    if (error) throw error;

    res.status(200).json({
      success: true,
      data: instructor
    });
  } catch (err) {
    winston.error('Error updating instructor profile:', err);
    next(err);
  }
};

// @desc    Get instructor courses
// @route   GET /api/v1/instructors/me/courses
// @access  Private (Instructor)
exports.getCourses = async (req, res, next) => {
  try {
    // First verify instructor exists
    const { data: instructor, error: instructorError } = await supabase
      .from('instructors')
      .select('id')
      .eq('user_id', req.user.id)
      .single();

    if (instructorError) throw instructorError;
    if (!instructor) {
      return res.status(404).json({
        success: false,
        message: 'Instructor profile not found'
      });
    }

    // Get instructor's courses
    const { data: courses, error } = await supabase
      .from('courses')
      .select('title, description, duration, difficulty, is_active')
      .eq('instructor_id', instructor.id);

    if (error) throw error;

    res.status(200).json({
      success: true,
      count: courses.length,
      data: courses.map(course => ({
        ...course,
        isActive: course.is_active
      }))
    });
  } catch (err) {
    winston.error('Error getting instructor courses:', err);
    next(err);
  }
};

// @desc    Add expertise
// @route   POST /api/v1/instructors/me/expertise/:skillId
// @access  Private (Instructor)
exports.addExpertise = async (req, res, next) => {
  try {
    // Verify skill exists
    const { data: skill, error: skillError } = await supabase
      .from('skills')
      .select('id')
      .eq('id', req.params.skillId)
      .single();

    if (skillError) throw skillError;
    if (!skill) {
      return res.status(404).json({
        success: false,
        message: 'Skill not found'
      });
    }

    // Get instructor ID
    const { data: instructor, error: instructorError } = await supabase
      .from('instructors')
      .select('id')
      .eq('user_id', req.user.id)
      .single();

    if (instructorError) throw instructorError;
    if (!instructor) {
      return res.status(404).json({
        success: false,
        message: 'Instructor profile not found'
      });
    }

    // Check if expertise already exists
    const { data: existingExpertise, error: expertiseError } = await supabase
      .from('instructor_skills')
      .select('*')
      .eq('instructor_id', instructor.id)
      .eq('skill_id', req.params.skillId);

    if (expertiseError) throw expertiseError;
    if (existingExpertise.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Skill already added to expertise'
      });
    }

    // Add expertise
    const { data: newExpertise, error } = await supabase
      .from('instructor_skills')
      .insert({
        instructor_id: instructor.id,
        skill_id: req.params.skillId
      })
      .select();

    if (error) throw error;

    // Get updated instructor profile
    const { data: updatedInstructor, error: profileError } = await supabase
      .from('instructors')
      .select(`
        *,
        expertise:skills(name, category)
      `)
      .eq('id', instructor.id)
      .single();

    if (profileError) throw profileError;

    res.status(200).json({
      success: true,
      data: updatedInstructor
    });
  } catch (err) {
    winston.error('Error adding expertise:', err);
    next(err);
  }
};

// @desc    Remove expertise
// @route   DELETE /api/v1/instructors/me/expertise/:skillId
// @access  Private (Instructor)
exports.removeExpertise = async (req, res, next) => {
  try {
    // Get instructor ID
    const { data: instructor, error: instructorError } = await supabase
      .from('instructors')
      .select('id')
      .eq('user_id', req.user.id)
      .single();

    if (instructorError) throw instructorError;
    if (!instructor) {
      return res.status(404).json({
        success: false,
        message: 'Instructor profile not found'
      });
    }

    // Remove expertise relationship
    const { error } = await supabase
      .from('instructor_skills')
      .delete()
      .eq('instructor_id', instructor.id)
      .eq('skill_id', req.params.skillId);

    if (error) throw error;

    // Get updated instructor profile
    const { data: updatedInstructor, error: profileError } = await supabase
      .from('instructors')
      .select(`
        *,
        expertise:skills(name, category)
      `)
      .eq('id', instructor.id)
      .single();

    if (profileError) throw profileError;

    res.status(200).json({
      success: true,
      data: updatedInstructor
    });
  } catch (err) {
    winston.error('Error removing expertise:', err);
    next(err);
  }
};
