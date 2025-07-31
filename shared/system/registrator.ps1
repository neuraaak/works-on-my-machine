## ////////////////
## Enhanced Windows Context Menu Registrator for Works On My Machine
## PowerShell Version with improved functionality
## ////////////////

# Script type detection and configuration
class ScriptType {
    static [hashtable] $Extensions = @{
        '.py' = 'python'
        '.ps1' = 'powershell'
        '.bat' = 'batch'
        '.cmd' = 'batch'
        '.exe' = 'executable'
    }

    static [hashtable] $Icons = @{
        'python' = 'C:\Windows\py.exe'
        'powershell' = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        'batch' = 'C:\Windows\System32\cmd.exe'
        'executable' = $null
    }

    static [string] DetectType([string]$filePath) {
        $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
        if ([ScriptType]::Extensions.ContainsKey($ext)) {
            return [ScriptType]::Extensions[$ext]
        }
        return 'executable'
    }

    static [string] GetDefaultIcon([string]$scriptType) {
        return [ScriptType]::Icons[$scriptType]
    }

    static [string] BuildCommand([string]$scriptType, [string]$scriptPath) {
        $result = switch ($scriptType) {
            'python' {
                $pythonExe = (Get-Command python -ErrorAction SilentlyContinue) ?? 
                            (Get-Command python3 -ErrorAction SilentlyContinue) ?? 
                            (Get-Command py -ErrorAction SilentlyContinue)
                if ($pythonExe) {
                    "`"$($pythonExe.Source)`" `"$scriptPath`" `"%V`""
                } else {
                    "py `"$scriptPath`" `"%V`""
                }
            }
            'powershell' {
                "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`" `"%V`""
            }
            'batch' {
                "cmd.exe /c `"$scriptPath`" `"%V`""
            }
            'executable' {
                "`"$scriptPath`" `"%V`""
            }
            default {
                "`"$scriptPath`" `"%V`""
            }
        }
        return $result
    }
}

# Generate enhanced registry key name
function Get-RegistryKeyName {
    param ([string]$filePath)

    # Get the file name without the extension
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($filePath)

    # Replace underscores and hyphens with spaces and split
    $fileName = $fileName -replace '_|=-', ' '
    $parts = $fileName -split ' ' | Where-Object { $_ -ne '' }

    # Convert to camelCase
    if ($parts.Count -gt 0) {
        $registryKey = $parts[0].ToLower()
        for ($i = 1; $i -lt $parts.Count; $i++) {
            if ($parts[$i]) {
                $registryKey += $parts[$i].Substring(0,1).ToUpper() + $parts[$i].Substring(1).ToLower()
            }
        }
    } else {
        $registryKey = "worksOnMyMachine"
    }

    # Add prefix for Works On My Machine if not already present
    if (-not ($registryKey.StartsWith("works") -or $registryKey.StartsWith("dev"))) {
        $registryKey = "wom" + $registryKey.Substring(0,1).ToUpper() + $registryKey.Substring(1)
    }

    return $registryKey.Trim()
}

# Validate script path
function Test-ScriptPath {
    param ([string]$scriptPath)
    
    if (-not (Test-Path $scriptPath)) {
        Write-Host "❌ Script file does not exist: $scriptPath" -ForegroundColor Red
        return $false
    }
    
    if (-not (Test-Path $scriptPath -PathType Leaf)) {
        Write-Host "❌ Path is not a file: $scriptPath" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Validate and normalize icon path
function Resolve-IconPath {
    param ([string]$iconInput, [string]$scriptType)
    
    switch ($iconInput.ToLower()) {
        { $_ -in @('powershell', 'ps') } {
            return 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        }
        { $_ -in @('python', 'py') } {
            return 'C:\Windows\py.exe'
        }
        { $_ -in @('cmd', 'batch') } {
            return 'C:\Windows\System32\cmd.exe'
        }
        'auto' {
            return [ScriptType]::GetDefaultIcon($scriptType)
        }
        default {
            if (Test-Path $iconInput) {
                return $iconInput
            } else {
                Write-Host "⚠️  Icon not found: $iconInput" -ForegroundColor Yellow
                return [ScriptType]::GetDefaultIcon($scriptType)
            }
        }
    }
}

# Enhanced function to add registry entries
function Add-ContextMenuEntry {
    param (
        [string]$regPath,
        [string]$command,
        [string]$muiverb,
        [string]$iconPath
    )
    
    try {
        New-Item -Path $regPath -Force | Out-Null
        
        if ($iconPath) {
            New-ItemProperty -Path $regPath -Name "Icon" -Value $iconPath -Force | Out-Null
        }
        New-ItemProperty -Path $regPath -Name "MUIVerb" -Value $muiverb -Force | Out-Null
        
        $commandPath = "$regPath\command"
        New-Item -Path $commandPath -Force | Out-Null
        Set-ItemProperty -Path $commandPath -Name "(Default)" -Value $command
        
        return $true
    }
    catch {
        Write-Host "❌ Error adding registry entry: $_" -ForegroundColor Red
        return $false
    }
}

# List existing context menu entries
function Show-ContextMenuEntries {
    Write-Host "📋 Existing Context Menu Entries:" -ForegroundColor Cyan
    
    $pathsToCheck = @(
        "Registry::HKEY_CURRENT_USER\Software\Classes\Directory\shell",
        "Registry::HKEY_CURRENT_USER\Software\Classes\Directory\background\shell"
    )
    
    foreach ($basePath in $pathsToCheck) {
        Write-Host "`n📁 $basePath" -ForegroundColor Yellow
        
        if (Test-Path $basePath) {
            $entries = Get-ChildItem $basePath -ErrorAction SilentlyContinue
            if ($entries) {
                foreach ($entry in $entries) {
                    $muiVerb = Get-ItemProperty -Path $entry.PSPath -Name "MUIVerb" -ErrorAction SilentlyContinue
                    if ($muiVerb) {
                        Write-Host "   ✓ $($entry.PSChildName) - $($muiVerb.MUIVerb)" -ForegroundColor Green
                    } else {
                        Write-Host "   • $($entry.PSChildName)" -ForegroundColor Gray
                    }
                }
            } else {
                Write-Host "   (no entries)" -ForegroundColor Gray
            }
        } else {
            Write-Host "   (path not found)" -ForegroundColor Gray
        }
    }
}

# Remove context menu entry
function Remove-ContextMenuEntry {
    param ([string]$keyName)
    
    $pathsToRemove = @(
        "Registry::HKEY_CURRENT_USER\Software\Classes\Directory\shell\$keyName",
        "Registry::HKEY_CURRENT_USER\Software\Classes\Directory\background\shell\$keyName"
    )
    
    $removed = 0
    foreach ($path in $pathsToRemove) {
        if (Test-Path $path) {
            try {
                Remove-Item -Path "$path\command" -Force -ErrorAction SilentlyContinue
                Remove-Item -Path $path -Force
                Write-Host "✅ Removed: $path" -ForegroundColor Green
                $removed++
            }
            catch {
                Write-Host "❌ Error removing $path : $_" -ForegroundColor Red
            }
        }
    }
    
    if ($removed -eq 0) {
        Write-Host "⚠️  No entries found with key: $keyName" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Removed $removed context menu entries" -ForegroundColor Green
    }
}

## ////////////////
## => MAIN SCRIPT
## ////////////////

param(
    [string]$ScriptPath,
    [string]$MuiVerb,
    [string]$IconInput = "auto",
    [switch]$List,
    [switch]$Remove,
    [string]$RemoveKey,
    [switch]$Interactive,
    [switch]$DryRun,
    [switch]$Help
)

# Show help
if ($Help -or $args.Contains("--help") -or $args.Contains("-h")) {
    Write-Host @"
Enhanced Windows Context Menu Registrator for Works On My Machine
PowerShell Version

Usage:
  .\registrator.ps1 "script_path" "Action Title" ["icon_path"]
  .\registrator.ps1 -List
  .\registrator.ps1 -Remove -RemoveKey "keyName"
  .\registrator.ps1 -Interactive

Examples:
  .\registrator.ps1 "C:\tools\my_script.py" "My Python Action"
  .\registrator.ps1 "C:\tools\script.ps1" "PowerShell Action" "powershell"
  .\registrator.ps1 "C:\tools\deploy.bat" "Deploy Project" "auto"
  .\registrator.ps1 -List
  .\registrator.ps1 -Remove -RemoveKey "womMyScript"

Options:
  -List           : List existing context menu entries
  -Remove         : Remove context menu entry
  -RemoveKey      : Key name to remove
  -Interactive    : Interactive mode
  -DryRun         : Show what would be done without making changes
  -Help           : Show this help message

Icon options: auto, powershell, python, cmd, or full path to icon file
"@ -ForegroundColor Cyan
    exit 0
}

# List mode
if ($List) {
    Show-ContextMenuEntries
    exit 0
}

# Remove mode
if ($Remove -and $RemoveKey) {
    if ($DryRun) {
        Write-Host "🔍 Would remove context menu entry: $RemoveKey" -ForegroundColor Yellow
    } else {
        Remove-ContextMenuEntry -keyName $RemoveKey
    }
    exit 0
}

# Interactive mode or missing parameters
if ($Interactive -or (-not $ScriptPath -or -not $MuiVerb)) {
    if (-not $ScriptPath) {
        $ScriptPath = Read-Host "Enter the full path to the script or executable"
    }
    if (-not $MuiVerb) {
        $MuiVerb = Read-Host "Enter the action title for the context menu"
    }
    if (-not $IconInput -or $IconInput -eq "auto") {
        $IconInput = Read-Host "Enter icon type (auto/powershell/python/cmd) or path [auto]"
        if (-not $IconInput) { $IconInput = "auto" }
    }
}

# Validate script path
if (-not (Test-ScriptPath -scriptPath $ScriptPath)) {
    exit 1
}

# Auto-detect script type
$scriptType = [ScriptType]::DetectType($ScriptPath)

# Resolve icon path
$iconPath = Resolve-IconPath -iconInput $IconInput -scriptType $scriptType

# Generate registry key name
$registryKeyName = Get-RegistryKeyName -filePath $ScriptPath

# Create registry paths
$regPathFile = "Registry::HKEY_CURRENT_USER\Software\Classes\Directory\shell\$registryKeyName"
$regPathDirectory = "Registry::HKEY_CURRENT_USER\Software\Classes\Directory\background\shell\$registryKeyName"

# Build appropriate command
$command = [ScriptType]::BuildCommand($scriptType, $ScriptPath)

# Display configuration
Write-Host "🔧 Adding to Windows Context Menu" -ForegroundColor Cyan
Write-Host "📜 Script: $ScriptPath" -ForegroundColor White
Write-Host "🎯 Type: $scriptType" -ForegroundColor White
Write-Host "🏷️  Title: $MuiVerb" -ForegroundColor White
Write-Host "🎨 Icon: $($iconPath ?? 'Default file icon')" -ForegroundColor White
Write-Host "🔑 Registry Key: $registryKeyName" -ForegroundColor White
Write-Host "⚡ Command: $command" -ForegroundColor White

if ($DryRun) {
    Write-Host "`n🔍 Dry run mode - no changes made" -ForegroundColor Yellow
    Write-Host "✅ Configuration validated successfully" -ForegroundColor Green
    exit 0
}

# Add entries
Write-Host "`n📝 Adding registry entries..." -ForegroundColor Cyan
$successFile = Add-ContextMenuEntry -regPath $regPathFile -command $command -muiverb $MuiVerb -iconPath $iconPath
$successDir = Add-ContextMenuEntry -regPath $regPathDirectory -command $command -muiverb $MuiVerb -iconPath $iconPath

if ($successFile -and $successDir) {
    Write-Host "`n✅ Context menu added successfully as '$registryKeyName'!" -ForegroundColor Green
    Write-Host "💡 Entries will appear in folder and background context menus" -ForegroundColor Yellow
    Write-Host "📋 To remove later: .\registrator.ps1 -Remove -RemoveKey $registryKeyName" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Error adding context menu entries" -ForegroundColor Red
    exit 1
}

# Optional pause (only in interactive mode)
if ($Interactive) {
    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
