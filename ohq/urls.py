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
    
    ]