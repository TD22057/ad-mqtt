FROM python:3.10.7

COPY requirements.txt /home/
RUN pip install -r /home/requirements.txt

COPY ad_mqtt /home/ad_mqtt/
COPY run.py setup.py /home/

#By default, docker instances will log only to screen
ENV ADMQTT_LOG_SCREEN=True
ENV ADMQTT_LOG_FILE=

#Mounting zones config file
VOLUME [ "/home/devices.py" ]

WORKDIR /home/
CMD ["python", "/home/run.py"] 