"""Genera il progetto Power BI ARCADE-direzione (.pbip) dalle viste di PostgreSQL.

Modello (TMDL) e pagine del report (PBIR) nascono da questo file: una modifica si fa qui
e si rigenera. Il report legge solo le viste dello schema `arcade`, le sole leggibili da
`bad_powerbi`; i KPI non si ricalcolano in DAX (decisione 0003): le misure fanno solo
somme e massimi di colonne già calcolate nelle viste.

Uso (dalla cartella power-platform/powerbi):
    python -I genera_report.py
Output: ARCADE-direzione.pbip, ARCADE-direzione.SemanticModel/, ARCADE-direzione.Report/
La password non è mai nei file: Power BI Desktop la chiede alla prima connessione.
"""
import json
import os
import shutil

NOME = "ARCADE-direzione"
BASE = os.path.dirname(os.path.abspath(__file__))
SERVER = "aws-1-eu-central-1.pooler.supabase.com:5432"
DATABASE = "postgres"

S = "https://developer.microsoft.com/json-schemas/fabric/"
T = "\t"

# ---------------------------------------------------------------------------
# Modello: una tabella per vista. tipo: s testo, i intero, n decimale, d data, t data e ora
# ---------------------------------------------------------------------------
TIPI = {"s": ("string", "type text"), "i": ("int64", "Int64.Type"), "n": ("double", "type number"),
        "d": ("dateTime", "type date"), "t": ("dateTime", "type datetime")}
FORMATI = {"d": "dd/mm/yyyy", "t": "dd/mm/yyyy hh:nn"}


def tabella(nome, vista, colonne, misure=(), passi=(), nascoste=()):
    return dict(nome=nome, vista=vista, colonne=colonne, misure=misure, passi=passi, nascoste=nascoste)


# Passi Power Query aggiuntivi (righe M), applicati dopo la lettura della vista
SOLO_FIERA = 'Righe = Table.SelectRows(Vista, each [padiglione] = null)'
SOLO_PAD = 'Righe = Table.SelectRows(Vista, each [padiglione] <> null)'
ORA_ROMA = ('Righe = Table.TransformColumns(Vista, {{"istante", each DateTimeZone.RemoveZone('
            'DateTimeZone.SwitchZone(_, 1)), type datetime}})')  # dicembre: Roma = UTC+1
PAD_DA_STAND = 'Righe = Table.AddColumn(Vista, "padiglione", each Text.Start([codice_stand], 2), type text)'

TABELLE = [
    tabella("Edizione", "v_kpi_rinnovo",
            [("edizione", "s"), ("edizione_precedente", "s"), ("espositori_precedenti", "i"),
             ("espositori_attuali", "i"), ("espositori_rinnovati", "i"), ("espositori_persi", "i"),
             ("espositori_nuovi", "i"), ("tasso_rinnovo", "n")],
            [("Tasso di rinnovo", "MAX(Edizione[tasso_rinnovo])", "0.0%"),
             ("Espositori rinnovati", "SUM(Edizione[espositori_rinnovati])", "#,0"),
             ("Espositori persi", "SUM(Edizione[espositori_persi])", "#,0"),
             ("Espositori nuovi", "SUM(Edizione[espositori_nuovi])", "#,0"),
             ("Espositori attuali", "SUM(Edizione[espositori_attuali])", "#,0")]),
    tabella("Visitatori", "v_kpi_visitatori",
            [("edizione", "s"), ("ingressi_padiglioni", "i"), ("visitatori_giornalieri", "n"), ("visitatori_unici", "n")],
            [("Visitatori giornalieri", "SUM(Visitatori[visitatori_giornalieri])", "#,0"),
             ("Ingressi ai padiglioni", "SUM(Visitatori[ingressi_padiglioni])", "#,0"),
             ("Visitatori unici", "SUM(Visitatori[visitatori_unici])", "#,0")]),
    tabella("Visitatori giorno", "v_kpi_visitatori_giorno",
            [("edizione", "s"), ("giorno", "d"), ("visitatori", "n"), ("biglietti", "i")],
            [("Visitatori del giorno", "SUM('Visitatori giorno'[visitatori])", "#,0")]),
    tabella("Presenze", "v_presenze_stimate",
            [("edizione", "s"), ("istante", "t"), ("padiglione", "s"), ("presenti", "n")],
            [("Presenti stimati", "SUM(Presenze[presenti])", "#,0")], [ORA_ROMA]),
    tabella("Picco padiglione", "v_kpi_picco_padiglione",
            [("edizione", "s"), ("padiglione", "s"), ("istante", "t"), ("presenti", "n")],
            [("Picco del padiglione", "MAX('Picco padiglione'[presenti])", "#,0")], [ORA_ROMA]),
    tabella("Picco fiera", "v_kpi_picco_fiera",
            [("edizione", "s"), ("istante", "t"), ("presenti", "n")],
            [("Picco della fiera", "MAX('Picco fiera'[presenti])", "#,0")], [ORA_ROMA]),
    tabella("Saturazione fiera", "v_kpi_saturazione",
            [("edizione", "s"), ("padiglione", "s"), ("stand_disponibili", "i"), ("stand_venduti", "i"),
             ("mq_disponibili", "n"), ("mq_venduti", "n"), ("saturazione_mq", "n")],
            [("Saturazione della fiera", "MAX('Saturazione fiera'[saturazione_mq])", "0.0%"),
             ("Stand venduti fiera", "SUM('Saturazione fiera'[stand_venduti])", "#,0")],
            [SOLO_FIERA], nascoste=("padiglione",)),
    tabella("Saturazione padiglione", "v_kpi_saturazione",
            [("edizione", "s"), ("padiglione", "s"), ("stand_disponibili", "i"), ("stand_venduti", "i"),
             ("mq_disponibili", "n"), ("mq_venduti", "n"), ("saturazione_mq", "n")],
            [("Saturazione", "MAX('Saturazione padiglione'[saturazione_mq])", "0.0%"),
             ("Mq venduti", "SUM('Saturazione padiglione'[mq_venduti])", "#,0"),
             ("Mq disponibili", "SUM('Saturazione padiglione'[mq_disponibili])", "#,0"),
             ("Stand venduti", "SUM('Saturazione padiglione'[stand_venduti])", "#,0"),
             ("Stand disponibili", "SUM('Saturazione padiglione'[stand_disponibili])", "#,0")],
            [SOLO_PAD]),
    tabella("Ricavo fiera", "v_kpi_ricavo_mq",
            [("edizione", "s"), ("padiglione", "s"), ("ricavo", "n"), ("mq_venduti", "n"), ("ricavo_per_mq", "n")],
            [("Ricavo per mq fiera", "MAX('Ricavo fiera'[ricavo_per_mq])", "#,0 €"),
             ("Imponibile firmato", "SUM('Ricavo fiera'[ricavo])", "#,0 €")],
            [SOLO_FIERA], nascoste=("padiglione",)),
    tabella("Ricavo padiglione", "v_kpi_ricavo_mq",
            [("edizione", "s"), ("padiglione", "s"), ("ricavo", "n"), ("mq_venduti", "n"), ("ricavo_per_mq", "n")],
            [("Ricavo per mq", "MAX('Ricavo padiglione'[ricavo_per_mq])", "#,0 €"),
             ("Ricavo dei padiglioni", "SUM('Ricavo padiglione'[ricavo])", "#,0 €")],
            [SOLO_PAD]),
    tabella("Costo contatto", "v_kpi_costo_contatto",
            [("edizione", "s"), ("id_espositore", "s"), ("codice_stand", "s"), ("imponibile", "n"),
             ("contatti", "i"), ("costo_per_contatto", "n"), ("padiglione", "s")],
            [("Contatti raccolti", "SUM('Costo contatto'[contatti])", "#,0"),
             ("Costo per contatto dello stand", "MAX('Costo contatto'[costo_per_contatto])", "#,0 €")],
            [PAD_DA_STAND]),
    tabella("Costo contatto fiera", "v_kpi_costo_contatto_fiera",
            [("edizione", "s"), ("stand_con_contatti", "i"), ("contatti", "n"), ("costo_per_contatto", "n")],
            [("Costo per contatto", "MAX('Costo contatto fiera'[costo_per_contatto])", "#,0 €")]),
    tabella("Visite stand", "v_visite_stand_ora",
            [("edizione", "s"), ("codice_stand", "s"), ("ora", "t"), ("scansioni", "i"), ("padiglione", "s"), ("ora_del_giorno", "i")],
            [("Visite agli stand", "SUM('Visite stand'[scansioni])", "#,0")],
            [PAD_DA_STAND, 'Ore = Table.AddColumn(Righe, "ora_del_giorno", each Time.Hour([ora]), Int64.Type)']),
    tabella("Contratti", "v_incassi_contratto",
            [("id_contratto", "s"), ("edizione", "s"), ("id_espositore", "s"), ("codice_stand", "s"), ("stato", "s"),
             ("imponibile", "n"), ("acconto_scadenza", "d"), ("acconto_pagato_il", "d"), ("saldo_scadenza", "d"),
             ("saldo_pagato_il", "d"), ("stato_pagamenti", "s")],
            [("Numero contratti", "COUNTROWS(Contratti)", "#,0"),
             ("Imponibile contratti", "SUM(Contratti[imponibile])", "#,0 €")]),
    tabella("Vendite biglietti", "v_vendite_biglietti_giorno",
            [("edizione", "s"), ("giorno", "d"), ("canale", "s"), ("biglietti", "i"), ("persone", "i"), ("ricavo_biglietti", "n")],
            [("Biglietti venduti", "SUM('Vendite biglietti'[biglietti])", "#,0"),
             ("Ricavo biglietti", "SUM('Vendite biglietti'[ricavo_biglietti])", "#,0 €")]),
    tabella("Conversione", "v_kpi_conversione",
            [("edizione", "s"), ("biglietti_venduti", "i"), ("biglietti_entrati", "i"), ("tasso_conversione", "n")],
            [("Tasso di conversione", "MAX(Conversione[tasso_conversione])", "0.0%")]),
]


def q(nome):
    """Nome di tabella o colonna nella sintassi TMDL/DAX."""
    return f"'{nome}'" if any(c in nome for c in " -'") else nome


def m_query(t):
    tipi = ", ".join(f'{{"{c}", {TIPI[k][1]}}}' for c, k in t["colonne"]
                     if not any(c in p for p in t["passi"] if "AddColumn" in p and f'"{c}"' in p))
    righe = ['Origine = PostgreSQL.Database(Server, Database)',
             f'Vista = Origine{{[Schema="arcade", Item="{t["vista"]}"]}}[Data]']
    ultimo = "Vista"
    for p in t["passi"]:
        nome = p.split(" = ")[0]
        p = p.replace("(Vista,", f"({ultimo},")
        righe.append(p)
        ultimo = nome
    righe.append(f"Tipi = Table.TransformColumnTypes({ultimo}, {{{tipi}}})")
    colonne = ", ".join(f'"{c}"' for c, _ in t["colonne"])
    righe.append(f"Colonne = Table.SelectColumns(Tipi, {{{colonne}}})")
    corpo = (",\n").join(righe)
    return "let\n" + "\n".join("    " + r for r in corpo.split("\n")) + "\nin\n    Colonne"


def tmdl_tabella(t):
    out = [f"table {q(t['nome'])}", ""]
    for nome, expr, fmt in t["misure"]:
        out += [f"{T}measure {q(nome)} = {expr}", f"{T}{T}formatString: {fmt}", ""]
    for c, k in t["colonne"]:
        out.append(f"{T}column {q(c)}")
        out.append(f"{T}{T}dataType: {TIPI[k][0]}")
        if k in FORMATI:
            out.append(f"{T}{T}formatString: {FORMATI[k]}")
        if c in t["nascoste"]:
            out.append(f"{T}{T}isHidden")
        out.append(f"{T}{T}summarizeBy: none")
        out.append(f"{T}{T}sourceColumn: {c}")
        out.append("")
    out.append(f"{T}partition {q(t['nome'])} = m")
    out.append(f"{T}{T}mode: import")
    out.append(f"{T}{T}source =")
    out += [f"{T}{T}{T}{r}" for r in m_query(t).split("\n")]
    out.append("")
    return "\n".join(out)


def scrivi(percorso, testo):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w", encoding="utf-8", newline="\n") as f:
        f.write(testo)


def scrivi_json(percorso, dati):
    scrivi(percorso, json.dumps(dati, ensure_ascii=False, indent=2) + "\n")


def genera_modello(radice):
    sm = os.path.join(radice, f"{NOME}.SemanticModel")
    scrivi_json(os.path.join(sm, "definition.pbism"),
                {"$schema": S + "item/semanticModel/definitionProperties/1.0.0/schema.json", "version": "4.0", "settings": {}})
    d = os.path.join(sm, "definition")
    scrivi(os.path.join(d, "database.tmdl"), "database\n\tcompatibilityLevel: 1567\n")
    modello = ["model Model", f"{T}culture: it-IT", f"{T}defaultPowerBIDataSourceVersion: powerBI_V3",
               f"{T}sourceQueryCulture: it-IT", f"{T}dataAccessOptions", f"{T}{T}legacyRedirects",
               f"{T}{T}returnErrorValuesAsNull", ""]
    modello += [f"ref table {q(t['nome'])}" for t in TABELLE]
    scrivi(os.path.join(d, "model.tmdl"), "\n".join(modello) + "\n")
    scrivi(os.path.join(d, "expressions.tmdl"),
           f'expression Server = "{SERVER}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\n'
           f'expression Database = "{DATABASE}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n')
    rel = []
    for t in TABELLE:
        if t["nome"] != "Edizione":
            nome = "rel_" + t["nome"].lower().replace(" ", "_")
            rel += [f"relationship {nome}", f"{T}fromColumn: {q(t['nome'])}.edizione", f"{T}toColumn: Edizione.edizione", ""]
    scrivi(os.path.join(d, "relationships.tmdl"), "\n".join(rel))
    for t in TABELLE:
        scrivi(os.path.join(d, "tables", f"{t['nome']}.tmdl"), tmdl_tabella(t))


# ---------------------------------------------------------------------------
# Report: elementi visivi
# ---------------------------------------------------------------------------
def campo(tab, prop, misura=False):
    k = "Measure" if misura else "Column"
    return {k: {"Expression": {"SourceRef": {"Entity": tab}}, "Property": prop}}


def proiezione(tab, prop, misura=False):
    return {"field": campo(tab, prop, misura), "queryRef": f"{tab}.{prop}", "nativeQueryRef": prop}


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def contenitore(titolo):
    return {"title": [{"properties": {"show": lit("true"), "text": lit("'" + titolo.replace("'", "''") + "'")}}]}


def visual(nome, x, y, w, h, tipo, ruoli, titolo=None, z=0):
    stato = {r: {"projections": [proiezione(*p) for p in pp]} for r, pp in ruoli.items()}
    v = {"visualType": tipo, "query": {"queryState": stato}, "drillFilterOtherVisuals": True}
    if titolo:
        v["visualContainerObjects"] = contenitore(titolo)
    return {"$schema": S + "item/report/definition/visualContainer/2.0.0/schema.json",
            "name": nome, "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z},
            "visual": v}


def colonne(nome, x, y, w, h, cat, valori, titolo, serie=None):
    ruoli = {"Category": [cat], "Y": valori}
    if serie:
        ruoli["Series"] = [serie]
    return visual(nome, x, y, w, h, "clusteredColumnChart", ruoli, titolo)


def linee(nome, x, y, w, h, cat, valori, titolo, serie=None):
    ruoli = {"Category": [cat], "Y": valori}
    if serie:
        ruoli["Series"] = [serie]
    return visual(nome, x, y, w, h, "lineChart", ruoli, titolo)


def ciambella(nome, x, y, w, h, cat, valore, titolo):
    return visual(nome, x, y, w, h, "donutChart", {"Category": [cat], "Y": [valore]}, titolo)


def tabella_v(nome, x, y, w, h, campi, titolo):
    return visual(nome, x, y, w, h, "tableEx", {"Values": campi}, titolo)


def filtro(nome, x, y, w, h, tab, col, titolo):
    return visual(nome, x, y, w, h, "slicer", {"Values": [(tab, col)]}, titolo)


def M(tab, nome):
    return (tab, nome, True)


ED = ("Edizione", "edizione")

# Pagine: (nome, titolo, [elementi visivi]). Canvas 1280 x 720.
PAGINE = [
    ("pb01_sintesi", "PB-01 Sintesi direzione", [
        colonne("v01_visitatori", 20, 20, 400, 330, ED, [M("Visitatori", "Visitatori giornalieri")], "Visitatori giornalieri per edizione"),
        colonne("v01_picco", 440, 20, 400, 330, ED, [M("Picco fiera", "Picco della fiera")], "Picco di presenza stimato"),
        colonne("v01_saturazione", 860, 20, 400, 330, ED, [M("Saturazione fiera", "Saturazione della fiera")], "Saturazione degli spazi (mq)"),
        colonne("v01_ricavo_mq", 20, 370, 400, 330, ED, [M("Ricavo fiera", "Ricavo per mq fiera")], "Ricavo per metro quadro"),
        colonne("v01_imponibile", 440, 370, 400, 330, ED, [M("Ricavo fiera", "Imponibile firmato")], "Imponibile dei contratti firmati"),
        colonne("v01_costo_contatto", 860, 370, 400, 330, ED, [M("Costo contatto fiera", "Costo per contatto")], "Costo per contatto"),
    ]),
    ("pb02_padiglioni", "PB-02 Padiglioni e spazi", [
        colonne("v02_saturazione", 20, 20, 610, 330, ("Saturazione padiglione", "padiglione"),
                [M("Saturazione padiglione", "Saturazione")], "Saturazione per padiglione",
                serie=("Saturazione padiglione", "edizione")),
        colonne("v02_ricavo_mq", 650, 20, 610, 330, ("Ricavo padiglione", "padiglione"),
                [M("Ricavo padiglione", "Ricavo per mq")], "Ricavo per mq per padiglione",
                serie=("Ricavo padiglione", "edizione")),
        colonne("v02_ricavo", 20, 370, 610, 330, ("Ricavo padiglione", "padiglione"),
                [M("Ricavo padiglione", "Ricavo dei padiglioni")], "Ricavo per padiglione",
                serie=("Ricavo padiglione", "edizione")),
        tabella_v("v02_tabella", 650, 370, 610, 330,
                  [("Saturazione padiglione", "edizione"), ("Saturazione padiglione", "padiglione"),
                   M("Saturazione padiglione", "Stand venduti"), M("Saturazione padiglione", "Stand disponibili"),
                   M("Saturazione padiglione", "Mq venduti"), M("Saturazione padiglione", "Mq disponibili"),
                   M("Saturazione padiglione", "Saturazione")], "Stand e metri quadri venduti"),
    ]),
    ("pb03_rinnovi", "PB-03 Espositori e rinnovi", [
        colonne("v03_movimenti", 20, 20, 820, 400, ED,
                [M("Edizione", "Espositori rinnovati"), M("Edizione", "Espositori persi"), M("Edizione", "Espositori nuovi")],
                "Espositori tornati, persi e nuovi"),
        colonne("v03_tasso", 860, 20, 400, 400, ED, [M("Edizione", "Tasso di rinnovo")], "Tasso di rinnovo"),
        tabella_v("v03_tabella", 20, 440, 1240, 260,
                  [ED, ("Edizione", "edizione_precedente"), M("Edizione", "Espositori attuali"),
                   M("Edizione", "Espositori rinnovati"), M("Edizione", "Espositori persi"),
                   M("Edizione", "Espositori nuovi"), M("Edizione", "Tasso di rinnovo")],
                  "Rinnovi per edizione (2026 provvisorio fino al caricamento dei contratti)"),
    ]),
    ("pb04_vendite", "PB-04 Vendite 2026 e incassi", [
        filtro("v04_filtro", 20, 20, 300, 120, "Edizione", "edizione", "Edizione"),
        ciambella("v04_stato", 340, 20, 450, 300, ("Contratti", "stato"), M("Contratti", "Numero contratti"), "Contratti per stato"),
        ciambella("v04_pagamenti", 810, 20, 450, 300, ("Contratti", "stato_pagamenti"), M("Contratti", "Numero contratti"),
                  "Stato dei pagamenti"),
        colonne("v04_imponibile", 20, 160, 300, 160, ("Contratti", "stato"), [M("Contratti", "Imponibile contratti")],
                "Imponibile per stato"),
        tabella_v("v04_tabella", 20, 340, 1240, 360,
                  [("Contratti", "id_contratto"), ("Contratti", "codice_stand"), ("Contratti", "stato"),
                   M("Contratti", "Imponibile contratti"), ("Contratti", "acconto_scadenza"), ("Contratti", "acconto_pagato_il"),
                   ("Contratti", "saldo_scadenza"), ("Contratti", "saldo_pagato_il"), ("Contratti", "stato_pagamenti")],
                  "Contratti dell'edizione"),
    ]),
    ("pb05_pubblico", "PB-05 Pubblico e biglietteria", [
        filtro("v05_filtro", 20, 20, 300, 120, "Edizione", "edizione", "Edizione"),
        linee("v05_giorni", 340, 20, 920, 330, ("Vendite biglietti", "giorno"), [M("Vendite biglietti", "Biglietti venduti")],
              "Biglietti venduti per giorno di acquisto", serie=("Vendite biglietti", "canale")),
        colonne("v05_canali", 20, 370, 400, 330, ("Vendite biglietti", "canale"), [M("Vendite biglietti", "Biglietti venduti")],
                "Biglietti per canale"),
        colonne("v05_conversione", 440, 370, 400, 330, ED, [M("Conversione", "Tasso di conversione")],
                "Biglietti venduti che diventano ingressi"),
        colonne("v05_visitatori", 860, 370, 400, 330, ("Visitatori giorno", "giorno"),
                [M("Visitatori giorno", "Visitatori del giorno")], "Visitatori per giorno di fiera"),
        colonne("v05_ricavo", 20, 160, 300, 190, ED, [M("Vendite biglietti", "Ricavo biglietti")], "Ricavo biglietti"),
    ]),
    ("pb06_affluenza", "PB-06 Affluenza", [
        filtro("v06_filtro", 20, 20, 300, 120, "Edizione", "edizione", "Edizione"),
        linee("v06_curva", 340, 20, 920, 420, ("Presenze", "istante"), [M("Presenze", "Presenti stimati")],
              "Presenze stimate ogni 5 minuti (permanenza 120 minuti)", serie=("Presenze", "padiglione")),
        tabella_v("v06_picco_padiglione", 20, 460, 820, 240,
                  [("Picco padiglione", "edizione"), ("Picco padiglione", "padiglione"), ("Picco padiglione", "istante"),
                   M("Picco padiglione", "Picco del padiglione")], "Picco per padiglione"),
        tabella_v("v06_picco_fiera", 860, 460, 400, 240,
                  [("Picco fiera", "edizione"), ("Picco fiera", "istante"), M("Picco fiera", "Picco della fiera")],
                  "Picco della fiera"),
        colonne("v06_ingressi", 20, 160, 300, 280, ED, [M("Visitatori", "Ingressi ai padiglioni")], "Ingressi ai padiglioni"),
    ]),
    ("pb07_stand", "PB-07 Stand e contatti", [
        filtro("v07_filtro", 20, 20, 300, 120, "Edizione", "edizione", "Edizione"),
        colonne("v07_ore", 340, 20, 920, 330, ("Visite stand", "ora_del_giorno"), [M("Visite stand", "Visite agli stand")],
                "Visite agli stand per ora del giorno", serie=("Visite stand", "padiglione")),
        colonne("v07_costo", 20, 160, 300, 190, ED, [M("Costo contatto fiera", "Costo per contatto")], "Costo per contatto"),
        tabella_v("v07_tabella", 20, 370, 1240, 330,
                  [("Costo contatto", "codice_stand"), ("Costo contatto", "padiglione"), ("Costo contatto", "id_espositore"),
                   M("Costo contatto", "Contatti raccolti"), M("Costo contatto", "Costo per contatto dello stand")],
                  "Costo per contatto per stand (stand senza contatti: costo vuoto)"),
    ]),
]


def genera_report(radice):
    rp = os.path.join(radice, f"{NOME}.Report")
    scrivi_json(os.path.join(rp, "definition.pbir"),
                {"$schema": S + "item/report/definitionProperties/2.0.0/schema.json", "version": "4.0",
                 "datasetReference": {"byPath": {"path": f"../{NOME}.SemanticModel"}}})
    d = os.path.join(rp, "definition")
    scrivi_json(os.path.join(d, "version.json"),
                {"$schema": S + "item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    scrivi_json(os.path.join(d, "report.json"),
                {"$schema": S + "item/report/definition/report/1.0.0/schema.json",
                 "themeCollection": {}, "layoutOptimization": "None"})
    scrivi_json(os.path.join(d, "pages", "pages.json"),
                {"$schema": S + "item/report/definition/pagesMetadata/1.0.0/schema.json",
                 "pageOrder": [p[0] for p in PAGINE], "activePageName": PAGINE[0][0]})
    for nome, titolo, elementi in PAGINE:
        pd = os.path.join(d, "pages", nome)
        scrivi_json(os.path.join(pd, "page.json"),
                    {"$schema": S + "item/report/definition/page/1.0.0/schema.json", "name": nome,
                     "displayName": titolo, "displayOption": "FitToPage", "height": 720, "width": 1280})
        for e in elementi:
            scrivi_json(os.path.join(pd, "visuals", e["name"], "visual.json"), e)


def genera():
    for sotto in (f"{NOME}.SemanticModel", f"{NOME}.Report"):
        p = os.path.join(BASE, sotto)
        if os.path.isdir(p):
            # si rigenera tutto, tranne le impostazioni locali di Desktop (.pbi)
            for voce in os.listdir(p):
                if voce != ".pbi":
                    v = os.path.join(p, voce)
                    shutil.rmtree(v) if os.path.isdir(v) else os.remove(v)
    scrivi_json(os.path.join(BASE, f"{NOME}.pbip"),
                {"$schema": S + "pbip/pbipProperties/1.0.0/schema.json", "version": "1.0",
                 "artifacts": [{"report": {"path": f"{NOME}.Report"}}], "settings": {"enableAutoRecovery": True}})
    genera_modello(BASE)
    genera_report(BASE)
    nvis = sum(len(p[2]) for p in PAGINE)
    print(f"OK: {len(TABELLE)} tabelle, {sum(len(t['misure']) for t in TABELLE)} misure, "
          f"{len(PAGINE)} pagine, {nvis} elementi visivi")


if __name__ == "__main__":
    genera()
