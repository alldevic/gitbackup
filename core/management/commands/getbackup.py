import time

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files import File
from core.models import (Repo, Backup, TaskModel)
import subprocess


class Command(BaseCommand):
    help = 'Создание бэкапов'

    def handle(self, *args, **options):
        start_time = time.time()
        start_date = timezone.now()
        repos = Repo.objects.all()

        working_dir = "tmp"
        subprocess.run(["mkdir", working_dir])

        task = None
        if repos:
            task = TaskModel.objects.create(
                taskname="getcontainers",
                lastrunned=start_date
            )
        # mkdir repo.name
        # cd repo.name
        # git clone --mirror git@some.origin/reponame reponame.git
        # mv reponame.git .git
        # git init
        # git checkout --
        # cd ..
        # tar -czf reponame.tar.gz reponame.git
        # rm -rf reponame.git

        for repo in repos:
            repo_name = f"{repo.name}.git"
            repo_bundle = f"{repo.name}.tar.gz"
            repo_work_dir = f"./{working_dir}/{repo_name}"
            subprocess.run(["mkdir", repo_work_dir])
            subprocess.run(["git", "clone", "--mirror", repo.url, repo_name],
                           cwd=repo_work_dir)
            subprocess.run(["mv", repo_name, ".git"], cwd=repo_work_dir)
            subprocess.run(["git", "init"], cwd=repo_work_dir)
            subprocess.run(["git", "checkout", "--", ], cwd=repo_work_dir)
            subprocess.run(["tar", "-czf", repo_bundle, repo_name],
                           cwd=working_dir)

            subprocess.run(["rm", "-rf", repo_work_dir])

            f = File(open(f"{working_dir}/{repo_bundle}", 'rb'))
            Backup.objects.create(repo=repo, file=f, task=task)

        subprocess.run(["rm", "-rf", working_dir])

        elapsed = time.time()
        self.stdout.write(self.style.SUCCESS(
            "--- Total %s seconds ---" % (elapsed - start_time)))
