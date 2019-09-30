import os
import sys

sys.path.insert(0, '../..') # parent of django_comments_xtd directory
sys.path.insert(0, '..') # demos directory

if __name__ == "__main__":
    import importlib
    from django.core.management import execute_from_command_line

    found = importlib.util.find_spec('settings')
    if not found:
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
        sys.exit(1)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comp.settings")
    execute_from_command_line(sys.argv)
