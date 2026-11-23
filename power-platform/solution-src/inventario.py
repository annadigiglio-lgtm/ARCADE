"""Inventario in sola lettura della Solution ARCADE BAD -> docs/wiki/inventario-dataverse.md.

Legge customizations.xml di uno zip della Solution (export del portale o versione generata)
e scrive, per ogni tabella: colonne custom (tipo, obbligatoria, lunghezza/precisione/limiti),
chiavi alternative e relazioni; poi flussi cloud, riferimenti di connessione e variabili
d'ambiente (senza i valori). Non tocca Dataverse.

Uso:  python -I inventario.py ../solution-build/ARCADEBAD_1_0_0_2.zip
"""
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

TIPI = {"nvarchar": "Testo", "ntext": "Testo multiriga", "decimal": "Decimale", "int": "Numero intero",
        "datetime": "Data", "bit": "Sì/No", "picklist": "Scelta", "lookup": "Lookup"}
OBBL = {"required": "Sì", "none": "No", "recommended": "Consigliata", "systemrequired": "Sistema"}


def dettaglio(a):
    t = a.findtext("Type")
    if t in ("nvarchar", "ntext"):
        return f"max {a.findtext('MaxLength')}" + (" (email)" if a.findtext("Format") == "email" else "")
    if t == "decimal":
        return f"precisione {a.findtext('Accuracy')}, min {a.findtext('MinValue')}, max {a.findtext('MaxValue')}"
    if t == "int":
        return f"min {a.findtext('MinValue')}, max {a.findtext('MaxValue')}"
    if t == "datetime":
        return "Solo data" if a.findtext("Behavior") == "2" else f"comportamento {a.findtext('Behavior')}"
    if t in ("picklist", "bit"):
        return ", ".join(o.find("labels/label").get("description") for o in a.findall("optionset/options/option"))
    return ""


TIPI_VAR = {"100000000": "Testo", "100000001": "Numero", "100000002": "Sì/No", "100000003": "JSON"}
CONNETTORI = {"shared_commondataserviceforapps": "Dataverse", "shared_office365": "Office 365 Outlook",
              "shared_onedriveforbusiness": "OneDrive for Business"}


def avvio(trigger):
    """Descrive in breve il trigger di un flusso cloud."""
    t = trigger.get("type")
    if t == "Recurrence":
        r = trigger["recurrence"]
        unita = {"Minute": ("minuto", "minuti"), "Hour": ("ora", "ore"), "Day": ("giorno", "giorni"),
                 "Week": ("settimana", "settimane"), "Month": ("mese", "mesi")}
        sing, plur = unita.get(r["frequency"], (r["frequency"], r["frequency"]))
        ogni = sing if r["interval"] == 1 else f"{r['interval']} {plur}"
        giorni_it = {"Monday": "lunedì", "Tuesday": "martedì", "Wednesday": "mercoledì", "Thursday": "giovedì",
                     "Friday": "venerdì", "Saturday": "sabato", "Sunday": "domenica"}
        quando = dict(r.get("schedule", {}), weekDays=[giorni_it.get(g, g) for g in r.get("schedule", {}).get("weekDays", [])])
        ore = ", ".join(f"{h}:{m:02d}" for h in quando.get("hours", []) for m in quando.get("minutes", [0]))
        giorni = ", ".join(quando["weekDays"])
        return f"ricorrenza ogni {ogni}" + (f" ({giorni})" if giorni else "") + (f" alle {ore}" if ore else "")
    if t == "Request":
        return "dall'app (Power Apps V2)" if trigger.get("kind") == "PowerAppV2" else "manuale (pulsante)"
    if t == "OpenApiConnectionWebhook":
        p = trigger["inputs"]["parameters"]
        msg = {1: "creata", 2: "eliminata", 3: "modificata", 4: "creata o modificata"}.get(p.get("subscriptionRequest/message"), "?")
        return f"riga di `{p.get('subscriptionRequest/entityname')}` {msg}"
    return t


def flussi(z, root):
    """Righe markdown per flussi, riferimenti di connessione e variabili d'ambiente."""
    righe, uso = [], {}
    for w in root.findall("Workflows/Workflow"):
        js = w.findtext("JsonFileName").lstrip("/")
        d = json.loads(z.read(js).decode("utf-8-sig"))["properties"]
        refs = {k: v["connection"]["connectionReferenceLogicalName"] for k, v in d.get("connectionReferences", {}).items()}
        for r in refs.values():
            uso.setdefault(r, []).append(w.get("Name").split("–")[1].strip() if "–" in w.get("Name") else w.get("Name"))
        trig = next(iter(d["definition"]["triggers"].values()))
        righe.append(f"| {w.get('Name')} | {'attivo' if w.findtext('StateCode') == '1' else 'spento'} | {avvio(trig)} "
                     f"| {', '.join(CONNETTORI.get(k, k) for k in refs)} |")
    out = ["## Flussi cloud", "", "| Flusso | Stato | Avvio | Connettori |", "|---|---|---|---|", *sorted(righe), "",
           "## Riferimenti di connessione", "", "| Nome | Connettore | Usato da |", "|---|---|---|"]
    for c in root.findall("connectionreferences/connectionreference"):
        nome = c.get("connectionreferencelogicalname")
        con = c.findtext("connectorid").rsplit("/", 1)[-1]
        out.append(f"| `{nome}` | {CONNETTORI.get(con, con)} | {', '.join(sorted(uso.get(nome, []))) or 'nessun flusso'} |")
    out += ["", "## Variabili d'ambiente", "",
            "I valori non si riportano qui: contengono indirizzi email del team.", "",
            "| Nome | Tipo | Valore predefinito | Valore corrente nell'export |", "|---|---|---|---|"]
    cartelle = sorted({n.split("/")[1] for n in z.namelist() if n.startswith("environmentvariabledefinitions/")})
    for c in cartelle:
        x = ET.fromstring(z.read(f"environmentvariabledefinitions/{c}/environmentvariabledefinition.xml"))
        valore = f"environmentvariabledefinitions/{c}/environmentvariablevalues.json" in z.namelist()
        out.append(f"| `{x.get('schemaname')}` | {TIPI_VAR.get(x.findtext('type'), x.findtext('type'))} "
                   f"| {'sì' if x.findtext('defaultvalue') else 'no'} | {'sì' if valore else 'no'} |")
    return out + [""]


def main(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        root = ET.fromstring(z.read("customizations.xml"))
        sol = ET.fromstring(z.read("solution.xml"))
        parte_flussi = flussi(z, root)
    rels = [r for r in root.findall("EntityRelationships/EntityRelationship") if r.get("Name").startswith("g5_")]
    out = ["# Stato Dataverse – Solution ARCADE BAD", "",
           f"Generato da `power-platform/solution-src/inventario.py` su `{os.path.basename(zip_path)}` "
           f"(versione {sol.findtext('SolutionManifest/Version')}, editore "
           f"{sol.findtext('SolutionManifest/Publisher/UniqueName')}, prefisso "
           f"`{sol.findtext('SolutionManifest/Publisher/CustomizationPrefix')}`). Sola lettura.", "",
           "Colonne di sistema (`createdon`, `ownerid`, `statecode`, GUID `g5_<tabella>id`…) escluse: "
           "non fanno parte di `schema.sql`.", ""]
    for e in root.findall("Entities/Entity"):
        name = e.findtext("Name")
        info = e.find("EntityInfo/entity")
        attrs = [a for a in info.findall("attributes/attribute") if a.findtext("IsCustomField") == "1"]
        out += [f"## `{name}` – {info.find('LocalizedNames/LocalizedName').get('description')}", "",
                f"Proprietà: {info.findtext('OwnershipTypeMask')}; change tracking: "
                f"{'sì' if info.findtext('ChangeTrackingEnabled') == '1' else 'no'}; "
                f"entity set Web API: `{info.findtext('EntitySetName')}`.", "",
                "| Colonna | Nome | Tipo | Obbl. | Dettaglio |", "|---|---|---|---|---|"]
        for a in attrs:
            prim = " **(primaria)**" if "PrimaryName" in (a.findtext("DisplayMask") or "") else ""
            out.append(f"| `{a.findtext('LogicalName')}`{prim} | {a.find('displaynames/displayname').get('description')} "
                       f"| {TIPI.get(a.findtext('Type'), a.findtext('Type'))} "
                       f"| {OBBL.get(a.findtext('RequiredLevel'), a.findtext('RequiredLevel'))} | {dettaglio(a)} |")
        keys = info.findall("EntityKeys/EntityKey")
        out += ["", "Chiavi alternative: " + ("; ".join(
            f"`{k.findtext('LogicalName')}` = ({', '.join(x.text for x in k.findall('EntityKeyAttributes/AttributeName'))})"
            for k in keys) or "nessuna")]
        mine = [r for r in rels if r.findtext("ReferencingEntityName") == name]
        out += ["", "Relazioni N:1: " + ("; ".join(
            f"`{r.findtext('ReferencingAttributeName')}` → `{r.findtext('ReferencedEntityName')}` "
            f"(eliminazione: {r.findtext('CascadeDelete')})" for r in mine) or "nessuna"), ""]
    out += [f"Totale: {len(root.findall('Entities/Entity'))} tabelle, "
            f"{sum(1 for e in root.findall('Entities/Entity') for a in e.findall('EntityInfo/entity/attributes/attribute') if a.findtext('IsCustomField') == '1')} colonne custom, "
            f"{len(root.findall('Entities/Entity/EntityInfo/entity/EntityKeys/EntityKey'))} chiavi, {len(rels)} relazioni, "
            f"{len(root.findall('Workflows/Workflow'))} flussi.", ""]
    out[-2:-2] = parte_flussi
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "wiki", "inventario-dataverse.md")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(out[-2])


if __name__ == "__main__":
    main(sys.argv[1])
