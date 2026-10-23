<#
Carica i dati storici 2024-2025 del cliente nel database.

Uso, dalla cartella ARCADE:
    .\db\caricamento\carica.ps1                       # database condiviso (file .env)
    .\db\caricamento\carica.ps1 -FileEnv .env.local   # database locale di prova
    .\db\caricamento\carica.ps1 -Dati "C:\percorso\ARCADE_Milano_dati"

I dati di connessione si leggono dal file indicato (escluso da Git),
vedi .env.example, .env.local.example e docs/wiki/guida-caricamento.md.
#>
param(
    [string]$Dati = (Join-Path $PSScriptRoot '..\..\..\MATERIALI CLIENTE\ARCADE_Milano_dati'),
    [string]$FileEnv = '.env'
)
$ErrorActionPreference = 'Stop'

# --- Dati di connessione dal file .env (o .env.local) ---
$radice = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$fileEnv = Join-Path $radice $FileEnv
if (-not (Test-Path $fileEnv)) {
    throw "Manca il file $FileEnv in $radice. Copiare il file .example corrispondente e compilarlo."
}
# Si riparte da zero: nessun valore rimasto da un'esecuzione precedente nello stesso terminale
'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_SSLMODE' |
    ForEach-Object { Remove-Item "env:$_" -ErrorAction SilentlyContinue }
Get-Content $fileEnv | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*?)\s*$') {
        Set-Item "env:$($Matches[1])" $Matches[2].Trim('"')
    }
}
# Valori predefiniti = database condiviso Supabase
if (-not $env:DB_PORT)    { $env:DB_PORT = '5432' }
if (-not $env:DB_NAME)    { $env:DB_NAME = 'postgres' }
if (-not $env:DB_SSLMODE) { $env:DB_SSLMODE = 'require' }
$env:PGHOST = $env:DB_HOST
$env:PGPORT = $env:DB_PORT
$env:PGDATABASE = $env:DB_NAME
$env:PGUSER = $env:DB_USER
$env:PGPASSWORD = $env:DB_PASSWORD
$env:PGSSLMODE = $env:DB_SSLMODE
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
Write-Host "Database: $env:PGHOST`:$env:PGPORT/$env:PGDATABASE (utente $env:PGUSER)"

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
