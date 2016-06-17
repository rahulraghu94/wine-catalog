FROM ubuntu:latest
MAINTAINER Rahul Raghhunath "rahulraghu94@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3.5 build-essential

COPY . /server
WORKDIR /server

RUN pip3 install flask SQLAlchemy

CMD ["python3.5", "server.py"].