from django.contrib import admin

from log_entries.models import LogEntry, ZeekConnLog

admin.site.register(LogEntry)
admin.site.register(ZeekConnLog)
