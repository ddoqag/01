# Claude项目智能集成脚本
# 将d:\claude备份集成到当前项目目录

param(
    [switch]$DryRun,
    [switch]$Force
)

function Write-Color-Text {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Start-Integration {
    Write-Color-Text "Claude Project Integration Starting..." "Green"
    Write-Color-Text "Source: d:\claude" "Cyan"
    Write-Color-Text "Target: $(Get-Location)" "Cyan"

    # Check backup directory
    if (-not (Test-Path "d:\claude")) {
        Write-Color-Text "ERROR: Backup directory d:\claude not found" "Red"
        exit 1
    }

    if ($DryRun) {
        Write-Color-Text "PREVIEW MODE - Integration operations:" "Yellow"
        Write-Color-Text "  - Merge project files from backup" "Gray"
        Write-Color-Text "  - Merge .claude configuration intelligently" "Gray"
        Write-Color-Text "  - Add missing Python scripts" "Gray"
        Write-Color-Text "  - Update configuration files" "Gray"
        return
    }

    try {
        # 1. Copy project files (excluding conflicts)
        Write-Color-Text "Step 1: Copying project files..." "Cyan"
        $excludeItems = @(
            '.claude', '.git', 'node_modules', '__pycache__',
            'claude*', 'npm*', 'npx*', 'imagemin*',
            '*.ps1', '*.bat', '*.cmd'
        )

        Get-ChildItem -Path "d:\claude" -Exclude $excludeItems | ForEach-Object {
            if (-not (Test-Path $_.Name)) {
                Write-Color-Text "  + Adding: $($_.Name)" "Green"
                Copy-Item -Path $_.FullName -Destination . -Recurse -Force
            } else {
                Write-Color-Text "  - Skipping existing: $($_.Name)" "Yellow"
            }
        }

        # 2. Intelligent .claude configuration merge
        Write-Color-Text "Step 2: Merging .claude configuration..." "Cyan"
        if (Test-Path "d:\claude\.claude") {
            # Copy only non-conflicting items from .claude
            Get-ChildItem -Path "d:\claude\.claude" | ForEach-Object {
                $targetPath = ".\.claude\$($_.Name)"
                if (-not (Test-Path $targetPath)) {
                    Write-Color-Text "  + Adding config: $($_.Name)" "Green"
                    Copy-Item -Path $_.FullName -Destination $targetPath -Recurse -Force
                } else {
                    Write-Color-Text "  - Preserving existing: $($_.Name)" "Yellow"
                }
            }
        }

        # 3. Merge settings files
        Write-Color-Text "Step 3: Merging settings..." "Cyan"
        if (Test-Path "d:\claude\settings.json") {
            if (-not (Test-Path "settings.local.json")) {
                Copy-Item -Path "d:\claude\settings.json" -Destination "settings.local.json"
                Write-Color-Text "  + Added: settings.local.json" "Green"
            } else {
                Write-Color-Text "  - Preserving existing: settings.local.json" "Yellow"
            }
        }

        # 4. Copy key Python files if they don't exist
        Write-Color-Text "Step 4: Adding Python scripts..." "Cyan"
        $keyPythonFiles = @(
            "agentflow_coordinator.py",
            "communication_protocol.py",
            "enhanced_flow_agent.py",
            "agentflow_general_launcher.py"
        )

        foreach ($file in $keyPythonFiles) {
            $sourceFile = "d:\claude\$file"
            if ((Test-Path $sourceFile) -and (-not (Test-Path $file))) {
                Copy-Item -Path $sourceFile -Destination "."
                Write-Color-Text "  + Added: $file" "Green"
            }
        }

        # 5. Create/update project CLAUDE.md
        Write-Color-Text "Step 5: Updating project documentation..." "Cyan"
        if (Test-Path "d:\claude\CLAUDE.md") {
            $claudeContent = Get-Content "d:\claude\CLAUDE.md" -Raw
            # Add integration note at the beginning
            $integrationNote = @"

# 项目集成说明
## 集成状态: 已完成 ✅
## 集成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
## 备份源: d:\claude
## 集成目录: $(Get-Location)

"@
            $updatedContent = $integrationNote + $claudeContent
            Set-Content -Path "CLAUDE_INTEGRATED.md" -Value $updatedContent
            Write-Color-Text "  + Created: CLAUDE_INTEGRATED.md" "Green"
        }

        # 6. Create integration summary
        Write-Color-Text "Step 6: Creating integration summary..." "Cyan"
        $summary = @"
Claude Project Integration Summary
==================================
Integration Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Source Directory: d:\claude
Target Directory: $(Get-Location)

Added Components:
- Project directories (agents, commands, plugins, etc.)
- Python scripts and tools
- Configuration files
- Documentation

Preserved Components:
- Existing .claude configuration
- npm tools and utilities
- Existing plugins and settings

Next Steps:
1. Restart Claude to apply new configuration
2. Check CLAUDE_INTEGRATED.md for project details
3. Run available Python scripts as needed
"@
        Set-Content -Path "INTEGRATION_SUMMARY.txt" -Value $summary
        Write-Color-Text "  + Created: INTEGRATION_SUMMARY.txt" "Green"

        Write-Color-Text "`n🎉 Integration completed successfully!" "Green"
        Write-Color-Text "✅ Project files integrated into current directory" "Cyan"
        Write-Color-Text "✅ Configuration merged intelligently" "Cyan"
        Write-Color-Text "✅ Documentation updated" "Cyan"
        Write-Color-Text "`nNext: Restart Claude to see integrated features" "Yellow"

    } catch {
        Write-Color-Text "ERROR during integration: $($_.Exception.Message)" "Red"
        exit 1
    }
}

# Show help
if ($args -contains '-help' -or $args -contains '--help') {
    Write-Color-Text "Claude Project Integration Script" "Green"
    Write-Color-Text "Usage: .\integrate_backup.ps1 [options]" "White"
    Write-Color-Text "Options:" "Cyan"
    Write-Color-Text "  -DryRun     Preview mode" "White"
    Write-Color-Text "  -Force      Force integration" "White"
    Write-Color-Text "`nThis script intelligently integrates d:\claude backup into" "White"
    Write-Color-Text "the current directory while preserving existing setup." "Gray"
    exit 0
}

# Start integration
Start-Integration