const express = require('express');
const courseController = require('../controllers/courseController');
const { protect, authorize } = require('../middleware/authMiddleware');

const router = express.Router();

// Public routes
router.get('/', courseController.getCourses);
router.get('/:id', courseController.getCourse);

// Protected routes (require authentication)
router.use(protect);

// Instructor-only routes
// router.use(authorize('admin'));

router.post('/', courseController.createCourseWithModules);
router.put('/:id', courseController.updateCourse);
router.delete('/:id', courseController.deleteCourse);
router.post('/:id/materials', courseController.addMaterial);
router.post('/:id/quizzes', courseController.addQuiz);

module.exports = router;
