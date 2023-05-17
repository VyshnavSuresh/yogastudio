from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import request
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.db.models import F

from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import pre_save
from datetime import date
from django.core.validators import MinValueValidator,MaxValueValidator




STATUS_CHOICES = (
    ('approved', 'Approved'),
    ('pending', 'Pending'),
)
def validate_image_file(value):
    if not value.name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        raise ValidationError(_('Only image files are allowed.'))

class RegisteredStudent(models.Model):
    user_id=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    usertype = models.CharField(max_length=20, default='Student')
    phone = models.BigIntegerField()
    status = models.CharField(max_length=15, default='pending', choices=STATUS_CHOICES)
    email = models.EmailField(max_length=100, unique=True, default='')
    student_image = models.ImageField(upload_to='profile_image/', unique=True,default='', validators=[validate_image_file])




    def __str__(self):
        return "{} {}".format(self.first_name,self.last_name)



def validate_file_extension(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError(_('Only PDF files are allowed.'))


class RegisteredInstructor(models.Model):
    user_id=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    usertype = models.CharField(max_length=20, default='Instructor')
    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    phone = models.BigIntegerField()
    email = models.EmailField(max_length=100, unique=True, default='')
    instructor_image = models.ImageField(upload_to='profile_image/', unique=True,default='',validators=[validate_image_file, validate_file_extension])
    cv = models.FileField(upload_to="file")
    certificate = models.FileField(upload_to="file")
    status = models.CharField(max_length=15, default='pending', choices=STATUS_CHOICES)
    bio = models.TextField(max_length=500, blank=True)


    def __str__(self):
        return "{} {}".format(self.first_name,self.last_name)

class Courses(models.Model):
    STAT = (
        ('upcoming', 'Upcoming'),
        ('in_progress', 'In Progress'),
        ('ended', 'Ended')
    )
    course=models.CharField(max_length=30,unique=True)
    duration = models.CharField(max_length=50,null=True, blank=True)
    amount=models.PositiveIntegerField(default=100)
    course_image = models.ImageField(upload_to='course_image/', unique=True,default='', validators=[validate_image_file])
    slug=models.SlugField()
    desc=models.TextField(max_length=200)
    start_date=models.DateField()
    end_date=models.DateField()
    user_id=models.OneToOneField(RegisteredInstructor,on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STAT, default='upcoming')




    class Meta:
        verbose_name="Courses"
        verbose_name_plural="Courses"

    @property
    def calculate_duration(self):
        duration = self.end_date - self.start_date
        return f"{duration.days} days"

    def save(self, *args, **kwargs):
        self.duration = self.calculate_duration
        super().save(*args, **kwargs)

    def __str__(self):
        return self.course

    def get_course_url(self):
        return reverse('yogaapp:studentdashboard',kwargs={"c_slug":self.slug})

    def get_course_video_url(self):
        return reverse('yogaapp:studentdashboard',kwargs={"c_slug":self.slug})

@receiver(pre_save, sender=Courses)
def update_course_status(sender, instance, **kwargs):
    today = date.today()
    if instance.start_date > today:
        instance.status = 'upcoming'
    elif instance.end_date < today:
        instance.status = 'ended'
    else:
        instance.status = 'in_progress'

class Salary(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    instructor = models.ForeignKey(RegisteredInstructor, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def clean(self):
        if self.amount <= 500:
            raise ValidationError('Amount must be greater than 500.')

        if Salary.objects.filter(course=self.course, instructor=self.instructor).exists():
            raise ValidationError('Salary for this course and instructor already exists.')

        if not self.course.user_id == self.instructor:
            raise ValidationError('The selected instructor is not associated with the selected course.')


class Course_purchase(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    course=models.ForeignKey(Courses,on_delete=models.CASCADE)
    purhase_date=models.DateField(auto_now=True)
    end_date=models.DateField(null=True)



class Videos(models.Model):
    title=models.CharField(max_length=30,unique=True)
    slug=models.SlugField()
    course=models.ForeignKey(Courses,on_delete=models.CASCADE)
    video=models.FileField(upload_to='videos')
    video_url = models.URLField(blank=True)
    class Meta:
        verbose_name="Videos"
        verbose_name_plural="Videos"

    def __str__(self):
        return self.title

    def get_course_video_url(self):
        course_slug=Courses.objects.get(course=self.course).slug
        return reverse('yogaapp:studentdashboard',args=[course_slug,self.slug])


class Feedback(models.Model):
    user = models.ForeignKey(RegisteredStudent, on_delete=models.CASCADE)
    course = models.OneToOneField(Courses, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedbackdate = models.DateField(auto_now_add=True)


class Category(models.Model):
    title= models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.title


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    product_image = models.ImageField(upload_to='product_image/', unique=True)
    price = models.PositiveIntegerField(default=1)
    stock = models.PositiveIntegerField(default=1)
    description = models.TextField(max_length=1000, default='')
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    gst_rate = models.FloatField(default=0.18) # 18% GST by default

    @property
    def price_with_gst(self):
        return round(self.price + (self.price * self.gst_rate), 2)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            self.price = float(self.price)
        except ValueError:
            raise ValueError('Price must be a number')
        super(Product, self).save(*args, **kwargs)




class Cart(models.Model):
    user=models.ForeignKey(RegisteredStudent,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    product_qty=models.IntegerField(default=1)
    price=models.DecimalField(max_digits=20,decimal_places=2,default=0)

    def get_product_price(self):
        price=[self.product.price]
        return sum(price)


class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)


    def __str__(self):
        return f'{self.recipient_name}, {self.address}, {self.city}, {self.state}, {self.zip_code}'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(blank=True,null=True)
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.user)

class OrderPlaced(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Received', 'Received'),
        ('Shipped', 'Shipped'),
        ('On The Way', 'On The Way'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),

    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=50, choices=STATUS, default='Pending')
    ordered_date = models.DateTimeField(auto_now_add=True)
    is_ordered = models.BooleanField(default=False)
    payment=models.ForeignKey(Payment,on_delete=models.CASCADE,default='')
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE)


    def total_cost(self):
        return self.quantity


    def __str__(self):
        return str(self.user)



class Whishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)



class Daily_Progress(models.Model):
    user=models.ForeignKey(RegisteredStudent,on_delete=models.CASCADE)
    video=models.ForeignKey(Videos,on_delete=models.CASCADE)
    day=models.DateField(auto_now=True)
    course=models.ForeignKey(Courses,on_delete=models.CASCADE)
    progress=models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])


class Course_Completed(models.Model):
    user=models.ForeignKey(RegisteredStudent,on_delete=models.CASCADE)
    course=models.ForeignKey(Courses,on_delete=models.CASCADE)
    date_completed=models.DateField(auto_now=True)