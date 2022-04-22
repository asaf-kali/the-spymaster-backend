from django.contrib import admin

from api.models import SpymasterUser


@admin.register(SpymasterUser)
class TheSpymasterUserAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name", "email"]
    search_fields = ["username", "first_name", "last_name", "email"]
