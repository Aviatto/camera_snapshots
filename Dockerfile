FROM python

WORKDIR /usr/src/app

COPY ./build ./build

### Preping for the python script ###
	
	## Variabels ##
		ARG DEFAULT_CONFIG_FOLDER_NAME=config
		ARG DEFAULT_CONFIG_FILE_NAME=cameras.json
		ARG DEFAULT_SNAPS_FOLDER_NAME=snaps
		ARG DEFAULT_SNAPS_TIME_OF_DAY=14

		ENV CONFIG_FOLDER_NAME=${DEFAULT_CONFIG_FOLDER_NAME}
		ENV CONFIG_FILE_NAME=${DEFAULT_CONFIG_FILE_NAME}
		ENV SNAPS_FOLDER_NAME=${DEFAULT_SNAPS_FOLDER_NAME}
		ENV SNAPS_TIME_OF_DAY=${DEFAULT_SNAPS_TIME_OF_DAY}
	
	RUN pip install --no-cache-dir -r ./build/requirements.txt

### Installing setting up the cron job ### 
	RUN apt-get update && apt-get -y install cron


RUN rm -rf ./build

COPY ./app .

RUN chmod u+x setup.sh

CMD ./setup.sh && rm setup.sh && cron && tail -f /var/log/cron.log