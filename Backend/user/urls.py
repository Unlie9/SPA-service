from django.urls import path, include

from user.views import CreateUserView, LoginUserView
from rest_framework.authtoken import views

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", LoginUserView.as_view(), name="login")
]

app_name = "user"
