# AD-003 Domain Controller + ADCS Setup - castle.local
# 3-Phase approach across reboots:
#   Phase 1: Install AD DS + ADCS features + rename + reboot
#   Phase 2: Promote to DC (Install-ADDSForest) + reboot
#   Phase 3: Install ADCS CA + configure ESC1 vulnerable template + create users + plant flags

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
# PHASE 1: Install features + rename + reboot
# ============================================================
if ($phase -eq "1") {
    Log "Phase 1: Setting hostname to DC03"
    Rename-Computer -NewName "DC03" -Force -ErrorAction SilentlyContinue

    Log "Phase 1: Installing AD-Domain-Services feature"
    $result = Install-WindowsFeature AD-Domain-Services -IncludeManagementTools -ErrorAction Stop
    Log "Phase 1: AD DS feature: ExitCode=$($result.ExitCode), Success=$($result.Success)"

    Log "Phase 1: Installing AD-Certificate feature"
    $result2 = Install-WindowsFeature AD-Certificate -IncludeManagementTools -ErrorAction Stop
    Log "Phase 1: ADCS feature: ExitCode=$($result2.ExitCode), Success=$($result2.Success)"

    if (-not $result.Success) {
        Log "Phase 1: FATAL - AD DS feature installation failed"
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
    Log "Phase 2: Starting DC promotion for castle.local"

    try {
        Import-Module ADDSDeployment -ErrorAction Stop
        Log "Phase 2: ADDSDeployment module loaded"
    } catch {
        Log "Phase 2: FATAL - Cannot load ADDSDeployment module: $_"
        exit 1
    }

    try {
        $promoteResult = Install-ADDSForest `
            -DomainName "castle.local" `
            -DomainNetBIOSName "CASTLE" `
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
# PHASE 3: Install ADCS + configure ESC1 + create users + flags
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

    # Create svc_sql user
    Log "Phase 3: Creating svc_sql"
    try {
        New-ADUser -Name "svc_sql" -SamAccountName "svc_sql" `
            -UserPrincipalName "svc_sql@castle.local" `
            -AccountPassword (ConvertTo-SecureString "SqlSvc@2024!" -AsPlainText -Force) `
            -Enabled $true -PasswordNeverExpires $true `
            -Description "MSSQL service account"
        Set-ADUser -Identity "svc_sql" -ServicePrincipalNames @{Add="MSSQLSvc/DB01.castle.local:1433"}
        Log "Phase 3: svc_sql created with SPN"
    } catch { Log "svc_sql error: $_" }

    # Install ADCS Certification Authority
    Log "Phase 3: Installing ADCS Certification Authority"
    try {
        Install-AdcsCertificationAuthority `
            -CAType EnterpriseRootCA `
            -CACommonName "castle-DC03-CA" `
            -KeyLength 2048 `
            -HashAlgorithmName SHA256 `
            -CryptoProviderName "RSA#Microsoft Software Key Storage Provider" `
            -ValidityPeriod Years `
            -ValidityPeriodUnits 5 `
            -Force
        Log "Phase 3: ADCS CA installed successfully"
    } catch { Log "ADCS CA error: $_" }

    # Configure ESC1 vulnerable template
    Log "Phase 3: Creating ESC1 vulnerable certificate template"
    try {
        $configNC = ([ADSI]"LDAP://RootDSE").configurationNamingContext
        $templateDN = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"
        $container = [ADSI]"LDAP://$templateDN"
        $newTemplate = $container.Create("pKICertificateTemplate", "CN=VulnTemplate")

        $newTemplate.Put("displayName", "VulnTemplate")
        $newTemplate.Put("flags", 131680)
        $newTemplate.Put("pKIDefaultKeySpec", 1)
        $newTemplate.Put("pKIMaxIssuingDepth", 0)
        $newTemplate.Put("pKICriticalExtensions", @("2.5.29.15"))
        $newTemplate.Put("pKIExtendedKeyUsage", @("1.3.6.1.5.5.7.3.2"))
        $newTemplate.Put("msPKI-Template-Schema-Version", 2)
        $newTemplate.Put("msPKI-Template-Minor-Revision", 1)
        $newTemplate.Put("msPKI-RA-Signature", 0)
        $newTemplate.Put("msPKI-Enrollment-Flag", 0)
        $newTemplate.Put("msPKI-Private-Key-Flag", 16842768)
        # ESC1: CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT - allows attacker to specify any SAN
        $newTemplate.Put("msPKI-Certificate-Name-Flag", 1)
        $newTemplate.SetInfo()

        # Grant Authenticated Users enrollment rights
        $authUsers = New-Object System.Security.Principal.SecurityIdentifier("S-1-5-11")
        $enrollGuid = [Guid]"0e10c968-78fb-11d2-90d4-00c04f79dc55"
        $ace = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
            $authUsers, "ExtendedRight", "Allow", $enrollGuid)
        $newTemplate.ObjectSecurity.AddAccessRule($ace)
        $newTemplate.CommitChanges()

        # Publish template to CA
        $caContainer = [ADSI]"LDAP://CN=castle-DC03-CA,CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"
        $existing = @($caContainer.Properties["certificateTemplates"].Value)
        $existing += "VulnTemplate"
        $caContainer.Put("certificateTemplates", $existing)
        $caContainer.SetInfo()
        Log "Phase 3: ESC1 VulnTemplate created and published"
    } catch { Log "ESC1 template error: $_" }

    # Plant flags (read from OEM flags file injected by platform)
    Log "Phase 3: Planting flags"
    $flagsFile = "C:\OEM\flags.env"
    $flagVars = @{}
    if (Test-Path $flagsFile) {
        Get-Content $flagsFile | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') { $flagVars[$Matches[1]] = $Matches[2] }
        }
        Log "Phase 3: Loaded flags from $flagsFile"
    } else {
        Log "Phase 3: WARNING - $flagsFile not found, using fallback"
    }
    $flagDC = if ($flagVars["FLAG_DC"]) { $flagVars["FLAG_DC"] } else { "FLAG{domain_admin_via_certificate}" }
    $flagXP = if ($flagVars["FLAG_XPCMD"]) { $flagVars["FLAG_XPCMD"] } else { "FLAG{xp_cmdshell_rce_on_db}" }
    $flagADCS = if ($flagVars["FLAG_ADCS"]) { $flagVars["FLAG_ADCS"] } else { "FLAG{adcs_esc1_cert_forged}" }

    $flagDC | Out-File -Encoding ASCII C:\flag.txt
    $flagADCS | Out-File -Encoding ASCII C:\Users\Public\adcs_flag.txt

    # Disable firewall so AD ports (88/389/445/etc.) are reachable from the Docker network
    Log "Phase 3: Disabling Windows Firewall"
    Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled False

    # Cleanup
    schtasks /delete /tn "AD-Setup" /f 2>&1 | Out-Null
    "done" | Out-File -Encoding ASCII $StateFile
    "ready" | Out-File -Encoding ASCII $ReadyFile
    Log "Phase 3 complete - AD-003 DC+ADCS fully configured!"
    exit 0
}

Log "Unknown phase: $phase"
