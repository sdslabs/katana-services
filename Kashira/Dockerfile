FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip

WORKDIR /opt/kashira/
COPY ./src/ .

RUN pip3 install -r requirements.txt

EXPOSE 80

CMD ["/bin/bash", "-c", "python3 /opt/kashira/app.py" ]
