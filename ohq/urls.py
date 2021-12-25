from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'ohq'
urlpatterns = [
    path(route="", view=views.CourseListView.as_view(), name="index"),
    path("search", views.search, name="search"),
    path("course/<int:pk>", views.CourseQueueView.as_view(), name="course_queue"),

    ]