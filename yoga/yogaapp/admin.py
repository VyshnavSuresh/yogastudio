from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
# from django.admin import loader
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.db.models import Sum

from schedule.models import ClassSchedule, Attendance

from .models import RegisteredInstructor, RegisteredStudent, Feedback, Courses, Course_purchase, Videos, Category, \
    Product, Payment, OrderPlaced, Salary
from django.contrib.auth.models import Group,User

# Register your models here.
#admin.site.register(Register)
#admin.site.register(StudentRegister)
#admin.site.register(Course)


admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(RegisteredInstructor)
class RegisterInstructorAdmin(admin.ModelAdmin):
    list_display=('first_name','last_name','phone','email','cv','certificate')
    ordering = ('first_name',)
    search_fields = ('first_name','email')
    list_per_page = 10
    list_filter = ('first_name','email')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False,
            'Groups': False
        })

        return super().render_change_form(request, context, add, change, form_url, obj)




@admin.register(RegisteredStudent)
class RegisterStudentAdmin(admin.ModelAdmin):
    list_display=('first_name','last_name','phone','email')
    ordering = ('first_name',)
    search_fields = ('first_name','email')
    list_per_page = 10
    list_filter = ('first_name','email')
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': True,
            'show_save_and_continue': True,
            'show_save_and_add_another': True,
            'show_delete': False,
            'Groups': False
        })

        return super().render_change_form(request, context, add, change, form_url, obj)


#
#
# @admin.register(Course)
# class courseAdmin(admin.ModelAdmin):
#     list_display=('coursename','startdate','duration','amount','instructor')
#     ordering = ('coursename',)
#     search_fields = ('firstname','email')
#     list_per_page = 10
#     list_filter = ('coursename','startdate','duration')
#
#
# @admin.register(Feedback)
# class feedbackAdmin(admin.ModelAdmin):
#     list_display=('email','feedback','feedbackdate','course_name')
#     ordering = ('course_name',)
#     search_fields = ('email','feedbackdate')
#     list_per_page = 10
#     list_filter = ('email','feedbackdate','course_name')

# admin.site.register(RegisteredInstructor)
# admin.site.register(RegisteredStudent)








class AdminPermission(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(User,AdminPermission)



class CourseAdmin(admin.ModelAdmin):
    list_display = ('course','duration','amount','slug','desc','user_id')
    list_per_page = 10
    list_editable = ('duration','amount')
    prepopulated_fields = {'slug':('course',)}

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': True,
            'show_save_and_continue': True,
            'show_save_and_add_another':True,
            'show_delete': False,
            'Groups': False
        })

        return super().render_change_form(request, context, add, change, form_url, obj)


admin.site.register(Courses,CourseAdmin)



# class VideoAdmin(admin.ModelAdmin):
#     prepopulated_fields = {'slug':('title',)}
# admin.site.register(Videos,VideoAdmin)

class PurchaseManagement(admin.ModelAdmin):
    list_display = ("user","course","purhase_date","end_date")
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False,
            'Groups': False
        })

        return super().render_change_form(request, context, add, change, form_url, obj)



admin.site.register(Course_purchase,PurchaseManagement)

admin.site.register(Category)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=('name','category','product_image','price')

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display=('user','amount','razorpay_order_id','razorpay_payment_id','razorpay_payment_status','paid','total_amount')

    def total_amount(self, obj):
        # Calculate the total amount of all payments
        total = Payment.objects.aggregate(Sum('amount'))['amount__sum']
        return total

    total_amount.short_description = 'Total Amount'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False,
            'Groups': False
        })

        return super().render_change_form(request, context, add, change, form_url, obj)




@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display=('user','product','quantity','status','ordered_date','payment')


@admin.register(Videos)
class videosModelAdmin(admin.ModelAdmin):
     list_display=('title','course')

     def has_delete_permission(self, request, obj=None):
         return request.user.is_superuser

     def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
         context.update({
             'show_save': False,
             'show_save_and_continue': False,
             'show_save_and_add_another': False,
             'show_delete': False,
             'Groups': False
         })

         return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(ClassSchedule)
class classscheduleModelAdmin(admin.ModelAdmin):
    list_display = ('course', 'start_time','end_time', 'instructor')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False,
            'Groups': False
        })

        return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(Attendance)
class attendanceModelAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_schedule', 'is_present')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False,
            'Groups': False
        })

        return super().render_change_form(request, context, add, change, form_url, obj)



from django.contrib import admin
from django.contrib import messages
from django.db.models import F
from .models import Salary

from django.core.exceptions import ValidationError

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['course', 'instructor', 'amount', 'date']

    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
            if 'Salary object' not in message:
                super().message_user(request, message, level, extra_tags, fail_silently)
