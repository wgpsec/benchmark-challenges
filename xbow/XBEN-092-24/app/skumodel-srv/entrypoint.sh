#!/bin/bash

# Write flag at runtime
echo -n "$FLAG" > /flag.txt

# Start PHP-FPM
php-fpm -D

# Start Nginx
nginx -g 'daemon off;'
