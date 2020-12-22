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

        # git clone --mirror git@some.origin/reponame reponame.git
        # cd reponame.git
        # git bundle create reponame.bundle --all
        # cp reponame.bundle dest_dir
        # cd ..
        # rm -rf reponame.git
        for repo in repos:
            repo_name = f"{repo.name}.git"
            repo_bundle = f"{repo.name}.bundle"
            subprocess.run(["git", "clone", "--mirror", repo.url, repo_name],
                           cwd=f"./{working_dir}")
            subprocess.run(["git", "bundle", "create", repo_bundle, "--all"],
                           cwd=f"./{working_dir}/{repo_name}")
            subprocess.run(["cp", repo_bundle, ".."],
                           cwd=f"./{working_dir}/{repo_name}")
            subprocess.run(["rm", "-rf", f"./{repo_name}"],
                           cwd=f"./{working_dir}")
            f = File(open(f'/app/{working_dir}/{repo_bundle}', 'rb'))
            Backup.objects.create(repo=repo, file=f)

        subprocess.run(["rm", "-rf", working_dir])
        if repos:
            TaskModel.objects.create(
                taskname="getcontainers",
                lastrunned=start_date
            )

        elapsed = time.time()
        self.stdout.write(self.style.SUCCESS(
            "--- Total %s seconds ---" % (elapsed - start_time)))
