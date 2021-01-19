FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /django_project
WORKDIR /django_project
ADD requirements.txt /django_project/
RUN apt update \
    && apt install default-libmysqlclient-dev build-essential -y \
    && pip install --upgrade pip \
    && pip install --trusted-host pypi.python.org -r requirements.txt \
    && rm /usr/local/lib/python3.9/site-packages/disqus/__init__.py \
    && apt install -y locales \
    && locale-gen ko_KR.UTF-8 \
    && apt install fonts-nanum fonts-nanum-coding fonts-nanum-extra \
    && apt remove default-libmysqlclient-dev build-essential -y
ENV LC_ALL ko_KR.UTF-8
