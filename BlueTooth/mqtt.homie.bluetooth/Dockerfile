FROM python:3

WORKDIR /usr/src/app
mkdir bt

#COPY requirements.txt ./
RUN pip install --no-cache-dir pybluez homie 

COPY . ./bt
COPY bluemaestroscan.py .

CMD [ "python", "./bt/your-daemon-or-script.py" ]