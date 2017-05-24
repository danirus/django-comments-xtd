#!/bin/bash

pushd `dirname $0` > /dev/null
PRJPATH=`pwd`
popd > /dev/null
FIXTURESPATH=${PRJPATH}/../fixtures

check_ret() {
    [[ $? -ne 0 ]] && echo "Failed." && exit 1
}

cd ${PRJPATH}

#------------------------------
echo "Checking Django version... "
# Retrieve 1.7 as 1.07, so that they can be compared as decimal numbers.
version=`python -c 'import django; print("%d.%02d" % django.VERSION[:2])'`
if [[ ${version} < "1.07" ]]; then
    python manage.py syncdb --noinput || check_ret
    python manage.py migrate django_comments_xtd || check_ret
else
    python manage.py migrate --noinput || check_ret
fi

#------------------------------
echo "Loading fixture files... "
fixtures=(auth sites articles quotes)
for file in ${fixtures[@]}; do
    python manage.py loaddata ${FIXTURESPATH}/${file}.json || check_ret
done
