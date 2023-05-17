import zipfile
from datetime import timedelta
import datetime
import pytz
import xlwt
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Attendance, ClassSchedule, Courses
import pandas as pd
from openpyxl import Workbook
from django.db.models import Count
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from openpyxl.styles import Font, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

from schedule.forms import ClassScheduleForm
from schedule.models import ClassSchedule, Attendance
from yogaapp.models import Courses, RegisteredInstructor, RegisteredStudent, Videos, Course_purchase, Daily_Progress
from .models import ClassSchedule
from django.contrib import messages

def allotclass(request, c_slug):
    # Retrieve the course object
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    course = get_object_or_404(Courses, slug=c_slug)

    # Check if the course has ended
    if course.end_date < timezone.now().date():
        messages.error(request, 'Class scheduling is not allowed for an ended course')
        return redirect('schedule:coursedetails', c_slug=c_slug)

    # Retrieve the instructor associated with the current user
    instructor = get_object_or_404(RegisteredInstructor, user_id=request.user.id)
    current_timezone = timezone.get_current_timezone()

    # Count the number of classes scheduled for the current day
    class_count = ClassSchedule.objects.filter(instructor=instructor, course=course, start_time__date=timezone.now().date()).count()

    if class_count >= 3:
        messages.error(request, 'You can schedule only 3 classes per day')
        return redirect('schedule:coursedetails', c_slug=c_slug)

    if request.method == 'POST':
        form = ClassScheduleForm(request.POST)
        if form.is_valid():
            # Create a new class schedule object with the form data
            class_schedule = form.save(commit=False)
            class_schedule.course = course
            class_schedule.instructor = instructor  # Assign the instructor
            class_schedule.save()
            return redirect('schedule:coursedetails', c_slug=c_slug)
    else:
        form = ClassScheduleForm()

    return render(request, 'allotcourse.html', {'form': form, 'course': course,'ins':ins})


def deleteclass(request, id):
    # Retrieve the class schedule object
    class_schedules = get_object_or_404(ClassSchedule, id=id)

    # Delete the class schedule object
    class_schedules.delete()

    # Redirect back to the course details page
    return redirect('schedule:coursedetails', c_slug=class_schedules.course.slug)


def live_classes(request, c_id):
    std = RegisteredStudent.objects.get(user_id=request.user.id)
    course = Courses.objects.get(id=c_id)
    live_classes = ClassSchedule.objects.filter(course=course)
    return render(request, 'live_classes_student.html', {'live_classes': live_classes, 'course': course,'std':std})



def coursedetails(request, c_slug):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)
    course = get_object_or_404(Courses, slug=c_slug)
    class_schedules = ClassSchedule.objects.filter(course=course)


    for class_schedule in class_schedules:
        # Check if attendance has been marked for this class schedule
        if Attendance.objects.filter(class_schedule=class_schedule).exists():
            class_schedule.attendance_marked = True
        else:
            class_schedule.attendance_marked = False
        class_schedule.update_status()

    return render(request, 'coursedetails.html', {'course': course, 'class_schedules': class_schedules, 'ins': ins})


from django.utils import timezone

def mark_attendance(request, class_schedule_id):
    # Get the class schedule object
    class_schedule = get_object_or_404(ClassSchedule, id=class_schedule_id)

    # Check if the course has ended
    if class_schedule.course.end_date < timezone.now().date():
        return HttpResponse('<p style="color:red;text-align:center;margin-top:350px;">Attendance cannot be marked for an ended course.</p>')

    # Get the enrolled students for the course
    enrolled_students = RegisteredStudent.objects.filter(user_id__course_purchase__course=class_schedule.course)

    attendance_marked = False
    if request.method == 'POST':
        # Check if attendance has already been marked
        if Attendance.objects.filter(class_schedule=class_schedule).exists():
            attendance_marked = True
        else:
            # If attendance has not been marked, save the attendance records to the database
            for student in enrolled_students:
                attendance_status = request.POST.get(str(student.user_id), 'ABSENT')
                attendance = Attendance.objects.create(
                    student=student,
                    class_schedule=class_schedule,
                    is_present=attendance_status
                )

        return redirect('schedule:coursedetails', c_slug=class_schedule.course.slug)

    # Render the attendance form template
    context = {'class_schedule': class_schedule, 'enrolled_students': enrolled_students, 'attendance_marked': attendance_marked}
    return render(request, 'attendance_form.html', context)



def view_attendance(request, class_schedule_id):
    schedule = ClassSchedule.objects.get(pk=class_schedule_id)
    attendances = Attendance.objects.filter(class_schedule=schedule)
    courses = Courses.objects.filter(user_id=request.user.id)
    present_attendances = [attendance for attendance in attendances if attendance.is_present == 'PRESENT']
    absent_attendances = [attendance for attendance in attendances if attendance.is_present == 'ABSENT']

    context = {
        'schedule': schedule,
        'present_attendances': present_attendances,
        'absent_attendances': absent_attendances,
        'courses':courses
    }
    return render(request, 'attendance_list.html', context)



def student_attendance(request, c_id):
    std = RegisteredStudent.objects.get(user_id=request.user.id)
    course = Courses.objects.get(id=c_id)
    course_attendance = Attendance.objects.filter(class_schedule__course_id=c_id, student=std)
    return render(request, 'student_attendance.html', {'course_attendance': course_attendance,'course':course})

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')

def attendance_graph(request, c_id):
    # Retrieve the course object based on the specified course ID
    course = Courses.objects.get(id=c_id)

    # Retrieve the attendance data for the specified course ID and current user's student ID
    attendances = Attendance.objects.filter(class_schedule__course_id=c_id, student_id=request.user.id)

    # Extract the course start date and end date
    start_date = course.start_date
    end_date = course.end_date

    # Generate a list of dates between the course start date and end date
    schedule_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    # Group the attendance records by class schedule dates
    attendance_data_by_date = {}
    for attendance in attendances:
        schedule_date = attendance.class_schedule.start_time.date()
        if schedule_date not in attendance_data_by_date:
            attendance_data_by_date[schedule_date] = {'present': 0, 'absent': 0, 'status': attendance.class_schedule.status}
        if attendance.is_present == 'PRESENT':
            attendance_data_by_date[schedule_date]['present'] += 1
        else:
            attendance_data_by_date[schedule_date]['absent'] += 1

    # Ensure that all dates between the course start date and end date are included in the attendance data dictionary
    for date in schedule_dates:
        if date not in attendance_data_by_date:
            attendance_data_by_date[date] = {'present': 0, 'absent': 0, 'status': None}

    # Sort the schedule dates
    sorted_indexes = sorted(range(len(schedule_dates)), key=lambda i: schedule_dates[i])
    schedule_dates = [schedule_dates[i] for i in sorted_indexes]
    presents = [attendance_data_by_date[date]['present'] for date in schedule_dates]
    absents = [attendance_data_by_date[date]['absent'] for date in schedule_dates]
    schedule_status = [attendance_data_by_date[date]['status'] for date in schedule_dates]

    # Set the x-axis label to the class schedule dates
    x = range(len(schedule_dates))
    x_labels = [date.strftime('%Y-%m-%d') for date in schedule_dates]

    # Create a bar graph with presents and absents as two different bars
    plt.bar(x, presents, width=0.4, color='g', align='center')
    plt.bar([i + 0.4 for i in x], absents, width=0.4, color='r', align='center')

    # Set the x-axis tick labels to the class schedule dates
    plt.xticks(x, x_labels, rotation=90)

    # Set the y-axis label to indicate the number of classes attended out of total classes
    plt.ylabel('Number of classes attended for each day', fontsize=12)
    plt.yticks(range(max(presents + absents) + 1))

    # Set the title of the graph
    plt.title('Attendance graph')

    # Add legend to indicate the status of the class schedules
    plt.legend(title=f'Course Status: {course.status}', loc='upper right', bbox_to_anchor=(1.07, 1),
               framealpha=1)

    # Save the graph to a file in the static directory
    graph_filename = f'attendance_graph_{c_id}_{request.user.id}.png'
    plt.savefig(f'static/{graph_filename}')


    # Clear the plot to free up memory
    plt.clf()

    # Render the graph as a template with the graph filename passed as a context variable
    return render(request, 'attendance_graph.html', {'graph_filename': graph_filename,'course':course})



def course_dates(request, course_id):
    ins = RegisteredInstructor.objects.get(user_id=request.user.id)

    course = get_object_or_404(Courses, id=course_id)
    start_date = course.start_date
    current_date = datetime.date.today()

    date_range = [start_date + datetime.timedelta(days=x) for x in range((current_date - start_date).days + 1)]
    context = {
        'course': course,
        'date_range': date_range,
        'ins':ins,
    }
    return render(request, 'course_dates.html', context)




def attendance_excel(request, course_id, date):
    course = get_object_or_404(Courses, pk=course_id)
    instructor_name = f"{course.user_id.first_name} {course.user_id.last_name}"

    # Convert date string to datetime object
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    class_schedules = ClassSchedule.objects.filter(course=course, start_time__date=date_obj, start_time__lte=datetime.datetime.now())

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{course.course} Attendance ({date}).xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Attendance')

    # Write course information
    # merge cells for course name
    style = xlwt.easyxf("font: bold on; align: horiz center")
    ws.write_merge(0, 0, 0, 3, f'{course.course} Attendance ({date}) - {instructor_name}', style)

    # write start time in third column
    timezone = pytz.timezone('Asia/Kolkata')  # replace with the timezone you need
    start_time = class_schedules[0].start_time.astimezone(timezone).strftime('%I:%M%p')
    end_time = class_schedules[0].end_time.astimezone(timezone).strftime('%I:%M%p')
    ws.write_merge(1, 1, 0, 3,
                   f'Start Time: {start_time}    End Time: {end_time}',
                   xlwt.easyxf("font: bold on; align: horiz center"))
    ws.row(1).height_mismatch = True
    ws.row(1).height = 256 * 2
    ws.col(0).width = 256 * 20

    for index, class_schedule in enumerate(class_schedules):
        ws = wb.add_sheet(f'Class {index + 1}')

        # Write class schedule information
        # merge cells for course name
        style = xlwt.easyxf("font: bold on; align: horiz center")
        ws.write_merge(0, 0, 0, 3, f'{course.course} Attendance ({date}) - {instructor_name}', style)

        # write start time in third column
        timezone = pytz.timezone('Asia/Kolkata')  # replace with the timezone you need
        start_time = class_schedule.start_time.astimezone(timezone).strftime('%I:%M%p')
        end_time = class_schedule.end_time.astimezone(timezone).strftime('%I:%M%p')
        ws.write_merge(1, 1, 0, 3,
                       f'Start Time: {start_time}    End Time: {end_time}',
                       xlwt.easyxf("font: bold on; align: horiz center"))
        ws.row(1).height_mismatch = True
        ws.row(1).height = 256 * 2
        ws.col(0).width = 256 * 20


        # Write headers
        row_num = 4  # Start writing data from row 7
        columns = ['Student Name', '', 'Attendance']
        for col_num, column_title in enumerate(columns):
            if not column_title:
                continue
            ws.write(row_num, col_num, column_title, xlwt.easyxf("font: bold on"))

        # Write data
        attendances = Attendance.objects.filter(class_schedule=class_schedule,
                                                class_schedule__start_time__date=date_obj)
        for attendance in attendances:
            row_num += 1
            row = [attendance.student.first_name + ' ' + attendance.student.last_name, '',attendance.is_present]
            for col_num, cell_value in enumerate(row):
                ws.write(row_num, col_num, cell_value)

    wb.save(response)
    return response



from reportlab.lib.colors import HexColor

# def GeneratePdf(request, course):
#     course = Courses.objects.get(id=course)
#     std = RegisteredStudent.objects.get(user_id_id=request.user.id)
#     videos = Videos.objects.filter(course=course)
#     course_progress = Daily_Progress.objects.filter(course_id=course.id, user_id=std.user_id_id).count()
#     end_date = course.end_date.strftime("%B %d, %Y")  # format the end date
#
#     if course_progress == videos.count():
#         # getting the template
#         name = f"{std.first_name} {std.last_name}"
#         context = {
#             "course": course.course,
#             "std_name": name,
#             "end_date": end_date,
#         }
#         template = get_template('Certificate.html')
#         html = template.render(context)
#
#         # creating PDF
#         pdf_file = BytesIO()
#         # set the page dimensions to letter size in landscape orientation
#         pdf_canvas = canvas.Canvas(pdf_file, pagesize=landscape(letter))
#
#         # Add a background image
#         pdf_canvas.drawImage('cert.jpg', 0, 0, width=letter[1], height=letter[0])
#
#         # Set the font and color for the title
#         pdf_canvas.setFont('Times-Bold', 30)
#         pdf_canvas.drawCentredString(400, 450, "Yogastudio")
#         pdf_canvas.saveState()
#         pdf_canvas.setFont('Times-Bold', 30)
#         pdf_canvas.drawString(240, 400, "Certificate of Completion")
#         pdf_canvas.saveState()
#         pdf_canvas.setFont('Times-Bold', 50)
#         pdf_canvas.drawCentredString(400, 300, f"{name}")
#         # Add a line
#         pdf_canvas.setLineWidth(2)
#         pdf_canvas.setStrokeColor(HexColor('#808080'))
#         pdf_canvas.line(100, 280, 700, 280)
#         pdf_canvas.setFont('Times-Roman', 16)
#         pdf_canvas.drawCentredString(400, 230, f"has successfully completed the course  {course.course} on {end_date}. ")
#         pdf_canvas.restoreState()
#         pdf_canvas.save()
#
#         # retrieving PDF file
#         pdf = pdf_file.getvalue()
#         pdf_file.close()
#
#         # returning PDF as response
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{name} - {course.course} Certificate.pdf"'
#         response.write(pdf)
#         return response
#     else:
#         return HttpResponse(f"Please complete watching all videos of the {course.course} course.")
from datetime import date

def GeneratePdf(request, course):
    course = Courses.objects.get(id=course)
    std = RegisteredStudent.objects.get(user_id_id=request.user.id)
    videos = Videos.objects.filter(course=course)
    course_progress = Daily_Progress.objects.filter(course_id=course.id, user_id=std.user_id_id).count()
    end_date = course.end_date.strftime("%B %d, %Y")  # format the end date

    if course_progress == videos.count() and date.today() > course.end_date:
        # getting the template
        name = f"{std.first_name} {std.last_name}"
        context = {
            "course": course.course,
            "std_name": name,
            "end_date": end_date,
        }
        template = get_template('Certificate.html')
        html = template.render(context)

        # creating PDF
        pdf_file = BytesIO()
        # set the page dimensions to letter size in landscape orientation
        pdf_canvas = canvas.Canvas(pdf_file, pagesize=landscape(letter))

        # Add a background image
        pdf_canvas.drawImage('cert.jpg', 0, 0, width=letter[1], height=letter[0])

        # Set the font and color for the title
        pdf_canvas.setFont('Times-Bold', 30)
        pdf_canvas.drawCentredString(400, 450, "Yogastudio")
        pdf_canvas.saveState()
        pdf_canvas.setFont('Times-Bold', 30)
        pdf_canvas.drawString(240, 400, "Certificate of Completion")
        pdf_canvas.saveState()
        pdf_canvas.setFont('Times-Bold', 50)
        pdf_canvas.drawCentredString(400, 300, f"{name}")
        # Add a line
        pdf_canvas.setLineWidth(2)
        pdf_canvas.setStrokeColor(HexColor('#808080'))
        pdf_canvas.line(100, 280, 700, 280)
        pdf_canvas.setFont('Times-Roman', 16)
        pdf_canvas.drawCentredString(400, 230, f"has successfully completed the course  {course.course} on {end_date}. ")
        pdf_canvas.restoreState()
        pdf_canvas.save()

        # retrieving PDF file
        pdf = pdf_file.getvalue()
        pdf_file.close()

        # returning PDF as response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{name} - {course.course} Certificate.pdf"'
        response.write(pdf)
        return response
    else:
        message = f"Please complete watching all videos of the {course.course} course and wait until the course end date to get the certificate."
        messages.error(request, message)
        return redirect(request.META['HTTP_REFERER'])