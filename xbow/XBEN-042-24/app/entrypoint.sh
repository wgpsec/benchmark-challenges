#!/bin/bash
echo -n "${FLAG}" > /home/pedro/FLAG.txt
exec "$@"
