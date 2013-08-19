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

