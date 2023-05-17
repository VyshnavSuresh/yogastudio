from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.shortcuts import render

from yogaapp.models import Courses, RegisteredInstructor, RegisteredStudent, Course_purchase


# Create your views here.
def Sentmessage(request,c_id):
    user = RegisteredStudent.objects.get(user_id=request.user.id)
    c = Course_purchase.objects.filter(user_id=request.user.id).values_list('course_id', flat=True)
    courses = Courses.objects.filter(id__in=c)
    course = Courses.objects.get(id=c_id)

    if request.method=="POST":
        msg=request.POST['message']
        course=Courses.objects.get(id=c_id)
        instructor=RegisteredInstructor.objects.get(user_id=course.user_id)
        instructor_id=User.objects.get(username=instructor.user_id)
        student_fname = user.first_name
        student_lname = user.last_name
        course_title = course.course
        email_subject = f"Yogastudio - Message from {student_fname} {student_lname} ({course_title} student)"
        email_body = f"{msg}\n\nSent by {student_fname} {student_lname} from the {course_title} course."
        email = EmailMessage(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [instructor_id],
        )
        email.fail_silently = True
        email.send()
        messages.success(request,"Mail send successfully")
        return render(request, "Message.html", {"msg": msg,'user':user,'c':courses,'course':course})

    return render(request,"Message.html",{'user':user,'c':courses,'course':course})