docker-compose -f docker-compose-deploy.yml pull web
docker-compose -f docker-compose-deploy.yml stop web
docker-compose -f docker-compose-deploy.yml rm -f web
docker-compose -f docker-compose-deploy.yml up -d web
