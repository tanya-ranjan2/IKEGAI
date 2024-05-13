FROM python:3.11

RUN mkdir app
WORKDIR /app

ADD /app /app

RUN pip install -r requirements.txt

RUN apt-get update
RUN apt install -y libgl1-mesa-glx
RUN apt install -y libopencv-dev
EXPOSE 6069
