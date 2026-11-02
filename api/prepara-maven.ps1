$ErrorActionPreference = 'Stop'
$tools = Join-Path (Split-Path $PSScriptRoot -Parent) '.tools'
New-Item -ItemType Directory -Force -Path $tools | Out-Null
$zip = Join-Path $tools 'maven.zip'
$base = 'https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/apache-maven-3.9.9-bin.zip'
Invoke-WebRequest -UseBasicParsing $base -OutFile $zip
$checksum = (Invoke-WebRequest -UseBasicParsing "$base.sha512").Content.Trim().ToLowerInvariant()
if ((Get-FileHash -LiteralPath $zip -Algorithm SHA512).Hash.ToLowerInvariant() -ne $checksum) { throw 'Checksum Maven non valido.' }
Expand-Archive -LiteralPath $zip -DestinationPath $tools -Force
Write-Host 'Maven pronto nella cartella locale .tools.'
