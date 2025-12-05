#!/usr/bin/env pwsh
$basedir=Split-Path $MyInvocation.MyCommand.Definition -Parent

$exe=""
if ($PSVersionTable.PSVersion -lt "6.0" -or $IsWindows) {
  # Fix case when both the Windows and Linux builds of Node
  # are installed in the same directory
  $exe=".exe"
}
$ret=0
if (Test-Path "$basedir/node$exe") {
  # Support pipeline input
  if ($MyInvocation.ExpectingInput) {
    $input | & "$basedir/node$exe"  "$basedir/node_modules/@anthropic-ai/claude-code/cli.js" $args
  } else {
    & "$basedir/node$exe"  "$basedir/node_modules/@anthropic-ai/claude-code/cli.js" $args
  }
  $ret=$LASTEXITCODE
} else {
  # Try to find node.exe in common locations
  $nodePath = ""
  if (Test-Path "C:\Program Files\nodejs\node.exe") {
    $nodePath = "C:\Program Files\nodejs\node.exe"
  } elseif (Test-Path "C:\Program Files (x86)\nodejs\node.exe") {
    $nodePath = "C:\Program Files (x86)\nodejs\node.exe"
  } else {
    $nodePath = "node.exe"
  }

  # Support pipeline input
  if ($MyInvocation.ExpectingInput) {
    $input | & $nodePath  "$basedir/node_modules/@anthropic-ai/claude-code/cli.js" $args
  } else {
    & $nodePath  "$basedir/node_modules/@anthropic-ai/claude-code/cli.js" $args
  }
  $ret=$LASTEXITCODE
}
exit $ret
