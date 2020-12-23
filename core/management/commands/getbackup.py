import time

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files import File
from core.models import (Repo, Backup, TaskModel)
import subprocess
from pathlib import Path


class Command(BaseCommand):
    help = 'Создание бэкапов'

    def handle(self, *args, **options):
        start_time = time.time()
        start_date = timezone.now()
        repos = Repo.objects.all()

        working_dir = "tmp"
        task = TaskModel(taskname="getcontainers", lastrunned=start_date)
        if not Path(working_dir).is_dir():
            res = subprocess.run(["mkdir", working_dir], capture_output=True)
            if res.returncode != 0:
                task.successful = False
                task.returncode = res.returncode
                task.stdout = res.stdout
                task.stderr = res.stderr
                task.save()
                return

        # mkdir repo.name
        # cd repo.name
        # git clone --mirror git@some.origin/reponame reponame.git
        # mv reponame.git .git
        # git init
        # git checkout --
        # cd ..
        # tar -czf reponame.tar.gz reponame.git
        # rm -rf reponame.git
        backup_list = []
        for repo in repos:
            repo_name = f"{repo.name}.git"
            repo_bundle = f"{repo.name}.tar.gz"
            repo_work_dir = f"./{working_dir}/{repo_name}"
            res = subprocess.run(["mkdir", repo_work_dir], capture_output=True)
            if res.returncode != 0:
                task.successful = False
                task.returncode = res.returncode
                task.args = res.args
                task.stdout = res.stdout
                task.stderr = res.stderr
                task.save()
                return

            res = subprocess.run(["git", "clone", "--mirror", repo.url, repo_name],
                                 cwd=repo_work_dir, capture_output=True)
            if res.returncode != 0:
                task.successful = False
                task.returncode = res.returncode
                task.args = res.args
                task.stdout = res.stdout
                task.stderr = res.stderr
                task.save()
                return

            res = subprocess.run(["mv", repo_name, ".git"],
                                 cwd=repo_work_dir, capture_output=True)
            if res.returncode != 0:
                task.successful = False
                task.returncode = res.returncode
                task.args = res.args
                task.stdout = res.stdout
                task.stderr = res.stderr
                task.save()
                return

            res = subprocess.run(["git", "init"],
                                 cwd=repo_work_dir, capture_output=True)
            if res.returncode != 0:
                task.successful = False
                task.returncode = res.returncode
                task.args = res.args
                task.stdout = res.stdout
                task.stderr = res.stderr
                task.save()
                return

            res = subprocess.run(["git", "checkout", "--", ],
                                 cwd=repo_work_dir, capture_output=True)
            if res.returncode != 0:
                task.successful = False
                task.returncode = res.returncode
                task.args = res.args
                task.stdout = res.stdout
                task.stderr = res.stderr
                task.save()
                return

            res = subprocess.run(["tar", "-czf", repo_bundle, repo_name],
                                 cwd=working_dir, capture_output=True)
            if res.returncode != 0:
                task.successful = False
                task.returncode = res.returncode
                task.args = res.args
                task.stdout = res.stdout
                task.stderr = res.stderr
                task.save()
                return

            res = subprocess.run(["rm", "-rf", repo_work_dir],
                                 capture_output=True)
            if res.returncode != 0:
                task.successful = False
                task.returncode = res.returncode
                task.args = res.args
                task.stdout = res.stdout
                task.stderr = res.stderr
                task.save()
                return

            f = File(open(f"{working_dir}/{repo_bundle}", 'rb'))
            backup_list += [Backup(repo=repo, file=f, task=task)]

        res = subprocess.run(["rm", "-rf", working_dir], capture_output=True)
        if res.returncode != 0:
            task.successful = False
            task.returncode = res.returncode
            task.args = res.args
            task.stdout = res.stdout
            task.stderr = res.stderr
            task.save()
            return
        task.save()

        for backup in backup_list:
            backup.save()

        elapsed = time.time()
        self.stdout.write(self.style.SUCCESS(
            "--- Total %s seconds ---" % (elapsed - start_time)))
