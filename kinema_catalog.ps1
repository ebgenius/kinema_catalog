<#
.SYNOPSIS
  kinema_catalog launcher for Windows.

.DESCRIPTION
  Docker Desktop's own WSL distro has no GUI stack, so this wrapper runs the real
  launcher (kinema_catalog.sh) inside your Ubuntu-style WSL distro, where WSLg
  provides the X/Wayland display that RViz and Gazebo draw on.

  Every argument is forwarded verbatim:

    .\kinema_catalog.ps1                    interactive picker
    .\kinema_catalog.ps1 --list
    .\kinema_catalog.ps1 ur5e
    .\kinema_catalog.ps1 go2 -v gz
    .\kinema_catalog.ps1 fr3 -d humble

  Use -WslDistro to target a specific distro when you have more than one.

  To target a specific distro when you have more than one, pass -WslDistro <name>.

.NOTES
  This script deliberately declares no param() block and reads $args directly.
  A typed parameter would bind the first positional argument ('spot') as the
  distro name, and [CmdletBinding()] would swallow '-v' as an alias of -Verbose,
  mangling '-v gz'. Reading $args keeps every argument verbatim for the Linux
  launcher, which is the only thing that should be parsing them.
#>

$ErrorActionPreference = 'Stop'

# Pull out our own -WslDistro; everything else is forwarded untouched.
$WslDistro = $null
$forwardArgs = @()
for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -in @('-WslDistro', '--wsl-distro')) {
        if ($i + 1 -ge $args.Count) {
            Write-Host "error: $($args[$i]) needs a distro name" -ForegroundColor Red
            exit 1
        }
        $WslDistro = $args[$i + 1]
        $i++
    }
    else {
        $forwardArgs += $args[$i]
    }
}

function Write-Info { param([string]$m) Write-Host "==> $m" -ForegroundColor Cyan }
function Write-Warn { param([string]$m) Write-Host "warning: $m" -ForegroundColor Yellow }
function Die {
    param([string]$m)
    Write-Host "error: $m" -ForegroundColor Red
    exit 1
}

# --------------------------------------------------------------------- wsl checks
if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    Die "WSL is not installed. Install it with:  wsl --install -d Ubuntu"
}

# `wsl -l -q` emits UTF-16LE; normalise to clean strings.
$rawList = & wsl.exe -l -q 2>$null
$distros = @($rawList | ForEach-Object { ($_ -replace "`0", '').Trim() } | Where-Object { $_ })

if (-not $distros) {
    Die "No WSL distros installed. Install one with:  wsl --install -d Ubuntu"
}

if (-not $WslDistro) {
    # Prefer the default distro, but never the Docker Desktop helper distros:
    # they ship no GUI libraries and no WSLg socket.
    $usable = @($distros | Where-Object { $_ -notmatch '^docker-desktop' })
    if (-not $usable) {
        Die "Only Docker Desktop's helper distros are installed; they cannot display a GUI. Install a normal distro:  wsl --install -d Ubuntu"
    }
    $WslDistro = $usable[0]
}
elseif ($distros -notcontains $WslDistro) {
    Die "WSL distro '$WslDistro' not found. Available: $($distros -join ', ')"
}

Write-Info "using WSL distro: $WslDistro"

# --------------------------------------------------------------- path translation
$repoRoot = $PSScriptRoot
$wslPath = (& wsl.exe -d $WslDistro -e wslpath -a "$repoRoot" 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $wslPath) {
    Die "Could not translate '$repoRoot' into a WSL path."
}
$wslPath = ($wslPath -replace "`0", '').Trim()

# ------------------------------------------------------------------ docker check
& wsl.exe -d $WslDistro -e bash -lc "command -v docker >/dev/null 2>&1" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Die @"
docker is not available inside WSL distro '$WslDistro'.

Enable it in Docker Desktop:
  Settings -> Resources -> WSL integration -> turn on '$WslDistro' -> Apply & restart
"@
}

& wsl.exe -d $WslDistro -e bash -lc "docker info >/dev/null 2>&1" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Die "The docker daemon is not reachable from WSL. Start Docker Desktop and try again."
}

# ------------------------------------------------------------------ wslg warning
& wsl.exe -d $WslDistro -e bash -lc "test -d /mnt/wslg" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warn "WSLg (/mnt/wslg) not detected — the GUI may not appear. Update WSL with:  wsl --update"
}

# ------------------------------------------------------------------------- launch
# Quote each argument for bash so things like 'ur_type:=ur5e' survive intact.
$forwarded = ($forwardArgs | ForEach-Object { "'" + ($_ -replace "'", "'\''") + "'" }) -join ' '
$command = "cd '$wslPath' && bash ./kinema_catalog.sh $forwarded"

& wsl.exe -d $WslDistro -e bash -lc $command
exit $LASTEXITCODE
