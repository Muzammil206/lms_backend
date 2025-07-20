const { supabase } = require('../config');
const { protect, authorize } = require('../middleware/authMiddleware');
const winston = require('winston');

// @desc    Get all users
// @route   GET /api/v1/admin/users
// @access  Private/Admin
exports.getUsers = async (req, res, next) => {
  try {
    // Base query
    let query = supabase
      .from('users')
      .select('*', { count: 'exact' })
      .neq('role', 'system');

    // Filtering
    const filters = { ...req.query };
    const removeFields = ['select', 'sort', 'page', 'limit'];
    removeFields.forEach(param => delete filters[param]);

    // Apply filters
    Object.entries(filters).forEach(([key, value]) => {
      query = query.eq(key, value);
    });

    // Select fields
    if (req.query.select) {
      const fields = req.query.select.split(',');
      query = query.select(fields.join(','));
    }

    // Sort
    if (req.query.sort) {
      const sortBy = req.query.sort.split(',').map(field => {
        return field.startsWith('-') 
          ? { column: field.substring(1), order: 'desc' }
          : { column: field, order: 'asc' };
      });
      sortBy.forEach(sort => {
        query = query.order(sort.column, { ascending: sort.order === 'asc' });
      });
    } else {
      query = query.order('created_at', { ascending: false });
    }

    // Pagination
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 25;
    const startIndex = (page - 1) * limit;

    // Execute query with pagination
    const { data: users, error, count } = await query
      .range(startIndex, startIndex + limit - 1);

    if (error) throw error;

    // Pagination result
    const pagination = {};
    const total = count;

    if (startIndex + limit < total) {
      pagination.next = {
        page: page + 1,
        limit
      };
    }

    if (startIndex > 0) {
      pagination.prev = {
        page: page - 1,
        limit
      };
    }

    res.status(200).json({
      success: true,
      count: users.length,
      pagination,
      data: users
    });
  } catch (err) {
    winston.error('Error getting users:', err);
    next(err);
  }
};

// @desc    Get single user
// @route   GET /api/v1/admin/users/:id
// @access  Private/Admin
exports.getUser = async (req, res, next) => {
  try {
    const { data: user, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', req.params.id)
      .single();

    if (error) throw error;
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.status(200).json({
      success: true,
      data: user
    });
  } catch (err) {
    winston.error('Error getting user:', err);
    next(err);
  }
};

// @desc    Update user
// @route   PUT /api/v1/admin/users/:id
// @access  Private/Admin
exports.updateUser = async (req, res, next) => {
  try {
    const { data: user, error } = await supabase
      .from('users')
      .update(req.body)
      .eq('id', req.params.id)
      .select()
      .single();

    if (error) throw error;
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.status(200).json({
      success: true,
      data: user
    });
  } catch (err) {
    winston.error('Error updating user:', err);
    next(err);
  }
};

// @desc    Delete user
// @route   DELETE /api/v1/admin/users/:id
// @access  Private/Admin
exports.deleteUser = async (req, res, next) => {
  try {
    // First delete user from auth
    const { error: authError } = await supabase.auth.admin.deleteUser(req.params.id);
    if (authError) throw authError;

    // Then delete from public.users table
    const { error } = await supabase
      .from('users')
      .delete()
      .eq('id', req.params.id);

    if (error) throw error;

    res.status(200).json({
      success: true,
      data: {}
    });
  } catch (err) {
    winston.error('Error deleting user:', err);
    next(err);
  }
};

// @desc    Get system statistics
// @route   GET /api/v1/admin/stats
// @access  Private/Admin
exports.getStats = async (req, res, next) => {
  try {
    // Get counts from all tables
    const { count: users } = await supabase
      .from('users')
      .select('*', { count: 'exact', head: true });

    const { count: courses } = await supabase
      .from('courses')
      .select('*', { count: 'exact', head: true });

    const { count: skills } = await supabase
      .from('skills')
      .select('*', { count: 'exact', head: true });

    res.status(200).json({
      success: true,
      data: {
        users,
        courses,
        skills
      }
    });
  } catch (err) {
    winston.error('Error getting system stats:', err);
    next(err);
  }
};

// @desc    Toggle course status
// @route   PUT /api/v1/admin/courses/:id/toggle
// @access  Private/Admin
exports.toggleCourseStatus = async (req, res, next) => {
  try {
    // Get current status
    const { data: course, error: fetchError } = await supabase
      .from('courses')
      .select('is_active')
      .eq('id', req.params.id)
      .single();

    if (fetchError) throw fetchError;
    if (!course) {
      return res.status(404).json({
        success: false,
        message: 'Course not found'
      });
    }

    // Toggle status
    const { data: updatedCourse, error } = await supabase
      .from('courses')
      .update({ is_active: !course.is_active })
      .eq('id', req.params.id)
      .select()
      .single();

    if (error) throw error;

    res.status(200).json({
      success: true,
      data: updatedCourse
    });
  } catch (err) {
    winston.error('Error toggling course status:', err);
    next(err);
  }
};

// @desc    Flag course for review
// @route   PUT /api/v1/admin/courses/:id/flag
// @access  Private/Admin
exports.flagCourse = async (req, res, next) => {
  try {
    // Increment flag count
    const { data: course, error } = await supabase.rpc('increment_flags', {
      course_id: req.params.id
    });

    if (error) throw error;
    if (!course) {
      return res.status(404).json({
        success: false,
        message: 'Course not found'
      });
    }

    res.status(200).json({
      success: true,
      data: course
    });
  } catch (err) {
    winston.error('Error flagging course:', err);
    next(err);
  }
};
