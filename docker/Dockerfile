# --- python3.6 image with gcc (required for dependency installation)
FROM python:3.6


# --- install global requirements 
COPY requirements.txt /usr/src/
# filter out local packages
RUN grep -v "-e git" -i /usr/src/requirements.txt > /usr/src/requirements_clean.txt

RUN pip3 install -r /usr/src/requirements_clean.txt


# --- setup app directory and install swagger requirements
RUN mkdir -p /usr/src/app

COPY python-flask-server /usr/src/app

# RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

RUN pip3 install -e /usr/src/app

WORKDIR /usr/src/app


# --- make the service directory, copy code, and install as local package
RUN mkdir /usr/src/service

COPY subsidy_service /usr/src/service

RUN pip3 install -e /usr/src/service


# --- mount point for configuration files
VOLUME /etc/config/subsidy_service


# --- expose port 8080 and start the app on run
EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
