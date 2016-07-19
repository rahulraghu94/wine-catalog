FROM ubuntu:latest
MAINTAINER Rahul Raghhunath "rahulraghu94@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3.5 build-essential

COPY . /server
WORKDIR /server

RUN pip3 install flask 
RUN pip3 install SQLAlchemy 
RUN pip3 install flask_httpauth
RUN pip3 install passlib

EXPOSE 5000

CMD ["python3.5", "server.py"].
