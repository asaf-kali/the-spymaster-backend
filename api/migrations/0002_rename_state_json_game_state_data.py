# Generated by Django 4.0.4 on 2022-04-30 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="game",
            old_name="state_json",
            new_name="state_data",
        ),
    ]