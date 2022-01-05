from django.db.models import constraints
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Student, Instructor, Course, Queue, SubQueue
from django.contrib.auth.models import User, UserManager
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import re

# Create your views here.
class CourseListView(generic.ListView):
    model = Course
    template_name = "course_list.html"
    context_object_name = "course_list"

    # def get_queryset(self):
    #     courses = Course.objects.all()
    #     return courses

def search(request):
    if request.method == "POST":
        context = {}
        template = "ohq/search_result.html"

        query = request.POST["search_query"]
        context["search_query"] = query
        subject, number, session = re.compile("([a-zA-Z]+)?([0-9]+)?([a-zA-Z]+)?").match(query).groups()
        course_list = None

        if subject:
            course_list = Course.objects.filter(code__istartswith=query).all()
        else:
            if number:
                course_list = Course.objects.filter(code__icontains=number).all()

        if len(course_list) == 0:
            course_list = Course.objects.filter(course_name__icontains=query).all()

        if len(course_list) == 0:
            context["no_result"] = "No results for {}, try another keywords".format(query)
            
        context["course_list"] = course_list
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

    def get_context_data(self, **kwargs):
        def get_queue(course):
            result = []
            query_set = Queue.objects.filter(course=course).order_by("joined_time").all()
            for q in query_set:
                temp = {}
                temp["first_name"] = q.student.user.first_name
                temp["question"] = q.question
                temp["queue_checkbox_id"] = q.student.user.username
                result.append(temp)
            return result

        def get_subqueue(course):
            result = []
            query_set = SubQueue.objects.filter(course=course, instructor=self.request.user.instructor).order_by("sub_queue__joined_time").all()
            sub_queue = query_set[0].sub_queue.all()
            for q in sub_queue:
                print(q)
                temp = {}
                temp["first_name"] = q.student.user.first_name
                temp["question"] = q.question
                temp["queue_checkbox_id"] = q.student.user.username
                result.append(temp)
            return result

        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
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
                joined_time = queue_obj.joined_time
                context["number_in_queue"] = get_position_in_queue(self.request.user, course, joined_time)
                context["student_question"] = queue_obj.question
        return context


def change_queue_status(request, pk):
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        is_instructor = check_is_instructor(request.user, course)
        if is_instructor:
            course.status = not course.status
            course.save()
    return redirect(request.META['HTTP_REFERER'])

def set_meeting_link(request, pk):
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
            if request.META['HTTP_REFERER'][-13:] == "login_request":
                return redirect("ohq:index")
            return redirect(request.META['HTTP_REFERER'])
        else:
            context["message"] = "Invalid username or password!"
            return render(request, "ohq/login.html", context)
    else:
        return render(request, "ohq/login.html", context)

def logout_request(request):
    logout(request)
    return redirect("ohq:index")

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
    context = {}
    if request.method == "POST":
        preferred_name = request.POST["user[preferred_name]"]
        if not preferred_name:
            context["name_message"] = "Preferred name is set same as your first name."
            return render(request, "ohq/manage_account.html", context)
        else:
            request.user.preferred_name = preferred_name
            request.user.save()
            context["success_name_message"] = "New preferred name is set."
            return render(request, "ohq/manage_account.html", context)
    else:
        return render(request, "ohq/manage_account.html", context)

def join_queue(request, pk):
    context = {}
    if request.method == "POST":
        student_question = request.POST["student_question"]
        course = get_object_or_404(Course, pk=pk)
        if Queue.objects.filter(course=course, student=request.user.student).count() > 0:
            # joined queue, change student question
            print("change here")
            queue = Queue.objects.filter(course=course, student=request.user.student).all()[0]
            queue.question = student_question
            queue.save()
        else: # haven't joined queue
            Queue.objects.create(course=course, student=request.user.student, \
                question=student_question)
        return redirect(request.META['HTTP_REFERER'])
    else:
        return render(request, "ohq/manage_account.html", context)


# TODO: new stuff
def invite_students(request, pk):
    context = {}
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        queues = Queue.objects.filter(course=course).all()
        sub_queue = SubQueue.objects.create(course=course)
        sub_queue.instructor.add(request.user.instructor)
        question = ""
        for q in queues:
            username = q.student.user.username
            if request.POST[username] == "yes":
                sub_queue.sub_queue.add(q)
                if len(question) + len(q.question) + 1 < SubQueue.question.field.max_length:
                    question += q.question + "\n"
        sub_queue.question = question
        sub_queue.save()
        if sub_queue.sub_queue.count() == 0:
            sub_queue.delete()
        # print(sub_queue.sub_queue)
                
        
        
    else:
        return render(request, "ohq/manage_account.html", context)

def change_queue_status(request, pk):
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        is_instructor = check_is_instructor(request.user, course)
        if is_instructor:
            course.status = not course.status
            course.save()
    return redirect(request.META['HTTP_REFERER'])
