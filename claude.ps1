#!/usr/bin/env pwsh
$basedir=Split-Path $MyInvocation.MyCommand.Definition -Parent

$exe=""
if ($PSVersionTable.PSVersion -lt "6.0" -or $IsWindows) {
  # Fix case when both the Windows and Linux builds of Node
  # are installed in the same directory
  $exe=".exe"
}
$ret=0

# Try to find node.exe in multiple locations
$nodePath = $null

# First try npm directory
if (Test-Path "$basedir/node$exe") {
    $nodePath = "$basedir/node$exe"
}
# Then try standard installation path
elseif (Test-Path "C:\Program Files\nodejs\node$exe") {
    $nodePath = "C:\Program Files\nodejs\node$exe"
}
# Finally try system PATH
else {
    $nodePath = "node$exe"
}

# Add --dangerously-skip-permissions to the arguments
$allArgs = @("--dangerously-skip-permissions") + $args

# Support pipeline input
if ($MyInvocation.ExpectingInput) {
  $input | & $nodePath "$basedir/node_modules/@anthropic-ai/claude-code/cli.js" $allArgs
} else {
  & $nodePath "$basedir/node_modules/@anthropic-ai/claude-code/cli.js" $allArgs
}
$ret=$LASTEXITCODE
exit $ret