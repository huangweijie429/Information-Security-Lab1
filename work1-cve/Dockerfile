# Deliberately vulnerable image: phpMyAdmin 4.8.1 (CVE-2018-12613).
# Same base image and configuration as the public Vulhub environment.
FROM vulhub/phpmyadmin:4.8.1

COPY config.inc.php /var/www/html/config.inc.php

EXPOSE 80
