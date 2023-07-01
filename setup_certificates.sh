#!/bin/sh

# Получаем сертификаты с помощью Certbot
certbot certonly --webroot \
    --webroot-path=/var/www/html \
    --email your-timosha9911@gmail.com \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d tla.bank.smodata.net

# Копируем сертификаты в контейнер с Nginx
echo "Копирование сертификатов в контейнер с Nginx..."
docker cp /etc/letsencrypt/live/tla.bank.smodata.net/fullchain.pem nginx:/etc/nginx/certs/fullchain.pem
docker cp /etc/letsencrypt/live/tla.bank.smodata.net/privkey.pem nginx:/etc/nginx/certs/privkey.pem

# Перезапуск контейнера Nginx с использованием Docker Remote API
echo "Перезапуск контейнера с Nginx..."
DOCKER_HOST=unix:///var/run/docker.sock docker restart nginx

echo "Настройка сертификатов завершена"

