FROM python:3.9.12-slim-buster

# copy list of necessary python modules and install them
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY src/ /app
WORKDIR /app

COPY bin/ /sbin/
RUN chmod +x /sbin/startup.sh

ENTRYPOINT ["/sbin/startup.sh"]