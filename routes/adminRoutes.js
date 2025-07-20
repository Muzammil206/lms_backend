const express = require('express');
const adminController = require('../controllers/adminController');
const { protect, authorize } = require('../middleware/authMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);
router.use(authorize('admin'));

// User routes
router.get('/users', adminController.getUsers);
router.get('/users/:id', adminController.getUser);
router.put('/users/:id', adminController.updateUser);
router.delete('/users/:id', adminController.deleteUser);

// Stats route
router.get('/stats', adminController.getStats);

// Course moderation routes
router.put('/courses/:id/status', adminController.toggleCourseStatus);
router.put('/courses/:id/flag', adminController.flagCourse);

module.exports = router;
