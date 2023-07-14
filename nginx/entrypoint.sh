#!/bin/sh

envsubst '$SSL_CERTIFICATE_PATH $SSL_CERTIFICATE_KEY_PATH' < /etc/nginx/nginx.template.conf > /etc/nginx/conf.d

exec nginx -g "daemon off;"

