# Generated by Django 3.0.5 on 2021-07-16 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_auto_20210716_0002"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tagrecipe",
            old_name="ingredient",
            new_name="tag",
        ),
    ]
