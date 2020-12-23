#! /usr/bin/env sh

set -o errexit
set -o pipefail

if [[ ${DEBUGPY} == 'TRUE' ]] || [[ ${DEBUGPY} == 'True' ]] || [[ ${DEBUGPY} == '1' ]]; then
    echo >&2 "Starting debug server with debugpy..."
    python3 -m debugpy --listen 0.0.0.0:5678 \
        -m uvicorn gitbackup.asgi:application \
            --host 0.0.0.0 \
            --port 8000 \
            --access-log \
            --use-colors \
            --log-level info \
            --lifespan off \
            --reload &
fi

echo >&2 "Migrating..."
python3 manage.py migrate

echo >&2 "Collect static..."
python3 manage.py collectstatic --noinput

echo >&2 "Init schedule tassk"
python3 manage.py inittasks

if [[ ${DEBUGPY} == 'TRUE' ]] || [[ ${DEBUGPY} == 'True' ]] || [[ ${DEBUGPY} == '1' ]]; then
    wait
elif [[ ${DEBUG} == 'TRUE' ]] || [[ ${DEBUG} == 'True' ]] || [[ ${DEBUG} == '1' ]]; then
    echo >&2 "Starting debug server..."
    exec python3 -m uvicorn gitbackup.asgi:application \
            --host 0.0.0.0 \
            --port 8000 \
            --access-log \
            --use-colors \
            --log-level info \
            --lifespan off \
            --reload
else
    echo >&2 "Starting prod server..."
    exec python3 -m uvicorn gitbackup.asgi:application \
            --host 0.0.0.0 \
            --port 8000 \
            --access-log \
            --use-colors \
            --log-level info \
            --lifespan off
fi
fi
