Provisioning
============

Any templates referred to can be found in the deploy_tools directory of the repo.

Make sure 443 is open in the CLIMB security group for new server.


### Filemaker server and RESTfm

- Set php.ini max_execution_time = 60 for Filemaker PHP installation
(otherwise full plate sample updates may time out)
- For debugging, restfm verbose logs go to C:/Windows/Temp when enabled


### Required packages:

* nginx
* Python 3
* Git
* pip
* virtualenv
* letsencrypt
* nodejs
* npm
* yuglify

##### Notes:
* symlink node `sudo ln -s /usr/bin/nodejs /usr/bin/node`
* install yuglify globally `sudo npm -g install yuglify`

### Nginx
* Copy `nginx.conf` template to `/etc/nginx/`
* Copy `ssl-params.conf` template to `/etc/nginx/snippets`
* Copy `microbesng.uk` template to `/etc/nginx/sites-available`
* `ln -s /etc/nginx/sites-available/microbesng.uk /etc/nginx/sites-enabled/microbesng.uk`
* disable default site `rm /etc/nginx/sites-enabled/default`
* `mkdir /tmp/letsencrypt`
* `cd /etc/ssl/certs`
* `openssl dhparam -out dhparam.pem 4096`

##### If transferring from  existing server:
* copy existing letsencrypt certs:
  * copy `fullchain.pem` and `privkey.pem` from `/etc/letsencrypt/live/` on existing server (follow symlinks)
  * to `/etc/nginx/ssl/microbesng.uk` on new server
  * edit `/etc/nginx/sites-available/microbesng.uk` to point at temp certs in `/etc/nginx/ssl/microbesng.uk`
  * once DNS has been changed, you can proceed to setup letsencrypt

##### If starting from scratch (DNS already points at new server)
  * `sudo letsencrypt certonly -a webroot --webroot-path=/tmp/letsencrypt -d microbesng.uk`

##### Check nginx config is valid:
  * `nginx -t`

### Gunicorn
  * copy template to `/etc/systemd/system/gunicorn-microbesng.uk.service`
  * `mkdir /var/log/gunicorn`, ubuntu user has write permissions
  * `sudo systemctl enable gunicorn-microbesng.uk`
  * `sudo systemctl start gunicorn-microbesng.uk`
  * Check log in `/var/log/gunicorn/`


### Setup Django site

#### Folder structure:
    Assume we have a user account at /home/username, the folder structure will be:

    /home/username
    └── sites
        └── SITENAME
             ├── database
             ├── source
             ├── static

##### On server:
  * `mkdir -p ~/sites/microbesng.uk`

##### On local machine:
  * `pip install fabric`
  * Clone the repo from https://github.com/MRC-CLIMB/bryn
  * Obtain local settings files (from previous server, or Nick)
    1. `~/sites/microbesng.uk/source/mngweb/settings/local.py`
  * from local deploy_tools dir:
    * **If DNS still points at previous server, add new ip to your hosts file before proceeding**
    * Don't just use the ip of the new server, since the fabric script makes use of the hostname
    * `fab deploy:host=ubuntu@microbesng.uk`
    * This should clone repo to remote machine, setup venv, install requirements, consolidate static files etc.

##### On server:
  * Overwrite `~/sites/microbesng.uk/database/db.sqlite3` with latest copy from existing server
  * `sudo systemctl restart gunicorn-microbesng.uk`
  * `sudo service nginx restart`


### Setup letsencrypt (after DNS change)
  * `sudo letsencrypt certonly -a webroot --webroot-path=/tmp/letsencrypt -d microbesng.uk`
  * edit `/etc/nginx/sites-available/microbesng.uk` to point at certs in `/etc/letsencrypt/live/microbesng.uk`
  * setup auto-renew crontab:
    * `30 2 * * 1 /opt/letsencrypt/letsencrypt-auto renew >> /var/log/le-renew.log`
    * `35 2 * * 1 /bin/systemctl reload nginx`
    
