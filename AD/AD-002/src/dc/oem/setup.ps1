# AD-002 Domain Controller Automated Setup - north.local
# 3-Phase approach across reboots:
#   Phase 1: Install AD DS feature + rename computer + reboot
#   Phase 2: Promote to DC (Install-ADDSForest) + reboot
#   Phase 3: Create users with ACL misconfigurations + plant flags

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
    Log "Phase 1: Setting hostname to DC02"
    Rename-Computer -NewName "DC02" -Force -ErrorAction SilentlyContinue

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
    Log "Phase 2: Starting DC promotion for north.local"

    try {
        Import-Module ADDSDeployment -ErrorAction Stop
        Log "Phase 2: ADDSDeployment module loaded"
    } catch {
        Log "Phase 2: FATAL - Cannot load ADDSDeployment module: $_"
        exit 1
    }

    try {
        $promoteResult = Install-ADDSForest `
            -DomainName "north.local" `
            -DomainNetBIOSName "NORTH" `
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
# PHASE 3: Create users with ACL misconfigurations + plant flags
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

    # Create OU
    Log "Phase 3: Creating CorpUsers OU"
    try { New-ADOrganizationalUnit -Name "CorpUsers" -Path "DC=north,DC=local" } catch { Log "OU error: $_" }

    # portal_svc - initial foothold via SQLi
    Log "Phase 3: Creating portal_svc"
    try {
        New-ADUser -Name "portal_svc" -SamAccountName "portal_svc" `
            -UserPrincipalName "portal_svc@north.local" `
            -Path "OU=CorpUsers,DC=north,DC=local" `
            -AccountPassword (ConvertTo-SecureString "Portal@Svc2024!" -AsPlainText -Force) `
            -Enabled $true -PasswordNeverExpires $true `
            -Description "Web portal service account"
    } catch { Log "portal_svc error: $_" }

    # it_support - AS-REP Roasting target
    Log "Phase 3: Creating it_support (AS-REP Roasting target)"
    try {
        New-ADUser -Name "it_support" -SamAccountName "it_support" `
            -UserPrincipalName "it_support@north.local" `
            -Path "OU=CorpUsers,DC=north,DC=local" `
            -AccountPassword (ConvertTo-SecureString "ITsupport#2024" -AsPlainText -Force) `
            -Enabled $true -PasswordNeverExpires $true `
            -Description "IT support technician"
        Set-ADAccountControl -Identity "it_support" -DoesNotRequirePreAuth $true
        Log "Phase 3: it_support created with PreAuth disabled"
    } catch { Log "it_support error: $_" }

    # dev_lead - ACL chain intermediate
    Log "Phase 3: Creating dev_lead"
    try {
        New-ADUser -Name "dev_lead" -SamAccountName "dev_lead" `
            -UserPrincipalName "dev_lead@north.local" `
            -Path "OU=CorpUsers,DC=north,DC=local" `
            -AccountPassword (ConvertTo-SecureString "D3vL3ad!Str0ng" -AsPlainText -Force) `
            -Enabled $true -PasswordNeverExpires $true `
            -Description "Development team lead"
    } catch { Log "dev_lead error: $_" }

    # IT-Admins group with DCSync rights
    Log "Phase 3: Creating IT-Admins group"
    try {
        New-ADGroup -Name "IT-Admins" -GroupScope Global `
            -Path "OU=CorpUsers,DC=north,DC=local" `
            -Description "IT Administrators"
    } catch { Log "IT-Admins error: $_" }

    # ACL: it_support -> GenericAll -> dev_lead
    Log "Phase 3: Setting ACL - it_support GenericAll on dev_lead"
    try {
        $victim = Get-ADUser "dev_lead"
        $attacker = Get-ADUser "it_support"
        $acl = Get-Acl "AD:\$($victim.DistinguishedName)"
        $ace = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
            $attacker.SID, "GenericAll", "Allow")
        $acl.AddAccessRule($ace)
        Set-Acl -Path "AD:\$($victim.DistinguishedName)" -AclObject $acl
        Log "Phase 3: ACL set - it_support GenericAll on dev_lead"
    } catch { Log "ACL dev_lead error: $_" }

    # ACL: dev_lead -> WriteDACL -> IT-Admins
    Log "Phase 3: Setting ACL - dev_lead WriteDACL on IT-Admins"
    try {
        $group = Get-ADGroup "IT-Admins"
        $attacker = Get-ADUser "dev_lead"
        $acl = Get-Acl "AD:\$($group.DistinguishedName)"
        $ace = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
            $attacker.SID, "WriteDacl", "Allow")
        $acl.AddAccessRule($ace)
        Set-Acl -Path "AD:\$($group.DistinguishedName)" -AclObject $acl
        Log "Phase 3: ACL set - dev_lead WriteDACL on IT-Admins"
    } catch { Log "ACL IT-Admins error: $_" }

    # Grant IT-Admins DCSync rights
    Log "Phase 3: Granting DCSync rights to IT-Admins"
    try {
        $group = Get-ADGroup "IT-Admins"
        $domainDN = (Get-ADDomain).DistinguishedName
        $acl = Get-Acl "AD:\$domainDN"
        $guidReplChanges = [guid]"1131f6aa-9c07-11d1-f79f-00c04fc2dcd2"
        $guidReplChangesAll = [guid]"1131f6ad-9c07-11d1-f79f-00c04fc2dcd2"
        $ace1 = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
            $group.SID, "ExtendedRight", "Allow", $guidReplChanges)
        $ace2 = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
            $group.SID, "ExtendedRight", "Allow", $guidReplChangesAll)
        $acl.AddAccessRule($ace1)
        $acl.AddAccessRule($ace2)
        Set-Acl -Path "AD:\$domainDN" -AclObject $acl
        Log "Phase 3: DCSync rights granted to IT-Admins"
    } catch { Log "DCSync rights error: $_" }

    # Plant flags (use environment variables if available for dynamic flag support)
    Log "Phase 3: Planting flags"
    $flagDC = if ($env:FLAG_DC) { $env:FLAG_DC } else { "FLAG{dcsync_domain_fully_compromised}" }
    $flagASREP = if ($env:FLAG_ASREP) { $env:FLAG_ASREP } else { "FLAG{asrep_roast_it_support}" }
    $flagACL = if ($env:FLAG_ACL) { $env:FLAG_ACL } else { "FLAG{acl_chain_privilege_escalation}" }

    $flagDC | Out-File -Encoding ASCII C:\flag.txt

    $dir = "C:\Users\it_support"
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $flagASREP | Out-File -Encoding ASCII "$dir\flag.txt"

    $dir = "C:\Users\dev_lead"
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $flagACL | Out-File -Encoding ASCII "$dir\flag.txt"

    # Cleanup
    schtasks /delete /tn "AD-Setup" /f 2>&1 | Out-Null
    "done" | Out-File -Encoding ASCII $StateFile
    "ready" | Out-File -Encoding ASCII $ReadyFile
    Log "Phase 3 complete - AD-002 DC fully configured!"
    exit 0
}

Log "Unknown phase: $phase"
