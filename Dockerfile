# --- python3.6 image with gcc (required for dependency installation)
FROM python:3.6-stretch

ENV TZ="Europe/Amsterdam"

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

RUN apt-get update && \
    apt-get install -y cron man-db vim

RUN pip3 install --upgrade pip

# --- copy files and install requirements
COPY requirements.txt /usr/src/

RUN pip3 install -r /usr/src/requirements.txt

COPY python-flask-server /usr/src/python-flask-server

COPY subsidy_service /usr/src/subsidy_service

# --- Add command line scripts and cron jobs
COPY scripts/*.py /usr/src/scripts/

ADD docker_run.sh /bin

WORKDIR /usr/src


# --- Install local packages
RUN pip3 install -e /usr/src/python-flask-server && \
    pip3 install -e /usr/src/subsidy_service

RUN mkdir -p /etc/subsidy_service/config/
RUN chmod 777 /etc/subsidy_service/config/

# --- mount points for configuration files and logs
VOLUME /etc/subsidy_service/logs


# --- customize bashrc
#ADD docker/bashrc_addendum /tmp
#
#RUN cat /tmp/bashrc_addendum >> /root/.bashrc


# --- expose port 8080 and start the app on run
EXPOSE 8080

ENTRYPOINT ["/bin/bash"]

CMD ["docker_run.sh"]

#ENTRYPOINT ["python3"]
#
#CMD ["-m", "swagger_server"]
