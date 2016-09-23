Provisioning
============

## Filemaker server and RESTfm

- Set php.ini max_execution_time = 60 for Filemaker PHP installation
(otherwise full plate sample updates may time out)
- For debugging, restfm verbose logs go to C:/Windows/Temp when enabled


## Required packages:

* nginx
* Python 3
* Git
* pip
* virtualenv
* nodejs
* npm
* yuglify

## Nginx Virtual Host config

* see nginx.template.conf2
* replace SITENAME with, eg, staging.microbesng.uk

## Letsencrypt

Follow this guide https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04
Use /tmp/letsencrypt for document root

crontab
30 2 * * 1 /opt/letsencrypt/letsencrypt-auto renew >> /var/log/le-renew.log
35 2 * * 1 /bin/systemctl reload nginx

to update client
cd /opt/letsencrypt
sudo git pull

## Node / NPM + Yuglify
sudo apt-get install nodejs
sudo ln -s /usr/bin/nodejs /usr/bin/node
sudo apt-get install npm
sudo npm -g install yuglify

## Systemd

* see gunicorn-microbesng.uk.service template
* replace SITENAME with, eg, microbesng.uk
  
save it as something.service in /etc/systemd/system/ 
systemctl enable something 
systemctl start something
systemctl daemon-reload (before enable)

## Folder structure:
Assume we have a user account at /home/username

/home/username
└── sites
    └── SITENAME
         ├── database
         ├── source
         ├── static
