from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'ohq'
urlpatterns = [
    path("", view=views.CourseListView.as_view(), name="index"),
    path("search", views.prepare_search, name="prepare_search"),
    path("search/q=<str:query>", views.search, name="search"),
    path("login_request", views.login_request, name="login_request"),
    path("logout", views.logout_request, name="logout"),
    path("login", views.login_request, name="login"),
    path("signup", views.signup_request, name="signup_request"),
    path("password", views.change_password, name="change_password"),
    path("change_preferred_name", views.change_preferred_name, name="change_preferred_name"),
    path("my_courses", views.MyCourseListView.as_view(), name="my_courses"),
    path("course/<int:pk>/change_status", views.change_queue_status, name="change_status"),
    path("course/<int:pk>/meeting_link", views.set_meeting_link, name="set_meeting_link"),
    path("course/<int:pk>", views.CourseQueueView.as_view(), name="course_queue"),
    path("course/<int:pk>/join_queue", views.join_queue, name="join_queue"),
    path("course/<int:pk>/quit_queue", views.quit_queue, name="quit_queue"),
    path("course/<int:pk>/invite_students", views.invite_students, name="invite_students"),
    path("course/<int:pk>/next_student", views.next_student, name="next_student"),
    path("course/<int:pk>/put_back", views.put_back, name="put_back"),
    path("course/<int:pk>/clear_queue", views.clear_queue, name="clear_queue"),
    path("course/<int:pk>/star_course", views.star_course, name="star_course"),
    path("course/<int:pk>/ajax", views.refresh_queue_view, name="refresh_queue_view"),

    ]