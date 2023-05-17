# Generated by Django 4.1.1 on 2023-03-29 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yogaapp', '0008_alter_courses_course_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='courses',
            name='status',
            field=models.CharField(choices=[('upcoming', 'Upcoming'), ('in_progress', 'In Progress'), ('ended', 'Ended')], default='upcoming', max_length=20),
        ),
    ]