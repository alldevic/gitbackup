from django.contrib import admin

from core.models import (Repo, TaskModel, Backup)


@admin.register(Repo)
class RepoAdmin(admin.ModelAdmin):
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
