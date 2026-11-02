param(
    [ValidateSet('avvia','compila','stato','log','ferma')]
    [string]$Azione = 'avvia',
    [string]$FileEnv = '.env.docker.local'
)
$ErrorActionPreference = 'Stop'
$dockerArcade = (Get-Command docker.exe -ErrorAction SilentlyContinue).Source
if (-not $dockerArcade) {
    $candidatiArcade = @(
        (Join-Path $env:LOCALAPPDATA 'Programs/DockerDesktop/resources/bin/docker.exe'),
        (Join-Path $env:ProgramFiles 'Docker/Docker/resources/bin/docker.exe')
    )
    $dockerArcade = $candidatiArcade | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $dockerArcade) { throw 'Docker non trovato. Installare e avviare Docker Desktop.' }
# Docker's credential helper must be available to the build process too.
$env:PATH = (Split-Path $dockerArcade -Parent) + ';' + $env:PATH
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath $FileEnv)) { throw "Manca $FileEnv. Vedere docs/wiki/docker.md." }
    & $dockerArcade compose --env-file $FileEnv config --quiet
    if ($LASTEXITCODE -ne 0) { throw 'Configurazione Docker non valida.' }
    switch ($Azione) {
        'avvia' { & $dockerArcade compose --env-file $FileEnv up --build -d }
        'compila' { & $dockerArcade compose --env-file $FileEnv build }
        'stato' { & $dockerArcade compose --env-file $FileEnv ps }
        'log' { & $dockerArcade compose --env-file $FileEnv logs --tail 60 app }
        'ferma' { & $dockerArcade compose --env-file $FileEnv stop app }
    }
    if ($LASTEXITCODE -ne 0) { throw "Operazione Docker '$Azione' non riuscita." }
} finally { Pop-Location }
