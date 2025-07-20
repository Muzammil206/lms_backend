const { supabase } = require('../config');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const winston = require('winston');
const sendEmail = require('../utils/email');

// Generate token
const getToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRE
  });
};

// @desc    Register user
// @route   POST /api/v1/auth/register
// @access  Public
exports.register = async (req, res, next) => {

  
  try {
    const { username, email, password, role } = req.body;
   


    // Sign up user with Supabase
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          username,
          role: role || 'user'
        }
      }
    });

    if (error) {
      winston.error('Supabase registration error:', error);
      throw error;
    }

    // Create user profile in public.users table
    const { error: profileError } = await supabase
      .from('users')
      .insert([{
        id: data.user.id,
        username,
        email,
        role: role || 'user'
      }]);

    if (profileError) {
      winston.error('Supabase profile creation error:', profileError);
      throw profileError;
    }

    // Return session instead of JWT
    res.status(201).json({
      success: true,
      session: data.session
    });
  } catch (err) {
    winston.error('Error registering user:', err);
    next(err);
  }
};

// @desc    Login user
// @route   POST /api/v1/auth/login
// @access  Public
exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Please provide an email and password'
      });
    }

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
    }

    res.status(200).json({
      success: true,
      session: data.session
    });
  } catch (err) {
    winston.error('Error logging in user:', err);
    next(err);
  }
};

// @desc    Get current logged in user
// @route   GET /api/v1/auth/me
// @access  Private
exports.getMe = async (req, res, next) => {
  try {
    const { data: { user }, error } = await supabase.auth.getUser();

    if (error) {
      winston.error('Supabase get user error:', error);
      throw error;
    }

    // Get additional user data from public.users table
    const { data: profile, error: profileError } = await supabase
      .from('users')
      .select('id, username, email, role, created_at')
      .eq('id', user.id)
      .single();

    if (profileError) {
      winston.error('Supabase profile fetch error:', profileError);
      throw profileError;
    }

    res.status(200).json({
      success: true,
      data: {
        ...profile,
        createdAt: profile.created_at
      }
    });
  } catch (err) {
    winston.error('Error getting user profile:', err);
    next(err);
  }
};


