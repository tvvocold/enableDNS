# enableDNS

enableDNS is a DNS management solution written in Django and realeased under the GPLv2 license. Zones are written directly to a MySQL database (in theory you can use PostgreSQL as well), and read by bind9 through the DLZ (dinamically loadable zones) module.

All interaction is done through a REST api. The core itself does not handle user registration in any way, but you can add users through the admin interface, which is enabled by default.

Setting everything up by hand takes 30 min or less if you copy/paste fast enough :)  
**autoinstall-edns.sh** installs everything for you in a couple of minutes (tested on Ubuntu 12.04).

## Supported DNS record types

* A
* AAAA
* MX
* NS
* CNAME
* TXT
* SRV
* PTR


## Installing the core

There are basically two parts to installing enableDNS, and having a fully functional DNS solution. The first part is installing the core itself, and the second part is installing your nameservers and taking care of the MySQL (or PostgreSQL) replication to all the nameservers.

The following instructions assume you are using Ubuntu 12.04 and that you have already created a user (let's say edns) which will run enableDNS.

We'll start by installing the needed dependencies:

```shell
sudo apt-get install python-virtualenv python-pip mysql-server fakeroot
sudo apt-get build-dep python-mysqldb python-ipaddr uwsgi
```

Create the needed databases and grant privileges for our app. We will be using these credentials in our settings.py to connect to the database. I sugest you se a stronger password then the one bellow:

```shell
create database dnsAdmin;
create database bind9;
grant all on dnsAdmin.* to 'edns'@'localhost' identified by 'secret';
grant all on bind9.* to 'edns'@'localhost' identified by 'secret';
flush privileges;
```

Now install the core:

```shell
mkdir -p /home/edns/workspace/enableDNS
cd /home/edns/workspace/enableDNS
git clone git@github.com:ROHOST/enableDNS.git edns
virtualenv venv
. venv/bin/activate
cd edns
pip install -r requirements.txt
```

You now have the app and all its dependencies installed. You may want to change some settings in settings.py. At bare minimum you will probably want to change the database settings. Make sure you use the same user/password/database you used earlier:

```python
DATABASES = {
    'default': {
        'NAME': 'dnsAdmin',  # Main database for django
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'edns',
        'PASSWORD': 'secret',
        'HOST': '127.0.0.1'
    },
    'bind': {
        'NAME': 'bind9',  # Database to be replicated to all nameservers
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'edns',
        'PASSWORD': 'secret',
        'HOST': '127.0.0.1'
    }
}
```

Next we must sync our database. This part is a bit odd because enableDNS needs 2 databases to work and django south does not obey the normal django database routers when it comes to syncing. Django has a nifty feature that allows you to write an allow_syncdb() method inside your database router and exclude some tables from one database or the other. But South is like the honey badger, [it does not give a s**t](https://www.youtube.com/watch?v=4r7wHMg5Yjg). So we have to sync the same tables for both databases.

```shell
./manage.py syncdb  # Go ahed and create an admin user here
./manage.py migrate
./manage.py syncdb --database=bind --noinput
./manage.py migrate --database=bind
```

Next, edit uwsgi.ini and change any setting you might need. Here are a few settings you might want to change:

```ini
uid = 1000
gid = 1000
http = 127.0.0.1:8080
virtualenv = /home/edns/workspace/enableDNS/venv
touch-reload= /home/edns/workspace/enableDNS/edns/restart.txt
chdir = /home/edns/workspace/enableDNS/edns
check-static = /home/edns/workspace/enableDNS/edns/public
```

Run the collectstatic management command to pull the CSS and js files for rest_framework and admin interfaces.

```shell
./manage.py collectstatic
```

At this point we should be good to go. You should be able to start enableDNS using the following command:

```shell
uwsgi --ini uwsgi.ini
```

Point your browser to: http://127.0.0.1:8080 and you should be redirected to the API. Before performing any operations, you should create a normal user. You may add users by logging into the admin interface at:


http://127.0.0.1:8080/admin


Each user will have a maximum of 5 domains he can create. You can edit user profiles and add more if you wish. There is also a 1000 record limit. That can be tweaked as well.

The API has 3 renderers enabled: api, json and YAML. The api renderer is a browser friendly, clickable interface that you can use to test the API inside the browser. The api allows 2 authentication mechanisms: session based and basic authentication (in the future maybe even OAuth). For testing purposes, you can login usging:


http://127.0.0.1:8080/api/v1.0/api-auth/login/


# Installing the nameservers

We have a 4 nameserver setup. There is one master mysql server and 4 readonly slaves. On each slave we have a BIND9 server installed, with DLZ enabled which connects to the local MySQL slave. I will not cover setting up replication and the individual nameservers. In this example, we will be using only one server. It should be relatively easy however to extend your setup to as many nameservers as you want. You only have to provision a server somewhere, install bind, setup replication, and you are good to go.


## Rebuilding BIND

In Ubuntu 12.04, bind has DLZ is disabled by default. So we will have to rebuild the package in order to get DLZ functionallity.

```shell
sudo apt-get install build-essential libmysqlclient-dev
# libmysqlclient-dev is needed for --with-dlz-mysql
sudo apt-get build-dep bind9
```

Download the bind9 source:

```shell
# you can choose any other destination directory
cd /tmp
apt-get source bind9
cd bind9-9.8.1.dfsg.P1/
```

We need to modify debian/rules to include the DLZ flag and delete an ifdef from sdlz_helper.c:

```shell
sed -ie '
/.*--enable-threads.*/i\
\t\t--with-dlz-mysql \\' debian/rules
sed -i '/#ifdef DLZ/d;$d' contrib/dlz/drivers/sdlz_helper.c
```
 Or you can perform these modifications manually if you wish. These files may change and the sed commands may stop working. But you get an ideea of what you have to do :). 

 Now build the package:

 ```shell
dpkg-buildpackage -rfakeroot -b
 ```

In the end you should have a bunch of debs generated. Just install them using:

```shell
cd ..
dpkg -i *.deb #  I am lazy...
```

You will probably want to mark them all for manual update so they don't get replaced with the packages in the repo and find yourself without DLZ.

## Edit bind configuration file

We need to let bind know how to querie zones from the database. On Ubuntu, the file we need to edit is:

```shell
/etc/bind/named.conf.local
```

Add the following at the end:

```shell
dlz "Mysql zone" {
   database "mysql
   {host=127.0.0.1 dbname=bind9 user=bind pass=supersecretpassword}
   {select zone from dns_records where zone = '$zone$'}
   {select ttl, type, priority, case when lower(type) = 'soa' then concat_ws(' ', data, resp_person, serial, refresh, retry, expire, minimum) else data end from dns_records where zone = '$zone$' and host = '$record$'}";
};

```

Lets grant user bind select access to the database:

```shell
mysql
grant SELECT,USAGE on bind9.* to 'bind'@'localhost' identified by 'supersecretpassword';
flush privileges;
```

Start bind and you should be up and running:

```shell
/etc/init.d/bind9 start
```

Feel free to browse the API. There are a few examples on how to add and edit zones. Have fun with it :).

To test if it worked, you can use something like:

```shell
host example.com 127.0.0.1
host -t MX example.com 127.0.0.1
```

Where example.com is the domain you will be adding using the API.


## Dynamic DNS update

Due to popular demand I have added an API similar to that of DynDNS. Most routers and SANs have an option to update their IP with a dynamic DNS service. The URL you can use is:

http://username:password@127.0.0.1:8080/nic/update/?myip=192.168.0.1&hostname=1

The only difference is that you need to use the DNS entry ID instead of the hostname itself. That should not be a problem and shoud work on most dynamic DNS update applications.

The myip parameter can be left out if you do not need to update to an IP other then the one you are accessing EnableDNS with. Basically the hostname will be updated to the IP shown by:

http://127.0.0.1:8080/ip
