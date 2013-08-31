#!/bin/bash
# Auth: Ionut Cadariu
# Desc: Script to install enableDNS
# Date:  07-26-2013

# Please edit the following

ednsUSER="edns"         # enableDNS user
ednsPASS=""             # enableDNS password
BINDUSER="bind"         # Bind MySQL user
BINDPASS=""             # Bind MySQL password
DATABASE="dnsAdmin"     # dnsdatabase
BINDDB="bind9"          # bind database
WORKSPACE="/home/$ednsUSER/workspace/enableDNS"

# Installation process starts here

[ -z "$ednsPASS" ] && read -p "Please provide password for $ednsUSER: " ednsPASS
[ -z "$BINDPASS" ] && read -p "Please provide password for $BINDUSER: " BINDPASS

initial_checks()
{
    #
    # This function will upgrade the system packages and install the necessary ones
    #

    grep "deb-src" /etc/apt/sources.list > /dev/null 2>&1
    [ "$?" -ne 0 ] && echo "I need dep-src in /etc/apt/sources.list to continue... Please add them and press Enter" && read

    sudo apt-get update && apt-get upgrade -y       # system upgrade

    dpkg -s git > /dev/null 2>&1                    # check if git package is installed
    [ "$?" -ne 0 ] && sudo apt-get install git -y

    sudo apt-get install python-virtualenv python-pip mysql-server fakeroot -y
    sudo apt-get build-dep python-mysqldb python-ipaddr uwsgi -y

    [ $? -ne 0 ] && read -p  "Error installing packages. Do you want to continue? Y/n -  " answer
    [ "$answer" == 'n' ] && exit 1
    echo
}

core_part()
{
    #
    # Function used to install the core part of enableDNS
    #

    read -p  "Please provide MySQL root password in order to create databases and grant permissions: " SQLPASS

    mysql -u root -p$SQLPASS <<EOF
create database $DATABASE;
create database $BINDDB;
grant all on $DATABASE.* to '$ednsUSER'@localhost identified by '$ednsPASS';
grant all on $BINDDB.* to '$ednsUSER'@localhost identified by '$ednsPASS';
flush privileges;
EOF

    [ $? -ne 0 ] && read -p  "Error during database creation. Do you want to continue? Y/n -  " answer
    [ "$answer" == 'n' ] && exit 1

    id $ednsUSER > /dev/null 2>&1                       # Check if user exists
    [ $? -ne 0 ] && sudo useradd -m $ednsUSER

    mkdir -p $WORKSPACE
    cd $WORKSPACE

    git clone git@github.com:ROHOST/enableDNS.git edns

    [ $? -ne 0 ] && read -p  "Errors while git clone. Do you want to continue? Y/n -  " answer
    [ "$answer" == 'n' ] && exit 1

    virtualenv venv
    . $WORKSPACE/venv/bin/activate
    cd $WORKSPACE/edns
    pip install -r requirements.txt
    cat > $WORKSPACE/edns/project/local_settings.py <<EOF
DATABASES = {
    'default': {
        'NAME': '$DATABASE',  # Main database for django
        'ENGINE': 'django.db.backends.mysql',
        'USER': '$ednsUSER',
        'PASSWORD': '$ednsPASS',
        'HOST': '127.0.0.1'
    },
    'bind': {
        'NAME': '$BINDDB',  # Database to be replicated to all nameservers
        'ENGINE': 'django.db.backends.mysql',
        'USER': '$ednsUSER',
        'PASSWORD': '$ednsPASS',
        'HOST': '127.0.0.1'
    }
}
EOF

    $WORKSPACE/edns/manage.py syncdb
    $WORKSPACE/edns/manage.py migrate
    $WORKSPACE/edns/manage.py syncdb --database=bind --noinput
    $WORKSPACE/edns/manage.py migrate --database=bind

    [ $? -ne 0 ] && read -p  "Errors while executing manage.py. Do you want to continue? Y/n -  " answer
    [ "$answer" == 'n' ] && exit 1

    ednsUID=$(id -u $ednsUSER)
    ednsGID=$(id -g $ednsUSER)

    read -p "Enter IP address. Default address is set: 127.0.0.1 - " IPADDR
    IPADDR=${IPADDR:-127.0.0.1}

    sed -i 's|/^uid = .*|uid = '$ednsUID'|' "$WORKSPACE/edns/uwsgi.ini"
    sed -i 's|/^gid = .*|uid = '$ednsGID'|' "$WORKSPACE/edns/uwsgi.ini"
    sed -i 's|^http = .*|http = '$IPADDR:8080'|' "$WORKSPACE/edns/uwsgi.ini"
    sed -i 's|^virtualenv = .*|virtualenv = '$WORKSPACE/venv'|' "$WORKSPACE/edns/uwsgi.ini"
    sed -i 's|^touch-reload.*|touch-reload = '$WORKSPACE/edns/restart.txt'|' "$WORKSPACE/edns/uwsgi.ini"
    sed -i 's|^chdir = .*|chdir = '$WORKSPACE/edns'|' "$WORKSPACE/edns/uwsgi.ini"
    sed -i 's|^check-static = .*|check-static = '$WORKSPACE/edns/public'|' "$WORKSPACE/edns/uwsgi.ini"

    $WORKSPACE/edns/manage.py collectstatic
    $WORKSPACE/venv/bin/uwsgi --ini $WORKSPACE/edns/uwsgi.ini &

}

bind_rebuild()
{
    #
    # Function used to reconfigure bind
    #

    sudo apt-get install build-essential libmysqlclient-dev -y
    sudo apt-get build-dep bind9
    cd /tmp
    apt-get source bind9
    cd bind9*

    sed -ie '
    /.*--enable-threads.*/i\
    \t\t--with-dlz-mysql \\' debian/rules
    sed -i '/#ifdef DLZ/d;$d' contrib/dlz/drivers/sdlz_helper.c
    sed -i '22i\\trecursive no\;' /etc/bind/named.conf.options
    dpkg-buildpackage -rfakeroot -b

    cd ..
    dpkg -i *.deb

    cat >> /etc/bind/named.conf.local <<EOF
dlz "Mysql zone" {
   database "mysql
   {host=127.0.0.1 dbname=$BINDDB user=$BINDUSER pass=$BINDPASS}
   {select zone from dns_records where zone = '\$zone$'}
   {select ttl, type, priority, case when lower(type) = 'soa' then concat_ws(' ', data, resp_person, serial, refresh, retry, expire, minimum) else data end from dns_records where zone = '\$zone$' and host = '\$record$'}";
};
EOF
    echo
    read -p  "Please provide MySQL root password in order to create databases and grant permissions for bind: " SQLPASS
    mysql -u root -p$SQLPASS <<EOF
grant SELECT,USAGE on $BINDDB.* to '$BINDUSER'@localhost identified by '$BINDPASS';
flush privileges;
EOF
    /etc/init.d/bind9 restart

    [ $? -ne 0 ] && echo "Errors detected. I'll exit now!" && exit 1

    echo "Testing bind..."
    host enabledns.com 127.0.0.1 > /dev/null
    host -t MX enabledns.com 127.0.0.1 > /dev/null

    if [ $? -ne 0 ]; then
        echo "Errors detected. Please see above!"
        exit 1
    else
        echo "Tests completed successfully."
    fi

    if [ $UID -eq 0 ]
    then
        chown -R $ednsUSER:$ednsUSER /home/$ednsUSER/workspace
    fi
}


initial_checks
core_part
bind_rebuild


if [ $? -eq 0 ]; then
    echo "
    #######################################################################################################################################################

    Point your browser to: http://$IPADDR:8080 and you should be redirected to the API. Before performing any operations, you should create a normal user.
    You may add users by logging into the admin interface at:

    http://$IPADDR:8080/admin

    Each user will have a maximum of 5 domains he can create. You can edit user profiles and add more if you wish. There is also a 1000 record limit. That
    can be tweaked as well. The API has 3 renderer's enabled: api, json and YAML. The api renderer is a browser friendly interface that you can use to test
    the API inside the browser. The api allows 2 authentication mechanisms: session based and basic authentication (in the future maybe even OAuth).
    For testing purposes, you can login using:

    http://$IPADDR:8080/api/v1.0/api-auth/login/

    #######################################################################################################################################################
    "
fi

