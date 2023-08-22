FROM node:18-slim AS build
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm config set registry https://registry.npmmirror.com/
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN mkdir -p /usr/src/app/clinic_admin/node_modules && \
    rm -rf /usr/src/app/clinic_admin/node_modules && \
    pnpm --dir /usr/src/app/clinic_admin/ install

RUN pnpm --dir /usr/src/app/clinic_admin/ run build && \
    mv /usr/src/app/clinic_admin/dist /usr/src/app/clinic_admin_dist && \
    rm -rf /usr/src/app/clinic_admin


FROM python:3-slim
ENV DJANGO_PRODUCTION=1
COPY --from build /usr/src/app /usr/src/app
WORKDIR /usr/src/app

COPY deploy/sources.list /etc/apt/sources.list
RUN rm /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y nginx tini && \
    rm -rf /var/lib/apt/lists/* && \
    sed -i 's/worker_processes auto/worker_processes 2/g' /etc/nginx/nginx.conf && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -r requirements.txt --no-cache-dir

RUN echo "daemon off;" >> /etc/nginx/nginx.conf && \
    sed -i 's/worker_processes auto/worker_processes 4/g' /etc/nginx/nginx.conf && \
    python manage.py collectstatic --noinput

COPY deploy/nginx-app.conf /etc/nginx/sites-available/default
COPY deploy/supervisor-app.conf /etc/supervisor/conf.d/

EXPOSE 80
ENTRYPOINT [ "/bin/bash", "deploy/entrypoint.sh" ]
CMD ["supervisord", "-n"]
