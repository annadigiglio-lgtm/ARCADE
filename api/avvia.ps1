param(
    [string]$FileEnv = '.env.local',
    [switch]$PreparaDemo,
    [switch]$SoloCompila,
    [switch]$SenzaCompilare
)
$ErrorActionPreference = 'Stop'
$radice = Split-Path $PSScriptRoot -Parent
$percorsoEnv = Join-Path $radice $FileEnv
if (-not (Test-Path -LiteralPath $percorsoEnv)) { throw "Manca $FileEnv nella cartella ARCADE." }
Get-Content -LiteralPath $percorsoEnv | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*?)\s*$') { Set-Item "env:$($Matches[1])" $Matches[2].Trim('"') }
}
if (-not $env:DB_HOST -or -not $env:DB_USER -or -not $env:DB_PASSWORD) { throw 'Compilare DB_HOST, DB_USER e DB_PASSWORD nel file ambiente.' }
if ($PreparaDemo -and $env:DB_HOST -notin @('localhost','127.0.0.1')) { throw 'Gli utenti demo si creano solo in locale.' }
$maven = (Get-Command mvn.cmd -ErrorAction SilentlyContinue).Source
if (-not $maven) { $maven = Join-Path $radice '.tools/apache-maven-3.9.9/bin/mvn.cmd' }
if (-not (Test-Path -LiteralPath $maven)) { throw 'Installare Maven oppure eseguire .\api\prepara-maven.ps1.' }
$java = (Get-Command java -ErrorAction Stop).Source
$env:JAVA_HOME = Split-Path (Split-Path $java -Parent) -Parent
if (-not $env:ARCADE_JWT_SECRET) {
    $random = New-Object byte[] 48
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($random) } finally { $rng.Dispose() }
    $env:ARCADE_JWT_SECRET = [Convert]::ToBase64String($random)
}
Push-Location $PSScriptRoot
try {
    if (-not $SenzaCompilare) {
        & $maven --batch-mode --no-transfer-progress "-Dmaven.repo.local=$radice/.tools/m2" package
        if ($LASTEXITCODE -ne 0) { throw 'Compilazione o test falliti.' }
    }
    if ($SoloCompila) { return }
    $jar = Join-Path $PSScriptRoot 'target/arcade-api-0.1.0.jar'
    if ($PreparaDemo) {
        & $java -jar $jar '--spring.main.web-application-type=none' '--arcade.provision-demo=true'
    } else {
        Write-Host 'Aprire http://localhost:8080. Demo ferma al 20/12/2025 11:55 (modificabile con ARCADE_DEMO_ISTANTE).'
        & $java -jar $jar
    }
    if ($LASTEXITCODE -ne 0) { throw 'Avvio non riuscito.' }
} finally { Pop-Location }
