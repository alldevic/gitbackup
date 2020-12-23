import os
import os.path
import shutil
import subprocess
import tarfile
import time
from pathlib import Path, PurePath

from core.models import Backup, Repo, TaskModel
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from dulwich import porcelain


class Command(BaseCommand):
    help = 'Создание бэкапов'

    def handle(self, *args, **options):
        start_time = time.time()
        start_date = timezone.now()
        repos = Repo.objects.all()

        working_dir = "tmp"
        task = TaskModel(taskname="getcontainers", lastrunned=start_date)

        try:
            if not Path(working_dir).is_dir():
                Path(working_dir).mkdir()

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
                name = repo.url.split('/')[-1]
                repo_name = name \
                    if name.endswith(".git") \
                    else f"{name}.git"

                repo_bundle = f"{repo_name}.tar.gz"
                repo_work_dir = f"./{working_dir}/{repo_name}"
                if Path(repo_work_dir).is_dir():
                    remove(repo_work_dir)
                Path(repo_work_dir).mkdir()
                porcelain.clone(repo.url, bare=True)
                porcelain.clone(repo.url, checkout=True)

                # run(["git", "clone", "--mirror", repo.url, repo_name],
                #     task, repo_work_dir)
                # Path(Path(repo_work_dir).resolve() / repo_name) \
                #     .rename(Path(repo_work_dir).resolve()/".git")

                # run(["git", "init"], task, repo_work_dir)
                # run(["git", "checkout", "--"], task, repo_work_dir)
                make_tarfile(f"{working_dir}/{repo_bundle}", repo_work_dir)
                remove(repo_work_dir)

                f = File(open(f"{working_dir}/{repo_bundle}", 'rb'))
                backup_list += [Backup(repo=repo, file=f, task=task)]

            task.save()

            for backup in backup_list:
                backup.save()

        except subprocess.CalledProcessError as ex:
            self.stdout.write(self.style.ERROR(ex))
            if ex.stdout:
                self.stdout.write(self.style.ERROR(ex.stdout))
            if ex.stderr:
                self.stdout.write(self.style.ERROR(ex.stderr))

        finally:
            remove(working_dir)
            elapsed = time.time()
            self.stdout.write(self.style.SUCCESS(
                "--- Total %s seconds ---" % (elapsed - start_time)))


def run(args, task, cwd="."):
    res = subprocess.run(args, cwd=cwd, capture_output=True)

    if res.returncode != 0:
        task.successful = False
        task.returncode = res.returncode
        task.args = res.args
        task.stdout = res.stdout
        task.stderr = res.stderr
        task.save()
        raise subprocess.CalledProcessError(res.returncode, res.args)


def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


def make_tarfile(out_file, source_dir):
    with tarfile.open(out_file, "w:gz", format=tarfile.GNU_FORMAT) as tar:
        tar.add(source_dir, arcname=PurePath(source_dir).name)
