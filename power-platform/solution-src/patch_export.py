"""Corregge l'export reale di ARCADE BAD e produce una nuova versione da reimportare.

Parte dall'export non gestito scaricato dal portale (formato garantito da Dataverse) e aggiunge:
  1. le chiavi alternative mancanti (le stesse di genera_solution.py / docs/wiki/schema-dataverse.md);
  2. tutte le colonne di schema.sql nelle viste (pubblica, ricerca avanzata, associata, ricerca);
  3. i campi di ricerca rapida utili (es. ragione sociale e partita IVA dell'espositore).

Uso:
    python -I patch_export.py <cartella export estratto> <versione nuova>
    python -I patch_export.py ../solution/export_1_0_0_1_raw 1.0.0.2
Output: ../solution-build/ARCADEBAD_<versione>.zip
"""
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I non aggiunge la cartella dello script
from genera_solution import TABLES, LANG  # una sola definizione del modello

# Campi aggiuntivi per la ricerca rapida (oltre alla colonna primaria, già presente)
QUICK_FIND = {
    "g5_espositore": ["g5_ragione_sociale", "g5_partita_iva", "g5_citta"],
    "g5_padiglione": ["g5_nome"],
    "g5_voce_listino": ["g5_descrizione"],
    "g5_riga_contratto": ["g5_codice_voce"],
}
# Viste da completare: 0 pubblica, 1 ricerca avanzata, 2 associata, 4 ricerca rapida, 64 ricerca (lookup)
VIEW_TYPES = {"0", "1", "2", "4", "64"}


def add_keys(entity, table):
    info = entity.find("EntityInfo/entity")
    keys = info.find("EntityKeys")
    if keys is None:
        keys = ET.Element("EntityKeys")
        attrs_pos = list(info).index(info.find("attributes"))
        info.insert(attrs_pos + 1, keys)  # subito dopo <attributes>, come nell'export
    present = {k.findtext("LogicalName") for k in keys.findall("EntityKey")}
    added = 0
    for kname, cols in table["keys"]:
        if kname in present:
            continue
        schema = kname.replace("g5_key_", "g5_KEY_")
        k = ET.SubElement(keys, "EntityKey")
        ET.SubElement(k, "Name").text = schema
        ET.SubElement(k, "LogicalName").text = kname
        ET.SubElement(k, "IntroducedVersion").text = "1.0.0.0"
        ET.SubElement(k, "IsCustomizable").text = "0"
        ka = ET.SubElement(k, "EntityKeyAttributes")
        for c in cols:
            ET.SubElement(ka, "AttributeName").text = c
        dn = ET.SubElement(k, "displaynames")
        ET.SubElement(dn, "displayname", description=schema.replace("g5_", ""), languagecode=str(LANG))
        added += 1
    return added


def complete_view(query, table):
    cols = [c["name"] for c in table["cols"]]
    primary = next(c["name"] for c in table["cols"] if c.get("primary"))
    row = query.find("layoutxml/grid/row")
    if row is not None:
        for cell in list(row):
            row.remove(cell)
        for c in cols:
            width = "300" if c == primary else "150"
            ET.SubElement(row, "cell", name=c, width=width)
    ent = query.find("fetchxml/fetch/entity")
    if ent is not None:
        have = {a.get("name") for a in ent.findall("attribute")}
        pos = len(ent.findall("attribute"))
        for c in cols:
            if c not in have:
                ent.insert(pos, ET.Element("attribute", name=c))
                pos += 1
        if query.findtext("querytype") == "4":
            qf = next((f for f in ent.findall("filter") if f.get("isquickfindfields") == "1"), None)
            if qf is not None:
                there = {cnd.get("attribute") for cnd in qf.findall("condition")}
                for c in QUICK_FIND.get(table["name"], []):
                    if c not in there:
                        ET.SubElement(qf, "condition", attribute=c, operator="like", value="{0}")


def main(src, version):
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
    cust = ET.parse(os.path.join(src, "customizations.xml"))
    by_name = {t["name"]: t for t in TABLES}
    keys_added, views = 0, 0
    for entity in cust.getroot().findall("Entities/Entity"):
        name = entity.findtext("Name")
        table = by_name[name]
        keys_added += add_keys(entity, table)
        for q in entity.findall("SavedQueries/savedqueries/savedquery"):
            if q.findtext("querytype") in VIEW_TYPES:
                complete_view(q, table)
                views += 1

    sol = ET.parse(os.path.join(src, "solution.xml"))
    sol.getroot().find("SolutionManifest/Version").text = version

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution-build")
    out = os.path.normpath(os.path.join(out_dir, f"ARCADEBAD_{version.replace('.', '_')}.zip"))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("solution.xml", ET.tostring(sol.getroot(), encoding="utf-8", xml_declaration=True))
        z.writestr("customizations.xml", ET.tostring(cust.getroot(), encoding="utf-8", xml_declaration=True))
        with open(os.path.join(src, "[Content_Types].xml"), "rb") as f:
            z.writestr("[Content_Types].xml", f.read())
    print(f"OK: +{keys_added} chiavi, {views} viste completate, versione {version} -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
