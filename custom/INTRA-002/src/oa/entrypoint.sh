#!/bin/bash
echo -n "${FLAG:-FLAG{pickle_deserialization_rce}}" > /flag.txt
exec "$@"
