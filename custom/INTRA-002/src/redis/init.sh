#!/bin/bash
redis-cli SET flag "$FLAG_READABLE"
redis-cli SET admin_note "Internal cache - do not expose externally"
