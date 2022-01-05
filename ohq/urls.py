from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'ohq'
urlpatterns = [
    path(route="", view=views.CourseListView.as_view(), name="index"),
    path("search", views.search, name="search"),
    path("course/<int:pk>", views.CourseQueueView.as_view(), name="course_queue"),
    path("login_request", views.login_request, name="login_request"),
    path("logout", views.logout_request, name="logout"),
    path("login", views.login_request, name="login"),
    path("course/<int:pk>/change_status", views.change_queue_status, name="change_status"),
    path("course/<int:pk>/meeting_link", views.set_meeting_link, name="set_meeting_link"),
    path("signup", views.signup_request, name="signup_request"),
    path("password", views.change_password, name="change_password"),
    path("change_preferred_name", views.change_preferred_name, name="change_preferred_name"),
    path("course/<int:pk>/join_queue", views.join_queue, name="join_queue"),
    path("course/<int:pk>/invite_students", views.invite_students, name="invite_students"),
    path("course/<int:pk>/next_student", views.next_student, name="next_student"),

    ]