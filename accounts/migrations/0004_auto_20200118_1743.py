# Generated by Django 2.2.6 on 2020-01-18 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20200102_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='introduction',
            field=models.CharField(blank=True, max_length=100, verbose_name='한 줄 소개'),
        ),
    ]
