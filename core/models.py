import os
import uuid

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


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
    fullname = filename.split('/')[-1]
    name, ext = fullname.split('.', 1)
    return os.path.join('files', f"{name}_{uuid.uuid4().hex[:12]}.{ext}")


class Backup(models.Model):
    repo = models.ForeignKey("Repo", on_delete=models.SET_NULL, null=True)
    file = models.FileField("backup", upload_to=get_file_path)
    created = models.DateTimeField("created", auto_now_add=True)
    task = models.ForeignKey("TaskModel", on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "бэкап"
        verbose_name_plural = "бэкапы"


class TaskModel(models.Model):
    lastrunned = models.DateTimeField("lastrunned",
                                      auto_now=False,
                                      auto_now_add=False,
                                      editable=False)
    taskname = models.CharField("taskname", max_length=50, editable=False)
    successful = models.BooleanField("successful",
                                     default=True,
                                     editable=False)
    returncode = models.IntegerField("returncode", default=0)
    stdout = models.TextField(editable=False, null=True, blank=True)
    stderr = models.TextField(editable=False, null=True, blank=True)
    args = models.TextField(editable=False, null=True, blank=True)

    def __str__(self) -> str:
        format = "%Y/%m/%d %H:%M:%S"
        return f"{self.taskname} - {self.lastrunned.strftime(format)}"

    class Meta:
        verbose_name = "запуск"
        verbose_name_plural = "запуски"


@receiver(pre_delete, sender=Backup)
def delete(sender, instance, using, **kwargs):
    os.remove(instance.file.path)
