FROM python:3

WORKDIR /app
RUN mkdir /config

#COPY requirements.txt ./
RUN pip install --no-cache-dir pybluez homie

COPY . .
RUN ls -la
CMD [ "python", "mqtt.bluetooth.py", "-c","/config/config.json" ]