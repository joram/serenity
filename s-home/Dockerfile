FROM kyma/docker-nginx
COPY src /var/www
COPY ./.nginx_serenity /etc/nginx/sites-enabled/serenity
COPY ./.htpasswd /etc/nginx/
CMD 'nginx'
