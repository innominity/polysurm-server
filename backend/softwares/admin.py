from django.contrib import admin
from .models import SoftwareApp, SoftwareAppTask


class SoftwareAppAdmin(admin.ModelAdmin):
    list_display = ['guid', 'name', 'description', 'slug', 'created_at']
    list_display_links = ['guid', 'name', 'slug']
    search_fields = ['guid', 'name', 'slug']


admin.site.register(SoftwareApp, SoftwareAppAdmin)


class SoftwareAppTaskAdmin(admin.ModelAdmin):
    list_display = ['guid', 'software_app', 'created_at', 'status', 'status_update']
    list_display_links = ['guid', 'software_app']
    search_fields = ['guid']


admin.site.register(SoftwareAppTask, SoftwareAppTaskAdmin)