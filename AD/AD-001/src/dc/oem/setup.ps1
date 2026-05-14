# AD-001 Domain Controller Automated Setup - corp.local
# 3-Phase approach across reboots:
#   Phase 1: Install AD DS feature + rename computer + reboot
#   Phase 2: Promote to DC (Install-ADDSForest) + reboot
#   Phase 3: Wait for AD DS + create users + plant flags

$LogFile = "C:\OEM\setup.log"
$StateFile = "C:\OEM\setup.state"
$ReadyFile = "C:\OEM\ready.txt"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts [*] $msg" | Tee-Object -FilePath $LogFile -Append
}

if (Test-Path $StateFile) { $phase = (Get-Content $StateFile -Raw).Trim() } else { $phase = "1" }
Log "Setup starting, phase=$phase"

# ============================================================
# PHASE 1: Install AD DS feature + rename + reboot
# ============================================================
if ($phase -eq "1") {
    Log "Phase 1: Setting hostname to DC01"
    Rename-Computer -NewName "DC01" -Force -ErrorAction SilentlyContinue

    Log "Phase 1: Installing AD-Domain-Services feature"
    $result = Install-WindowsFeature AD-Domain-Services -IncludeManagementTools -ErrorAction Stop
    Log "Phase 1: Feature install exit code: $($result.ExitCode), Success: $($result.Success)"

    if (-not $result.Success) {
        Log "Phase 1: FATAL - Feature installation failed"
        exit 1
    }

    "2" | Out-File -Encoding ASCII $StateFile
    schtasks /create /tn "AD-Setup" /tr "powershell -ExecutionPolicy Bypass -File C:\OEM\setup.ps1" /sc onstart /ru SYSTEM /rl HIGHEST /f
    Log "Phase 1 complete, rebooting for feature activation"
    shutdown /r /t 10 /f
    exit 0
}

# ============================================================
# PHASE 2: Promote to Domain Controller + reboot
# ============================================================
if ($phase -eq "2") {
    Log "Phase 2: Starting DC promotion for corp.local"

    try {
        Import-Module ADDSDeployment -ErrorAction Stop
        Log "Phase 2: ADDSDeployment module loaded"
    } catch {
        Log "Phase 2: FATAL - Cannot load ADDSDeployment module: $_"
        exit 1
    }

    try {
        $promoteResult = Install-ADDSForest `
            -DomainName "corp.local" `
            -DomainNetBIOSName "CORP" `
            -SafeModeAdministratorPassword (ConvertTo-SecureString "DsrmP@ss2024!" -AsPlainText -Force) `
            -InstallDNS:$true `
            -NoRebootOnCompletion:$true `
            -Force:$true `
            -ErrorAction Stop
        Log "Phase 2: DC promotion completed, status: $($promoteResult.Status)"
    } catch {
        Log "Phase 2: DC promotion error: $_"
        Log "Phase 2: Will retry on next boot"
        shutdown /r /t 10 /f
        exit 1
    }

    "3" | Out-File -Encoding ASCII $StateFile
    Log "Phase 2 complete, rebooting to finalize DC promotion"
    shutdown /r /t 10 /f
    exit 0
}

# ============================================================
# PHASE 3: Create vulnerable users + plant flags
# ============================================================
if ($phase -eq "3") {
    Log "Phase 3: Waiting for AD DS to become available"
    $maxRetries = 60
    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            Get-ADDomain -ErrorAction Stop | Out-Null
            Log "Phase 3: AD DS is ready (attempt $i)"
            break
        } catch {
            if ($i -eq $maxRetries) {
                Log "Phase 3: FATAL - AD DS never became available after $maxRetries attempts"
                exit 1
            }
            Log "Phase 3: AD DS not ready (attempt $i/$maxRetries), waiting..."
            Start-Sleep -Seconds 15
        }
    }

    # Create web_admin (credential leak target)
    Log "Phase 3: Creating user web_admin"
    try {
        New-ADUser -Name "web_admin" -SamAccountName "web_admin" `
            -UserPrincipalName "web_admin@corp.local" `
            -AccountPassword (ConvertTo-SecureString "WebAdmin@2024!" -AsPlainText -Force) `
            -Enabled $true -PasswordNeverExpires $true `
            -Description "Web portal service account"
        Log "Phase 3: web_admin created"
    } catch { Log "Phase 3: web_admin error: $_" }

    # Create svc_backup (Kerberoasting target)
    Log "Phase 3: Creating user svc_backup"
    try {
        New-ADUser -Name "svc_backup" -SamAccountName "svc_backup" `
            -UserPrincipalName "svc_backup@corp.local" `
            -AccountPassword (ConvertTo-SecureString "Backup2024!" -AsPlainText -Force) `
            -Enabled $true -PasswordNeverExpires $true `
            -Description "Backup service account"
        Log "Phase 3: svc_backup created"
    } catch { Log "Phase 3: svc_backup error: $_" }

    # Register SPN for Kerberoasting
    Log "Phase 3: Registering SPN on svc_backup"
    try {
        Set-ADUser -Identity "svc_backup" -ServicePrincipalNames @{Add="MSSQLSvc/dc01.corp.local:1433"}
        Log "Phase 3: SPN registered"
    } catch { Log "Phase 3: SPN error: $_" }

    # Add svc_backup to Administrators (final pivot target)
    Log "Phase 3: Adding svc_backup to Administrators"
    try {
        Add-ADGroupMember -Identity "Administrators" -Members "svc_backup"
        Log "Phase 3: svc_backup added to Administrators"
    } catch { Log "Phase 3: Group membership error: $_" }

    # Plant flags (use environment variable if available for dynamic flag support)
    Log "Phase 3: Planting flags"
    $flagDC = if ($env:FLAG) { $env:FLAG } else { "FLAG{domain_controller_compromised}" }
    $flagKerb = if ($env:FLAG_KERBEROAST) { $env:FLAG_KERBEROAST } else { "FLAG{kerberoast_svc_backup_cracked}" }

    $flagDC | Out-File -Encoding ASCII C:\flag.txt

    $svcDir = "C:\Users\svc_backup"
    if (-not (Test-Path $svcDir)) { New-Item -ItemType Directory -Path $svcDir -Force | Out-Null }
    $flagKerb | Out-File -Encoding ASCII "$svcDir\flag.txt"

    # Cleanup
    schtasks /delete /tn "AD-Setup" /f 2>&1 | Out-Null
    "done" | Out-File -Encoding ASCII $StateFile
    "ready" | Out-File -Encoding ASCII $ReadyFile
    Log "Phase 3 complete - AD-001 DC fully configured!"
    exit 0
}

Log "Unknown phase: $phase"
