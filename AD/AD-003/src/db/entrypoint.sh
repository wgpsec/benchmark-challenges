#!/bin/bash

echo -n "$FLAG" > /flag.txt
chmod 444 /flag.txt

# Find sqlcmd path
SQLCMD="/opt/mssql-tools18/bin/sqlcmd"
SQLCMD_OPTS="-C"
if [ ! -f "$SQLCMD" ]; then
    SQLCMD="/opt/mssql-tools/bin/sqlcmd"
    SQLCMD_OPTS=""
fi

/opt/mssql/bin/sqlservr &
MSSQL_PID=$!

for i in $(seq 1 90); do
    $SQLCMD -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "SELECT 1" $SQLCMD_OPTS -b > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        sleep 5
        echo "[*] SQL Server is ready, running init script..."
        $SQLCMD -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -i /opt/mssql-scripts/init.sql $SQLCMD_OPTS -b
        if [ $? -ne 0 ]; then
            echo "[!] Init failed, retrying in 10s..."
            sleep 10
            $SQLCMD -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -i /opt/mssql-scripts/init.sql $SQLCMD_OPTS -b
        fi
        # Insert dynamic flag into Secrets table
        $SQLCMD -S localhost -U sa -P "$MSSQL_SA_PASSWORD" $SQLCMD_OPTS -b -Q \
            "UPDATE CastleApp.dbo.Secrets SET value='$FLAG' WHERE key_name='db_flag'"
        echo "[*] Init complete."
        break
    fi
    sleep 2
done

wait $MSSQL_PID
