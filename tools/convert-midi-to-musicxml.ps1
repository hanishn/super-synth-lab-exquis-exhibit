[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
  [string]$InputMidi,

  [Parameter(Mandatory = $true)]
  [string]$OutputMusicXml,

  [string]$MuseScoreExe = 'MuseScore4.exe'
)

$ErrorActionPreference = 'Stop'

# MIDI deliberately stops at performed events.  MuseScore Studio owns the
# established import/notation inference step; SSLI consumes its MusicXML output
# and OSMD only engraves that standard score in the browser.  Keep this adapter
# intentionally small rather than growing a second score writer in this repo.
$inputPath = (Resolve-Path -LiteralPath $InputMidi).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputMusicXml)
if ([System.IO.Path]::GetExtension($outputPath).ToLowerInvariant() -notin @('.musicxml', '.xml', '.mxl')) {
  throw 'OutputMusicXml must end in .musicxml, .xml, or .mxl.'
}

$exe = Get-Command $MuseScoreExe -ErrorAction SilentlyContinue
if (-not $exe) {
  throw "MuseScore Studio was not found as '$MuseScoreExe'. Install it, add MuseScore4.exe to PATH, or pass -MuseScoreExe with its full path."
}

$outputDirectory = Split-Path -Parent $outputPath
if ($outputDirectory -and -not (Test-Path -LiteralPath $outputDirectory)) {
  New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}

& $exe.Source -o $outputPath $inputPath
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $outputPath -PathType Leaf)) {
  throw "MuseScore conversion failed for '$inputPath'."
}

Write-Output "Created MusicXML: $outputPath"
