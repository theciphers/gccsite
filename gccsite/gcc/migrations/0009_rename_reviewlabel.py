# Generated by Django 2.2.3 on 2019-07-27 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gcc', '0008_event_is_long'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ApplicantLabel',
            new_name='ReviewLabel',
        ),
    ]