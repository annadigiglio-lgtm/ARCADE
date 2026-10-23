<#
Crea (o ricrea da zero) il database LOCALE di prova "arcade" e ci carica lo storico 2024-2025.
Serve per provare modifiche allo schema e alle viste prima di eseguirle sul database condiviso.

Uso, dalla cartella ARCADE:
    .\db\crea_db_locale.ps1

I dati di connessione si leggono da .env.local (copiare .env.local.example).
ATTENZIONE: il database locale indicato in DB_NAME viene cancellato e ricreato.
#>
$ErrorActionPreference = 'Stop'

$radice = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$fileEnv = Join-Path $radice '.env.local'
if (-not (Test-Path $fileEnv)) {
    throw "Manca il file .env.local in $radice. Copiare .env.local.example in .env.local e compilarlo."
}
Get-Content $fileEnv | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*?)\s*$') {
        Set-Item "env:$($Matches[1])" $Matches[2].Trim('"')
    }
}
if ($env:DB_HOST -notin @('localhost', '127.0.0.1')) {
    throw "Questo script lavora solo su un database locale (DB_HOST=localhost), non su $env:DB_HOST."
}
$env:PGHOST = $env:DB_HOST
$env:PGPORT = $env:DB_PORT
$env:PGUSER = $env:DB_USER
$env:PGPASSWORD = $env:DB_PASSWORD
$env:PGSSLMODE = $env:DB_SSLMODE
$env:PGCLIENTENCODING = 'UTF8'

$psql = (Get-Command psql -ErrorAction SilentlyContinue).Source
if (-not $psql) {
    $psql = Get-ChildItem 'C:\Program Files\PostgreSQL\*\bin\psql.exe' -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $psql) { throw 'psql non trovato: installare PostgreSQL.' }

$nome = $env:DB_NAME
Write-Host "Ricreo il database locale '$nome' su ${env:PGHOST}:$env:PGPORT..."

# 1. Database nuovo e vuoto (ci si collega al database di sistema "postgres")
& $psql -X -q -v ON_ERROR_STOP=1 -d postgres -c "DROP DATABASE IF EXISTS $nome WITH (FORCE);" -c "CREATE DATABASE $nome ENCODING 'UTF8' TEMPLATE template0;"
if ($LASTEXITCODE -ne 0) { throw 'Creazione del database non riuscita.' }

# 2. Schema, dati di base, viste (gli stessi file usati su Supabase)
& $psql -X -q -v ON_ERROR_STOP=1 -d $nome `
    -f (Join-Path $PSScriptRoot 'schema.sql') `
    -f (Join-Path $PSScriptRoot 'dati_base.sql') `
    -f (Join-Path $PSScriptRoot 'viste_kpi.sql') `
    -f (Join-Path $PSScriptRoot 'viste_api.sql')
if ($LASTEXITCODE -ne 0) { throw 'Creazione dello schema non riuscita.' }

# 3. Dati storici
& (Join-Path $PSScriptRoot 'caricamento\carica.ps1') -FileEnv '.env.local'
