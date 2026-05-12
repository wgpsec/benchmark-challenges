#!/bin/bash
echo "<?php ${FLAG} ?>" > /FLAG.php
exec "$@"
