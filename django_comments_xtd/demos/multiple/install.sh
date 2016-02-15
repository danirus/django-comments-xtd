#!/bin/bash

pushd `dirname $0` > /dev/null
PRJPATH=`pwd`
popd > /dev/null
FIXTURESPATH=${PRJPATH}/fixtures

check_ret() {
    [[ $? -ne 0 ]] && echo "Failed." && exit 1
}

cd ${PRJPATH}


#------------------------------
printf "Checking Django version... "
django_version=`python -c 'import django; print(django.get_version())'`
printf "${django_version}\n"

if [[ ${django_version} < 1.7 ]]; then
    python manage.py syncdb --noinput || check_ret
    python manage.py migrate django_comments_xtd || check_ret
else
    python manage.py migrate --noinput || check_ret
fi

#------------------------------
printf "Checking django_comments_xtd parent app... "
django_comments=`python -c 'import imp
try:
    imp.find_module("django_comments")
    print("django_comments")
except ImportError:
    print("django.contrib.comments")
'`
printf "${django_comments}\n"

fixtures=(auth sites blog projects ${django_comments} django_comments_xtd)
for file in ${fixtures[@]}; do
    python manage.py loaddata ${FIXTURESPATH}/${file}.json || check_ret
done
