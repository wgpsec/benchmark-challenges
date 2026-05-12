#!/bin/bash
echo -n "$FLAG" > /tmp/flag
exec "$@"
