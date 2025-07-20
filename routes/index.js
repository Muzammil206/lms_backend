const express = require('express');
const authRoutes = require('./authRoutes');
const studentRoutes = require('./studentRoutes');
const courseRoutes = require('./courseRoutes');
const skillRoutes = require('./skillRoutes');
const instructorRoutes = require('./instructorRoutes');
const adminRoutes = require('./adminRoutes');
const errorHandler = require('../middleware/errorHandler');

const router = express.Router();

// API version 1 routes
router.use('/api/v1/auth', authRoutes);
router.use('/api/v1/students', studentRoutes);
router.use('/api/v1/courses', courseRoutes);
router.use('/api/v1/skills', skillRoutes);
router.use('/api/v1/instructors', instructorRoutes);
router.use('/api/v1/admin', adminRoutes);

// Error handling middleware
router.use(errorHandler);

module.exports = router;
