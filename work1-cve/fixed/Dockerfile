# Fixed image: the 4.8 branch fixed CVE-2018-12613 in 4.8.2 (PMASA-2018-4);
# 5.2.2 is the maintained release that includes the fix.
# Build from the parent directory so config.inc.php is in the context:
#   docker build -f fixed/Dockerfile -t hdu-is/cve-2018-12613:fixed .
FROM phpmyadmin:5.2.2

COPY config.inc.php /var/www/html/config.inc.php

EXPOSE 80
