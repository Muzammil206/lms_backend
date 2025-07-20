const express = require('express');
const studentController = require('../controllers/studentController');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Student profile routes
router.get('/me', studentController.getProfile);

// Course routes
router.post('/courses/:courseId', studentController.enrollCourse);
router.put('/courses/:courseId/progress', studentController.updateProgress);

// Skill routes
router.post('/skills/:skillId', studentController.addSkill);
router.put('/skills/:skillId', studentController.updateProficiency);

module.exports = router;
