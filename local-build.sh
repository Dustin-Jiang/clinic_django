cd clinic_admin && yarn run build && cd ..
docker login docker.bitnp.net
docker build -t "docker.bitnp.net/bitnp/clinic/clinic_django:local-build" .
docker push docker.bitnp.net/bitnp/clinic/clinic_django:local-build
