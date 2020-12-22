from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from core.models import Backup, Repo, TaskModel


class BackupInline(admin.TabularInline):
    model = Backup


@admin.register(Repo)
class RepoAdmin(ImportExportActionModelAdmin):
    list_display = ('name', 'url', 'private')
    list_filter = ('private', )
    search_fields = ('name',)
    inlines = [BackupInline, ]


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ('id', 'repo', 'task', 'file', 'created',)
    list_filter = ('repo', )
    search_fields = ('repo',)


@admin.register(TaskModel)
class TaskModelAdmin(admin.ModelAdmin):
    list_display = ('taskname', 'lastrunned',)
    search_fields = ('taskname',)
    inlines = [BackupInline, ]
