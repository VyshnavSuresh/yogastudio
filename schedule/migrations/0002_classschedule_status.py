# Generated by Django 4.1.1 on 2023-03-30 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='classschedule',
            name='status',
            field=models.CharField(choices=[('Upcoming', 'Upcoming'), ('In_Progress', 'In Progress'), ('Ended', 'Ended')], default='Upcoming', max_length=20),
        ),
    ]
