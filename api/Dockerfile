FROM python:3.10.9-slim-buster

WORKDIR /app

# set environment variables to prevent pyc and stdout/err buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install required linux modules
RUN apt update
RUN apt install libmagic-dev git supervisor cron telnet -y

# install dependencies
RUN pip install --upgrade pip
COPY ../requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 5000

COPY .. .
COPY ../supervisord.conf /etc/supervisor/conf.d/

RUN mkdir -p /etc/ssh/ssh_config.d
RUN touch /etc/ssh/ssh_config.d/ssh.conf
ENV FLASK_APP=api/app.py

RUN chmod u+x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]