#!/bin/sh

cert_path="/etc/letsencrypt/live/tla.bank.smodata.net/fullchain.pem"
if [ -f "$cert_path" ]; then
  echo "Сертификаты уже существуют"
  exit 0
fi

echo "Выпуск нового сертификата..."

if certbot certonly --standalone --preferred-challenges http \
  --http-01-port 80 \
  --non-interactive \
  --email timosha9911@gmail.com \
  --agree-tos \
  --no-eff-email \
  -d tla.bank.smodata.net; then
  echo "Сертификаты успешно созданы"
  exit 0
else
  echo "Произошла ошибка при выпуске сертификатов"
  exit 1
fi

echo "Настройка сертификатов завершена"


