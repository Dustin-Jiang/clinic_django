FROM python:3.9-slim-bullseye
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ENV DJANGO_PRODUCTION=1

# Use sed because of potential file owner issue
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org/debian-security|mirrors.tuna.tsinghua.edu.cn/debian-security|g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|mirrors.tuna.tsinghua.edu.cn/debian-security|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y libpq5 libpq-dev gcc nginx supervisor && \
    rm -rf /var/lib/apt/lists/* && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt --no-cache-dir

RUN apt-get remove -y libpq-dev gcc && apt-get autoremove -y 

COPY . /usr/src/app/

RUN echo "daemon off;" >> /etc/nginx/nginx.conf && \
    python manage.py collectstatic --noinput

COPY deploy/nginx-app.conf /etc/nginx/sites-available/default
COPY deploy/supervisor-app.conf /etc/supervisor/conf.d/

EXPOSE 80
ENTRYPOINT [ "/bin/bash", "deploy/entrypoint.sh" ]
CMD ["supervisord", "-n"]
