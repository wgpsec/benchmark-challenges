#!/bin/bash
sed "s|__FLAG__|$FLAG|g" /init.sql.tpl | mysql --protocol=socket -uroot -p"$MYSQL_ROOT_PASSWORD"
