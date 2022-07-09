from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from api.models import SpymasterUser
from api.models.game import Game


@admin.register(SpymasterUser)
class TheSpymasterUserAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name", "email"]
    search_fields = ["username", "first_name", "last_name", "email"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["id"]
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
