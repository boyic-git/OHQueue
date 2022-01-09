from django.db.models import constraints
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from .models import Student, Instructor, Course, Queue
from django.contrib.auth.models import User, UserManager
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import re


# Create your views here.
class CourseListView(generic.ListView):
    model = Course
    template_name = "ohq/course_list.html"
    context_object_name = "course_list"

    def get_teaching_courses(self):
        is_instructor = Instructor.objects.filter(user=self.request.user).count()
        # at least teaching one courses
        if is_instructor:
            query = Instructor.objects.filter(user=self.request.user)\
                .all()[0].teaching_course.all()
            return query
        return Course.objects.none()
    
    def get_starred_courses(self):
        return Student.objects.filter(user=self.request.user).all()[0]\
            .starred_course.all()
        
    def render_to_response(self, context):
        if not self.request.user.id:
            return redirect('ohq:login')
        return super(CourseListView, self).render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # preferred_courses are the courses being taught or starred by the user
        if not self.request.user.id:
            return context
        teaching_courses = self.get_teaching_courses()
        starred_courses = self.get_starred_courses()
        preferred_courses = teaching_courses.union(starred_courses)
        rest_courses = Course.objects.all().difference(preferred_courses)
        context["teaching_courses"] = teaching_courses
        context["starred_courses"] = starred_courses
        context["rest_courses"] = rest_courses
        # print(self.request.session.get_expiry_age())
        self.request.session.set_expiry(self.request.session.get_expiry_age())
        return context


class MyCourseListView(generic.ListView):
    model = Course
    template_name = "ohq/my_courses.html"
    context_object_name = "course_list"

    def get_teaching_courses(self):
        is_instructor = Instructor.objects.filter(user=self.request.user).count()
        # at least teaching one courses
        if is_instructor:
            query = Instructor.objects.filter(user=self.request.user)\
                .all()[0].teaching_course.all()
            return query
        return Instructor.objects.none()
    
    def get_starred_courses(self):
        return Student.objects.filter(user=self.request.user).all()[0]\
            .starred_course.all()

    def render_to_response(self, context):
        if not self.request.user.id:
            return redirect('ohq:login')
        return super(MyCourseListView, self).render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # preferred_courses are the courses being taught or starred by the user
        if not self.request.user.id:
            return context
        teaching_courses = self.get_teaching_courses()
        starred_courses = self.get_starred_courses()
        context["teaching_courses"] = teaching_courses
        context["starred_courses"] = starred_courses
        self.request.session.set_expiry(self.request.session.get_expiry_age())
        return context

def prepare_search(request):
    request.session.set_expiry(request.session.get_expiry_age())
    if request.method == "POST":
        context = {}
        query = request.POST["search_query"]
        if not query or query.isspace():
            query = " "
        url = "search/q={}".format(query)
        return redirect(url)

    else:
        return render(request, "ohq/course_list.html")

def search(request, query):
    def get_teaching_courses():
        is_instructor = Instructor.objects.filter(user=request.user).count()
        # at least teaching one courses
        if is_instructor:
            query = Instructor.objects.filter(user=request.user)\
                .all()[0].teaching_course.all()
            return query
        return Instructor.objects.none()
    
    def get_starred_courses():
        return Student.objects.filter(user=request.user).all()[0]\
            .starred_course.all()

    request.session.set_expiry(request.session.get_expiry_age())
    if request.method == "GET":
        context = {}
        template = "ohq/search_result.html"

        context["search_query"] = query
        course_list = Course.objects.none()
        if query == " ":
            context["no_result"] = "You are searching for empty keywords. Here are all the courses."
            course_list = Course.objects.all()
        else:
            subject, number, _session = re.compile("([a-zA-Z]+)?([0-9]+)?([a-zA-Z]+)?").match(query).groups()
            if subject:
                course_list = Course.objects.filter(code__istartswith=query).all()
            else:
                if number:
                    course_list = Course.objects.filter(code__icontains=number).all()
            if len(course_list) == 0:
                context["no_result"] = "No results for {}, try another keywords".format(query)
        if len(course_list) == 0:
            course_list = Course.objects.filter(course_name__icontains=query).all()
        
        teaching_courses = get_teaching_courses()
        starred_courses = get_starred_courses()
        context["teaching_courses"] = teaching_courses.intersection(course_list)
        context["starred_courses"] = starred_courses.intersection(course_list)
        context["rest_courses"] = course_list.difference(teaching_courses, starred_courses)
        return render(request, template, context)

    else:
        return render(request, "ohq/course_list.html")


def check_is_instructor(user, course):
    is_instructor = False
    if user.id is not None:
        results = Instructor.objects.filter(user=user, teaching_course=course).count()
        if results > 0:
            is_instructor = True
    return is_instructor

def get_position_in_queue(user, course, joined_time):
    if user.id is not None:
        result = Queue.objects.filter(course=course, joined_time__lt=joined_time).count()
        return result
    return 0

def check_is_joined(user, course):
    if Queue.objects.filter(course=course, student=user.student).count() > 0:
        return True
    return False

def get_number_in_queue(course):
    return Queue.objects.filter(course=course).count()

class CourseQueueView(generic.DetailView):
    model = Course
    template_name = "ohq/course_queue.html"

    def render_to_response(self, context):
        if not self.request.user.id:
            return redirect('ohq:login')
        return super(CourseQueueView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        def get_queue(course):
            result = []
            query_set = Queue.objects.filter(course=course).order_by("joined_time").all()
            for q in query_set:
                temp = {}
                temp["first_name"] = q.student.user.first_name
                temp["question"] = q.question
                temp["queue_checkbox_id"] = q.student.user.username
                temp["invited"] = q.invited
                result.append(temp)
            return result

        def get_subqueue(course):
            result = []
            query_set = Queue.objects.filter(course=course, instructor=self.request.user.instructor).order_by("joined_time").all()
            if len(query_set) == 0:
                return result
            for q in query_set:
                temp = {}
                temp["first_name"] = q.student.user.first_name
                temp["question"] = q.question
                temp["queue_checkbox_id"] = q.student.user.username
                temp["invited"] = q.invited
                result.append(temp)
            return result

        context = super().get_context_data(**kwargs)
        if not self.request.user.id:
            return context
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        context["course_status"] = course.status
        is_instructor = check_is_instructor(self.request.user, course)
        if is_instructor:
            context["is_instructor"] = is_instructor
            context["queue"] = get_queue(course)
            context["sub_queue"] = get_subqueue(course)
        else:
            is_joined = check_is_joined(self.request.user, course)
            if not is_joined:
                context["is_joined"] = False
                context["number_in_queue"] = get_number_in_queue(course)
            else:
                # only 1 queue object per user allowed
                context["is_joined"] = True
                queue_obj = get_object_or_404(Queue, student=self.request.user.student)
                context["is_invited"] = queue_obj.invited
                joined_time = queue_obj.joined_time
                context["number_in_queue"] = get_position_in_queue(self.request.user, course, joined_time)
                context["student_question"] = queue_obj.question
                if queue_obj.invited:
                    context["link"] = course.meeting_link
        self.request.session.set_expiry(self.request.session.get_expiry_age())
        return context


def change_queue_status(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        is_instructor = check_is_instructor(request.user, course)
        if is_instructor:
            course.status = not course.status
            course.save()
    return redirect(request.META['HTTP_REFERER'])

def set_meeting_link(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        is_instructor = check_is_instructor(request.user, course)
        meeting_link = request.POST["meeting_link"]
        if is_instructor:
            course.meeting_link = meeting_link
            course.save()
    return redirect(request.META['HTTP_REFERER'])


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["user[username]"]
        password = request.POST["user[password]"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # http://localhost:8000/login_request
            return redirect("ohq:index")
        else:
            context["message"] = "Invalid username or password!"
            return render(request, "ohq/login.html", context)
    else:
        return render(request, "ohq/login.html", context)

def logout_request(request):
    logout(request)
    return redirect("ohq:login")

def signup_request(request):
    context = {}
    context["email"] = ""
    context["username"] = ""
    context["first_name"] = ""
    context["last_name"] = ""
    if request.method == "POST":
        username = request.POST["user[username]"]
        password = request.POST["user[password]"]
        password_confirm = request.POST["user[password1]"]
        email = request.POST["user[email]"]
        first_name = request.POST["user[first_name]"]
        last_name = request.POST["user[last_name]"]

        context["email"] = email
        context["username"] = username
        context["first_name"] = first_name
        context["last_name"] = last_name

        # check if username is taken
        is_exist = False
        try:
            User.objects.get(username=username)
            is_exist = True
        except:
            pass
        if is_exist: # username is taken
            context["message"] = "Username is taken! Try login or using a different username."
            return render(request, "ohq/signup.html", context)
        else: # okay to signup with the username
            # check if passwords matches
            if password != password_confirm:
                context["message"] = "Passwords do not match!"
                return render(request, "ohq/signup.html", context)
            user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
            student = Student.objects.create(user=user)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # http://localhost:8000/login_request
            if request.META['HTTP_REFERER'][-6:] == "signup":
                return redirect("ohq:index")
            return redirect(request.META['HTTP_REFERER'])
        else:
            context["message"] = "Invalid username or password!"
            return render(request, "ohq/login.html", context)
    else:
        return render(request, "ohq/signup.html", context)

def change_password(request):
    if not request.user.id:
        return redirect("ohq:login")
    context = {}
    if request.method == "POST":
        old_password = request.POST["user[old_password]"]
        password = request.POST["user[password]"]
        password_confirm = request.POST["user[password1]"]
        user = authenticate(username=request.user.username, password=old_password)
        if user is None:
            context["password_message"] = "Invalid password! Try again."
            return render(request, "ohq/change_password.html", context)
        else:
            if password != password_confirm:
                context["password_message"] = "New passwords do not match!"
                return render(request, "ohq/manage_account.html", context)
            # elif old_password == password:
            #     context["message"] = "New password should be different from old password!"
            #     return render(request, "ohq/change_password.html", context)
            else:
                user.set_password(password)
                user.save()
                user = authenticate(username=request.user.username, password=password)
                login(request, user)
                context["success_password_message"] = "Passowrd is successfully changed."
                return render(request, "ohq/manage_account.html", context)
    else:
        return render(request, "ohq/manage_account.html", context)
    
def change_preferred_name(request):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    context = {}
    if request.method == "POST":
        preferred_name = request.POST["user[preferred_name]"]
        if not preferred_name:
            context["name_message"] = "Preferred name is set same as your first name."
            return render(request, "ohq/manage_account.html", context)
        else:
            request.user.student.preferred_name = preferred_name
            request.user.save()
            context["success_name_message"] = "New preferred name is set."
            return render(request, "ohq/manage_account.html", context)
    else:
        return render(request, "ohq/manage_account.html", context)

def join_queue(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    context = {}
    if request.method == "POST":
        student_question = request.POST["student_question"]
        course = get_object_or_404(Course, pk=pk)
        if Queue.objects.filter(course=course, student=request.user.student).count() > 0:
            # joined queue, change student question
            queue = Queue.objects.filter(course=course, student=request.user.student).all()[0]
            queue.question = student_question
            queue.save()
        else: # haven't joined queue
            Queue.objects.create(course=course, student=request.user.student, \
                question=student_question)
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect("ohq:index")

def quit_queue(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    context = {}
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        if Queue.objects.filter(course=course, student=request.user.student).count() > 0:
            # joined queue, change student question
            queue = Queue.objects.filter(course=course, student=request.user.student).all()[0]
            queue.delete()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect("ohq:index")

def invite_students(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    context = {}
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        queues = Queue.objects.filter(course=course).all()
        for q in queues:
            if q.invited:
                q.delete()
            else:
                username = q.student.user.username
                if request.POST[username] == "yes":
                    q.instructor.add(request.user.instructor)
                    q.invited = True
                    q.save()
        return redirect(request.META['HTTP_REFERER'])       
    else:
        return redirect("ohq:index")

def next_student(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    context = {}
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        previous_students = Queue.objects.filter(course=course, invited=True).all()
        next_students = Queue.objects.filter(course=course, invited=False).order_by("joined_time").all()
        for q in previous_students:
                if q.invited:
                    q.delete()
        if len(next_students) == 0:
            return redirect(request.META['HTTP_REFERER'])
        else:
            next_student = next_students[0]
            next_student.instructor.add(request.user.instructor)
            next_student.invited = True
            next_student.save()
            return redirect(request.META['HTTP_REFERER'])       
    else:
        return redirect("ohq:index")

def put_back(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    context = {}
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        queues = Queue.objects.filter(course=course, invited=True).all()
        for q in queues:
            username = q.student.user.username
            if request.POST[username] == "yes":
                q.instructor.remove(request.user.instructor)
                q.invited = False
                q.save()
        return redirect(request.META['HTTP_REFERER'])       
    else:
        return redirect("ohq:index")

def clear_queue(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    context = {}
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        queues = Queue.objects.filter(course=course).all()
        for q in queues:
            q.delete()
        return redirect(request.META['HTTP_REFERER'])       
    else:
        return redirect("ohq:index")

def star_course(request, pk):
    if not request.user.id:
        return redirect("ohq:login")
    request.session.set_expiry(request.session.get_expiry_age())
    context = {}
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        student = request.user.student
        if Student.objects.filter(user=request.user, starred_course=course).count() > 0:
            student.starred_course.remove(course)
        else:
            student.starred_course.add(course)
        student.save()
        return redirect(request.META['HTTP_REFERER'])       
    else:
        return redirect("ohq:index")

## TODO: look here
## NOTE: test the ajax view in a test page
def refresh_queue_view(request, pk):
    def get_queue(course):
        result = []
        query_set = Queue.objects.filter(course=course).order_by("joined_time").all()
        for q in query_set:
            temp = {}
            temp["first_name"] = q.student.user.first_name
            temp["question"] = q.question
            temp["queue_checkbox_id"] = q.student.user.username
            temp["invited"] = q.invited
            result.append(temp)
        return result

    def get_subqueue(course):
        result = []
        query_set = Queue.objects.filter(course=course, instructor=request.user.instructor).order_by("joined_time").all()
        if len(query_set) == 0:
            return result
        for q in query_set:
            temp = {}
            temp["first_name"] = q.student.user.first_name
            temp["question"] = q.question
            temp["queue_checkbox_id"] = q.student.user.username
            temp["invited"] = q.invited
            result.append(temp)
        return result

    context = {}
    context["number"] = request.user.id
    
    if not request.user.id:
        return context
    course = get_object_or_404(Course, pk=pk)
    context["course_status"] = course.status
    context["course_pk"] = course.pk
    is_instructor = check_is_instructor(request.user, course)
    if is_instructor:
        context["is_instructor"] = is_instructor
        context["queue"] = get_queue(course)
        context["sub_queue"] = get_subqueue(course)
    else:
        is_joined = check_is_joined(request.user, course)
        if not is_joined:
            context["is_joined"] = False
            context["number_in_queue"] = get_number_in_queue(course)
        else:
            # only 1 queue object per user allowed
            context["is_joined"] = True
            queue_obj = get_object_or_404(Queue, student=request.user.student)
            context["is_invited"] = queue_obj.invited
            joined_time = queue_obj.joined_time
            context["number_in_queue"] = get_position_in_queue(request.user, course, joined_time)
            context["student_question"] = queue_obj.question
            if queue_obj.invited:
                context["link"] = course.meeting_link
    request.session.set_expiry(request.session.get_expiry_age())
    return render(request, "ohq/course_queue_status_student.html", context)
