# Produce SQL autosufficiente per SQL Editor, senza credenziali o dati personali.
$ErrorActionPreference = 'Stop'
$destinazione = Join-Path $PSScriptRoot 'pubblica_api_supabase.sql'
$parti = @(
    '-- Generato da db/prepara_pubblicazione_supabase.ps1: non modificare questo file a mano.',
    '-- Eseguire come proprietario dello schema arcade (postgres) nello SQL Editor Supabase.',
    '-- Aggiorna le viste KPI e aggiunge le viste/funzioni API; non ricrea tabelle e non cancella dati.',
    'BEGIN;',
    (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'viste_kpi.sql') -Raw -Encoding UTF8),
    (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'viste_api.sql') -Raw -Encoding UTF8),
    'GRANT SELECT ON ALL TABLES IN SCHEMA arcade TO bid_app;',
    'GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA arcade TO bid_app;',
    "SELECT * FROM arcade.presenze_al('2025-12-20T11:55:00+01:00'::timestamptz);",
    'COMMIT;'
)
[System.IO.File]::WriteAllText($destinazione, ($parti -join "`n"), (New-Object System.Text.UTF8Encoding($false)))
Write-Host 'Creato db/pubblica_api_supabase.sql per SQL Editor.'
