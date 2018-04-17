# --- python3.6 image with gcc (required for dependency installation)
FROM python:3.6

RUN pip install --upgrade pip

# --- install global requirements 
COPY requirements.txt /usr/src/
# filter out local packages
RUN grep -v "-e git" -i /usr/src/requirements.txt > /usr/src/requirements_clean.txt

RUN pip3 install -r /usr/src/requirements_clean.txt


# --- setup app directory and install swagger server
RUN mkdir -p /usr/src/app

COPY python-flask-server /usr/src/app

RUN pip3 install /usr/src/app

WORKDIR /usr/src/app


# --- make the service directory, copy code, and install as local package
RUN mkdir /usr/src/service

COPY subsidy_service /usr/src/service

RUN pip3 install /usr/src/service


# --- mount points for configuration files and logs
VOLUME /etc/subsidy_service

VOLUME /etc/subsidy_service/logs


# --- expose port 8080 and start the app on run
EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
