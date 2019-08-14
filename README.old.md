# 诊所预约系统

## 部署

`docker run -d -p 80:80 --name clinic --link clinic-db:mysql -e SECRET_KEY=XXXX -e YUNPIAN_APIKEY=xxxxxxxx git.bitnp.net:5005/bitnp/clinic_django:master`

注意：

数据库必须加上`--character-set-server=utf8 --collation-server=utf8_general_ci`

（这都9102年了mariadb的默认编码还是latin

加入第一个用户：

`docker exec -it clinic python manage.py createsuperuser`