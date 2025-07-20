const express = require('express');
const instructorController = require('../controllers/instructorController');
const { protect, authorize } = require('../middleware/authMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);
router.use(authorize('instructor'));

// Profile routes
router.get('/me', instructorController.getProfile);
router.put('/me', instructorController.updateProfile);

// Course routes
router.get('/me/courses', instructorController.getCourses);

// Expertise routes
router.post('/me/expertise/:skillId', instructorController.addExpertise);
router.delete('/me/expertise/:skillId', instructorController.removeExpertise);

module.exports = router;
