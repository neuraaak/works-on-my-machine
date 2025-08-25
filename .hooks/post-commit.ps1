# Post-commit hook for WOMM project (PowerShell version)
# Automatically creates version tags after commits

param(
    [string]$CommitHash = ""
)

# Get project root (parent of .hooks directory)
$ProjectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $ProjectRoot

Write-Host "🏷️  Running post-commit tag management..." -ForegroundColor Cyan

# Function to read version from pyproject.toml
function Get-VersionFromPyProject {
    $pyprojectPath = Join-Path $ProjectRoot "pyproject.toml"
    if (Test-Path $pyprojectPath) {
        $content = Get-Content $pyprojectPath -Raw
        if ($content -match 'version\s*=\s*"([^"]+)"') {
            return $matches[1]
        }
    }
    return $null
}

# Function to read version from setup.py (fallback)
function Get-VersionFromSetup {
    $setupPath = Join-Path $ProjectRoot "setup.py"
    if (Test-Path $setupPath) {
        $content = Get-Content $setupPath -Raw
        # Try double quotes first
        if ($content -match 'version\s*=\s*"([^"]+)"') {
            return $matches[1]
        }
        # Try single quotes
        if ($content -match "version\s*=\s*'([^']+)'") {
            return $matches[1]
        }
    }
    return $null
}

# Function to get major version
function Get-MajorVersion {
    param([string]$Version)
    if ($Version -match '^(\d+)\.') {
        return $matches[1]
    }
    return $null
}

# Function to create or move tag
function Set-GitTag {
    param(
        [string]$TagName,
        [string]$CommitHash
    )
    
    # Check if tag exists
    $existingTag = git tag -l $TagName 2>$null
    if ($existingTag) {
        Write-Host "🔄 Moving existing tag '$TagName' to current commit..." -ForegroundColor Yellow
        # Delete local tag
        git tag -d $TagName 2>$null
        # Delete remote tag if it exists
        git push origin :refs/tags/$TagName 2>$null
    }
    
    # Create new tag
    git tag $TagName $CommitHash
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Created tag '$TagName' on commit $CommitHash" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Failed to create tag '$TagName'" -ForegroundColor Red
        return $false
    }
}

# Function to push tag to remote
function Push-GitTag {
    param([string]$TagName)
    
    Write-Host "📤 Pushing tag '$TagName' to remote..." -ForegroundColor Cyan
    git push origin $TagName 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tag '$TagName' pushed to remote" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Failed to push tag '$TagName' to remote (may not exist)" -ForegroundColor Yellow
    }
}

# Main execution
try {
    # Get current commit hash if not provided
    if (-not $CommitHash) {
        $CommitHash = git rev-parse HEAD
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to get current commit hash" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "📝 Current commit: $CommitHash" -ForegroundColor Gray
    
    # Read version from pyproject.toml or setup.py
    $version = Get-VersionFromPyProject
    if (-not $version) {
        $version = Get-VersionFromSetup
    }
    
    if (-not $version) {
        Write-Host "❌ Could not find version in pyproject.toml or setup.py" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "📦 Project version: $version" -ForegroundColor Cyan
    
    # Get major version
    $majorVersion = Get-MajorVersion $version
    if (-not $majorVersion) {
        Write-Host "❌ Could not extract major version from '$version'" -ForegroundColor Red
        exit 1
    }
    
    # Create version tag (e.g., v2.6.1)
    $versionTag = "v$version"
    $versionTagCreated = Set-GitTag -TagName $versionTag -CommitHash $CommitHash
    
    # Create major version tag (e.g., v2-latest)
    $majorTag = "v$majorVersion-latest"
    $majorTagCreated = Set-GitTag -TagName $majorTag -CommitHash $CommitHash
    
    # Push tags to remote if they were created successfully
    if ($versionTagCreated) {
        Push-GitTag -TagName $versionTag
    }
    
    if ($majorTagCreated) {
        Push-GitTag -TagName $majorTag
    }
    
    Write-Host "🎉 Post-commit tag management completed!" -ForegroundColor Green
    Write-Host "   Version tag: $versionTag" -ForegroundColor Gray
    Write-Host "   Major tag: $majorTag" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Error in post-commit hook: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
