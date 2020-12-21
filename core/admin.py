from django.contrib import admin

from core.models import (Repo, TaskModel, Backup)
from import_export.admin import ImportExportActionModelAdmin


@admin.register(Repo)
class RepoAdmin(ImportExportActionModelAdmin):
    list_display = ('name', 'url', 'private')
    search_fields = ('name',)


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ('repo', 'created',)
    search_fields = ('repo',)


@admin.register(TaskModel)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ('taskname', 'lastrunned',)
    search_fields = ('taskname',)
