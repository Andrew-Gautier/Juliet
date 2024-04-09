FROM php:7.3-apache
RUN a2enmod rewrite
COPY src/ /var/www/html/
EXPOSE 80