import importlib
import os
import sys

sys.path.insert(0, "../..")  # Parent of django_comments_xtd directory,
sys.path.insert(0, "..")  # and `example` directory.


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mockups_project.settings")
    try:
        from django.core.management import execute_from_command_line

        found = importlib.util.find_spec("settings")
        if not found:
            sys.stderr.write(
                "Error: Can't find the file 'settings.py' in the directory "
                f"containing {__file__!r}. It appears you've customized "
                "things.\nYou'll have to run django-admin.py, passing it "
                "your settings module.\n"
            )
            sys.exit(1)
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


if __name__ == "__main__":
    main()
