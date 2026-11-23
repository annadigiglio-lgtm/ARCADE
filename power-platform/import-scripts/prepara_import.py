"""Prepara i file di import Dataverse dai dati puliti di BID e li valida. Non scrive nulla in Dataverse.

Ingresso: power-platform/data/cleaned/  (letti in sola lettura da Supabase, schema arcade, 2026-11-03)
Uscita:   power-platform/data/import/
  NN_<tabella>.csv   formato di scambio (power-platform/README.md): nomi SQL, date AAAA-MM-GG, punto decimale
  NN_<tabella>.xlsx  per "Importa dati da Excel" del portale: intestazioni = nomi visualizzati Dataverse,
                     numeri e date come celle Excel (niente problemi di virgola/punto), lookup = codice
  report_validazione.md  conteggi, chiavi orfane, formati, totali di controllo (nessun dato personale)

Uso:  python prepara_import.py
"""
import csv
import os
import re
import sys
from datetime import date
from decimal import Decimal

from openpyxl import Workbook

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
SRC, OUT = os.path.join(BASE, "cleaned"), os.path.join(BASE, "import")

# Totali letti da Supabase con la stessa sessione: servono a provare che i file locali sono completi
ATTESI = {"conteggi": {"edizione": 3, "padiglione": 3, "espositore": 135, "stand": 130,
                       "voce_listino": 20, "contratto": 198, "riga_contratto": 950},
          "tot_importo": Decimal("1604733.50"), "tot_quantita": Decimal("12880.00"),
          "tot_imponibile": Decimal("1528040.95"), "tot_mq": Decimal("4677.0")}

# Descrizioni delle righe: in Supabase dipendono solo dal codice voce (verificato: 0 eccezioni);
# SPAZIO e MAGG dipendono dallo stand del contratto
DESCRIZIONE_VOCE = {
    "EX-ARR": "Arredo base", "EX-EL3": "Allaccio elettrico", "EX-EL6": "Allaccio elettrico",
    "EX-FIBRA": "Connessione fibra dedicata", "EX-PARK": "Parcheggio carico/scarico",
    "EX-PASS": "Pass espositore aggiuntivi", "SP-BADGE": "Logo su braccialetto d'ingresso",
    "SP-COSPLAY": "Sponsor contest cosplay", "SP-INDIE": "Sponsor Indie Showcase",
    "SP-SOCIAL": "Pacchetto contenuti social", "SP-STAGE": "Naming Main Stage",
    "SP-TORNEO": "Sponsor torneo esports",
}

# Colonne in uscita: (nome SQL, nome visualizzato Dataverse, tipo per Excel)
COLONNE = {
    "edizione": [("anno", "Anno", "t"), ("data_inizio", "Data inizio", "d"), ("data_fine", "Data fine", "d"),
                 ("ora_apertura", "Ora apertura", "t"), ("ora_chiusura", "Ora chiusura", "t")],
    "padiglione": [("codice", "Codice", "t"), ("nome", "Nome", "t")],
    "espositore": [("id_espositore", "ID espositore", "t"), ("ragione_sociale", "Ragione sociale", "t"),
                   ("partita_iva", "Partita IVA", "t"), ("settore", "Settore", "t"), ("citta", "Città", "t"),
                   ("referente", "Referente", "t"), ("email_referente", "Email referente", "t")],
    "stand": [("codice_stand", "Codice stand", "t"), ("padiglione", "Padiglione", "t"), ("mq", "Metri quadri", "n"),
              ("posizione", "Posizione", "t"), ("attivo_dal", "Attivo dal", "t")],
    "voce_listino": [("codice", "Codice", "t"), ("edizione", "Edizione", "t"), ("descrizione", "Descrizione", "t"),
                     ("unita", "Unità", "t"), ("prezzo_unitario", "Prezzo unitario", "n"),
                     ("disponibilita", "Disponibilità", "n"), ("note", "Note", "t")],
    "contratto": [("id_contratto", "ID contratto", "t"), ("edizione", "Edizione", "t"),
                  ("id_espositore", "Espositore", "t"), ("codice_stand", "Stand", "t"), ("stato", "Stato", "t"),
                  ("data_firma", "Data firma", "d"), ("imponibile_listino", "Imponibile a listino", "n"),
                  ("sconto_pct", "Sconto", "n"), ("imponibile", "Imponibile", "n"),
                  ("acconto_scadenza", "Scadenza acconto", "d"), ("acconto_pagato_il", "Acconto pagato il", "d"),
                  ("saldo_scadenza", "Scadenza saldo", "d"), ("saldo_pagato_il", "Saldo pagato il", "d"),
                  ("rinnovo", "Rinnovo", "b")],
    "riga_contratto": [("descrizione", "Descrizione", "t"), ("id_contratto", "Contratto", "t"), ("riga", "Riga", "n"),
                       ("codice_voce", "Codice voce", "t"), ("quantita", "Quantità", "n"),
                       ("prezzo_unitario", "Prezzo unitario", "n"), ("importo", "Importo", "n")],
}
ORDINE = ["edizione", "padiglione", "espositore", "stand", "voce_listino", "contratto", "riga_contratto"]


def leggi(nome):
    with open(os.path.join(SRC, nome + ".csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def espandi_righe(contratti, stand):
    """Ricostruisce le 950 righe dal formato compatto 'id:riga codice quantita prezzo;...'."""
    per_id = {c["id_contratto"]: c for c in contratti}
    righe = []
    with open(os.path.join(SRC, "riga_contratto_compatto.txt"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            idc, voci = line.split(":", 1)
            st = stand.get(per_id[idc]["codice_stand"]) if idc in per_id else None
            for voce in voci.split(";"):
                n, codice, q, p = voce.split(" ")
                if codice == "SPAZIO":
                    descr = "Area espositiva " + per_id[idc]["codice_stand"]
                elif codice == "MAGG":
                    descr = "Maggiorazione " + st["posizione"]
                else:
                    descr = DESCRIZIONE_VOCE[codice]
                q, p = Decimal(q), Decimal(p)
                righe.append({"id_contratto": idc, "riga": n, "codice_voce": codice, "descrizione": descr,
                              "quantita": f"{q:.2f}", "prezzo_unitario": f"{p:.2f}",
                              "importo": f"{(q * p).quantize(Decimal('0.01')):.2f}"})
    return righe


def valida(t):
    err, info = [], []
    ok_data = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def data(v, dove):
        if v and not ok_data.match(v):
            err.append(f"{dove}: data non AAAA-MM-GG ({v})")
        elif v:
            date.fromisoformat(v)

    for nome, attesi in ATTESI["conteggi"].items():
        n = len(t[nome])
        (info if n == attesi else err).append(f"{nome}: {n} righe (attese {attesi})")

    anni = {e["anno"] for e in t["edizione"]}
    pad = {p["codice"] for p in t["padiglione"]}
    esp = {e["id_espositore"] for e in t["espositore"]}
    std = {s["codice_stand"] for s in t["stand"]}
    ctr = {c["id_contratto"] for c in t["contratto"]}

    for e in t["edizione"]:
        data(e["data_inizio"], "edizione"); data(e["data_fine"], "edizione")
        if e["data_fine"] < e["data_inizio"]:
            err.append(f"edizione {e['anno']}: data_fine < data_inizio (R4)")
    piva = [e["partita_iva"] for e in t["espositore"]]
    for e in t["espositore"]:
        if not re.fullmatch(r"\d{11}", e["partita_iva"]):
            err.append(f"espositore {e['id_espositore']}: partita IVA non di 11 cifre (R3)")
    if len(set(piva)) != len(piva):
        err.append("espositore: partita IVA duplicata (chiave alternativa)")
    for s in t["stand"]:
        if s["padiglione"] not in pad: err.append(f"stand {s['codice_stand']}: padiglione orfano")
        if s["attivo_dal"] not in anni: err.append(f"stand {s['codice_stand']}: attivo_dal orfano")
        if Decimal(s["mq"]) <= 0: err.append(f"stand {s['codice_stand']}: mq <= 0")
        if s["posizione"] not in ("linea", "angolo", "penisola", "isola"):
            err.append(f"stand {s['codice_stand']}: posizione non valida")
    chiavi_vl = [(v["edizione"], v["codice"]) for v in t["voce_listino"]]
    if len(set(chiavi_vl)) != len(chiavi_vl): err.append("voce_listino: (edizione, codice) duplicata")
    for v in t["voce_listino"]:
        if v["edizione"] not in anni: err.append(f"voce_listino {v['codice']}: edizione orfana")

    occupati = set()
    for c in t["contratto"]:
        k = c["id_contratto"]
        if c["edizione"] not in anni: err.append(f"{k}: edizione orfana")
        if c["id_espositore"] not in esp: err.append(f"{k}: espositore orfano")
        if c["codice_stand"] not in std: err.append(f"{k}: stand orfano")
        if c["stato"] not in ("preventivo", "firmato", "annullato"): err.append(f"{k}: stato non valido")
        if c["stato"] == "firmato" and not c["data_firma"]: err.append(f"{k}: firmato senza data_firma (R2)")
        if not (Decimal(0) <= Decimal(c["sconto_pct"]) <= Decimal(1)): err.append(f"{k}: sconto_pct fuori 0..1")
        if c["rinnovo"] not in ("t", "f"): err.append(f"{k}: rinnovo non t/f")
        for col in ("data_firma", "acconto_scadenza", "acconto_pagato_il", "saldo_scadenza", "saldo_pagato_il"):
            data(c[col], k)
        if c["stato"] != "annullato":
            chiave = (c["edizione"], c["codice_stand"])
            if chiave in occupati: err.append(f"{k}: stand già venduto nella stessa edizione (R1)")
            occupati.add(chiave)

    viste = set()
    for r in t["riga_contratto"]:
        if r["id_contratto"] not in ctr: err.append(f"riga {r['id_contratto']}/{r['riga']}: contratto orfano")
        if (r["id_contratto"], r["riga"]) in viste: err.append(f"riga {r['id_contratto']}/{r['riga']}: duplicata")
        viste.add((r["id_contratto"], r["riga"]))
        if Decimal(r["quantita"]) <= 0: err.append(f"riga {r['id_contratto']}/{r['riga']}: quantita <= 0")

    tot = {"tot_importo": sum(Decimal(r["importo"]) for r in t["riga_contratto"]),
           "tot_quantita": sum(Decimal(r["quantita"]) for r in t["riga_contratto"]),
           "tot_imponibile": sum(Decimal(c["imponibile"]) for c in t["contratto"]),
           "tot_mq": sum(Decimal(s["mq"]) for s in t["stand"])}
    for k, v in tot.items():
        (info if v == ATTESI[k] else err).append(f"{k}: {v} (Supabase {ATTESI[k]})")

    # Solo segnalazione: regola non presente in schema.sql, quindi non è un vincolo
    diff = []
    somme = {}
    for r in t["riga_contratto"]:
        somme[r["id_contratto"]] = somme.get(r["id_contratto"], 0) + Decimal(r["importo"])
    for c in t["contratto"]:
        if somme.get(c["id_contratto"], 0) != Decimal(c["imponibile_listino"]):
            diff.append(c["id_contratto"])
    info.append(f"segnalazione: contratti con somma righe ≠ imponibile_listino: {len(diff)}"
                + (f" (es. {', '.join(diff[:5])})" if diff else ""))
    return err, info


def scrivi(t):
    os.makedirs(OUT, exist_ok=True)
    for i, nome in enumerate(ORDINE, 1):
        cols = COLONNE[nome]
        base = os.path.join(OUT, f"{i:02d}_{nome}")
        with open(base + ".csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerow([c[0] for c in cols])
            for r in t[nome]:
                w.writerow([r[c[0]] for c in cols])
        wb = Workbook()
        ws = wb.active
        ws.title = nome
        ws.append([c[1] for c in cols])
        for r in t[nome]:
            riga = []
            for col, _, tipo in cols:
                v = r[col]
                if v == "":
                    riga.append(None)
                elif tipo == "n":
                    riga.append(float(Decimal(v)) if "." in v else int(v))
                elif tipo == "d":
                    riga.append(date.fromisoformat(v))
                elif tipo == "b":
                    riga.append("Sì" if v == "t" else "No")
                else:
                    riga.append(v)
            ws.append(riga)
        for col_cells in ws.iter_cols(min_row=2):
            for cell in col_cells:
                if isinstance(cell.value, date):
                    cell.number_format = "yyyy-mm-dd"
                elif isinstance(cell.value, str):
                    cell.number_format = "@"  # testo: la partita IVA conserva gli zeri iniziali
        wb.save(base + ".xlsx")


def main():
    t = {n: leggi(n) for n in ORDINE[:-1]}
    stand = {s["codice_stand"]: s for s in t["stand"]}
    t["riga_contratto"] = espandi_righe(t["contratto"], stand)
    err, info = valida(t)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report_validazione.md"), "w", encoding="utf-8") as f:
        f.write("# Report di validazione import Dataverse\n\n")
        f.write(f"Esito: **{'OK' if not err else 'ERRORI'}** ({len(err)} errori)\n\n## Controlli superati\n\n")
        f.writelines(f"- {x}\n" for x in info)
        if err:
            f.write("\n## Errori\n\n")
            f.writelines(f"- {x}\n" for x in err)
        f.write("\nControlli: conteggi, chiavi orfane, unicità delle chiavi alternative, formati (date, "
                "partita IVA, scelte, sconto), R1 stand unico per edizione, R2 firmato con data, "
                "R4 date edizione, totali di controllo confrontati con Supabase.\n")
    if err:
        print("ERRORI:", *err[:20], sep="\n  ")
        sys.exit(1)
    scrivi(t)
    print("OK:", *info, sep="\n  ")


if __name__ == "__main__":
    main()
