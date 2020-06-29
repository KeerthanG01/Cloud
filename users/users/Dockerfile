
FROM python:3.6
EXPOSE 8080
ENV TEAM_NAME=CC_0044_0243_0963_1826
WORKDIR /users
COPY requirements.txt /users
RUN apt-get update
RUN pip3 install Flask-MySQLdb
RUN pip3 install -r requirements.txt
COPY app.py /users
CMD python app.py