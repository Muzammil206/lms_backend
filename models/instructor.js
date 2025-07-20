const mongoose = require('mongoose');

const InstructorSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  courses: [
    {
      type: mongoose.Schema.ObjectId,
      ref: 'Course'
    }
  ],
  bio: {
    type: String,
    maxlength: [500, 'Bio cannot be more than 500 characters']
  },
  expertise: [
    {
      type: mongoose.Schema.ObjectId,
      ref: 'Skill'
    }
  ],
  socialMedia: {
    twitter: String,
    linkedin: String,
    github: String
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Populate user data when querying instructors
InstructorSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'user',
    select: 'username email'
  });
  next();
});

module.exports = mongoose.model('Instructor', InstructorSchema);
