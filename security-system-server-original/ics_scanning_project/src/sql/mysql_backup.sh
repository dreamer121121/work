#!/bin/bash
#
# Backup the data of the MySQL.
#
BACKUP_DIR=/var/log/mysql_backup
LOG_TIME=`date +%Y%m%d%H%M`
MYSQL_CMD_PATH=/usr/bin
DB_NAME=ics_scanning
DB_USR=root
DB_PWD=8571512411

$MYSQL_CMD_PATH/mysqldump -u $DB_USR -p$DB_PWD $DB_NAME | gzip > ${BACKUP_DIR}/${DB_NAME}_${LOG_TIME}.sql.gz
