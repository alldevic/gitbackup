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


class Command(BaseCommand):
    help = 'Создание бэкапов'

    def handle(self, *args, **options):
        start_time = time.time()
        start_date = timezone.now()
        repos = Repo.objects.all()

        working_dir = "tmp"
        task = TaskModel(taskname="getcontainers", lastrunned=start_date)

        if not Path(working_dir).is_dir():
            Path(working_dir).mkdir()

        backup_list = []

        for repo in repos:
            try:
                self.print_succ(f"Begin {repo.name} - {repo.url}")
                curr_time = time.time()

                name = repo.url.split('/')[-1]
                repo_name = name \
                    if name.endswith(".git") \
                    else f"{name}.git"

                repo_bundle = f"{repo_name}.tar.gz"
                repo_work_dir = f"./{working_dir}/{repo_name}"
                if Path(repo_work_dir).is_dir():
                    remove(repo_work_dir)
                Path(repo_work_dir).mkdir()

                self.print_info("Clonning...")
                run(["git", "clone", "--mirror", repo.url, repo_name],
                    task, repo_work_dir)

                Path(Path(repo_work_dir).resolve() / repo_name) \
                    .rename(Path(repo_work_dir).resolve()/".git")

                self.print_info("Checkout...")
                run(["git", "init"], task, repo_work_dir)
                run(["git", "checkout", "--"], task, repo_work_dir)

                self.print_info("Make arch...")
                make_tarfile(f"{working_dir}/{repo_bundle}", repo_work_dir)
                remove(repo_work_dir)

                self.print_info("Create backup instance...")
                f = File(open(f"{working_dir}/{repo_bundle}", 'rb'))
                backup_list += [Backup(repo=repo, file=f, task=task)]

                self.print_elapsed(curr_time, f"Elapsed {repo.name}")

            except subprocess.CalledProcessError as ex:
                self.stdout.write(self.style.ERROR(
                    ' '.join(map(str, ex.args))))
                if ex.stdout:
                    self.stdout.write(self.style.ERROR(
                        ex.stdout.decode('utf8')))
                if ex.stderr:
                    self.stdout.write(self.style.ERROR(
                        ex.stderr.decode('utf8')))

        task.save()

        for backup in backup_list:
            backup.save()

        remove(working_dir)
        self.print_elapsed(start_time, "Total")

    def print_succ(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def print_info(self, message):
        self.stdout.write(message)

    def print_elapsed(self, start_time, prefix="Elapsed"):
        elapsed = time.time()
        self.stdout.write(self.style.SUCCESS(
            f"--- {prefix} {elapsed - start_time} seconds ---"))


def run(args, task, cwd="."):
    res = subprocess.run(args, cwd=cwd, capture_output=True)

    if res.returncode != 0:
        task.successful = False
        task.returncode = res.returncode
        if task.args:
            task.args += '\n'
            task.args += ' '.join(map(str, res.args))
        else:
            task.args = ' '.join(map(str, res.args))

        if task.stdout:
            task.stdout += '\n'
            task.stdout += res.stdout.decode("utf-8")
        else:
            task.stdout = res.stdout.decode("utf-8")

        if task.stderr:
            task.stderr += '\n'
            task.stderr += res.stderr.decode("utf-8")
        else:
            task.stderr = res.stderr.decode("utf-8")

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
