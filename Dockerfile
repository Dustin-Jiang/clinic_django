FROM python:3.9-slim-bullseye
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ENV DJANGO_PRODUCTION=1

# Use sed because of potential file owner issue
RUN sed -i 's/deb.debian.org/mirrors-tuna.bitnp.net/g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org/debian-security|mirrors-tuna.bitnp.net/debian-security|g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|mirrors-tuna.bitnp.net/debian-security|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y gcc nginx supervisor && \
    rm -rf /var/lib/apt/lists/* && \
    pip config set global.index-url http://pypi-tuna.bitnp.net/simple && \
    pip config set install.trusted-host pypi-tuna.bitnp.net

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt --no-cache-dir

RUN apt-get remove -y gcc && apt-get autoremove -y && apt-get clean -y

COPY . /usr/src/app/

RUN rm -rf /usr/src/app/clinic_admin/node_modules /usr/src/app/clinic_docs/node_modules

RUN echo "daemon off;" >> /etc/nginx/nginx.conf && \
    sed -i 's/worker_processes auto/worker_processes 10/g' /etc/nginx/nginx.conf && \
    python manage.py collectstatic --noinput

COPY deploy/nginx-app.conf /etc/nginx/sites-available/default
COPY deploy/supervisor-app.conf /etc/supervisor/conf.d/

EXPOSE 80
ENTRYPOINT [ "/bin/bash", "deploy/entrypoint.sh" ]
CMD ["supervisord", "-n"]
