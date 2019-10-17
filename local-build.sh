cd clinic_admin && yarn run build && cd ..
cd clinic_docs && yarn docs:build && cd ..
docker login docker.bitnp.net
docker build -t "docker.bitnp.net/bitnp/clinic/clinic_django:master" .
docker push docker.bitnp.net/bitnp/clinic/clinic_django:master
