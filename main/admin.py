from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'profileId', 'firstName', 'lastName', 'email']
    list_per_page = 20

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order']
    list_per_page = 20

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'duration']
    list_editable = ['price', 'duration', 'category']
    list_per_page = 20

admin.site.register(SkillCategory)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'comment', 'star', 'date']
    list_editable = ['star']
    list_per_page = 20


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'amount', 'status', 'date']
    list_editable = ['status']
    list_per_page = 20

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'link']
    list_per_page = 20

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['course', 'order', 'title']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'link']
    list_per_page = 20

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['topic', 'order', 'active']
    list_editable = ['order', 'active']
    list_per_page = 20
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['skill', 'status', 'course', 'date', 'url']
    list_filter = ['skill', 'status']
    list_per_page = 20

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['student', 'course']
    list_per_page = 20
    
admin.site.register(Quiz)
admin.site.register(Submission)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'order', 'question', 'answer']
    list_per_page = 20

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'remark', 'created']
    list_per_page = 20

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'seen', 'created']
    list_per_page = 20

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['date']
    list_per_page = 20

admin.site.register(Webhook)
admin.site.register(Log)