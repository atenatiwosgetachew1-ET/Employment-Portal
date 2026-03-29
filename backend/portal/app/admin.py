from django.contrib import admin

from .models import AuditLog, Notification, Profile, UserPreferences

admin.site.site_header = "admin"
admin.site.site_title = "admin"
admin.site.index_title = "admin"

admin.site.register(Profile)
admin.site.register(UserPreferences)
admin.site.register(Notification)
admin.site.register(AuditLog)
