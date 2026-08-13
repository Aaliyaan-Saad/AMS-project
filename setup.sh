#!/usr/bin/env bash
# AMS one-command setup: clone-independent, run from the project root.
# Creates a venv, installs dependencies, migrates the DB and seeds demo data.
set -e
cd "$(dirname "$0")"

echo "==> Checking Python 3"
command -v python3 >/dev/null || { echo "Python 3 is required but was not found."; exit 1; }

echo "==> Creating virtual environment"
if [ ! -d venv ]; then
  python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate

echo "==> Installing dependencies"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "==> Running migrations"
python manage.py migrate

echo "==> Seeding demo data"
python manage.py seed_demo

echo
echo "Done!"
echo
echo "Start the server with:"
echo "    source venv/bin/activate && python manage.py runserver"
echo
echo "Then open http://127.0.0.1:8000/  (login: admin@ams.com / Admin@123)"
echo
