#!/bin/bash
echo -n "${FLAG}" > /app/FLAG.txt
exec "$@"
