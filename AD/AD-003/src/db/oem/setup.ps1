# AD-003 Database Server Setup - castle.local
# 3-Phase approach:
#   Phase 1: Set hostname + reboot
#   Phase 2: Discover DC + set DNS + join domain + reboot
#   Phase 3: Install MSSQL + enable xp_cmdshell + plant flags

$LogFile = "C:\OEM\setup.log"
$StateFile = "C:\OEM\setup.state"
$ReadyFile = "C:\OEM\ready.txt"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts [*] $msg" | Tee-Object -FilePath $LogFile -Append
}

function Find-DomainController {
    Log "Discovering DC on local subnet..."
    $adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -ne "127.0.0.1" -and $_.PrefixOrigin -ne "WellKnown" }
    foreach ($adapter in $adapters) {
        $ip = $adapter.IPAddress
        $prefix = $adapter.PrefixLength
        $parts = $ip.Split(".")
        $subnet = "$($parts[0]).$($parts[1]).$($parts[2])"
        Log "Scanning subnet $subnet.0/$prefix for DC (port 389/LDAP)..."
        for ($i = 1; $i -le 254; $i++) {
            $target = "$subnet.$i"
            if ($target -eq $ip) { continue }
            try {
                $tcp = New-Object System.Net.Sockets.TcpClient
                $result = $tcp.BeginConnect($target, 389, $null, $null)
                $wait = $result.AsyncWaitHandle.WaitOne(500, $false)
                if ($wait -and $tcp.Connected) {
                    $tcp.Close()
                    Log "Found DC at $target (LDAP responding)"
                    return $target
                }
                $tcp.Close()
            } catch {}
        }
    }
    return $null
}

if (Test-Path $StateFile) { $phase = (Get-Content $StateFile -Raw).Trim() } else { $phase = "1" }
Log "DB01 setup starting, phase=$phase"

# ============================================================
# PHASE 1: Set hostname + reboot
# ============================================================
if ($phase -eq "1") {
    Log "Phase 1: Setting hostname to DB01"
    Rename-Computer -NewName "DB01" -Force -ErrorAction SilentlyContinue

    "2" | Out-File -Encoding ASCII $StateFile
    schtasks /create /tn "DB-Setup" /tr "powershell -ExecutionPolicy Bypass -File C:\OEM\setup.ps1" /sc onstart /ru SYSTEM /rl HIGHEST /f
    Log "Phase 1 complete, rebooting"
    shutdown /r /t 10 /f
    exit 0
}

# ============================================================
# PHASE 2: Discover DC + join domain + reboot
# ============================================================
if ($phase -eq "2") {
    Log "Phase 2: Waiting for DC to become available..."
    $DcIp = $null
    for ($attempt = 1; $attempt -le 60; $attempt++) {
        $DcIp = Find-DomainController
        if ($DcIp) { break }
        Log "Phase 2: DC not found (attempt $attempt/60), waiting 30s..."
        Start-Sleep -Seconds 30
    }

    if (-not $DcIp) {
        Log "Phase 2: FATAL - Could not find DC after 60 attempts"
        exit 1
    }

    Log "Phase 2: Setting DNS to DC at $DcIp"
    Get-NetAdapter | Set-DnsClientServerAddress -ServerAddresses @($DcIp)

    # Save DC IP for reference
    $DcIp | Out-File -Encoding ASCII "C:\OEM\dc_ip.txt"

    # Wait for domain to be resolvable
    Log "Phase 2: Waiting for castle.local domain..."
    for ($i = 1; $i -le 30; $i++) {
        try {
            Resolve-DnsName -Name "castle.local" -DnsOnly -ErrorAction Stop | Out-Null
            Log "Phase 2: Domain resolved"
            break
        } catch {
            Log "Phase 2: Domain not resolvable (attempt $i/30), waiting..."
            Start-Sleep -Seconds 10
        }
    }

    # Join domain
    Log "Phase 2: Joining castle.local domain"
    try {
        $cred = New-Object System.Management.Automation.PSCredential(
            "CASTLE\Administrator",
            (ConvertTo-SecureString "DsrmP@ss2024!" -AsPlainText -Force))
        Add-Computer -DomainName "castle.local" -Credential $cred -Force
        Log "Phase 2: Domain join successful"
    } catch { Log "Phase 2: Domain join error: $_" }

    "3" | Out-File -Encoding ASCII $StateFile
    Log "Phase 2 complete, rebooting after domain join"
    shutdown /r /t 10 /f
    exit 0
}

# ============================================================
# PHASE 3: Install MSSQL + enable xp_cmdshell + plant flags
# ============================================================
if ($phase -eq "3") {
    Log "Phase 3: Starting MSSQL installation"

    # Download MSSQL Express
    Log "Phase 3: Downloading MSSQL Express"
    $downloaded = $false
    for ($retry = 1; $retry -le 3; $retry++) {
        try {
            $url = "https://go.microsoft.com/fwlink/p/?linkid=2216019&clcid=0x409&culture=en-us&country=us"
            Invoke-WebRequest -Uri $url -OutFile "C:\OEM\SQLEXPR_x64.exe" -UseBasicParsing -TimeoutSec 300
            if ((Get-Item "C:\OEM\SQLEXPR_x64.exe").Length -gt 1MB) {
                $downloaded = $true
                Log "Phase 3: MSSQL download complete"
                break
            }
        } catch {
            Log "Phase 3: Download attempt $retry failed: $_"
            Start-Sleep -Seconds 30
        }
    }

    if ($downloaded) {
        # Install MSSQL Express
        Log "Phase 3: Installing MSSQL Express"
        $sqlArgs = '/Q /IACCEPTSQLSERVERLICENSETERMS /ACTION=Install /FEATURES=SQLEngine /INSTANCENAME=MSSQLSERVER /SQLSVCACCOUNT="CASTLE\svc_sql" /SQLSVCPASSWORD="SqlSvc@2024!" /SECURITYMODE=SQL /SAPWD="sa123456" /SQLSYSADMINACCOUNTS="CASTLE\Administrator" /TCPENABLED=1'
        Start-Process -FilePath "C:\OEM\SQLEXPR_x64.exe" -ArgumentList $sqlArgs -Wait -NoNewWindow
        Log "Phase 3: MSSQL installation complete"

        # Wait for SQL Server to start
        Log "Phase 3: Waiting for SQL Server service..."
        for ($i = 1; $i -le 12; $i++) {
            $svc = Get-Service -Name "MSSQLSERVER" -ErrorAction SilentlyContinue
            if ($svc -and $svc.Status -eq "Running") {
                Log "Phase 3: SQL Server is running"
                break
            }
            Start-Sleep -Seconds 10
        }

        # Enable xp_cmdshell
        Log "Phase 3: Enabling xp_cmdshell"
        try {
            Import-Module SqlServer -ErrorAction SilentlyContinue
            Invoke-Sqlcmd -Query "EXEC sp_configure 'show advanced options', 1; RECONFIGURE;" -ServerInstance "localhost"
            Invoke-Sqlcmd -Query "EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;" -ServerInstance "localhost"
            Log "Phase 3: xp_cmdshell enabled"
        } catch { Log "Phase 3: xp_cmdshell error: $_" }
    } else {
        Log "Phase 3: WARNING - MSSQL download failed, skipping installation"
    }

    # Plant flags (use environment variables if available for dynamic flag support)
    Log "Phase 3: Planting flags"
    $flagXP = if ($env:FLAG) { $env:FLAG } else { "FLAG{xp_cmdshell_rce_on_db}" }
    $flagADCS = if ($env:FLAG_ADCS) { $env:FLAG_ADCS } else { "FLAG{adcs_esc1_cert_forged}" }

    $flagXP | Out-File -Encoding ASCII C:\flag.txt
    $flagADCS | Out-File -Encoding ASCII C:\Users\Public\adcs_flag.txt

    # Cleanup
    schtasks /delete /tn "DB-Setup" /f 2>&1 | Out-Null
    "done" | Out-File -Encoding ASCII $StateFile
    "ready" | Out-File -Encoding ASCII $ReadyFile
    Log "Phase 3 complete - DB01 fully configured!"
    shutdown /r /t 10 /f
    exit 0
}

Log "Unknown phase: $phase"
