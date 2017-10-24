Deploy
======

Now your project finished and ready to deploy. Prepare the application with :doc:`/guide/wsgi`.
then you need to run application and control it.

Running
-------

With tools like `supervisor <http://supervisord.org/>`_ you can run,
monitor and control your application.
Follow the instructions on `supervisor <http://supervisord.org/>`_ documentation.

This is simple config for supervisor:

.. code-block:: ini

    [program:YourApplicationName]
    command=/path/to/my-virtualenv/bin/gunicorn -b :8080 wsgi:app
    directory=/path/to/my_application_directory
    autostart=true
    autorestart=true


Configure web server
--------------------

Finally you should configure web server to connect to application.
simple solution is using reverse proxy and it's available in most of web servers.

sample reverse proxy config for NGINX:

.. code-block:: nginx

    location / {
        rewrite /(.*) /$1  break;
        try_files $uri @proxy_to_my_application;
    }

    location @proxy_to_my_application {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # enable this if and only if you use HTTPS
        # proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Host $http_host;
        # we don't want nginx trying to do something clever with
        # redirects, we set the Host: header above already.
        proxy_redirect off;
        proxy_pass http://0.0.0.0:8080;
    }


Or Apache:

.. code-block:: apacheconf

    <Location />
        ProxyPass http://0.0.0.0:8080
        ProxyPassReverse http://0.0.0.0:8080
        Order allow,deny
        Allow from all
    </Location>
