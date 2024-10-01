from rest_framework import generics, viewsets
from .models import *
from .serializers import *
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import action
from django.contrib.auth import login, authenticate, logout
import re
from django.db.models import Q
from .encrypt_utils import encrypt, decrypt
from django.utils.crypto import get_random_string
import random
from .utils import *
import openai
import string
from django.http import FileResponse
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta
#from weasyprint import HTML, CSS
import io
import sys
import contextlib
from .py_paystack import Paystack

paystack_init = Paystack(settings.PAYSTACK_SECRET_KEY)
# Create your views here.
def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

def generate_token():
    key = ''
    for i in range(60):
        rand_char = random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
        key += rand_char
    return key

def generate(n):
    chars = string.ascii_lowercase + string.digits
    random_combination = ''.join(random.choice(chars) for _ in range(n))
    return random_combination

def generate_key(n):
    chars = string.ascii_uppercase + string.digits
    random_combination = ''.join(random.choice(chars) for _ in range(n))
    return random_combination

def generateCode(n):
    key = ''
    for i in range(n):
        rand_char = random.choice("1234567890")
        key += rand_char
    return key

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
        return False
    return True

def is_valid_username(username):
    pattern = r'^[a-zA-Z0-9]+$'
    if re.match(pattern, username):
        return True
    else:
        return False

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({
                    'message': "Invalid login credentials."
                })
        if user.check_password(password):
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                profile = Student.objects.get(user=user)
                if not profile.confirmedEmail:
                    return Response({
                        'message': f"Your account has not been activated. Please confirm your email to activate your account"
                    })
                if profile._2fa_enabled:
                    code = generateCode(8)
                    profile._2fa_code = code
                    profile.save()
                    confirmation_login(user.email, profile.firstName, code)
                    profile._2fa_date = timezone.now()
                    profile.save()
                    ho = user.email.split('@')[1]
                    return Response({
                        'message': f"Confirmation code has been sent to {user.email[:5]}*****@{ho}. It expires in 10 minutes.",
                        'email': user.email
                    })
                else:
                    #token.delete()
                    #new_token = Token.objects.create(user=user)
                    Log.objects.create(log=f"{user.username} logged in.", details={
                        "profile_id": f"{profile.profileId}",
                        "2FA_enabled": False
                    })
                    return Response({
                        'token': token.key
                    })
            else:
                return Response({
                    'message': "Your account has been deactivated. Kindly contact the administrator for more enquiries."
                })
        else:
            return Response({
                'message': "Invalid login credentials."
            })

class LMSViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LMS.objects.all()
    serializer_class = LmsSerializer
    permission_classes = [AllowAny]

class SetupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False,
            methods=['post'])
    def create_account(self, request, *args, **kwargs):
        email = request.data.get('email')
        f_name = request.data.get('first_name')
        l_name = request.data.get('last_name')
        password = request.data.get('password')
        #check if email is valid
        if not is_valid_email(email):
            return Response({
                'status': 'error',
                'message': f"Invalid email",
            })
        if not is_valid_password(password):
            return Response({
                'status': 'error',
                'message': f"Invalid password combination (minimum of 8 characters including letters, numbers and special characters)",
            })
        try:
            # check if username and email does not exist
            usernames = []
            emails = []
            users = User.objects.all()
            for user in users:
                emails.append(user.email)
            if email not in emails:
                new_user = User(email=email, first_name=f_name, last_name=l_name, username=email)
                new_user.set_password(password)
                new_user.save()
                try:
                    code = generateCode(8)
                    id = generate_key(8)
                    """
                    protocol = 'https://' if self.request.is_secure() else 'http://'
                    host_name = self.request.get_host()
                    full_url = f"{protocol}{host_name}/verify_email/{code}/"
                    """
                    data = {
                        
                    }
                    # create a new profile
                    new_profile = Student(user=new_user, email=email, firstName=f_name,
                                          lastName=l_name, confirmationCode=code,
                                          profileId=id, userData=data)
                    #print('he')
                    new_profile.save()
                    confirmation_email(email, f_name, code)
                    Notification.objects.create(
                        user=new_profile,
                        title="Welcome To Hoistflick",
                        details={
                            "type": "account",
                            "message": "We welcome you to Hoistflick. A verified digital skill acquisition platform"
                        }
                    )
                    new_profile.confirmationDate = timezone.now()
                    new_profile.save()
                    Log.objects.create(log=f"{new_user.username} created an account.", details={
                        "profile_id": f"{new_profile.profileId}"
                    })
                    return Response({
                        'status': 'success',
                        'email': email,
                        'message': f'Account created successfully. Confirmation code has been sent to {email}. It expires in 10 minutes.',
                    })
                except Exception as e:
                    return Response({
                        'status': 'error',
                        'message': f'{e}: Account created, Error generating profile',
                    })
            elif email in emails:
                return Response({
                    'status': 'error',
                    'message': f"Email {email} has already been used. Kindly use another email.",
                })
        except:
            return Response({
                'status': 'error',
                'message': f'Error occured while creating account',
            })
    
    @action(detail=False,
            methods=['post'])
    def confirm_email(self, request, *args, **kwargs):
        code = request.data.get('code')
        email = request.data.get('email')
        try:
            user = Student.objects.get(email=email)
            d = timezone.now()
            diff = d - user.confirmationDate
            if diff >= timedelta(minutes=10):
                user.confirmationCode = None
                user.save()
                return Response({
                    'status': 'error',
                    'message': "Confirmation code has already expired. kindly request another confirmation code.",
                })
            if user.confirmationCode == code:
                user.confirmedEmail = True
                user.save()
                Log.objects.create(log=f"{user.profileId} confirmed email.", details={
                    "profile_id": f"{user.profileId}",
                    "type": "account_creation"
                })
                return Response({
                    'status': "success",
                    "message": "Email confirmed successfully."
                })
            else:
                return Response({
                    'status': 'error',
                    'message': "Invalid Confirmation Code",
                })
        except Student.DoesNotExist:
            return Response({
                'status': 'error',
                'message': "Unregistered Email",
            })
    
    @action(detail=False,
            methods=['post'])
    def confirm_login(self, request, *args, **kwargs):
        code = request.data.get('code')
        email = request.data.get('email')
        try:
            user = Student.objects.get(email=email)
            d = timezone.now()
            diff = d - user._2fa_date
            if diff >= timedelta(minutes=10):
                user._2fa_code = None
                user.save()
                return Response({
                    'status': 'error',
                    'message': "Confirmation code has already expired. kindly login again to get another confirmation code.",
                })
            if user._2fa_code == code:
                token = Token.objects.get(user=user.user)
                #token.delete()
                #new_token = Token.objects.create(user=user.user)
                user._2fa_code = None
                user.save()
                Log.objects.create(log=f"{user.profileId} confirmed email.", details={
                    "profile_id": f"{user.profileId}",
                    "type": "2fa_login"
                })
                return Response({
                    'token': token.key
                })
            else:
                return Response({
                    'status': 'error',
                    'message': "Invalid Confirmation Code",
                })
        except Student.DoesNotExist:
            return Response({
                'status': 'error',
                'message': "Unregistered Email",
            })
    
    @action(detail=False,
            methods=['post'])
    def request_confirm_email(self, request, *args, **kwargs):
        code = generateCode(8)
        email = request.data.get('email')
        try:
            user = Student.objects.get(email=email)
            if user is not None:
                if not user.confirmedEmail:
                    user.confirmationCode = code
                    user.save()
                    confirmation_email(email, user.firstName, code)
                    user.confirmationDate = timezone.now()
                    user.save()
                    Log.objects.create(log=f"{user.profileId} requested for confirmation email", details={
                        "profile_id": f"{user.profileId}",
                        "type": "account_creation"
                    })
                    return Response({
                        'status': "success",
                        'email': email,
                        "message": f"Confirmation code has been resent to {email}. It expires in 10 minutes"
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': "Email has already been confirmed",
                    })
            else:
                return Response({
                    'status': 'error',
                    'message': "Unregistered Email",
                })
        except Student.DoesNotExist:
            return Response({
                'status': 'error',
                'message': "Unregistered Email",
            })

    @action(detail=False,
            methods=['post'])
    def forgot_password(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not is_valid_email(email):
            return Response({
                'status': 'error',
                'message': f"Invalid email",
            })
        try:
            user = User.objects.get(email=email)
            if user is not None:
                token = get_random_string(length=8)
                user.set_password(token)
                user.save()
                # send email
                send_password_email(email, user.first_name, token)
                return Response({
                    'status': 'success',
                    'message': f'Password reset instructions has been sent to {email}'
                })
            else:
                return Response({
                'status': 'error',
                'message': f"Unregistered email",
            })
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f"Unregistered email",
            })

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    @action(detail=False,
            methods=['get'])
    def user_profile(self, request, *args, **kwargs):
        try:
            profile = Student.objects.get(user=request.user)
            if profile is not None:
                return Response({
                    'status': "success",
                    "message": "data fetched successfully",
                    "data": StudentSerializer(profile).data
                })
            else:
                return Response({
                    'status': "error",
                    "message": "Invalid token"
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"Invalid token: {e}"
            })

    @action(detail=False,
            methods=['post'])
    def auth_2fa(self, request, *args, **kwargs):
        password = request.data.get('password')
        action = request.data.get('action')
        try:
            user = Student.objects.get(user=request.user)
            if request.user.check_password(password):
                if action is None:
                    return Response({
                        'status': 'error',
                        'message': "Invalid action parameter.",
                    })
                if action.lower() == "activate":
                    user._2fa_enabled = True
                    user.save()
                elif action.lower() == "deactivate":
                    user._2fa_enabled = False
                    user.save()
                else:
                    return Response({
                        'status': 'error',
                        'message': "Invalid action parameter.",
                    })
                return Response({
                    'status': "success",
                    "message": f"2 factor auhentication {action}d."
                })
            else:
                return Response({
                    'status': 'error',
                    'message': "Incorrect password",
                })
        except Student.DoesNotExist:
            return Response({
                'status': 'error',
                'message': "Unauthorized request",
            })

    @action(detail=False,
            methods=['post'])
    def change_password(self, request, *args, **kwargs):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        try:
            profile = Student.objects.get(user=request.user)
            if not is_valid_password(new_password):
                return Response({
                    'status': 'error',
                    'message': f"Invalid new password combination",
                })
            try:
                if request.user.check_password(old_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    return Response({
                        'status': "success",
                        "message": "Your password has been reset successfully!",
                    })
                else:
                    return Response({
                        'status': "error",
                        "message": "Incorrect password",
                    })
            except Exception as e:
                return Response({
                    'status': "error",
                    "message": f"error occured: {e}",
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid token"
            })

class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_skill_categories(self, request, *args, **kwargs):
        try:
            cats = SkillCategory.objects.all()
            if cats.exists():
                return Response({
                    'status': "success",
                    "message": "category list fetched",
                    'data': [SkillCategorySerializer(c).data for c in cats]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No category found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting categories"
            })
    @action(detail=False,
            methods=['get'])
    def get_popular_skills(self, request, *args, **kwargs):
        try:
            skills = Skill.objects.annotate(num_students=models.Count('students')).order_by('-num_students')[:10]
            if skills.exists():
                return Response({
                    'status': "success",
                    "message": "popular skill list fetched",
                    'data': [SkillSerializer(c).data for c in skills]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No skill found",
                })
        except Exception as e:
            print(str(e))
            return Response({
                'status': "error",
                "message": "Error occured while getting list"
            })
    @action(detail=False,
            methods=['get'])
    def get_free_skills(self, request, *args, **kwargs):
        try:
            skills = Skill.objects.filter(price=0).annotate(num_students=models.Count('students')).order_by('-num_students')[:5]
            if skills.exists():
                return Response({
                    'status': "success",
                    "message": "free skill list fetched",
                    'data': [SkillSerializer(c).data for c in skills]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No skill found",
                })
        except Exception as e:
            print(str(e))
            return Response({
                'status': "error",
                "message": "Error occured while getting list"
            })
    @action(detail=False,
            methods=['get'])
    def get_skills(self, request, *args, **kwargs):
        id = self.request.query_params.get('cat_id')
        sort = self.request.query_params.get('sort_by')
        try:
            skills = None
            if sort is None:
                sort = "title"
            if id is not None:
                cat = SkillCategory.objects.get(id=int(id))
                skills = Skill.objects.filter(category=cat).order_by(sort)
            else:
                skills = Skill.objects.all().order_by(sort)
            c_count = []
            v_count = []
            if skills.exists():
                for s in skills:
                    c_count.append(s.courses.count())
                    a = 0
                    for c in s.courses.all():
                        a += c.videos.count()
                    v_count.append(a)
                return Response({
                    'status': "success",
                    "message": "skill list fetched",
                    'data': [SkillSerializer(c).data for c in skills],
                    'c_count': c_count,
                    'v_count': v_count
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No skill found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting skills"
            })
    @action(detail=False,
            methods=['get'])
    def get_user_skills(self, request, *args, **kwargs):
        key = self.request.query_params.get('api_token')
        try:
            user = Student.objects.get(api_token=key)
            skills = Skill.objects.filter(students=user)
            c_count = []
            v_count = []
            s_count = []
            percent_list = []
            if skills.exists():
                for s in skills:
                    c_count.append(s.courses.count())
                    s_count.append(s.students.count())
                    a = 0
                    all_m = 0
                    read_m = 0
                    percent = 0
                    for c in s.courses.all():
                        a += c.videos.count()
                        ms = Material.objects.filter(topic__course=c)
                        all_m += ms.count()
                        for z in ms:
                            if z.read_by.filter(api_token=user.api_token).exists():
                                read_m += 1
                    if all_m > 0:
                        percent = int((read_m / all_m) * 100)
                    percent_list.append(percent)
                    v_count.append(a)
                return Response({
                    'status': "success",
                    "message": "skill list fetched",
                    'data': [SkillSerializer(c).data for c in skills],
                    'c_count': c_count,
                    'v_count': v_count,
                    's_count': s_count,
                    'p_list': percent_list
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No skill found",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while getting skills"
            })
    @action(detail=False,
            methods=['get'])
    def get_user_schedules(self, request, *args, **kwargs):
        key = self.request.query_params.get('api_token')
        try:
            user = Student.objects.get(api_token=key)
            sc = Schedule.objects.filter(students=user)
            if sc.exists():
                return Response({
                    'status': "success",
                    "message": "schedule list fetched",
                    'data': [ScheduleSerializer(c).data for c in sc]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No schedule found",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while getting schedules"
            })
    @action(detail=False,
            methods=['get'])
    def get_skill_courses(self, request, *args, **kwargs):
        id = self.request.query_params.get('skill_id')
        try:
            skill = Skill.objects.get(id=int(id))
            courses = skill.courses.all()
            if courses.exists():
                return Response({
                    'status': "success",
                    "message": "course list fetched",
                    'data': [CourseSerializer(c).data for c in courses]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No course found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting courses"
            })
    @action(detail=False,
            methods=['get'])
    def get_skill_reviews(self, request, *args, **kwargs):
        id = self.request.query_params.get('skill_id')
        try:
            skill = Skill.objects.get(id=int(id))
            reviews = skill.reviews.all()
            if reviews.exists():
                return Response({
                    'status': "success",
                    "message": "review list fetched",
                    'data': [ReviewSerializer(c).data for c in reviews]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No review found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting reviews"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_skill(self, request, *args, **kwargs):
        id = self.request.query_params.get('skill_id')
        try:
            skill = Skill.objects.get(id=int(id))
            return Response({
                'status': "success",
                "message": "skill details fetched",
                'data': SkillSerializer(skill).data,
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting skill details"
            })
    @action(detail=False,
            methods=['get'])
    def get_schedule(self, request, *args, **kwargs):
        id = self.request.query_params.get('schedule_id')
        try:
            schedule = Schedule.objects.get(id=int(id))
            return Response({
                'status': "success",
                "message": "schedule details fetched",
                'data': ScheduleSerializer(schedule).data,
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting schedule details"
            })
    @action(detail=False,
            methods=['post'])
    def enroll_skill(self, request, *args, **kwargs):
        id = request.POST.get('skill_id')
        key = request.POST.get('api_token')
        pk = settings.PAYSTACK_PUBLIC_KEY
        try:
            skill = Skill.objects.get(id=int(id))
            student = Student.objects.get(api_token=key)
            if student not in skill.students.all():
                if skill.price == 0:
                    skill.students.add(student)
                    skill.save()
                    note = Notification(title="New Course Enrolment", detail="", icon="fa-book", note=f"You have been successfully enrolled for {skill.title}.")
                    note.save()
                    note.owners.add(student)
                    note.save()
                    return Response({
                        'status': "success",
                        'mode': 'free',
                        'message': f'You have successfully enrolled for {skill.title}'
                    })
                else:
                    transaction = Payment.objects.create(amount=skill.price, email=student.email, user=student,
                                                    skill=skill, reference_id=f'RIGAN_{generateCode(20)}')
                    transaction.save()
                    return Response({
                        'status': "success",
                        'mode': 'paid',
                        'paystack_pub_key': pk,
                        'data': PaymentSerializer(transaction).data,
                        'skill': SkillSerializer(skill).data
                    })
            else:
                return Response({
                    'status': "error",
                    "message": f"You are already enrolled for \"{skill.title}\"",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while enrolling user"
            })
    @action(detail=False,
            methods=['post'])
    def verify_payment(self, request, *args, **kwargs):
        id = request.POST.get('reference_id')
        key = request.POST.get('api_token')
        try:
            trans = Payment.objects.get(reference_id=id)
            student = Student.objects.get(api_token=key)
            verified = trans.verify_payment()
            if verified:
                trans.status = "Successful"
                trans.save()
                skill = trans.skill
                skill.students.add(student)
                skill.save()
                note = Notification(title="New Course Enrolment", detail="", icon="fa-book", note=f"You have been successfully enrolled for {skill.title}.")
                note.save()
                note.owners.add(student)
                note.save()
                try:
                    generate_receipt(trans)
                    send_user_payment(student.user, trans.skill, trans)
                except Exception as e:
                    print(str(e))
                    send_user_payment(student.user, trans.skill, trans)
                return Response({
                    'status': "success",
                    'message': f'Payment successful! You have enrolled for {skill.title}'
                })
            else:
                trans.status = "Failed"
                trans.save()
                return Response({
                    'status': "error",
                    "message": f"Payment failed. Please Try Again",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while processing payment."
            })
    
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_courses(self, request, *args, **kwargs):
        id = self.request.query_params.get('skill_id')
        sort = self.request.query_params.get('sort_by')
        query = self.request.query_params.get('search')
        try:
            courses = None
            if sort is None:
                sort = "order"
            if query is None:
                query = ""
            if id is not None:
                skill = Skill.objects.get(id=int(id))
                courses = skill.courses.filter(title__icontains=query).order_by(sort)
            else:
                courses = Course.objects.filter(title__icontains=query).order_by(sort)
            if courses.exists():
                return Response({
                    'status': "success",
                    "message": "course list fetched",
                    'data': [CourseSerializer(c).data for c in courses]
                })
            else:
                return Response({
                    'status': 'status',
                    'message': "No course found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting courses"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_course(self, request, *args, **kwargs):
        id = self.request.query_params.get('course_id')
        try:
            course = Course.objects.get(id=int(id))
            skills = course.skills.all()
            return Response({
                'status': "success",
                "message": "course details fetched",
                'data': CourseSerializer(course).data,
                'skills': [SkillSerializer(s).data for s in skills]
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting course"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_quizzes(self, request, *args, **kwargs):
        id = self.request.query_params.get('course_id')
        key = self.request.query_params.get('api_token')
        try:
            course = Course.objects.get(id=int(id))
            quizzes = Quiz.objects.filter(course=course)
            if quizzes.exists():
                if key:
                    student = Student.objects.get(api_token=key)
                    for q in quizzes:
                        if Score.objects.filter(student=student, quiz=q).exists():
                            q.done = True
                        else:
                            q.done = False
                return Response({
                    'status': "success",
                    "message": "quiz list fetched",
                    'course': CourseSerializer(course).data,
                    'data': [QuizSerializer(c).data for c in quizzes]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No quiz found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting quizzes"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_quiz(self, request, *args, **kwargs):
        id = self.request.query_params.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=int(id))
            questions = Question.objects.filter(quiz=quiz)
            return Response({
                'status': "success",
                "message": "quiz details fetched",
                'data': QuizSerializer(quiz).data,
                'questions': [QuestionSerializer(q).data for q in questions]
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting quiz questions"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_quiz_ranking(self, request, *args, **kwargs):
        id = self.request.query_params.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=int(id))
            rankings = Score.objects.filter(quiz=quiz).order_by('-score')
            return Response({
                'status': "success",
                "message": "quiz ranking fetched",
                'data': [ScoreSerializer(q).data for q in rankings]
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting quiz rankings"
            })
    
    @action(detail=False,
            methods=['post'])
    def submit_quiz(self, request, *args, **kwargs):
        id = request.POST.get('quiz_id')
        key = request.POST.get('api_token')
        answers = request.POST.getlist('answers', [])
        #print(answers)
        try:
            quiz = Quiz.objects.get(id=int(id))
            student = Student.objects.get(api_token=key)
            no_of_que = len(answers)
            correct_ans = 0
            for a in answers:
                if a == 'correct':
                    correct_ans += 1
                else:
                    pass
            mark = int((correct_ans/no_of_que)*100)
            try:
                score = Score.objects.get(student=student, quiz=quiz)
                return Response({
                    'status': "success",
                    "message": f"You got {correct_ans} out of {no_of_que} questions. Your percentage is {mark}% and medal is {score.remark}. Your previous score on this quiz will not be overwritten.",
                    "course_id": quiz.course.id,
                    "quiz_id": quiz.id
                })
            except Score.DoesNotExist:
                remark = ""
                if mark < 41:
                    remark = "Copper"
                elif mark < 61:
                    remark = "Bronze"
                elif mark < 81:
                    remark = "Silver"
                else:
                    remark = "Gold"
                score = Score(student=student, quiz=quiz, score=mark, remark=remark)
                score.save()
                return Response({
                    'status': "success",
                    "message": f"You got {correct_ans} out of {no_of_que} questions. Your percentage is {mark}% and medal is {score.remark}",
                    "course_id": quiz.course.id,
                    "quiz_id": quiz.id
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while submitting quiz"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_materials(self, request, *args, **kwargs):
        id = self.request.query_params.get('course_id')
        key = self.request.query_params.get('api_token')
        try:
            read_m = 0
            course = Course.objects.get(id=int(id))
            materials = Material.objects.filter(topic__course=course)
            total_mat = materials.count()
            if materials.exists():
                if key:
                    profile = Student.objects.get(api_token=key)
                    for m in materials:
                        if m.read_by.filter(api_token=profile.api_token).exists():
                            m.read = True
                            read_m += 1
                        else:
                            m.read = False
                last_mat = Material.objects.filter(topic__course=course, active=True).last()
                percent = (read_m / total_mat) * 100
                return Response({
                    'status': "success",
                    "message": "material list fetched",
                    'course': CourseSerializer(course).data,
                    'data': [MaterialSerializer(c).data for c in materials],
                    'last_order': last_mat.order,
                    'percentage_read': int(percent)
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No material found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting materials"
            })
    
    @action(detail=False,
            methods=['post'])
    def edit_material(self, request, *args, **kwargs):
        id = request.POST.get('material_id')
        key = request.POST.get('api_token')
        content = request.POST.get('content')
        active = request.POST.get('active')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                mat = Material.objects.get(id=int(id))
                mat.content = content
                if active == 'true':
                    mat.active = True
                elif active == 'false':
                    mat.active = False
                mat.save()
                return Response({
                    'status': "success",
                    "message": "material edited successfully",
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while editing material"
            })
    
    @action(detail=False,
            methods=['post'])
    def add_material(self, request, *args, **kwargs):
        id = request.POST.get('topic_id')
        key = request.POST.get('api_token')
        content = request.POST.get('content')
        active = request.POST.get('active')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                top = Topic.objects.get(id=int(id))
                try:
                    Material.objects.get(topic=top)
                    return Response({
                        'status': "error",
                        "message": f"material for {top.title} already exists",
                    })
                except:
                    new_mat = Material(topic=top, content=content)
                    if active == 'true':
                        new_mat.active = True
                    elif active == 'false':
                        new_mat.active = False
                    new_mat.save()
                    emails = []
                    skills = Skill.objects.filter(courses=top.course)
                    for s in skills:
                        for u in s.students.all():
                            if u.user.email not in emails:
                                emails.append(u.user.email)
                            else:
                                pass
                    send_material_notification(emails, top.course.title, top.title)
                    return Response({
                        'status': "success",
                        "message": "material added successfully",
                    })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while editing material"
            })
    
    @action(detail=False,
            methods=['post'])
    def add_topic(self, request, *args, **kwargs):
        id = request.POST.get('course_id')
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        slug = slugify(title)
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                course = Course.objects.get(id=int(id))
                try:
                    Topic.objects.get(course=course, slug=slug)
                    return Response({
                        'status': "error",
                        "message": f"topic already exists in {course.title}",
                    })
                except:
                    new_top = Topic(course=course, title=title, slug=slug)
                    new_top.save()
                    return Response({
                        'status': "success",
                        "message": "topic added successfully",
                    })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while adding topic"
            })
    
    @action(detail=False,
            methods=['post'])
    def add_quiz(self, request, *args, **kwargs):
        id = request.POST.get('course_id')
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                course = Course.objects.get(id=int(id))
                try:
                    Quiz.objects.get(course=course, title__iexact=title)
                    return Response({
                        'status': "error",
                        "message": f"quiz already exists in {course.title}",
                    })
                except:
                    new_quiz = Quiz(course=course, title=title)
                    new_quiz.save()
                    return Response({
                        'status': "success",
                        "message": "quiz added successfully",
                    })
            else:
                return Response({
                    'status': 'error',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while adding quiz"
            })
    
    @action(detail=False,
            methods=['post'])
    def activate_quiz(self, request, *args, **kwargs):
        id = request.POST.get('quiz_id')
        key = request.POST.get('api_token')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                quiz = Quiz.objects.get(id=int(id))
                action = ""
                if quiz.active:
                    quiz.active = False
                    quiz.save()
                    action = "deactivated"
                else:
                    quiz.active = True
                    quiz.save()
                    action = "activated"
                    emails = []
                    skills = Skill.objects.filter(courses=quiz.course)
                    for s in skills:
                        for u in s.students.all():
                            if u.user.email not in emails:
                                emails.append(u.user.email)
                            else:
                                pass
                    send_quiz_notification(emails, quiz.course.title, quiz.title)
                return Response({
                    'status': "success",
                    "message": f"{quiz.title} {action} successfully",
                    "data": CourseSerializer(quiz.course).data
                })
            else:
                return Response({
                    'status': 'error',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured"
            })
    
    @action(detail=False,
            methods=['post'])
    def add_question(self, request, *args, **kwargs):
        id = request.POST.get('quiz_id')
        key = request.POST.get('api_token')
        order = request.POST.get('order')
        que = request.POST.get('question')
        a = request.POST.get('option_a')
        b = request.POST.get('option_b')
        c = request.POST.get('option_c')
        d = request.POST.get('option_d')
        ans = request.POST.get('answer')
        reason = request.POST.get('reason')
        image = request.FILES.get('image')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                quiz = Quiz.objects.get(id=int(id))
                try:
                    Question.objects.get(quiz=quiz, order=int(order), question=que)
                    
                    return Response({
                        'status': "error",
                        "message": f"question already exists in {quiz.title}",
                    })
                except:
                    new_que = Question(quiz=quiz, order=int(order), question=que, optionA=a,
                                        optionB=b, optionC=c, optionD=d, answer=ans, reason=reason)
                    new_que.save()
                    if image:
                        new_que.image = image
                        new_que.save()
                    return Response({
                        'status': "success",
                        "message": "question added successfully",
                        'data': QuizSerializer(quiz).data
                    })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while adding question"
            })
    
    @action(detail=False,
            methods=['post'])
    def edit_question(self, request, *args, **kwargs):
        id = request.POST.get('question_id')
        key = request.POST.get('api_token')
        order = request.POST.get('order')
        que = request.POST.get('question')
        a = request.POST.get('option_a')
        b = request.POST.get('option_b')
        c = request.POST.get('option_c')
        d = request.POST.get('option_d')
        ans = request.POST.get('answer')
        reason = request.POST.get('reason')
        image = request.FILES.get('image')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                question = Question.objects.get(id=int(id))
                question.order = order
                question.question = que
                question.optionA = a
                question.optionB = b
                question.optionC = c
                question.optionD = d
                question.answer = ans
                question.reason = reason
                question.save()
                if image:
                    question.image = image
                    question.save()
                quiz = question.quiz
                return Response({
                    'status': "success",
                    "message": "question edited successfully",
                    'data': QuizSerializer(quiz).data
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while editing question"
            })
    
    @action(detail=False,
            methods=['post'])
    def delete_question(self, request, *args, **kwargs):
        id = request.POST.get('question_id')
        key = request.POST.get('api_token')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                question = Question.objects.get(id=int(id))
                quiz = question.quiz
                if question.image:
                    question.image.delete()
                question.delete()
                return Response({
                    'status': "success",
                    "message": f"question {question.order} deleted successfully",
                    'data': QuizSerializer(quiz).data
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while deleting question"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_question(self, request, *args, **kwargs):
        id = self.request.query_params.get('question_id')
        try:
            question = Question.objects.get(id=int(id))
            return Response({
                'status': "success",
                "message": "question details fetched",
                'data': QuestionSerializer(question).data
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting question details"
            })
    
    @action(detail=False,
            methods=['post'])
    def add_video(self, request, *args, **kwargs):
        id = request.POST.get('course_id')
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        url = request.POST.get('url')
        des = request.POST.get('description')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                course = Course.objects.get(id=int(id))
                try:
                    Video.objects.get(course=course, link=url)
                    return Response({
                        'status': "error",
                        "message": f"video already exists in {course.title}",
                    })
                except:
                    new_vid = Video(course=course, title=title, link=url, description=des)
                    new_vid.save()
                    emails = []
                    skills = Skill.objects.filter(courses=course)
                    for s in skills:
                        for u in s.students.all():
                            if u.user.email not in emails:
                                emails.append(u.user.email)
                            else:
                                pass
                    send_video_notification(emails, course.title, title)
                    return Response({
                        'status': "success",
                        "message": "video added successfully",
                    })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while adding video"
            })
    
    @action(detail=False,
            methods=['post'])
    def edit_course(self, request, *args, **kwargs):
        id = request.POST.get('course_id')
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        slug = slugify(title)
        order = request.POST.get('order')
        image = request.FILES.get('image')
        skill_ids = request.POST.getlist('skill_ids', [])
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                sim_course = Course.objects.exclude(id=int(id)).filter(slug=slug)
                if sim_course.exists():
                    return Response({
                        'status': "error",
                        "message": f"course with title \"{title}\" already exists",
                    })
                else:
                    course = Course.objects.get(id=int(id))
                    course.title = title
                    course.slug = slug
                    course.order = order
                    course.save()
                    if image is not None:
                        course.image = image
                        course.save()
                    s_ids = [int(s_id) for s_id in skill_ids]
                    ex_skills = course.skills.all()
                    for s in ex_skills:
                        s.courses.remove(course)
                        s.save()
                    skills = Skill.objects.filter(id__in=s_ids)
                    for s in skills:
                        s.courses.add(course)
                        s.save()
                    return Response({
                        'status': "success",
                        "message": "course edited successfully",
                    })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while editing course"
            })
    
    @action(detail=False,
            methods=['post'])
    def add_course(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        slug = slugify(title)
        order = request.POST.get('order')
        image = request.FILES.get('image')
        skill_ids = request.POST.getlist('skill_ids', [])
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                sim_course = Course.objects.filter(slug=slug)
                if sim_course.exists():
                    return Response({
                        'status': "error",
                        "message": f"course with title \"{title}\" already exists",
                    })
                else:
                    course = Course(title=title, slug=slug, order=order)
                    course.save()
                    if image is not None:
                        course.image = image
                        course.save()
                    s_ids = [int(s_id) for s_id in skill_ids]
                    skills = Skill.objects.filter(id__in=s_ids)
                    for s in skills:
                        s.courses.add(course)
                        s.save()
                        note = Notification(title="New Course Alert", detail="course", icon="fa-book", note=f"A new course, \'{course.title}\' has been added to \'{s.title}\'.")
                        note.save()
                        for o in s.students.all():
                            note.owners.add(o)
                            note.save()
                    return Response({
                        'status': "success",
                        "message": "course added successfully",
                    })
            else:
                return Response({
                    'status': 'success',
                    'message': "user not authorized",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while adding course"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_videos(self, request, *args, **kwargs):
        id = self.request.query_params.get('course_id')
        try:
            course = Course.objects.get(id=int(id))
            videos = Video.objects.filter(course=course)
            if videos.exists():
                return Response({
                    'status': "success",
                    "message": "video list fetched",
                    'data': [VideoSerializer(c).data for c in videos]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No video found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting videos"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_topics(self, request, *args, **kwargs):
        id = self.request.query_params.get('course_id')
        try:
            course = Course.objects.get(id=int(id))
            topics = Topic.objects.filter(course=course)
            if topics.exists():
                return Response({
                    'status': "success",
                    "message": "topic list fetched",
                    'data': [TopicSerializer(c).data for c in topics]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No topic found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting topics"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_material(self, request, *args, **kwargs):
        id = self.request.query_params.get('material_id')
        try:
            material = Material.objects.get(id=int(id))
            return Response({
                'status': "success",
                "message": "material details fetched",
                'data': MaterialSerializer(material).data
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting course material"
            })
    
    @action(detail=False,
            methods=['get'])
    def read_material(self, request, *args, **kwargs):
        id = self.request.query_params.get('material_id')
        key = self.request.query_params.get('api_token')
        try:
            profile = Student.objects.get(api_token=key)
            material = Material.objects.get(id=int(id))
            if not material.read_by.filter(id=profile.id).exists():
                material.read_by.add(profile)
                material.save()
            return Response({
                'status': "success",
                "message": "material read",
                'data': CourseSerializer(material.topic.course).data
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while marking material"
            })
    
    @action(detail=False,
            methods=['post'])
    def run_code(self, request, *args, **kwargs):
        code = request.POST.get('code', '')
        try:
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output):
                    exec(code, {})
                    result = output.getvalue()
            except Exception as e:
                result = str(e)
            return Response({
                'result': result
            })
        except Exception as e:
            return Response({
                'result': str(e)
            })
    
    @action(detail=False,
            methods=['get'])
    def get_next_material(self, request, *args, **kwargs):
        id = self.request.query_params.get('topic_id')
        order = self.request.query_params.get('order')
        typ = self.request.query_params.get('type')
        try:
            topic = Topic.objects.get(id=int(id))
            try:
                material = Material.objects.get(order=int(order), topic__course=topic.course)
                return Response({
                    'status': "success",
                    "message": "material details fetched",
                    'data': MaterialSerializer(material).data
                })
            except Material.DoesNotExist:
                return Response({
                    'status': "error",
                    "message": f"You have reached the {typ} topic",
                    "type": "material"
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting course material",
                "type": "error"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_video(self, request, *args, **kwargs):
        id = self.request.query_params.get('video_id')
        try:
            video = Video.objects.get(id=int(id))
            return Response({
                'status': "success",
                "message": "video details fetched",
                'data': VideoSerializer(video).data,
            })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"Error occured while getting course video"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_certificate(self, request, *args, **kwargs):
        id = self.request.query_params.get('course_id')
        key = self.request.query_params.get('api_token')
        try:
            profile = Student.objects.get(api_token=key)
            course = Course.objects.get(id=int(id))
            cert = None
            try:
                cert = Certificate.objects.get(student=profile, course=course)
            except Certificate.DoesNotExist:
                html_content = f"""
                <html>
                    <head>
                        
                    </head>
                    <body>
                        <div style="width: 100%;position: relative;">
                            <img style="width: 100%;height: auto;" src="https://riganapi.pythonanywhere.com/media/hackode/certificate/certificate.png" alt="Certificate" />
                            <h2 style="font-family: 'Great Vibes', cursive;font-size: 2.2rem;position: absolute;top: 48%;left: 50%;transform: translateX(-50%);">{profile.first_name} {profile.last_name}</h2>
                            <h6 style="font-family: 'Montserrat', sans-serif;font-size: 1rem;position: absolute;top: 65%;left: 50%;transform: translateX(-50%);">\"{course.title}\"</h6>
                        </div>
                    </body>
                </html>
                """
                css_content = f"""
                body
                """
                #image_bytes = None
                
                pdf_file = BytesIO()
                #HTML(string=html_content).write_pdf(pdf_file, stylesheets=[CSS(string=css_content)])
                """
                with Image(file=pdf_file, resolution=300) as img:
                    img.format = 'png'
                    image_bytes = img.make_blob()
                """
                cert = Certificate(student=profile, course=course)
                cert.pdf_file.save(f'{course.title}_certificate_{profile.first_name}_{profile.last_name}.pdf', 
                                   ContentFile(pdf_file.getvalue()))
                #cert.png_file.save(f'{course.title}_certificate_{profile.first_name}_{profile.last_name}.png',
                #                   ContentFile(image_bytes))
                cert.save()
            return Response({
                'status': "success",
                "message": "certificate fetched",
                'data': CertificateSerializer(cert).data,
                'name': f"{profile.first_name} {profile.last_name}",
                'course': course.title
            })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while getting certificate"
            })
    
    @action(detail=False,
            methods=['get'])
    def download_file(self, request, *args, **kwargs):
        id = self.request.query_params.get('id')
        cert = Certificate.objects.get(id=int(id))
        try:
            cert_file = cert.pdf_file
            path = "http://127.0.0.1:8000/media/hackode/certificates/pdf/HTML_certificate_Paul_Mark_bQS4XKZ.pdf"
            with open(path, 'rb') as f:
                response = FileResponse(f)
                response['Content-Disposition'] = f'attachment; filename="{cert_file.name}"'
                return response
        except Exception as e:
            return Response({'message': str(e)})
  
class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_projects_admin(self, request, *args, **kwargs):
        id = self.request.query_params.get('course_id')
        key = self.request.query_params.get('api_token')
        try:
            admin = Student.objects.get(api_token=key)
            if admin.user.is_superuser:
                projects = None
                if id is not None:
                    course = Course.objects.get(id=int(id))
                    projects = Project.objects.filter(course=course)
                else:
                    projects = Project.objects.all()
                if projects.exists():
                    return Response({
                        'status': "success",
                        "message": "project list fetched",
                        'data': [ProjectSerializer(p).data for p in projects]
                    })
                else:
                    return Response({
                        'status': "success",
                        "message": "no project found",
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "Unauthorized access",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"Error occured: {e}",
            })
                    
    @action(detail=False,
            methods=['get'])
    def get_project_admin(self, request, *args, **kwargs):
        id = self.request.query_params.get('project_id')
        key = self.request.query_params.get('api_token')
        try:
            project = Project.objects.get(id=int(id))
            student = Student.objects.get(api_token=key)
            if student.user.is_superuser:
                return Response({
                    'status': "success",
                    "message": "project details fetched",
                    'data': ProjectASerializer(project).data,
                })
            else:
                return Response({
                    'status': "error",
                    "message": "Unauthorized access"
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"Error occured: {e}"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_projects(self, request, *args, **kwargs):
        id = self.request.query_params.get('skill_id')
        key = self.request.query_params.get('api_token')
        try:
            student = Student.objects.get(api_token=key)
            projects = []
            submission = []
            if id is not None:
                skill = Skill.objects.get(id=int(id))
                courses = skill.courses.all()
                for c in courses:
                    ps = Project.objects.filter(course=c, assigned_to=student)
                    if ps.exists():
                        for p in ps:
                            if p not in projects:
                                projects.append(p)
                            else:
                                pass
                    else:
                        pass
            else:
                skills = Skill.objects.filter(students=student)
                for s in skills:
                    courses = s.courses.all()
                    for c in courses:
                        ps = Project.objects.filter(course=c, assigned_to=student)
                        if ps.exists():
                            for p in ps:
                                if p not in projects:
                                    projects.append(p)
                                else:
                                    pass
                        else:
                            pass
            if len(projects) > 0:
                for p in projects:
                    try:
                        Submission.objects.get(project=p, student=student)
                        submission.append(True)
                    except Submission.DoesNotExist:
                        submission.append(False)
                #print(submission)
                return Response({
                    'status': "success",
                    "message": "project list fetched",
                    'submission': submission,
                    'data': [ProjectSerializer(p).data for p in projects]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "You have not beem assigned any project.",
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"{e}: Error occured while getting projects"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_submissions(self, request, *args, **kwargs):
        id = self.request.query_params.get('project_id')
        try:
            project = Project.objects.get(id=int(id))
            submissions = Submission.objects.filter(project=project)
            if submissions.exists():
                return Response({
                    'status': "success",
                    "message": "submission list fetched",
                    'data': [SubmissionSerializer(p).data for p in submissions]
                })
            else:
                return Response({
                    'status': 'success',
                    'message': "No submission found",
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting submissions"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_project(self, request, *args, **kwargs):
        id = self.request.query_params.get('project_id')
        key = self.request.query_params.get('api_token')
        try:
            project = Project.objects.get(id=int(id))
            student = Student.objects.get(api_token=key)
            try:
                submission = Submission.objects.get(student=student, project=project)
                return Response({
                    'status': "success",
                    "message": "project details fetched",
                    'data': ProjectSerializer(project).data,
                    'submission': SubmissionSerializer(submission).data
                })
            except:
                return Response({
                    'status': "success",
                    "message": "project details fetched",
                    'data': ProjectSerializer(project).data,
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting project detail"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_project_ranking(self, request, *args, **kwargs):
        id = self.request.query_params.get('project_id')
        try:
            project = Project.objects.get(id=int(id))
            subs = Submission.objects.filter(project=project, score__gte=1).order_by('-score')[:10]
            if subs.exists():
                return Response({
                    'status': "success",
                    "message": "project ranking fetched",
                    'data': [SubmissionSerializer(s).data for s in subs]
                })
            else:
                return Response({
                    'status': "success",
                    "message": "No ranking yet."
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting project ranking"
            })
    
    @action(detail=False,
            methods=['get'])
    def get_submission(self, request, *args, **kwargs):
        id = self.request.query_params.get('sub_id')
        try:
            submission = Submission.objects.get(id=int(id))
            return Response({
                'status': "success",
                "message": "submission details fetched",
                'data': SubmissionSerializer(submission).data
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while getting submission detail"
            })
    
    @action(detail=False,
            methods=['post'])
    def submit_project(self, request, *args, **kwargs):
        id = request.POST.get('project_id')
        key = request.POST.get('api_token')
        live = request.POST.get('live')
        repo = request.POST.get('repo')
        file = request.FILES.get('file')
        try:
            project = Project.objects.get(id=int(id))
            student = Student.objects.get(api_token=key)
            submit = ""
            if live.strip() == '' and repo.strip() == '' and file is None:
                return Response({
                    'status': 'error',
                    'message': 'All fields cannot be empty'
                })
            try:
                submission = Submission.objects.get(student=student, project=project)
                submission.source_code = repo
                submission.live_url = live
                submission.save()
                if file is not None:
                    submission.file = file
                    submission.save()
                submit = "New Submission"
                send_sub_submission(f"{submission.student.first_name} {submission.student.last_name}", submission.project.title, submit)
                return Response({
                    'status': "success",
                    "message": "Project submitted successfully"
                })
            except Submission.DoesNotExist:
                submission = Submission(student=student, project=project, source_code=repo, live_url=live, file=file)
                submission.save()
                submit = "Updated Submission"
                send_sub_submission(f"{submission.student.first_name} {submission.student.last_name}", submission.project.title, submit)
                return Response({
                    'status': "success",
                    "message": "Project submitted successfully"
                })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while submitting project"
            })
    
    @action(detail=False,
            methods=['post'])
    def edit_project(self, request, *args, **kwargs):
        id = request.POST.get('project_id')
        key = request.POST.get('api_token')
        des = request.POST.get('description')
        try:
            project = Project.objects.get(id=int(id))
            student = Student.objects.get(api_token=key)
            if not student.user.is_superuser:
                return Response({
                    'status': 'error',
                    'message': 'Unauthorized request'
                })
            project.description = des
            project.save()
            return Response({
                'status': "success",
                "message": "Project edited successfully"
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while editing project"
            })
    
    @action(detail=False,
            methods=['post'])
    def edit_submission(self, request, *args, **kwargs):
        id = request.POST.get('sub_id')
        key = request.POST.get('api_token')
        comment = request.POST.get('comment')
        score = request.POST.get('score')
        try:
            sub = Submission.objects.get(id=int(id))
            student = Student.objects.get(api_token=key)
            if not student.user.is_superuser:
                return Response({
                    'status': 'error',
                    'message': 'Unauthorized request'
                })
            sub.comment = comment
            sub.score = int(score)
            sub.save()
            note = Notification(title="Project Submission", detail="project", icon="fa-briefcase", note=f"Your project submission on {sub.project.title} has been graded.")
            note.save()
            note.owners.add(student)
            note.save()
            send_sub_comment(sub.student.email, sub.student.first_name, sub.project.title, sub.comment)
            return Response({
                'status': "success",
                "message": "Submission edited successfully"
            })
        except:
            return Response({
                'status': "error",
                "message": "Error occured while editing submission"
            })

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    @action(detail=False,
            methods=['get'])
    def get_notifications(self, request, *args, **kwargs):
        ne = self.request.query_params.get("new")
        try:
            profile = Student.objects.get(user=request.user)
            if ne is not None:
                if ne.lower() == "true":
                    notes = Notification.objects.filter(user=profile, seen=False)
                elif ne.lower() == "false":
                    notes = Notification.objects.filter(user=profile, seen=True)
            else:
                notes = Notification.objects.filter(user=profile)
            if notes.exists():
                for n in notes:
                    n.seen = True
                    n.save()
                return Response({
                    'status': "success",
                    "message": "Notifications fetched successfully.",
                    "data": [NotificationSerializer(a).data for a in notes]
                })
            else:
                return Response({
                    'status': "success",
                    "message": "No notifications."
                })
        except Exception as e:
            return Response({
                'status': "error",
                "message": f"Invalid token"
            })

  
