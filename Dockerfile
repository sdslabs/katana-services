FROM ubuntu:18.04

RUN apt-get update
WORKDIR /opt/katana/
COPY ./src/ .
RUN pip3 install -r requirements.txt
CMD [ "python3", "app.py" ]
EXPOSE 3004