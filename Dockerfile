FROM node:22-alpine AS build
COPY . /usr/src/app
WORKDIR /usr/src/app
ENV COREPACK_NPM_REGISTRY=https://registry.npmmirror.com
RUN corepack enable pnpm && pnpm config set registry https://registry.npmmirror.com/ && \
    cd /usr/src/app/clinic_admin_ng/ && pnpm install && pnpm build && \
    mv /usr/src/app/clinic_admin_ng/dist /usr/src/app/clinic_admin_dist && \
    rm -rf /usr/src/app/clinic_admin_ng


FROM python:3-slim
ENV DJANGO_PRODUCTION=1
COPY --from=build /usr/src/app /usr/src/app
WORKDIR /usr/src/app

COPY deploy/sources.list /etc/apt/sources.list
RUN rm /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y nginx tini && \
    rm -rf /var/lib/apt/lists/* && \
    sed -i 's/worker_processes auto/worker_processes 4/g' /etc/nginx/nginx.conf && \
    pip install -r requirements.txt --no-cache-dir && \
    echo "daemon off;" >> /etc/nginx/nginx.conf && \
    python manage.py collectstatic --noinput && \
    echo_supervisord_conf > /etc/supervisord.conf && \
    cat deploy/supervisor-app.conf >> /etc/supervisord.conf

COPY deploy/nginx-app.conf /etc/nginx/sites-available/default

EXPOSE 80
ENTRYPOINT [ "/bin/bash", "deploy/entrypoint.sh" ]
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]
