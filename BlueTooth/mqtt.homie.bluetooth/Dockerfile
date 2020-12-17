FROM python:3

WORKDIR /usr/src/app
RUN mkdir /config

#COPY requirements.txt ./
RUN pip install --no-cache-dir pybluez homie

COPY . .
RUN ls -la
CMD [ "python", "mqtt.homie.bluetooth.py -c /config/config.json" ]