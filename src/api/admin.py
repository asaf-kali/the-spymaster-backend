from django.contrib import admin

from api.models.user import SpymasterUser


@admin.register(SpymasterUser)
class TheSpymasterUserAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name", "email"]
    search_fields = ["username", "first_name", "last_name", "email"]


# @admin.register(Game)
# class GameAdmin(admin.ModelAdmin):
#     list_display = ["id"]
#     formfield_overrides = {
#         models.JSONField: {"widget": JSONEditorWidget},
#     }
