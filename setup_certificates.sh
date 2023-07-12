#!/bin/sh

cert_path="/etc/letsencrypt/live/tla1.bank.smodata.net/fullchain.pem"
if [ -f "$cert_path" ]; then
  echo "Сертификат есть"
else
  echo "Выпуск нового сертификата..."
  certbot certonly --webroot --webroot-path /var/www/certbot/ \
    --non-interactive \
    --email timosha9911@gmail.com \
    --agree-tos \
    --no-eff-email \
    -d tla1.bank.smodata.net
fi
echo "Настройка сертификатов завершена"

