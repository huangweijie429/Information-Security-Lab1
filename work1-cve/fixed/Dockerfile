# Fixed image: httpd 2.4.51 (patched) + least-privilege directory policy.
FROM httpd:2.4.51

# CGI stays enabled, but only inside cgi-bin — the traversal target /bin/sh is not reachable.
RUN sed -i -E \
      -e 's|^[[:space:]]*#ScriptAlias /cgi-bin/|ScriptAlias /cgi-bin/|' \
      -e 's|^[[:space:]]*#LoadModule cgid_module|LoadModule cgid_module|' \
      -e 's|^[[:space:]]*#LoadModule cgi_module|LoadModule cgi_module|' \
      /usr/local/apache2/conf/httpd.conf

# Hardening: the filesystem root is not authorised at all (fixed default of 2.4.51
# is already restrictive, this keeps the config explicit).
RUN printf '\n<Directory />\n    AllowOverride None\n    Require all denied\n</Directory>\n' \
      >> /usr/local/apache2/conf/httpd.conf

RUN printf '#!/bin/sh\necho "Content-Type: text/plain"\necho\necho "hello from cgi"\n' \
      > /usr/local/apache2/cgi-bin/hello.sh && chmod +x /usr/local/apache2/cgi-bin/hello.sh

EXPOSE 80
