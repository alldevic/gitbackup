from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from core.models import Backup, Repo, TaskModel
from django.urls import reverse
from django.utils.html import escape, mark_safe


class BackupInline(admin.TabularInline):
    model = Backup

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Repo)
class RepoAdmin(ImportExportActionModelAdmin):
    list_display = ('name', 'url', 'private')
    list_filter = ('private', )
    search_fields = ('name',)
    inlines = [BackupInline, ]


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ('id', 'repo_link', 'task_link', 'file', 'created',)
    list_filter = ('repo', 'task')
    search_fields = ('repo',)

    def repo_link(self, obj: Repo):
        link = reverse("admin:core_repo_change", args=[obj.repo.id])
        return mark_safe(f'<a href="{link}">{escape(obj.repo.__str__())}</a>')

    repo_link.short_description = 'Repo'
    repo_link.admin_order_field = 'repo'  # Make row sortable

    def task_link(self, obj: TaskModel):
        link = reverse("admin:core_taskmodel_change", args=[obj.task.id])
        return mark_safe(f'<a href="{link}">{escape(obj.task.__str__())}</a>')

    task_link.short_description = 'Repo'
    task_link.admin_order_field = 'repo'


@admin.register(TaskModel)
class TaskModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'taskname', 'lastrunned',)
    list_display_links = ('id', 'taskname',)
    search_fields = ('taskname',)
    inlines = [BackupInline, ]
