import uuid
from datetime import date, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings, BlobSasPermissions
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone

from schedule.models import ClassSchedule, Attendance
from yogastudio import settings
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from django.utils.text import slugify

from hashlib import sha256

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import VideoForm
from .models import RegisteredStudent, RegisteredInstructor, Feedback, Videos, Courses, Course_purchase, \
    Category, Cart, Product, Payment, OrderPlaced, Whishlist, Daily_Progress, Course_Completed, Salary  # Login
from .tokens import generate_token
from .forms import DeliveryAddressForm
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger

from .models import DeliveryAddress


# Create your views here.


def index(request):
    return render(request, "index.html")


def Studentregistration(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        student_image = request.FILES.get('student_image')

        if User.objects.filter(email=email).exists():
            messages.info(request, "Email already Exist...!")
            return redirect('yogaapp:studentregistration')
        else:
            data = User.objects.create_user(username=email, password=password)
            std = RegisteredStudent(user_id=data, phone=phone, first_name=firstname, last_name=lastname, email=email, student_image=student_image)
            data.is_active = False
            data.save()
            std.save()
            messages.info(request, "We have sent you a mail ,please confirm your mail id")
            # Welcome mail

            subject = 'Welcome Message'
            message = f'Hi {firstname} , \nWelcome to yogastudio.\n We have sent you a confirmation mail please confirm it.'
            from_mail = settings.EMAIL_HOST_USER
            to_list = [data.username]
            send_mail(subject, message, from_mail, to_list, fail_silently=True)

            # Confirmation mail

            current_site = get_current_site(request)
            email_subject = "Yogastudio Confirmation mail"
            message2 = render_to_string('email_confirmation.html', {

                'name': std.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(data.pk)),
                'token': generate_token.make_token(data)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [data.username],
            )
            email.fail_silently = True
            email.send()

            return redirect('yogaapp:login')

    return render(request, 'student_register.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        data = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        data = None

    if data is not None and generate_token.check_token(data, token):
        data.is_active = True

        data.save()

        messages.success(request, "Your Account has been activated!!")
        return redirect('yogaapp:login')
    else:
        return render(request, 'activation_failed.html')


def Login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active == True:
                login(request, user)
                if RegisteredStudent.objects.filter(user_id=request.user.id).exists():
                    return redirect("yogaapp:studentdashboard")
                    # return HttpResponse("Student login")
                elif RegisteredInstructor.objects.filter(user_id=request.user.id).exists():
                    # return HttpResponse("Instructor login")
                    return redirect("yogaapp:instructordashboard")
                else:

                    return redirect('admin/')
            else:
                messages.info("Please confirm your email id")

        else:
            messages.info(request, "Invalid credentials")
            return redirect('yogaapp:login')

    return render(request, 'login.html')


def Logout(request):
    logout(request)
    return redirect("yogaapp:login")


def Passwdemail(request):
    if request.method == "POST":
        email = request.POST['email']
        user = User.objects.get(username=email)
        std = RegisteredStudent.objects.get(user_id=user.id)
        current_site = get_current_site(request)
        email_subject = "Yogastudio Confirmation mail"
        message2 = render_to_string('password_reset.html', {

            'name': std.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.username],
        )
        email.fail_silently = True
        email.send()
        messages.info(request, "We have sent you a confirmation mail please confirm your email")

        return redirect("yogaapp:passwd_email")
    return render(request, "Passwdemail.html")


def forgotpassword(request, uidb64):
    if request.method == "POST":
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
        print(uid)
        password = request.POST['new_password']
        cpassword = request.POST['con_password']
        if password == cpassword:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password Reset Successful')
            return redirect("yogaapp:login")

        else:
            messages.error(request, 'Password Mismatch')
    return render(request, 'forgotpassword.html')


def Password_reset(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        data = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        data = None

    if data is not None and generate_token.check_token(data, token):
        return redirect('yogaapp:forgotpassword', uidb64)
    else:
        return render(request, 'activation_failed.html')



@login_required(login_url='login')
def studentdashboard(request, c_slug=None, v_slug=None):
    std = RegisteredStudent.objects.get(user_id=request.user.id)
    print(std.first_name)
    c_videos = None
    video_key = None
    if c_slug != None:
        course = get_object_or_404(Courses, slug=c_slug)
        print(course.pk)
        videos = Videos.objects.filter(course_id=course.pk)

        # Fetch the video URL from Azure Blob Storage for each video
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)
        for video in videos:
            blob_client = container_client.get_blob_client(video.title)
            video.video_url = blob_client.url

        paginator = Paginator(videos, 2)  # 10 videos per page
        try:
            page = int(request.GET.get('page', '1'))
        except:
            page = 1
        try:
            videos = paginator.page(page)
        except (EmptyPage, InvalidPage):
            videos = paginator.page(paginator.num_pages)
        if v_slug and c_slug != None:
            course_progress = Daily_Progress.objects.filter(course_id=course.id, user_id=std.user_id_id).count()
            if Course_Completed.objects.filter(course_id=course.id, user_id=std.user_id_id).exists():
                pass
            else:
                if course_progress == course.duration:
                    data = Course_Completed(course_id=course.id, user_id=std.user_id_id)
                    data.save()

            video = get_object_or_404(Videos, slug=v_slug)
            print(video.course_id)
            try:
                progress = get_object_or_404(Daily_Progress, video_id=video.id, user=request.user.id)
                progress_value = progress.progress
            except:
                progress_value = 0
            return render(request, 'studentdashboard.html', {"c_videos": videos, "video_key": video, "std": std,"instructor":course.user_id_id,'c_id':course.pk,"progress":progress_value})

        return render(request, 'studentdashboard.html', {"c_videos": videos, "std": std,"instructor":course.user_id_id,'c_id':course.pk,"course": course})

    else:
        id = request.user.id
        courses = Courses.objects.all()
        std = RegisteredStudent.objects.get(user_id=id)
        return render(request, 'studentdashboard.html', {'std': std, 'courses': courses})


def Progress_update(request, progress, video):
    try:
        std = RegisteredStudent.objects.get(user_id=request.user.id)
        v = Videos.objects.get(title=video)
        print(v.course)
        course = Courses.objects.get(course=v.course)
        print(course)
        p = Daily_Progress.objects.get(user_id=std, video_id=v)
        if p.progress < progress:
            p.progress = progress
            p.save()

    except:
        Daily_Progress(progress=progress, video_id=v.id, user=std, course=course).save()
    return HttpResponse("Hello")



def aboutcourse(request, c_id):
    user = RegisteredStudent.objects.get(user_id=request.user.id)
    course = Courses.objects.get(id=c_id)
    purchase_date = Course_purchase.objects.filter(user=request.user, course=course).values_list('purhase_date', flat=True).first()

    context = {
        'course': course,
        'purchase_date': purchase_date,
        'user': user
    }

    return render(request, 'aboutcourse.html', context)





def addvideo(request):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    courses = Courses.objects.filter(user_id=request.user.id)

    if request.method == 'POST':
        form = VideoForm(ins,request.POST, request.FILES)
        if form.is_valid():
            # Get the form data
            title = form.cleaned_data['title']
            course = form.cleaned_data['course']
            video_file = request.FILES['video']

            # Set up the Azure Blob Storage client
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)

            # Upload the video file to Azure Blob Storage
            blob_client = container_client.get_blob_client(title)
            blob_client.upload_blob(video_file)

            # Create a new video object in the database
            Videos(title=title, slug=slugify(title), course=course, video_url=blob_client.url).save()
            messages.success(request, 'Video uploaded successfully.')

            return redirect("yogaapp:addvideo")
    else:
        form = VideoForm(ins)

    return render(request, "Add_Video.html", {"form": form,'ins':ins,'courses':courses})

def Student_progress(request):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    c = Courses.objects.get(user_id_id=request.user.id)
    students = Daily_Progress.objects.filter(course_id=c.id)
    return render(request, "Student_progress.html", {"students": students})

def instructorviewvideos(request):
    # Retrieve all video objects from the database
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    c = Courses.objects.get(user_id_id=request.user.id)
    students = Daily_Progress.objects.filter(course_id=c.id)
    courses = Courses.objects.filter(user_id=ins)
    videos = Videos.objects.filter(course__in=courses)

    for video in videos:
        # Get the blob client for the video file
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)
        blob_client = container_client.get_blob_client(video.title)

        # Generate the blob URL without the SAS token
        blob_url = blob_client.url.split('?')[0]

        # Embed the video in an HTML5 video player
        video.html = f'<video src="{blob_url}" controls></video>'

    return render(request, 'instructorviewvideos.html', {'ins': ins, 'videos': videos,"students": students})

def delete_video(request, video_id):
    # Get the video object
    video = Videos.objects.get(id=video_id)

    # Delete the video file from Azure Blob
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)
    blob_client = container_client.get_blob_client(video.title)
    blob_client.delete_blob()

    # Delete the video object from the database
    video.delete()

    # Redirect to the instructor's video view
    return redirect('yogaapp:instructorviewvideos')



def studentviewprofile(request):
    user = RegisteredStudent.objects.get(user_id=request.user.id)
    return render(request, 'studentviewprofile.html', {'user': user})


def studentupdate(request):
    user = User.objects.get(id=request.user.id)
    std = RegisteredStudent.objects.get(user_id=request.user.id)
    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        phone = request.POST['phone']

        std.first_name = firstname
        std.last_name = lastname
        std.phone = phone
        if 'student_image' in request.FILES:
            student_image_file = request.FILES['student_image']
            std.student_image.delete()  # delete the old student_image file if it exists
            std.student_image.save(student_image_file.name, student_image_file, save=True)

        std.save()
        messages.success(request, 'Profile updated successfully')
        return redirect("yogaapp:studentviewprofile")
    return render(request, 'studentupdate.html', {'std': std})


def studentchangepassword(request):
    std= RegisteredStudent.objects.get(user_id=request.user.id)
    if request.method == "POST":
        old_password = request.POST.get('passwd', False)
        user = authenticate(username=request.user.username, password=old_password)
        if user != None:
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']
            if new_password == confirm_password:
                data = User.objects.get(id=request.user.id)
                data.set_password(new_password)
                data.save()
                messages.success(request, 'Password Changed Successfully')
                return redirect("yogaapp:login")
            else:
                messages.error(request, 'Password Mismatch')
        else:
            messages.error(request, 'Old Password Not Matching')
    return render(request, 'studentchangepassword.html',{'std':std})







# def coursesenrolled(request):
#     user = RegisteredStudent.objects.get(user_id=request.user.id)
#     c = Course_purchase.objects.filter(user_id=request.user.id).values_list('course_id', flat=True)
#     print(list(c))
#     courses = Courses.objects.filter(id__in=c)
#     return render(request, 'coursesenrolled.html', {'c': courses, 'user': user})
# def aboutcourse(request,c_id):
#     user = RegisteredStudent.objects.get(user_id=request.user.id)
#     courses_purchased = Course_purchase.objects.filter(user_id=request.user.id).values_list('course_id', flat=True)
#     purchase_dates = Course_purchase.objects.filter(user=request.user).values_list('purhase_date', flat=True)
#
#     purchased_course_details = []
#     for course_id in courses_purchased:
#         course_detail = Courses.objects.get(id=c_id)
#         purchased_course_details.append(course_detail)
#
#     context = {
#         'purchased_courses': purchased_course_details,
#         'purchase_date':purchase_dates,
#         'user':user
#     }
#
#     return render(request, 'aboutcourse.html', context)
















def availablecourses(request):
    user = RegisteredStudent.objects.get(user_id=request.user.id)
    try:
        pp = Course_purchase.objects.filter(user_id=request.user.id).values_list('course_id', flat=True)
        print(list(pp))
        j=list(pp)
    except:
        print('error')
    c = Courses.objects.all()
    return render(request, 'availablecourses.html', {'c': c, 'user': user,'endrolled':j})


def Course_endroll(request, c_slug):
    user = RegisteredStudent.objects.filter(user_id=request.user.id)
    c = Courses.objects.get(slug=c_slug)
    endroll = Course_purchase(course_id=c.id, user_id=request.user.id, end_date=c.end_date)
    endroll.save()
    return redirect("yogaapp:availablecourses")


def checkoutcourse(request, c_slug):
    user = RegisteredStudent.objects.get(user_id=request.user.id)
    course = get_object_or_404(Courses, slug=c_slug)


    razoramount = course.amount*100
    print(razoramount)
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
    data = {
        "amount": razoramount,
        "currency": "INR",
        "receipt": "order_rcptid_11"}
    payment_response = client.order.create(data=data)
    print(payment_response)
    order_id = payment_response['id']
    request.session['order_id'] = order_id
    order_status = payment_response['status']
    if order_status == 'created':
        payment = Payment(user_id=request.user.id,
                          amount=razoramount,
                          razorpay_order_id=order_id,
                          razorpay_payment_status=order_status)
        payment.save()
    request.session['course_id'] = course.id
    context = {
        'course': course,
        'user':user,
        'razoramount': razoramount
    }
    return render(request, 'checkoutcourse.html', context)

def payment_done_course(request):
    order_id = request.session['order_id']
    payment_id = request.GET.get('payment_id')
    print(payment_id)

    payment = Payment.objects.get(razorpay_order_id=order_id)

    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.course = Courses.objects.get(id=request.session['course_id'])
    payment.save()

    user = request.user.id
    course = payment.course.id
    purchase_date = datetime.now().date()
    end_date = purchase_date + timedelta(days=30)  # or any other duration you want to set
    course_purchase = Course_purchase(user_id=user, course_id=course, purhase_date=purchase_date, end_date=end_date)
    course_purchase.save()


    return redirect('yogaapp:availablecourses')




# @login_required(login_url='login')
# def checkout(request):
#     user = request.user.id
#     cart = Cart.objects.filter(user_id=user)
#     totalitem = 0
#     total = 0
#     for i in cart:
#         total += i.product.price * i.product_qty
#         totalitem = len(cart)
#     razoramount = total * 100
#     print(razoramount)
#     client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
#     data = {
#         "amount": razoramount,
#         "currency": "INR",
#         "receipt": "order_rcptid_11"}
#     payment_response = client.order.create(data=data)
#     print(payment_response)
#     order_id = payment_response['id']
#     request.session['order_id'] = order_id
#     order_status = payment_response['status']
#     if order_status == 'created':
#         payment = Payment(user_id=request.user.id,
#                           amount=total,
#                           razorpay_order_id=order_id,
#                           razorpay_payment_status=order_status)
#         payment.save()
#
#     delivery_addresses = DeliveryAddress.objects.filter(user=user)
#
#     return render(request, 'checkout.html',
#                   {'delivery_addresses': delivery_addresses, 'cart': cart, 'total': total, 'totalitem': totalitem,'razoramount': razoramount})
@login_required(login_url='login')
def checkout(request):
    user = request.user.id
    cart = Cart.objects.filter(user_id=user)
    totalitem = 0
    total = 0
    for i in cart:
        total += i.product.price * i.product_qty
        totalitem = len(cart)
    # Calculate the GST amount and add it to the total
    gst_amount = round(total * i.product.gst_rate, 2)
    total += gst_amount

    razoramount = total * 100
    print(razoramount)
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
    data = {
        "amount": razoramount,
        "currency": "INR",
        "receipt": "order_rcptid_11"}
    payment_response = client.order.create(data=data)
    print(payment_response)
    order_id = payment_response['id']
    request.session['order_id'] = order_id
    order_status = payment_response['status']
    if order_status == 'created':
        payment = Payment(user_id=request.user.id,
                          amount=total,
                          razorpay_order_id=order_id,
                          razorpay_payment_status=order_status)
        payment.save()

    delivery_addresses = DeliveryAddress.objects.filter(user=user)

    return render(request, 'checkout.html',
                  {'delivery_addresses': delivery_addresses, 'cart': cart, 'total': total, 'totalitem': totalitem, 'razoramount': razoramount, 'gst_amount': gst_amount})


def payment_done(request):
    order_id = request.session['order_id']
    payment_id = request.GET.get('payment_id')
    print(payment_id)

    payment = Payment.objects.get(razorpay_order_id=order_id)

    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()

    cart = Cart.objects.filter(user_id=request.user.id)

    delivery=DeliveryAddress.objects.get(user_id=request.user.id)
    print(delivery)

    for c in cart:
        OrderPlaced(user_id=request.user.id, product=c.product, quantity=c.product_qty, payment=payment,
                    is_ordered=True,delivery_address_id=delivery.id).save()
        c.delete()
        c.product.stock -= c.product_qty
        c.product.save()

    return redirect('yogaapp:orders')


# def feedback(request):
#     user = get_object_or_404(RegisteredStudent, user_id=request.user.id)
#     courses = Courses.objects.filter(course_purchase__user_id=request.user.id)
#
#     if request.method == 'POST':
#         course_id = request.POST.get('course')
#         feedback_text = request.POST.get('feedback')
#
#         course = get_object_or_404(Courses, pk=course_id)
#
#         if Feedback.objects.filter(course=course).exists():
#             # A Feedback object already exists for this course
#             # Redirect back to the feedback form with an error message
#             return render(request, 'feedback.html',
#                           {'courses': courses, 'user': user, 'error': 'Feedback already submitted for this course.'})
#
#         feedback = Feedback(user=user, course=course, feedback=feedback_text)
#         feedback.save()
#
#         # Redirect back to the feedback form with a success message
#         return render(request, 'feedback.html',
#                       {'courses': courses, 'user': user, 'success': 'Feedback submitted successfully.'})
#
#     return render(request, 'feedback.html', {'courses': courses, 'user': user})
def feedback(request):
    user = get_object_or_404(RegisteredStudent, user_id=request.user.id)
    courses = Courses.objects.filter(course_purchase__user_id=request.user.id)

    if request.method == 'POST':
        course_id = request.POST.get('course')
        feedback_text = request.POST.get('feedback')

        course = get_object_or_404(Courses, pk=course_id)

        if Feedback.objects.filter(course=course).exists():
            # A Feedback object already exists for this course
            # Redirect back to the feedback form with an error message
            messages.error(request, 'Feedback already submitted for this course.')
            return render(request, 'feedback.html', {'courses': courses, 'user': user})

        feedback = Feedback(user=user, course=course, feedback=feedback_text)
        feedback.save()

        # Redirect back to the feedback form with a success message
        messages.success(request, 'Feedback submitted successfully.')
        return render(request, 'feedback.html', {'courses': courses, 'user': user})

    return render(request, 'feedback.html', {'courses': courses, 'user': user})



def insrtructorregistration(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        cv = request.FILES.get('cv')
        certificate = request.FILES.get('certificate')
        password = request.POST.get('password')
        ins_image = request.FILES.get('ins_image')


        if User.objects.filter(username=email).exists():
            messages.info(request, "Email already Exist...!")
            return redirect('yogaapp:insrtructorregistration')
        else:
            user = User.objects.create_user(username=email, password=password)
            inst = RegisteredInstructor(user_id=user, first_name=firstname, last_name=lastname, phone=phone, cv=cv,
                                        certificate=certificate, email=email, instructor_image=ins_image)
            user.save()
            inst.save()
            messages.info(request, "We have sent you a mail ,please confirm your mail id")

            # Welcome mail

            subject = 'Welcome Message'
            message = f'Hi {firstname} , \nWelcome to yogastudio.'
            from_mail = settings.EMAIL_HOST_USER
            to_list = [user.username]
            send_mail(subject, message, from_mail, to_list, fail_silently=True)

            # Confirmation mail

            current_site = get_current_site(request)
            email_subject = "Yogastudio Confirmation mail"
            message2 = render_to_string('email_confirmation.html', {

                'name': inst.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [user.username],
            )
            email.fail_silently = True
            email.send()

            return redirect('yogaapp:login')
    return render(request, 'register.html')

@login_required(login_url='login')
def instructordashboard(request):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    courses = Courses.objects.filter(user_id=request.user.id)
    class_schedules = ClassSchedule.objects.filter(course__in=courses)
    context = {
        'ins': ins,
        'courses': courses,
        'class_schedules': class_schedules,
    }
    return render(request, 'instructordashboard.html', context)



def instructorviewprofile(request):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    courses = Courses.objects.filter(user_id=request.user.id)

    # Retrieve the salary details for the instructor's courses
    salary_details = Salary.objects.filter(course__user_id=request.user.id)

    return render(request, 'instructorviewprofile.html', {
        'ins': ins,
        'courses': courses,
        'salary_details': salary_details,
    })


def salary_details(request, salary_id):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    salary = Salary.objects.get(id=salary_id)
    courses = Courses.objects.filter(user_id=request.user.id)
    return render(request, 'salary_details.html', {'salary': salary,'courses':courses,'ins': ins})


def instructorchangepassword(request):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    courses = Courses.objects.filter(user_id=request.user.id)
    if request.method == "POST":
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            user = authenticate(username=request.user.username, password=old_password)
            if user != None:
                data = User.objects.get(username=user)
                data.set_password(new_password)
                data.save()
                messages.info(request, "Password updated successfully")
                return redirect("yogaapp:instructordashboard")
        else:
            messages.info(request, "Invalid password")

    return render(request, 'instructorchangepwd.html',{'ins':ins,'courses': courses})


# Allotted Students

def instructorallotedstudents(request):
    try:
        ins = RegisteredInstructor.objects.get(user_id=request.user.id)
        c = Courses.objects.get(user_id_id=request.user.id)
        purchase_stds = Course_purchase.objects.filter(course_id=c.id).values_list('user_id', flat=True)
        std = RegisteredStudent.objects.filter(user_id__in=purchase_stds)
        print(list(std))
        return render(request, 'instructorassignedstudents.html', {'course': c, 'std': std, 'ins': ins})
    except Courses.DoesNotExist:
        return HttpResponse('<p style="color:red;text-align:center;margin-top:350px;">You have not been allotted any course yet.</p>')





def instructorviewfeedback(request):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    courses = Courses.objects.filter(user_id=request.user.id)
    if not courses:
        return HttpResponse('<p style="color:red;text-align:center;margin-top:350px;">You have not been allotted any course yet.</p>')

    course = courses[0]
    feed = Feedback.objects.filter(course_id=course.id)
    std_ids = feed.values_list("user_id", flat=True)
    std = RegisteredStudent.objects.filter(user_id__in=std_ids)
    std_feed = zip(feed, std)
    return render(request, 'instructorviewfeedback.html', {'ins': ins, 'std_feed': std_feed,'courses':courses})


def instructorupdate(request):
    data = User.objects.get(id=request.user.id)
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    cv = ins.cv.url if ins.cv else None
    certificate = ins.certificate.url if ins.certificate else None
    instructor_image = ins.instructor_image.url if ins.instructor_image else None

    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        phone = request.POST['phone']
        bio = request.POST['bio']

        ins.first_name = firstname
        ins.last_name = lastname
        ins.phone = phone
        ins.bio = bio

        if 'cv' in request.FILES:
            cv_file = request.FILES['cv']
            ins.cv.delete()
            ins.cv.save(cv_file.name, cv_file, save=True)

        if 'certificate' in request.FILES:
            certificate_file = request.FILES['certificate']
            ins.certificate.delete()
            ins.certificate.save(certificate_file.name, certificate_file, save=True)

        if 'ins_image' in request.FILES:
            image_file = request.FILES['ins_image']
            ins.instructor_image.delete()
            ins.instructor_image.save(image_file.name, image_file, save=True)

        ins.save()
        messages.success(request, "Profile updated successfully")
        return redirect("yogaapp:instructorviewprofile")

    return render(request, 'instructorupdate.html',
                  {'ins': ins, 'cv': cv, 'certificate': certificate, 'instructor_image': instructor_image})


def Course_cancel(request, course_id):
    course = get_object_or_404(Course_purchase, course_id=course_id, user_id=request.user.id)
    course.delete()
    return redirect("yogaapp:coursesenrolled")


def product(request):
    category = Category.objects.all()
    products = Product.objects.all()
    num_items = Cart.objects.filter(user_id=request.user.id).count()
    wishlist_items = Whishlist.objects.filter(user_id=request.user.id).values_list('product_id', flat=True)

    # Price filter
    price_range = request.GET.get('price_range')
    if price_range:
        price_range = price_range.split('-')
        min_price = price_range[0]
        max_price = price_range[1]
        products = products.filter(price__gte=min_price, price__lte=max_price)
    else:
        # If price_range parameter is empty, show all products
        products = Product.objects.all()
    # Pagination code
    paginator = Paginator(products, 3)  # Show 10 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    return render(request, 'products.html', {'data': category, 'products': products, 'num_items': num_items, 'wishlist_items': wishlist_items})


def search(request):
    query = request.GET.get('q')
    category = Category.objects.all()
    num_items = Cart.objects.filter(user_id=request.user.id).count()

    if query:
        # If a search query was entered, filter products by name or description containing or starting with the query
        products = Product.objects.filter(Q(name__icontains=query) | Q(name__startswith=query))
        paginator = Paginator(products, 3)  # Show 3 products per page
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            products = paginator.page(paginator.num_pages)
        return render(request, 'products.html', {'data': category, 'products': products, 'num_items': num_items, 'query': query})
    else:
        # If no search query was entered, return all products
        product = Product.objects.all()
        paginator = Paginator(product, 3)  # Show 3 products per page
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            products = paginator.page(paginator.num_pages)
        return render(request, 'products.html', {'data': category, 'product': product, 'products': products, 'num_items': num_items})








def singleproduct(request, id):
    prod = Product.objects.filter(id=id)
    return render(request, 'singleproduct.html', {'prod': prod})


@login_required(login_url='login')
def addcart(request, id):
    user = request.user.id
    item = Product.objects.get(id=id)
    if item.stock > 0:
        if Cart.objects.filter(user_id=user, product_id=item).exists():
            messages.success(request, 'Product Already in the cart ')
            return redirect("yogaapp:product")
        else:
            product_qty = 1
            price = item.price * product_qty

            new_cart = Cart(user_id=user, product_id=item.id, product_qty=product_qty, price=price)
            new_cart.save()
            messages.success(request, 'Product added to the Cart ')
            return redirect("yogaapp:product")
            # return render(request,'product.html')


# Cart Quentity Plus Settings
def plusqty(request, id):
    cart = Cart.objects.filter(id=id)
    for cart in cart:
        if cart.product.stock > cart.product_qty:
            cart.product_qty += 1
            cart.price = cart.product_qty * cart.product.price
            cart.save()
            return redirect("yogaapp:cart")
        # messages.success(request, 'Out of Stock')
        return redirect("yogaapp:cart")


# Cart Quentity minus Settings
def minusqty(request, id):
    cart = Cart.objects.filter(id=id)
    for cart in cart:
        if cart.product_qty > 1:
            cart.product_qty -= 1
            cart.price = cart.product_qty * cart.product.price
            cart.save()
            return redirect("yogaapp:cart")
        return redirect("yogaapp:cart")


# View Cart Page
@login_required(login_url='login')
def cart(request):
    user = request.user.id
    cart = Cart.objects.filter(user_id=user)
    totalitem = 0
    total = 0
    for i in cart:
        total += i.product.price * i.product_qty
        totalitem = len(cart)

    category = Category.objects.all()
    # subcategory=Subcategory.objects.all()
    return render(request, 'addtocart.html',
                  {'cart': cart, 'total': total, 'category': category, 'totalitem': totalitem})


# Remove Items From Cart
@login_required(login_url='login')
def de_cart(request, id):
    Cart.objects.get(id=id).delete()
    return redirect("yogaapp:cart")




@login_required(login_url='login')
def orders(request):
    orders = OrderPlaced.objects.filter(
        user_id=request.user.id, is_ordered=True).order_by('ordered_date')
    delivery_address=DeliveryAddress.objects.filter(user_id=request.user.id)
    return render(request, 'orders.html',{'orders':orders,'delivery_address':delivery_address})






@login_required(login_url='login')
def delivery_address(request, pk=None):
    delivery_address = None
    if pk:
        delivery_address = DeliveryAddress.objects.get(pk=pk)
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST, instance=delivery_address)
        if form.is_valid():
            delivery_address = form.save(commit=False)
            delivery_address.user = request.user
            delivery_address.save()
            return redirect('yogaapp:checkout')
    else:
        form = DeliveryAddressForm(instance=delivery_address)
    return render(request, 'delivery_address.html', {'form': form})

# def delivery_address(request):

# if request.method == 'POST':
#     form = DeliveryAddressForm(request.POST)
#     if form.is_valid():
#         form.save()
#         messages.success(request, 'New Address Added')
#         return redirect("yogaapp:checkout")
#
#         # Redirect to success page or do something else
# else:
#     form = DeliveryAddressForm()
# return render(request, 'delivery_address.html', {'form': form})

# add to wishlist
@login_required(login_url='login')
def add_wishlist(request,id):
    user = request.user.id
    item=Product.objects.get(id=id)
    if Whishlist.objects.filter( user_id =user,product_id=item).exists():
        messages.success(request, 'Product Already in the wishlist ')
        return redirect('yogaapp:product')
    else:
            new_wishlist=Whishlist(user_id=user,product_id=item.id)
            new_wishlist.save()
            messages.success(request, 'Product added to the wishlist ')
            return redirect('yogaapp:product')



#Wishlist View page
@login_required(login_url='login')
def view_wishlist(request):
        num_items = Cart.objects.filter(user_id=request.user.id).count()
        count = Cart.objects.filter(user_id=request.user.id).count()
        w_count = Whishlist.objects.filter(user_id=request.user.id).count()
        user = request.user.id
        wish=Whishlist.objects.filter(user_id=user)
        category=Category.objects.all()
        return render(request,"wishlist.html",{'wishlist':wish,'category':category,'w_count':w_count,'count':count,'num_items':num_items})


# Remove Items From Wishlist
@login_required(login_url='login')
def de_wishlist(request,id):
    Whishlist.objects.get(id=id).delete()
    return redirect('yogaapp:view_wishlist')

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html= template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from .utils import render_to_pdf


# def get(request, id, *args, **kwargs, ):
#     std = RegisteredStudent.objects.get(user_id=request.user.id)
#     place = OrderPlaced.objects.get(id=id)
#     date = place.ordered_date
#     orders = OrderPlaced.objects.filter(user_id=request.user.id, ordered_date=date)
#     total = 0
#     for o in orders:
#         total = total + (o.product.price * o.quantity)
#     addrs = DeliveryAddress.objects.get(user_id=request.user.id)
#
#     data = {
#         "total": total,
#         "orders": orders,
#         "shipping": addrs,
#         "std":std,
#     }
#     pdf = render_to_pdf('report.html', data)
#     if pdf:
#         response = HttpResponse(pdf, content_type='application/pdf')
#         # filename = "Report_for_%s.pdf" %(data['id'])
#         filename = "Bill.pdf"
#         content = "inline; filename= %s" % (filename)
#         response['Content-Disposition'] = content
#         return response
#     return HttpResponse("Page Not Found")
def get(request, id, *args, **kwargs, ):
    std = RegisteredStudent.objects.get(user_id=request.user.id)
    place = OrderPlaced.objects.get(id=id)
    date = place.ordered_date
    orders = OrderPlaced.objects.filter(user_id=request.user.id, ordered_date=date)
    total = 0
    gst_total = 0
    for o in orders:
        product = o.product
        product_total = product.price * o.quantity
        gst_rate = product.gst_rate
        gst_amount = round(product_total * gst_rate, 2)
        total += product_total
        gst_total += gst_amount
    addrs = DeliveryAddress.objects.get(user_id=request.user.id)

    # Add GST amount to total
    total_with_gst = total + gst_total

    data = {
        "total": total_with_gst,
        "gst_amount": gst_total,
        "orders": orders,
        "shipping": addrs,
        "std":std,
    }
    pdf = render_to_pdf('report.html', data)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Bill.pdf"
        content = "inline; filename= %s" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Page Not Found")









