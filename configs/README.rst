Server configurations
=====================

Several server configurations are provided to configure the Supervisor, Nginx and Gunicorn. Below, hints are given to
how these configurations should be symlinked on the server::

    /etc/supervisor/conf.d/onepercentsite.conf => <project root>/configs/supervisor.<version>.conf
    /etc/nginx/sites-available/<version>.onepercentclub.conf => <project root>/configs/nginx.<version>.conf

Additionally, the ``gunicorn.conf`` is referenced in the supervisor configuration.
