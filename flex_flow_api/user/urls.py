from django.urls import path

from user import views

app_name = "user"
urlpatterns = [
    path(
        "login/",
        views.LoginView.as_view(),
        name="login"
    ),
    path(
        "register/",
        views.UserCreateView.as_view(),
        name="register"
    ),
    path(
        "me/",
        views.ManageUserView.as_view(),
        name="me"
    )
]
