const { supabase } = require('../config');
const { protect, authorize } = require('../middleware/authMiddleware');
const winston = require('winston');

// @desc    Get all skills
// @route   GET /api/v1/skills
// @access  Public
exports.getSkills = async (req, res, next) => {
  try {
    // Base query
    let query = supabase
      .from('skills')
      .select('*');

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
      query = query.order('popularity', { ascending: false });
    }

    // Pagination
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 25;
    const startIndex = (page - 1) * limit;

    // Execute query with pagination
    const { data: skills, error, count } = await query
      .range(startIndex, startIndex + limit - 1);

    if (error) throw error;

    // Pagination result
    const pagination = {};
    const total = count || (await supabase
      .from('skills')
      .select('*', { count: 'exact', head: true })).count;

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
      count: skills.length,
      pagination,
      data: skills
    });
  } catch (err) {
    winston.error('Error getting skills:', err);
    next(err);
  }
};

// @desc    Get single skill
// @route   GET /api/v1/skills/:id
// @access  Public
exports.getSkill = async (req, res, next) => {
  try {
    const { data: skill, error } = await supabase
      .from('skills')
      .select('*')
      .eq('id', req.params.id)
      .single();

    if (error) throw error;
    if (!skill) {
      return res.status(404).json({
        success: false,
        message: 'Skill not found'
      });
    }

    res.status(200).json({
      success: true,
      data: skill
    });
  } catch (err) {
    winston.error('Error getting skill:', err);
    next(err);
  }
};

// @desc    Create skill
// @route   POST /api/v1/skills
// @access  Private (Admin)
exports.createSkill = async (req, res, next) => {
  try {
    const { data: skill, error } = await supabase
      .from('skills')
      .insert(req.body)
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({
      success: true,
      data: skill
    });
  } catch (err) {
    winston.error('Error creating skill:', err);
    next(err);
  }
};

// @desc    Update skill
// @route   PUT /api/v1/skills/:id
// @access  Private (Admin)
exports.updateSkill = async (req, res, next) => {
  try {
    const { data: skill, error } = await supabase
      .from('skills')
      .update(req.body)
      .eq('id', req.params.id)
      .select()
      .single();

    if (error) throw error;
    if (!skill) {
      return res.status(404).json({
        success: false,
        message: 'Skill not found'
      });
    }

    res.status(200).json({
      success: true,
      data: skill
    });
  } catch (err) {
    winston.error('Error updating skill:', err);
    next(err);
  }
};

// @desc    Delete skill
// @route   DELETE /api/v1/skills/:id
// @access  Private (Admin)
exports.deleteSkill = async (req, res, next) => {
  try {
    const { error } = await supabase
      .from('skills')
      .delete()
      .eq('id', req.params.id);

    if (error) throw error;

    res.status(200).json({
      success: true,
      data: {}
    });
  } catch (err) {
    winston.error('Error deleting skill:', err);
    next(err);
  }
};
