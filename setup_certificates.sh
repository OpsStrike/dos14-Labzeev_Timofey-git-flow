#!/bin/sh

cert_path="/etc/letsencrypt/live/tla.bank.smodata.net/fullchain.pem"
if [ -f "$cert_path" ]; then
  echo "Сертификат есть"
else
  echo "Выпуск нового сертификата..."
  certbot certonly --standalone --preferred-challenges http \
    --http-01-port 80 \
    --non-interactive \
    --email timosha9911@gmail.com \
    --agree-tos \
    --no-eff-email \
    -d tla.bank.smodata.net
fi
echo "Настройка сертификатов завершена"

