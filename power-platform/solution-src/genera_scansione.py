"""Genera una Solution non gestita separata con la sola tabella g5_scansione_stand.

Perché separata: importare di nuovo ARCADE BAD intera sovrascriverebbe app e flussi
con la versione dello zip. Questa soluzione contiene solo la tabella nuova; dopo l'import
la tabella si aggiunge ad ARCADE BAD con "Aggiungi esistente".

Fonte: power-platform/app-scansione/README.md §5.1 (ricalca arcade.scansione_stand di db/schema.sql).
Prima dell'import la tabella g5_scansione_stand dell'export 1.0.0.5 va eliminata dal portale.

Uso (dalla cartella power-platform/solution-src):
    python -I genera_scansione.py
Output: ../solution-build/ARCADEBADScansione_1_0_0_0.zip
"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I non aggiunge la cartella dello script
from genera_solution import (ADDRESS, CONTENT_TYPES, LANG, OPT_PREFIX, datetime_, entity_xml,
                             labels, lookup, relationship_xml, text, whole)

NOME_SOLUZIONE = "ARCADEBADScansione"
VERSIONE = "1.0.0.0"

SCANSIONE = dict(
    name="g5_scansione_stand", disp="Scansione stand", plural="Scansioni stand", set="g5_scansione_stands",
    cols=[text("g5_id_scansione", "ID scansione", 36, True, True),
          lookup("g5_edizione", "Edizione", "g5_edizione", True),
          lookup("g5_stand", "Stand", "g5_stand", True),
          datetime_("g5_rilevato_il", "Rilevato il", True),
          whole("g5_quantita", "Quantità", 0, 1000, True),
          text("g5_origine", "Origine", 20, True)],
    keys=[("g5_key_scansione_stand", ["g5_id_scansione"])])


def customizations_xml():
    # Proprietà dell'utente (non dell'organizzazione): il ruolo ARCADE Scansione può
    # eliminare solo le righe create da chi ha scansionato ("Annulla ultima", README §5.3).
    # La proprietà non si può cambiare dopo la creazione della tabella.
    ent = entity_xml(SCANSIONE, with_keys=True).replace(
        "<OwnershipTypeMask>OrgOwned</OwnershipTypeMask>", "<OwnershipTypeMask>UserOwned</OwnershipTypeMask>")
    rels = "".join(relationship_xml(SCANSIONE, c) for c in SCANSIONE["cols"] if c["kind"] == "lookup")
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>"
            "<ImportExportXml xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
            "OrganizationVersion=\"9.2.26112.139\" OrganizationSchemaType=\"Standard\" "
            "CRMServerServiceabilityVersion=\"9.2.26113.00135\">"
            f"<Entities>{ent}</Entities><Roles></Roles><Workflows></Workflows>"
            "<FieldSecurityProfiles></FieldSecurityProfiles><Templates /><EntityMaps />"
            f"<EntityRelationships>{rels}</EntityRelationships><OrganizationSettings /><optionsets />"
            "<CustomControls /><EntityDataProviders />"
            f"<Languages><Language>{LANG}</Language></Languages></ImportExportXml>")


def solution_xml():
    # Le tabelle collegate (g5_edizione, g5_stand) esistono già nell'ambiente: non sono nella soluzione
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>"
            f"<ImportExportXml version=\"9.2.26112.139\" SolutionPackageVersion=\"9.2\" languagecode=\"{LANG}\" "
            "generatedBy=\"CrmLive\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
            "OrganizationVersion=\"9.2.26112.139\" OrganizationSchemaType=\"Standard\" "
            "CRMServerServiceabilityVersion=\"9.2.26113.00135\">"
            f"<SolutionManifest><UniqueName>{NOME_SOLUZIONE}</UniqueName>"
            f"{labels('LocalizedNames', 'LocalizedName', 'ARCADE BAD scansioni')}<Descriptions />"
            f"<Version>{VERSIONE}</Version><Managed>0</Managed>"
            "<Publisher><UniqueName>Gruppo5BAD</UniqueName>"
            f"{labels('LocalizedNames', 'LocalizedName', 'Gruppo5BAD')}<Descriptions />"
            "<EMailAddress xsi:nil=\"true\"></EMailAddress><SupportingWebsiteUrl xsi:nil=\"true\"></SupportingWebsiteUrl>"
            f"<CustomizationPrefix>g5</CustomizationPrefix><CustomizationOptionValuePrefix>{OPT_PREFIX}</CustomizationOptionValuePrefix>"
            f"<Addresses>{ADDRESS}</Addresses></Publisher>"
            f"<RootComponents><RootComponent type=\"1\" schemaName=\"{SCANSIONE['name']}\" behavior=\"0\" /></RootComponents>"
            "<MissingDependencies /></SolutionManifest></ImportExportXml>")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution-build")
    nome = f"{NOME_SOLUZIONE}_{VERSIONE.replace('.', '_')}.zip"
    with zipfile.ZipFile(os.path.join(out, nome), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("solution.xml", solution_xml())
        z.writestr("customizations.xml", customizations_xml())
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
    print(f"OK: g5_scansione_stand, {len(SCANSIONE['cols'])} colonne, 1 chiave -> {os.path.normpath(os.path.join(out, nome))}")
