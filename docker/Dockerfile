# --- python3.6 image with gcc (required for dependency installation)
FROM python:3.6

# --- make the app directory, install requirements, copy code
RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY python-flask-server/requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY python-flask-server /usr/src/app

# --- make the service directory, copy code, and pip install 
RUN mkdir /usr/src/service

COPY subsidy_service /usr/src/service

RUN pip3 install /usr/src/service

# --- include configuration files
RUN mkdir /etc/config
VOLUME /etc/config


# --- expose port 8080 and start the app on run
EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
