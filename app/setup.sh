#!/bin/sh

echo "00 ${SNAPS_TIME_OF_DAY} * * * /usr/local/bin/python /usr/src/app/snapshot.py --conf-folder-name ${CONFIG_FOLDER_NAME} \
		--conf-file-name ${CONFIG_FILE_NAME} --snap-folder-name ${SNAPS_FOLDER_NAME} >> /var/log/cron.log 2>&1" > /etc/cron.d/snap_cron

chmod 0644 /etc/cron.d/snap_cron

crontab /etc/cron.d/snap_cron

touch /var/log/cron.log

mkdir -p ./${CONFIG_FOLDER_NAME}/${SNAPS_FOLDER_NAME}