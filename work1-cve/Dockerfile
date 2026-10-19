# Deliberately vulnerable image: Apache httpd 2.4.49 (CVE-2021-41773).
# Mirrors the public Vulhub configuration needed to trigger the traversal.
FROM httpd:2.4.49

# 1) enable CGI so a traversed binary can be executed
RUN sed -i \
      -e 's/^#LoadModule cgid_module/LoadModule cgid_module/' \
      -e 's/^#LoadModule cgi_module/LoadModule cgi_module/' \
      /usr/local/apache2/conf/httpd.conf

# 2) allow the whole filesystem, the authorization mistake from the Vulhub PoC
RUN printf '\n<Directory />\n    AllowOverride None\n    Require all granted\n</Directory>\n' \
      >> /usr/local/apache2/conf/httpd.conf

# a harmless CGI script that proves code execution when traversed
RUN printf '#!/bin/sh\necho "Content-Type: text/plain"\necho\necho "hello from cgi"\n' \
      > /usr/local/apache2/cgi-bin/hello.sh && chmod +x /usr/local/apache2/cgi-bin/hello.sh

EXPOSE 80
