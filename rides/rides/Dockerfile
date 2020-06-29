FROM python:3.6
EXPOSE 8080
ENV TEAM_NAME=CC_0044_0243_0963_1826
WORKDIR /rides
COPY requirements.txt /rides
RUN apt-get update
RUN pip3 install Flask-MySQLdb
RUN pip3 install -r requirements.txt
COPY app1.py /rides
CMD python app1.py