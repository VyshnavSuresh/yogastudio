from django.urls import path
from .import views

app_name="schedule"

urlpatterns=[
    path("allotclass/<slug:c_slug>",views.allotclass,name="allotclass"),
    path("coursedetails/<slug:c_slug>", views.coursedetails, name="coursedetails"),
    path("deleteclass/<int:id>", views.deleteclass, name="deleteclass"),
    path('live_classes/<int:c_id>', views.live_classes, name='live_classes'),
    path('mark_attendance/<int:class_schedule_id>/', views.mark_attendance, name='mark_attendance'),
    path('view_attendance/<int:class_schedule_id>/', views.view_attendance, name='view_attendance'),
    path('student_attendance/<int:c_id>', views.student_attendance, name='student_attendance'),
    path('attendance_graph/<int:c_id>/', views.attendance_graph, name='attendance_graph'),
    path('attendance_excel/<int:course_id>/<str:date>', views.attendance_excel, name='attendance_excel'),
    path('course_dates/<int:course_id>/', views.course_dates, name='course_dates'),
    path('generate_certificate/<int:course>', views.GeneratePdf,name="generate_certificate"),

]