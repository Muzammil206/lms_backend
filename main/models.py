from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from tinymce.models import HTMLField
from .paystack import Paystack
from django.utils.encoding import force_str
import re
import random
from .utils import *


def generateCode(n):
    key = ''
    for i in range(n):
        rand_char = random.choice("1234567890")
        key += rand_char
    return key

# Create your models here.
class LMS(models.Model):
    title = models.CharField(max_length=100, default="Hoistflick", blank=True)
    subtitle = models.CharField(max_length=100, default="")
    primary_email = models.EmailField(blank=True)
    secondary_email = models.EmailField(blank=True)
    primary_phone = models.CharField(max_length=15, blank=True)
    secondary_phone = models.CharField(max_length=15, blank=True)
    privacy_policy = HTMLField(blank=True)
    terms_and_conditions = HTMLField(blank=True)
    about = HTMLField(blank=True)
    logo = models.ImageField(upload_to="lms/", blank=True, null=True)
    icon = models.ImageField(upload_to="lms/", blank=True, null=True)
    privacy_pdf = models.FileField(upload_to="lms/", blank=True, null=True)
    terms_pdf = models.FileField(upload_to="lms/", blank=True, null=True)
    def __str__(self):
        return f"{self.title}: {self.subtitle}"

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student")
    firstName = models.CharField(max_length=100, verbose_name="First Name", null=True)
    lastName = models.CharField(max_length=100, verbose_name="Last Name", null=True)
    email = models.EmailField(max_length=200, verbose_name="Email", null=True, blank=True)
    profileId = models.CharField(max_length=8, unique=True, null=True)
    confirmationCode = models.CharField(max_length=8, null=True, blank=True)
    confirmationDate = models.DateTimeField(null=True, blank=True)
    _2fa_code = models.CharField(max_length=8, null=True, blank=True)
    _2fa_date = models.DateTimeField(null=True, blank=True)
    verificationCode = models.CharField(max_length=6, null=True, blank=True)
    confirmedEmail = models.BooleanField(default=False)
    _2fa_enabled = models.BooleanField(default=False)
    userData = models.JSONField(default=dict, blank=True)
    def __str__(self):
        return f"{self.firstName} {self.lastName}"
    class Meta:
        ordering = ['firstName']

class Course(models.Model):
    title = models.CharField(max_length=250, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    order = models.IntegerField(default=1)
    image = models.ImageField(upload_to="hackode/courses/", null=True, blank=True)
    def __str__(self):
        return f'{self.title}'
    class Meta:
        ordering = ['order']
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super(Course, self).delete(*args, **kwargs)

class SkillCategory(models.Model):
    title = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to="hackode/skills/categories/", null=True, blank=True)
    def __str__(self):
        return f'{self.title}'
    class Meta:
        ordering = ['title']
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super(SkillCategory, self).delete(*args, **kwargs)

class Skill(models.Model):
    title = models.CharField(max_length=250, blank=True)
    description = HTMLField(blank=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="skills")
    image = models.ImageField(upload_to="hackode/skills/", null=True, blank=True)
    courses = models.ManyToManyField(Course, related_name="skills", blank=True)
    students = models.ManyToManyField(Student, related_name="courses_registered", blank=True)
    price = models.PositiveBigIntegerField(default=0)
    duration = models.CharField(max_length=200, blank=True, default="3 Months")
    def __str__(self):
        return f'{self.title}'
    class Meta:
        ordering = ['title']
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super(Skill, self).delete(*args, **kwargs)

class Review(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="reviews")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField(blank=True)
    star = models.PositiveIntegerField(default=5)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.user.__str__()}\'s review on {self.skill.title}'
    class Meta:
        ordering = ['-date']

class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="topics", null=True, blank=True)
    title = models.CharField(max_length=250, blank=True)
    slug = models.CharField(max_length=250, blank=True)
    order = models.IntegerField(default=0)
    def __str__(self):
        return f'{self.course.title} - {self.title}'
    def save(self, *args, **kwargs):
        if self.order == 0:
            last_topic = Topic.objects.filter(course=self.course).order_by('-order').first()
            if last_topic:
                self.order = last_topic.order + 1
            else:
                self.order = 1
        super(Topic, self).save(*args, **kwargs)
    class Meta:
        ordering = ['order']

class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="videos", null=True, blank=True)
    title = models.CharField(max_length=250, blank=True)
    link = models.URLField(blank=True)
    description = HTMLField(blank=True)
    def __str__(self):
        return f'{self.course.title} - {self.title}'
    class Meta:
        ordering = ['title']

class Project(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="projects", null=True, blank=True)
    title = models.CharField(max_length=250, blank=True)
    description = HTMLField(blank=True)
    image = models.ImageField(upload_to="hackode/courses/projects/", null=True, blank=True)
    link = models.URLField(blank=True)
    sent = models.BooleanField(default=False)
    created = models.DateField(default=timezone.now)
    assigned_to = models.ManyToManyField(Student, blank=True, related_name="projects_assigned")
    deadline = models.DateField(null=True, blank=True)
    def __str__(self):
        return f'{self.title} - {self.course.title}'
    class Meta:
        ordering = ['-created']
    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        if not self.sent:
            ems = [s.user.email for s in self.assigned_to.all()]
            print(ems)
            send_project_notification(ems, self.deadline, self.title, self.course.title)
            self.sent = True
            super(Project, self).save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super(Project, self).delete(*args, **kwargs)

class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions", null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="submissions", null=True, blank=True)
    source_code = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    score = models.IntegerField(verbose_name="Total Score", default=0)
    file = models.FileField(null=True, blank=True, upload_to=f"projects/files/{generateCode(5)}/")
    comment = HTMLField(null=True, blank=True)
    class Meta:
        ordering = ['-score']
    def __str__(self):
        return f'{self.student.__str__()} - {self.project.title}'
    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete()
        super(Submission, self).delete(*args, **kwargs)

class Quiz(models.Model):
    title = models.CharField(max_length=200, blank=True, default="a")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    active = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    class Meta:
        ordering = ['created']
    def __str__(self):
        return f'{self.title}'

class Material(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="materials", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    content = HTMLField(blank=True)
    active = models.BooleanField(default=True)
    read_by = models.ManyToManyField(Student, related_name="materials_read", blank=True)
    read = models.BooleanField(default=False)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return f'{self.topic.__str__()}\'s material'
    def save(self, *args, **kwargs):
        if self.order == 0:
            topic = self.topic
            if topic:
                self.order = topic.order
            else:
                self.order = 1
        super(Material, self).save(*args, **kwargs)

class Schedule(models.Model):
    skill = models.ForeignKey(Skill, null=True, on_delete=models.CASCADE, related_name="schedules")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="schedules")
    students =  models.ManyToManyField(Student, related_name="schedules", blank=True)
    date = models.DateTimeField(default=timezone.now)
    url = models.URLField(blank=True)
    venue = models.CharField(max_length=150, blank=True)
    description = HTMLField(blank=True)
    emails = models.CharField(max_length=25600, default="", blank=True)
    sent = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=(
        ("Pending", "Pending"),
        ("Ongoing", "Ongoing"),
        ("Done", "Done")
    ), default="Pending")
    class Meta:
        ordering = ['-date']
    def __str__(self):
        return f'{self.course.title}\'s schedule'
    def save(self, *args, **kwargs):
        super(Schedule, self).save(*args, **kwargs)
        ems = ",".join(s.user.email for s in self.students.all())
        self.emails = ems
        super(Schedule, self).save(*args, **kwargs)
        if not self.sent:
            es = self.get_email_list()
            print(es)
            da = self.date.strftime("%d/%m/%Y %I:%M%p")
            send_schedule_notification(es, da, self.venue, self.description, self.course.title, self.url)
            self.sent = True
            super(Schedule, self).save(*args, **kwargs)
    def get_email_list(self):
        return [email.strip() for email in self.emails.split(',')]
    
#Question Model
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name="Quiz", null=True)
    order = models.PositiveIntegerField(verbose_name="Question Order", default=1)
    question = HTMLField(null=True, blank=True, verbose_name="Question")
    image = models.ImageField(upload_to='questions/image/', blank=True, null=True, verbose_name='Question image')
    optionA = models.CharField(max_length=200, null=True, blank=True, verbose_name="Option A")
    optionB = models.CharField(max_length=200, null=True, blank=True, verbose_name="Option B")
    optionC = models.CharField(max_length=200, null=True, blank=True, verbose_name="Option C")
    optionD = models.CharField(max_length=200, null=True, blank=True, verbose_name="Option D")
    cat = (('optionA', 'optionA'), ('optionB', 'optionB'), ('optionC', 'optionC'), ('optionD', 'optionD'))
    answer = models.CharField(max_length=200, choices=cat)
    reason = models.TextField(default="", blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Question {self.order}'
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super(Question, self).delete(*args, **kwargs)
        
# Score Model
REMARK_CHOICES = (
    ('Gold', 'Gold'),
    ('Silver', 'Silver'),
    ('Bronze', 'Bronze'),
    ('Copper', 'Copper'),
)
class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="scores")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="score")
    score = models.IntegerField(verbose_name="Total Score")
    remark = models.CharField(max_length=100, choices=REMARK_CHOICES, null=True, blank=True, verbose_name="Remark")
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.student.__str__()}\'s score'
    class Meta:
        ordering = ['-score']

class Certificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="certificates", null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates", null=True, blank=True)
    pdf_file = models.FileField(null=True, upload_to=f"hackode/certificates/pdf/")
    png_file = models.FileField(null=True, upload_to=f"hackode/certificates/image/")
    def __str__(self):
        return f'{self.student.__str__()} - {self.course.title}'
    def delete(self, *args, **kwargs):
        if self.pdf_file:
            self.pdf_file.delete()
        if self.png_file:
            self.png_file.delete()
        super(Certificate, self).delete(*args, **kwargs)

TRANSACTION_STATUS = (
    ('Pending', 'Pending'),
    ('Successful', 'Successful'),
    ('Failed', 'Failed')
)
class Payment(models.Model):
    user = models.ForeignKey(Student, verbose_name="Payer Name", on_delete=models.CASCADE, related_name="transactions")
    skill = models.ForeignKey(Skill, verbose_name="Skill", on_delete=models.SET_NULL, null=True, related_name="payments")
    reference_id = models.CharField(verbose_name='Reference ID', max_length=250, null=True, blank=True)
    email = models.EmailField(max_length=250, null=True, blank=True)
    amount = models.PositiveIntegerField(default=0, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Transaction Date")
    receipt = models.FileField(null=True, blank=True, upload_to=f"receipts/{generateCode(5)}/")
    status = models.CharField(choices=TRANSACTION_STATUS, max_length=50, default="Pending")
    def __str__(self):
        return f'Ref: {self.reference_id}: {self.user.__str__()}'
    class Meta:
        ordering = ['-date']
    def delete(self, *args, **kwargs):
        if self.receipt:
            self.receipt.delete()
        super(Payment, self).delete(*args, **kwargs)
    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.reference_id, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.status = 'Successful'
            self.save()
        if self.status == 'Successful':
            return True
        return False

class Task(models.Model):
    date = models.DateField()
    def __str__(self):
        return f'{self.date}'
    class Meta:
        ordering = ['-date']

class Notification(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notifications", null=True)
    title = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    seen =  models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return f'{self.title}'

class Log(models.Model):
    log = models.CharField(max_length=200)
    details = models.JSONField(default=dict)
    created = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return f'{self.log}'

WEBHOOK_TYPE = (
    ('customerId', 'customerId'),
    ('Dispute', 'Dispute'),
    ('Refund', 'Refund'),
    ('DVA', 'DVA'),
    ('Invoice', 'Invoice'),
    ('Subscription', 'Subscription'),
    ('Transaction', 'Transaction'),
    ('Transfer', 'Transfer')
)
class Webhook(models.Model):
    type = models.CharField(max_length=50)
    reference = models.CharField(max_length=50)
    details = models.JSONField(default=dict)
    created = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return f'{self.reference} - {self.type}'
