"""Inventario in sola lettura della Solution ARCADE BAD -> docs/wiki/inventario-dataverse.md.

Legge customizations.xml di uno zip della Solution (export del portale o versione generata)
e scrive, per ogni tabella: colonne custom (tipo, obbligatoria, lunghezza/precisione/limiti),
chiavi alternative e relazioni. Non tocca Dataverse.

Uso:  python -I inventario.py ../solution-build/ARCADEBAD_1_0_0_2.zip
"""
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


def main(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        root = ET.fromstring(z.read("customizations.xml"))
        sol = ET.fromstring(z.read("solution.xml"))
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
            f"{len(root.findall('Entities/Entity/EntityInfo/entity/EntityKeys/EntityKey'))} chiavi, {len(rels)} relazioni.", ""]
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "wiki", "inventario-dataverse.md")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(out[-2])


if __name__ == "__main__":
    main(sys.argv[1])
