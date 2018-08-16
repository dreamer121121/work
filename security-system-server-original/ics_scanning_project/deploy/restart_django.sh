#!/bin/sh
echo "stop icsserver..."
ps aux|grep "python manage.py runserver" | awk '{print $2}' |xargs kill
echo "OK"
sleep 5
echo "start icsserver..."
cd /yun/website/backend/icsscan
python manage.py runserver > /var/log/django_console.log 2>&1 &
echo "OK"
