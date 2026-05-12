#!/bin/bash
sed "s|__FLAG__|$FLAG|g" /init.sql.tpl > /docker-entrypoint-initdb.d/01-data.sql
