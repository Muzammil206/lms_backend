const mongoose = require('mongoose');

const StudentSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  enrolledCourses: [
    {
      course: {
        type: mongoose.Schema.ObjectId,
        ref: 'Course'
      },
      progress: {
        type: Number,
        default: 0,
        min: 0,
        max: 100
      },
      completed: {
        type: Boolean,
        default: false
      },
      completionDate: Date
    }
  ],
  skills: [
    {
      skill: {
        type: mongoose.Schema.ObjectId,
        ref: 'Skill'
      },
      proficiency: {
        type: Number,
        default: 1,
        min: 1,
        max: 5
      },
      acquiredDate: {
        type: Date,
        default: Date.now
      }
    }
  ],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Create student profile when user registers
StudentSchema.post('save', async function(doc) {
  await doc.populate({
    path: 'user',
    select: 'username email role'
  }).execPopulate();
});

module.exports = mongoose.model('Student', StudentSchema);
