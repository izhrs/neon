# Generated by Django 5.0 on 2025-04-20 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_profile_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(default='media/user/profiles/default_vq1nbg', upload_to='media/user/profiles'),
        ),
    ]
