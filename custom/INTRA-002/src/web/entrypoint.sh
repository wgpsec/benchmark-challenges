#!/bin/bash
echo -n "$FLAG" > /flag.txt
exec "$@"
