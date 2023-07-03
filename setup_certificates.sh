#!/bin/bash

existing_cert=$(certbot certificates --domains tla.bank.smodata.net --cert-name tla.bank.smodata.net --format json)

cert_status=$(echo "$existing_cert" | jq -r '.[] | .status')

if [ "$cert_status" == "OK" ]; then
  echo "Существует действующий и валидный сертификат. Пропуск выписывания нового сертификата."
else
  echo "Выпуск нового сертификата..."
  certbot certonly \
    --email your-timosha9911@gmail.com \
    --agree-tos \
    --no-eff-email \
    -d tla.bank.smodata.net

fi

echo "Настройка сертификатов завершена"

nginx -g "daemon off;"
