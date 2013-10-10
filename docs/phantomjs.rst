PhantomJS
=========

Install PhantomJS as binary (or compile if you're on a development machine). Pay attention to the platform::

    $ uname -m
    x86_64  # If it says 32 bits, adjust the download link below...

    $ wget https://phantomjs.googlecode.com/files/phantomjs-1.9.1-linux-x86_64.tar.bz2

    $ bunzip2 phantomjs-1.9.1-linux-x86_64.tar.bz2
    $ tar -xf phantomjs-1.9.1-linux-x86_64.tar
    $ sudo mv phantomjs-1.9.1-linux-x86_64/bin/phantomjs /usr/local/bin/

Add to Supervisor::

    $ sudo vi /etc/supervisor/conf.d/onepercentsite.conf

Add the following snippet to the configuration file::

    [program:phantomjs]
    command=/usr/local/bin/phantomjs --wd
    directory=/var/www/onepercentsite
    umask=022
    user=onepercentsite
    autostart=true
    autorestart=true
    redirect_stderr=True
    stdout_logfile=/var/log/supervisor/phantomjs.log
    stderr_logfile=/var/log/supervisor/phantomjs-stderr.log

Reload Supervisor::

    $ sudo supervisorctl reload

Validate configuration::

    $ sudo supervisorctl status
    onepercentsite                   RUNNING    pid 25737, uptime 0:00:07
    phantomjs                        RUNNING    pid 25738, uptime 0:00:07

Optionally, on restricted servers: Allow localhost and the server's own public
IP address in Nginx, to prevent authorization issues.

For example, in Nginx::

    satisfy any;
    allow 127.0.0.1
    # allow <machine ip>


Debugging PhantomJS
-------------------

#. SSH to the webserver.
#. Validate if the webserver can access itself::

    $ wget 'https://<subdomain>.onepercentclub.com/nl/#!/projects'

#. If the error ``ERROR: cannot verify [...]`` appears, turn it into a warning with::

    $ wget --no-check-certificate 'https://<subdomain>.onepercentclub.com/nl/#!/projects'

#. If the response is ``Authorization failed.``, configure Nginx to allow local
   access without a password, for example::

    server {
        # ...

        satisfy any;

        # Allow PhantomJS to access the webserver locally.
        allow 127.0.0.1;
        allow <server IP address>

        # ...
    }

#. Save the following snipet as ``checklocal.js``::

    var page = require('webpage').create(),
        system = require('system'),
        t, address;

    if (system.args.length === 1) {
        console.log('Usage: loadspeed.js <some URL>');
        phantom.exit();
    }

    page.open(system.args[1], function () {
        page.render('preview.png');
        phantom.exit();
    });

#. To see what PhantomJS sees, you can generate a screenshot. Run::

    $ phantomjs --debug=true checklocal.js 'https://<subdomain>.onepercentclub.com/nl/#!/projects'

#. Finally, you can run PhantomJS, as you would with Supervisor::

    phantomjs --wd --ignore-ssl-errors=true --debug=true

#. Launch a server instance, or use the runserver command and request a URL
   with an escaped fragment.
