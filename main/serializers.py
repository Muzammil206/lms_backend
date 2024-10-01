from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class LmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LMS
        fields = ['title', 'subtitle', 'primary_email', 'secondary_email', 'primary_phone',
                  'secondary_phone', 'privacy_policy', 'terms_and_conditions', 'about', 'logo',
                  'icon', 'privacy_pdf', 'terms_pdf']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'firstName', 'lastName', 'email', 'profileId', '_2fa_enabled']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'order', 'title', 'image']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'pdf_file', 'png_file']

class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = ['id', 'title', 'image']

class SkillSerializer(serializers.ModelSerializer):
    category = SkillCategorySerializer(many=False, read_only=True)
    class Meta:
        model = Skill
        fields = ['id', 'title', 'category', 'description', 'image', 'duration', 'price']

class ScheduleSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(many=False, read_only=True)
    course = CourseSerializer(many=False, read_only=True)
    class Meta:
        model = Schedule
        fields = ['id', 'status', 'skill', 'course', 'date', 'url', 'venue', 'description']

class ReviewSerializer(serializers.ModelSerializer):
    user = StudentSerializer(many=False, read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'user', 'comment', 'star', 'date']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'reference_id', 'email', 'amount', 'status', 'date']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'link']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'order', 'title']

class ProjectSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'course', 'title', 'description', 'image', 'link',
                  'created', 'deadline']

class ProjectASerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)
    assigned_to = StudentSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'course', 'title', 'description', 'image', 'link',
                  'created', 'deadline', 'assigned_to']

class SubmissionSerializer(serializers.ModelSerializer):
    student = StudentSerializer(many=False, read_only=True)
    class Meta:
        model = Submission
        fields = ['id', 'source_code', 'score', 'file', 'live_url', 'comment', 'student']

class QuizSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'course', 'active', 'done']

class MaterialSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(many=False, read_only=True)
    class Meta:
        model = Material
        fields = ['id', 'order', 'read', 'topic', 'content', 'active']
        
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'order', 'question', 'image', 'optionA', 'optionB',
                  'optionC', 'optionD', 'answer', 'reason']

class ScoreSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(many=False, read_only=True)
    student = StudentSerializer(many=False, read_only=True)
    class Meta:
        model = Score
        fields = ['id', 'quiz', 'student', 'score', 'remark', 'created']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'details', 'created']
