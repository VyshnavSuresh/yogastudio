from django.urls import path
from . import views


app_name="yogaapp"

from django.contrib import admin
urlpatterns = [
    path('', views.index, name='index'),
    path('studentregistration', views.Studentregistration, name='studentregistration'),
    path('insrtructorregistration', views.insrtructorregistration, name='insrtructorregistration'),

    path('activate/<uidb64>/<token>', views.activate, name='activate'),

    path("passwd_email",views.Passwdemail,name="passwd_email"),
    path('passwordreset/<uidb64>/<token>', views.Password_reset, name='password_reset'),

    path('login/', views.Login, name='login'),
    path('forgotpassword/<uidb64>', views.forgotpassword, name='forgotpassword'),

    path('studentdashboard', views.studentdashboard, name='studentdashboard'),
    path('studentdashboard/<slug:c_slug>', views.studentdashboard, name='studentdashboard'),
    path('studentdashboard/<slug:c_slug>/<slug:v_slug>', views.studentdashboard, name='studentdashboard'),

    path('salary/<int:salary_id>/', views.salary_details, name='salary_details'),
    path('pdf/<int:id>/', views.get,name='pdf'),
    path("progress/<int:progress>/<video>",views.Progress_update,name="Progress_update"),
    path("student_progress", views.Student_progress, name="student_progress"),

    path('logout', views.Logout, name='logout'),
    path('studentviewprofile', views.studentviewprofile, name='studentviewprofile'),
    path('studentupdate', views.studentupdate, name='studentupdate'),
    path('studentchangepassword', views.studentchangepassword, name='studentchangepassword'),
    # path('coursesenrolled', views.coursesenrolled, name='coursesenrolled'),
    path('availablecourses', views.availablecourses, name='availablecourses'),
    path('endroll/<slug:c_slug>', views.Course_endroll, name='endroll'),
    path('course/<slug:c_slug>/checkoutcourse/', views.checkoutcourse, name='checkoutcourse'),
    path('payment_done_course/', views.payment_done_course, name='payment_done_course'),
    path('aboutcourse/<int:c_id>/', views.aboutcourse, name='aboutcourse'),







    path('instructorviewvideos', views.instructorviewvideos, name='instructorviewvideos'),
    path('feedback', views.feedback, name='feedback'),

    # path('searchbar', views.searchbar, name='searchbar'),

    path('instructordashboard', views.instructordashboard, name='instructordashboard'),
    path('instructorviewprofile', views.instructorviewprofile, name='instructorviewprofile'),
    path('instructorchangepassword', views.instructorchangepassword, name='instructorchangepassword'),
    path('instructorallotedstudents', views.instructorallotedstudents, name='instructorallotedstudents'),
    path('instructorviewfeedback', views.instructorviewfeedback, name='instructorviewfeedback'),
    path('instructorupdate', views.instructorupdate, name='instructorupdate'),
    path('addvideo', views.addvideo, name='addvideo'),




    path('course_cancel/<int:course_id>', views.Course_cancel, name='course_cancel'),

    path('product', views.product, name='product'),
    path('singleproduct/<int:id>/', views.singleproduct, name='singleproduct'),
    path('cart/', views.cart, name='cart'),

    path('addcart/<int:id>/', views.addcart, name='addcart'),
    path('de_cart/<int:id>/', views.de_cart, name='de_cart'),
    path('plusqty/<int:id>/', views.plusqty, name='plusqty'),
    path('minusqty/<int:id>/', views.minusqty, name='minusqty'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment_done/', views.payment_done, name='payment_done'),
    path('orders/', views.orders, name='orders'),
    path('search/', views.search, name='search'),


    path('delivery_address/', views.delivery_address, name='delivery_address'),
    path('delivery_address/<int:pk>/', views.delivery_address, name='edit_delivery_address'),
    path('add_wishlist/<int:id>/',views.add_wishlist,name='add_wishlist'),
    path('view_wishlist',views.view_wishlist,name='view_wishlist'),
    path('de_wishlist/<int:id>/',views.de_wishlist,name='de_wishlist'),
    path('delete-video/<int:video_id>/', views.delete_video, name='delete_video'),


]