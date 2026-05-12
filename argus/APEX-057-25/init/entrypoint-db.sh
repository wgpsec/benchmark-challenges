#!/bin/bash
sed "s|__FLAG__|${FLAG:-FLAG{mult1_t3n4nt_1s0l4t10n_f41lur3_t3n4nt_3sc4p3}}|g" /init.sql.tpl > /docker-entrypoint-initdb.d/01-data.sql
exec docker-entrypoint.sh "$@"
