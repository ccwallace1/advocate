# Generated by Django 3.2.16 on 2023-03-07 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_auto_20230306_2039'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='type',
            field=models.CharField(choices=[('project', 'Project'), ('program', 'Program')], default='program', max_length=20),
        ),
    ]
