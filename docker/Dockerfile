# --- python3.6 image with gcc (required for dependency installation)
FROM python:3.6

RUN pip3 install --upgrade pip


# --- copy files
COPY requirements.txt /usr/src/

COPY python-flask-server /usr/src/python-flask-server

COPY subsidy_service /usr/src/subsidy_service

WORKDIR /usr/src


# --- Install requirements (including local packages)
RUN pip3 install -r /usr/src/requirements.txt


# --- mount points for configuration files and logs
VOLUME /etc/subsidy_service/config

VOLUME /etc/subsidy_service/logs


# --- expose port 8080 and start the app on run
EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
