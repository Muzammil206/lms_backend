from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('lms', views.LMSViewSet)
router.register('accounts', views.SetupViewSet)
router.register('user', views.StudentViewSet, basename="profile")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.CustomAuthToken.as_view(), name="auth_login")
]
