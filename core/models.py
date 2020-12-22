import os

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.text import slugify


class Repo(models.Model):
    name = models.CharField("name", max_length=150)
    token = models.CharField("token", max_length=150, blank=True, null=True)
    private = models.BooleanField("private", default=False)
    url = models.URLField("url", max_length=250)
    comment = models.CharField(
        "comment", max_length=1000, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "репозиторий"
        verbose_name_plural = "репозитории"


def get_file_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return os.path.join('files', slugify(name, allow_unicode=True) + ext)


class Backup(models.Model):
    repo = models.ForeignKey("Repo", on_delete=models.DO_NOTHING)
    file = models.FileField("backup", upload_to=get_file_path)
    created = models.DateTimeField("created", auto_now_add=True)
    task = models.ForeignKey("TaskModel", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "бэкап"
        verbose_name_plural = "бэкапы"


class TaskModel(models.Model):
    lastrunned = models.DateTimeField(
        "lastrunned", auto_now=False, auto_now_add=False, editable=False)
    taskname = models.CharField("taskname", max_length=50)

    def __str__(self) -> str:
        return f"{self.taskname} - {self.lastrunned}"

    class Meta:
        verbose_name = "запуск"
        verbose_name_plural = "запуски"


@receiver(pre_delete, sender=Backup)
def delete(sender, instance, using, **kwargs):
    os.remove(instance.file.path)
