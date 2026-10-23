<#
Carica i dati storici 2024-2025 del cliente nel database.

Uso, dalla cartella ARCADE:
    .\db\caricamento\carica.ps1
    .\db\caricamento\carica.ps1 -Dati "C:\percorso\ARCADE_Milano_dati"

I dati di connessione si leggono dal file .env nella cartella ARCADE (escluso da Git),
vedi .env.example e docs/wiki/guida-caricamento.md.
#>
param(
    [string]$Dati = (Join-Path $PSScriptRoot '..\..\..\MATERIALI CLIENTE\ARCADE_Milano_dati')
)
$ErrorActionPreference = 'Stop'

# --- Dati di connessione dal file .env ---
$radice = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$fileEnv = Join-Path $radice '.env'
if (-not (Test-Path $fileEnv)) {
    throw "Manca il file .env in $radice. Copiare .env.example in .env e compilarlo."
}
Get-Content $fileEnv | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*?)\s*$') {
        Set-Item "env:$($Matches[1])" $Matches[2].Trim('"')
    }
}
$env:PGHOST = $env:DB_HOST
$env:PGPORT = '5432'
$env:PGDATABASE = 'postgres'
$env:PGUSER = $env:DB_USER
$env:PGPASSWORD = $env:DB_PASSWORD
$env:PGSSLMODE = 'require'
$env:PGCLIENTENCODING = 'UTF8'

# --- psql: dal PATH oppure dall'installazione di PostgreSQL ---
$psql = (Get-Command psql -ErrorAction SilentlyContinue).Source
if (-not $psql) {
    $psql = Get-ChildItem 'C:\Program Files\PostgreSQL\*\bin\psql.exe' -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $psql) { throw 'psql non trovato: installare PostgreSQL.' }

$Dati = (Resolve-Path $Dati).Path
Write-Host "Dati del cliente: $Dati"
Write-Host "Database: $env:PGHOST (utente $env:PGUSER)"

# --- 1. Fogli Excel -> CSV ---
python (Join-Path $PSScriptRoot 'excel_in_csv.py') (Join-Path $Dati 'ARCADE_Commerciale.xlsx') (Join-Path $Dati 'excel_csv')
if ($LASTEXITCODE -ne 0) { throw 'Conversione dell''Excel non riuscita.' }

# --- 2. Caricamento: una sola sessione psql, avviata dalla cartella dei dati ---
Push-Location $Dati
try {
    & $psql -X -q -v ON_ERROR_STOP=1 `
        -f (Join-Path $PSScriptRoot '00_staging.sql') `
        -f (Join-Path $PSScriptRoot '01_copia.sql') `
        -f (Join-Path $PSScriptRoot '02_trasforma.sql') `
        -f (Join-Path $PSScriptRoot '03_verifica.sql')
    if ($LASTEXITCODE -ne 0) { throw 'Caricamento non riuscito: nessuna modifica e'' stata salvata.' }
}
finally {
    Pop-Location
}
