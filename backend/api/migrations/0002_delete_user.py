# Generated by Django 3.0.5 on 2021-07-15 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="User",
        ),
    ]