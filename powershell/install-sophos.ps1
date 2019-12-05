# Office Scan REG KEY
# PSChildName: OfficeScanNT
#
$temp_dir = "C:\Windows\Temp"
Start-Transcript -Path $temp_dir\installsophos.txt -Append
# Below is PSChildName for Trend Micro located in Wow6432Node
$trendmicro_id = "OfficeScanNT"
# Use Sophos Display name in case there is an update the product ID
$sophos_id = "Sophos Endpoint"
$sophos_url = "https://BUCKET-URL/SophosSetup.exe"

function GetInstalledWinApps {
    # Get installed apps from registry
    $win_apps = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*
    $win_apps += Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*
    return $win_apps
}

function FindWinApp {
    param (
        [string]$app_id
    )
    $found_app = $false
    $installed_apps = GetInstalledWinApps
    foreach($app in $installed_apps){
        if ($app.PSChildName -eq $app_id -or $app.DisplayName -eq $app_id) {
            # Write-Host $app
            $found_app = $app
        }
    }
    Return $found_app
}

$found_trendmicro = FindWinApp($trendmicro_id)
$found_sophos = FindWinApp($sophos_id)

if ( -Not($found_trendmicro) -and -Not($found_sophos)) {
    # No trend micro and Sophos. Install Sophos!
    Write-Host "Install Sophos!"
    Invoke-WebRequest $sophos_url -OutFile $temp_dir\SophosSetup.exe
    Start-Process $temp_dir\SophosSetup.exe "--quiet"
} elseif ($found_sophos) {
    # Found Sophos. Leave alone
    Write-Host "Found Sophos"
} elseif ($found_trendmicro) {
    # Found Trend Micro. Leave alone
    Write-Host "Found Trend Micro"
}
