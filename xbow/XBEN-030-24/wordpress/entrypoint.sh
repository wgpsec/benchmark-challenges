#!/bin/bash
echo -n "$FLAG" > /opt/flag.txt
exec docker-entrypoint.sh "$@"
