import os
import subprocess
import sys


def main():
    # Run database migrations
    subprocess.check_call([sys.executable, "manage.py", "migrate"])

    # create static files
    subprocess.check_call([sys.executable, "manage.py", "collectstatic", "--noinput"])

    # Start the application
    os.execlp(
        "gunicorn", "gunicorn", "BlogApp.wsgi:application", "--bind", "0.0.0.0:8000"
    )


if __name__ == "__main__":
    main()
