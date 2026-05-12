#!/bin/bash
echo -n "${FLAG}" > /FLAG.txt
exec "$@"
