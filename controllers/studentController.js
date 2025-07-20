const { supabase } = require('../config');
const { protect } = require('../middleware/authMiddleware');
const winston = require('winston');


exports.getProfile = async (req, res, next) => {
  try {
    // Get student profile with relationships
    const { data: student, error } = await supabase
      .from('students')
      .select(`
        *,
        user:users(username, email, role),
        enrolledCourses:student_courses(
          course:courses(title, description, duration, difficulty),
          progress,
          completed
        ),
        skills:student_skills(
          skill:skills(name, category),
          proficiency
        )
      `)
      .eq('user_id', req.user.id)
      .single();

    if (error) throw error;
    if (!student) {
      return res.status(404).json({
        success: false,
        message: 'Student profile not found'
      });
    }

    // Format response to match previous structure
    const formattedResponse = {
      ...student,
      enrolledCourses: student.enrolledCourses.map(ec => ({
        course: ec.course,
        progress: ec.progress,
        completed: ec.completed
      })),
      skills: student.skills.map(s => ({
        skill: s.skill,
        proficiency: s.proficiency
      }))
    };

    res.status(200).json({
      success: true,
      data: formattedResponse
    });
  } catch (err) {
    winston.error('Error getting student profile:', err);
    next(err);
  }
};

// @desc    Enroll in a course
// @route   POST /api/v1/students/courses/:courseId
// @access  Private
exports.enrollCourse = async (req, res, next) => {
  try {
    // Verify course exists
    const { data: course, error: courseError } = await supabase
      .from('courses')
      .select('id')
      .eq('id', req.params.courseId)
      .single();

    if (courseError) throw courseError;
    if (!course) {
      return res.status(404).json({
        success: false,
        message: 'Course not found'
      });
    }

    // Get student ID
    const { data: student, error: studentError } = await supabase
      .from('students')
      .select('id')
      .eq('user_id', req.user.id)
      .single();

    if (studentError) throw studentError;
    if (!student) {
      return res.status(404).json({
        success: false,
        message: 'Student profile not found'
      });
    }

    // Check if already enrolled
    const { data: existingEnrollment, error: enrollmentError } = await supabase
      .from('student_courses')
      .select('*')
      .eq('student_id', student.id)
      .eq('course_id', req.params.courseId);

    if (enrollmentError) throw enrollmentError;
    if (existingEnrollment.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Already enrolled in this course'
      });
    }

    // Create enrollment
    const { error } = await supabase
      .from('student_courses')
      .insert({
        student_id: student.id,
        course_id: req.params.courseId,
        progress: 0,
        completed: false
      });

    if (error) throw error;

    res.status(200).json({
      success: true,
      message: 'Successfully enrolled in course'
    });
  } catch (err) {
    winston.error('Error enrolling in course:', err);
    next(err);
  }
};

// @desc    Update course progress
// @route   PUT /api/v1/students/courses/:courseId/progress
// @access  Private
exports.updateProgress = async (req, res, next) => {
  try {
    const { progress } = req.body;

    if (progress < 0 || progress > 100) {
      return res.status(400).json({
        success: false,
        message: 'Progress must be between 0 and 100'
      });
    }

    // Get student ID
    const { data: student, error: studentError } = await supabase
      .from('students')
      .select('id')
      .eq('user_id', req.user.id)
      .single();

    if (studentError) throw studentError;
    if (!student) {
      return res.status(404).json({
        success: false,
        message: 'Student profile not found'
      });
    }

    // Update progress
    const { data: updatedEnrollment, error } = await supabase
      .from('student_courses')
      .update({
        progress: progress,
        completed: progress === 100,
        completion_date: progress === 100 ? new Date().toISOString() : null
      })
      .eq('student_id', student.id)
      .eq('course_id', req.params.courseId)
      .select('*')
      .single();

    if (error) throw error;
    if (!updatedEnrollment) {
      return res.status(404).json({
        success: false,
        message: 'Course enrollment not found'
      });
    }

    // Get updated student profile
    const { data: updatedStudent, error: profileError } = await supabase
      .from('students')
      .select(`
        *,
        enrolledCourses:student_courses(
          course:courses(title, description, duration, difficulty),
          progress,
          completed
        )
      `)
      .eq('id', student.id)
      .single();

    if (profileError) throw profileError;

    res.status(200).json({
      success: true,
      data: updatedStudent
    });
  } catch (err) {
    winston.error('Error updating course progress:', err);
    next(err);
  }
};

// @desc    Add acquired skill
// @route   POST /api/v1/students/skills/:skillId
// @access  Private
exports.addSkill = async (req, res, next) => {
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

    // Get student ID
    const { data: student, error: studentError } = await supabase
      .from('students')
      .select('id')
      .eq('user_id', req.user.id)
      .single();

    if (studentError) throw studentError;
    if (!student) {
      return res.status(404).json({
        success: false,
        message: 'Student profile not found'
      });
    }

    // Check if skill already exists
    const { data: existingSkill, error: existingError } = await supabase
      .from('student_skills')
      .select('*')
      .eq('student_id', student.id)
      .eq('skill_id', req.params.skillId);

    if (existingError) throw existingError;
    if (existingSkill.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Skill already added'
      });
    }

    // Add skill
    const { error } = await supabase
      .from('student_skills')
      .insert({
        student_id: student.id,
        skill_id: req.params.skillId,
        proficiency: 1,
        acquired_date: new Date().toISOString()
      });

    if (error) throw error;

    // Update skill popularity
    await supabase.rpc('increment_skill_popularity', {
      skill_id: req.params.skillId
    });

    res.status(200).json({
      success: true,
      message: 'Successfully added skill'
    });
  } catch (err) {
    winston.error('Error adding skill:', err);
    next(err);
  }
};

// @desc    Update skill proficiency
// @route   PUT /api/v1/students/skills/:skillId
// @access  Private
exports.updateProficiency = async (req, res, next) => {
  try {
    const { proficiency } = req.body;

    if (proficiency < 1 || proficiency > 5) {
      return res.status(400).json({
        success: false,
        message: 'Proficiency must be between 1 and 5'
      });
    }

    const student = await Student.findOneAndUpdate(
      {
        user: req.user.id,
        'skills.skill': req.params.skillId
      },
      {
        $set: {
          'skills.$.proficiency': proficiency
        }
      },
      { new: true, runValidators: true }
    );

    if (!student) {
      return res.status(404).json({
        success: false,
        message: 'Student or skill not found'
      });
    }

    res.status(200).json({
      success: true,
      data: student
    });
  } catch (err) {
    winston.error('Error updating skill proficiency:', err);
    next(err);
  }
};
