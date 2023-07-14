#!/bin/sh

nginx -g "daemon off;" &

sleep 15

envsubst '$SSL_CERTIFICATE_PATH $SSL_CERTIFICATE_KEY_PATH' < /etc/nginx/conf.d/nginx.template.conf > /etc/nginx/conf.d/nginx.template.conf

nginx -s reload

tail -f /dev/null
