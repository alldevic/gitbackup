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

        # git clone --mirror git@some.origin/reponame reponame.git
        # cd reponame.git
        # git bundle create reponame.bundle --all
        # cp reponame.bundle dest_dir
        # cd ..
        # rm -rf reponame.git
        for repo in repos:
            repo_name = f"{repo.name}.git"
            repo_bundle = f"{repo.name}.bundle"
            subprocess.run(["git", "clone", "--mirror",
                            f'{repo.url}', f"{repo_name}"])
            # tmp = subprocess.run(["ls", "-la"])
            # self.stdout.write(self.style.SUCCESS(tmp.stdout))
            # subprocess.run(["cd", f"{repo_name}"])
            subprocess.run(["git", "bundle", "create",
                            f'{repo_bundle}', "--all"])
            subprocess.run(["cp", f'{repo_bundle}', "/app/media/"])
            # subprocess.run(["cd", ".."])
            subprocess.run(["rm", "-rf", f"{repo_name}"])
            f = File(open(f'/app/media/{repo_bundle}', 'rb'))
            Backup.objects.create(repo=repo,
                                  file=f)
        if repos:
            TaskModel.objects.create(
                taskname="getcontainers",
                lastrunned=start_date
            )

        elapsed = time.time()
        self.stdout.write(self.style.SUCCESS(
            "--- Total %s seconds ---" % (elapsed - start_time)))
