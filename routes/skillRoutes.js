const express = require('express');
const skillController = require('../controllers/skillController');
const { protect, authorize } = require('../middleware/authMiddleware');

const router = express.Router();

// Public routes
router.get('/', skillController.getSkills);
router.get('/:id', skillController.getSkill);

// Protected routes (require authentication)
router.use(protect);

// Admin-only routes
router.use(authorize('admin'));

router.post('/', skillController.createSkill);
router.put('/:id', skillController.updateSkill);
router.delete('/:id', skillController.deleteSkill);

module.exports = router;
