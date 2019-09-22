docker-compose -f docker-compose-deploy.yml pull web
docker-compose -f docker-compose-deploy.yml stop web
docker-compose -f docker-compose-deploy.yml rm web -f
docker-compose -f docker-compose-deploy.yml up -d web
