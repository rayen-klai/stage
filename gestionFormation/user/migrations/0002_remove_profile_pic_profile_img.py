# Generated by Django 4.2.2 on 2023-06-22 20:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='pic',
        ),
        migrations.AddField(
            model_name='profile',
            name='img',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='img'),
            preserve_default=False,
        ),
    ]
