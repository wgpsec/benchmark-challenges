# AD-002 Workstation Setup - Join north.local domain
# 3-Phase approach:
#   Phase 1: Set hostname + reboot
#   Phase 2: Discover DC + set DNS + reboot
#   Phase 3: Join domain + enable RDP

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
Log "WS01 setup starting, phase=$phase"

# ============================================================
# PHASE 1: Set hostname + reboot
# ============================================================
if ($phase -eq "1") {
    Log "Phase 1: Setting hostname to WS01"
    Rename-Computer -NewName "WS01" -Force -ErrorAction SilentlyContinue

    "2" | Out-File -Encoding ASCII $StateFile
    schtasks /create /tn "WS-Setup" /tr "powershell -ExecutionPolicy Bypass -File C:\OEM\setup.ps1" /sc onstart /ru SYSTEM /rl HIGHEST /f
    Log "Phase 1 complete, rebooting"
    shutdown /r /t 10 /f
    exit 0
}

# ============================================================
# PHASE 2: Discover DC + configure DNS + reboot
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

    # Save DC IP for next phase
    $DcIp | Out-File -Encoding ASCII "C:\OEM\dc_ip.txt"

    "3" | Out-File -Encoding ASCII $StateFile
    Log "Phase 2 complete, rebooting with new DNS"
    shutdown /r /t 10 /f
    exit 0
}

# ============================================================
# PHASE 3: Join domain + enable RDP
# ============================================================
if ($phase -eq "3") {
    $DcIp = (Get-Content "C:\OEM\dc_ip.txt" -Raw).Trim()
    Log "Phase 3: Using DC at $DcIp"

    # Wait for domain to be resolvable
    Log "Phase 3: Waiting for north.local domain..."
    for ($i = 1; $i -le 30; $i++) {
        try {
            $resolved = Resolve-DnsName -Name "north.local" -DnsOnly -ErrorAction Stop
            Log "Phase 3: Domain resolved successfully"
            break
        } catch {
            Log "Phase 3: Domain not resolvable (attempt $i/30), waiting..."
            Start-Sleep -Seconds 10
        }
    }

    # Join domain
    Log "Phase 3: Joining north.local domain"
    try {
        $cred = New-Object System.Management.Automation.PSCredential(
            "NORTH\Administrator",
            (ConvertTo-SecureString "DsrmP@ss2024!" -AsPlainText -Force))
        Add-Computer -DomainName "north.local" -Credential $cred -Force
        Log "Phase 3: Domain join successful"
    } catch {
        Log "Phase 3: Domain join error: $_"
    }

    # Enable RDP
    Log "Phase 3: Enabling RDP"
    Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0
    Enable-NetFirewallRule -DisplayGroup "Remote Desktop" -ErrorAction SilentlyContinue

    # Cleanup
    schtasks /delete /tn "WS-Setup" /f 2>&1 | Out-Null
    "done" | Out-File -Encoding ASCII $StateFile
    "ready" | Out-File -Encoding ASCII $ReadyFile
    Log "Phase 3 complete - WS01 joined north.local!"
    shutdown /r /t 10 /f
    exit 0
}

Log "Unknown phase: $phase"
