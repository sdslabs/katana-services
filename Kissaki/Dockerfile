FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip curl

WORKDIR /opt/kissaki/
COPY ./src/ .

RUN pip3 install -r requirements.txt

CMD ["/bin/bash", "-c", "python3 /opt/kissaki/app.py" ]
