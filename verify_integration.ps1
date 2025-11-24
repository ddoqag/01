# Claude项目集成验证脚本

function Write-Color-Text {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-Integration {
    Write-Color-Text "Verifying Claude Project Integration..." "Green"
    Write-Color-Text "======================================" "Gray"

    $results = @{}

    # Test 1: Python Scripts
    Write-Color-Text "`n1. Python Scripts Integration:" "Cyan"
    $pythonScripts = @(
        "agentflow_coordinator.py",
        "communication_protocol.py",
        "enhanced_flow_agent.py",
        "agentflow_general_launcher.py"
    )
    $scriptsFound = 0
    foreach ($script in $pythonScripts) {
        if (Test-Path $script) {
            $size = (Get-Item $script).Length
            Write-Color-Text "   ✓ $script ($(if($size -ge 1KB){'{0:N1}KB' -f ($size/1KB)}else{"$($size)B"}))" "Green"
            $scriptsFound++
        } else {
            Write-Color-Text "   ✗ $script" "Red"
        }
    }
    $results.PythonScripts = $scriptsFound -eq $pythonScripts.Count

    # Test 2: Configuration Files
    Write-Color-Text "`n2. Configuration Files:" "Cyan"
    $configFiles = @("settings.local.json", "CLAUDE_INTEGRATED.md", "INTEGRATION_SUMMARY.txt")
    $configsFound = 0
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            Write-Color-Text "   ✓ $file" "Green"
            $configsFound++
        } else {
            Write-Color-Text "   ✗ $file" "Red"
        }
    }
    $results.Configuration = $configsFound -ge 2  # At least 2 of 3

    # Test 3: .claude Directory Structure
    Write-Color-Text "`n3. .claude Directory:" "Cyan"
    $claudeDirs = @("agentflow-core", "agents", "plugins")
    $dirsFound = 0
    foreach ($dir in $claudeDirs) {
        if (Test-Path ".claude\$dir") {
            Write-Color-Text "   ✓ .claude\$dir" "Green"
            $dirsFound++
        } else {
            Write-Color-Text "   ✗ .claude\$dir" "Red"
        }
    }
    $results.ClaudeDirectory = $dirsFound -ge 2

    # Test 4: Preserved Components
    Write-Color-Text "`n4. Preserved Components:" "Cyan"
    $preservedItems = @(
        @{Name="claude.exe"; Path="claude"},
        @{Name="claude.ps1"; Path="claude.ps1"},
        @{Name="npm.exe"; Path="npm"},
        @{Name=".claude/plugins"; Path=".claude\plugins"}
    )
    $preservedCount = 0
    foreach ($item in $preservedItems) {
        if (Test-Path $item.Path) {
            Write-Color-Text "   ✓ $($item.Name)" "Green"
            $preservedCount++
        } else {
            Write-Color-Text "   ✗ $($item.Name)" "Red"
        }
    }
    $results.PreservedComponents = $preservedCount -ge 3

    # Test 5: Python Environment
    Write-Color-Text "`n5. Python Environment:" "Cyan"
    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            $version = & python --version 2>&1
            Write-Color-Text "   ✓ Python available: $version" "Green"
            $results.PythonEnvironment = $true
        } else {
            Write-Color-Text "   ⚠ Python not found" "Yellow"
            $results.PythonEnvironment = $false
        }
    } catch {
        Write-Color-Text "   ⚠ Python check failed" "Yellow"
        $results.PythonEnvironment = $false
    }

    # Generate Summary
    Write-Color-Text "`n" + "="*50 "Gray"
    Write-Color-Text "INTEGRATION VERIFICATION SUMMARY" "Yellow"
    Write-Color-Text "="*50 "Gray"

    $totalTests = $results.Count
    $passedTests = ($results.Values | Where-Object { $_ -eq $true }).Count
    $successRate = [math]::Round(($passedTests / $totalTests) * 100, 0)

    Write-Color-Text "Overall Success Rate: $successRate%" `
        -ForegroundColor $(if($successRate -ge 80){'Green'}elseif($successRate -ge 60){'Yellow'}else{'Red'})

    Write-Color-Text "`nTest Results:" "Cyan"
    Write-Color-Text "  • Python Scripts: $(if($results.PythonScripts){'✓ PASS'}else{'✗ FAIL'})" `
        -ForegroundColor $(if($results.PythonScripts){'Green'}else{'Red'})
    Write-Color-Text "  • Configuration: $(if($results.Configuration){'✓ PASS'}else{'✗ FAIL'})" `
        -ForegroundColor $(if($results.Configuration){'Green'}else{'Red'})
    Write-Color-Text "  • .claude Directory: $(if($results.ClaudeDirectory){'✓ PASS'}else->{'✗ FAIL'})" `
        -ForegroundColor $(if($results.ClaudeDirectory){'Green'}else{'Red'})
    Write-Color-Text "  • Preserved Components: $(if($results.PreservedComponents){'✓ PASS'}else{'✗ FAIL'})" `
        -ForegroundColor $(if($results.PreservedComponents){'Green'}else{'Red'})
    Write-Color-Text "  • Python Environment: $(if($results.PythonEnvironment){'✓ PASS'}else{'⚠ WARNING'})" `
        -ForegroundColor $(if($results.PythonEnvironment){'Green'}else{'Yellow'})

    # Recommendations
    Write-Color-Text "`nRecommendations:" "Cyan"
    if ($successRate -ge 80) {
        Write-Color-Text "  🎉 Integration successful! Your Claude environment is enhanced." "Green"
        Write-Color-Text "  💡 Restart Claude to see all new features." "Cyan"
        Write-Color-Text "  📚 Check CLAUDE_INTEGRATED.md for project details." "Cyan"
        Write-Color-Text "  🐍 Run 'python agentflow_coordinator.py --help' to explore new tools." "Cyan"
    } else {
        Write-Color-Text "  ⚠ Some integration issues detected." "Yellow"
        Write-Color-Text "  💡 Check the failed items above." "Cyan"
    }

    Write-Color-Text "`nProject Integration Status: $(if($successRate -ge 80){'COMPLETE ✅'}else{'PARTIAL ⚠️'})" `
        -ForegroundColor $(if($successRate -ge 80){'Green'}else{'Yellow'})

    return $successRate -ge 80
}

# Run verification
$success = Test-Integration
exit $(if($success){0}else{1})