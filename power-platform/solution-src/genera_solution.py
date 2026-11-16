"""Genera la Solution Dataverse non gestita ARCADE BAD (prefisso g5) da importare nel portale.

Fonte: docs/wiki/schema-dataverse.md (che ricalca db/schema.sql). Nessun dato, nessuna app:
solo tabelle, colonne, scelte, relazioni e (opzionale) chiavi alternative.

Uso:
    python -I genera_solution.py            # crea entrambi gli zip in ../solution-build/
Output:
    ARCADEBAD_1_0_0_0.zip              tabelle + relazioni + chiavi alternative
    ARCADEBAD_1_0_0_0_senza_chiavi.zip ripiego se l'import rifiuta le chiavi
"""
import os
import zipfile
from xml.sax.saxutils import quoteattr

LANG = 1040            # italiano: lingua base dell'ambiente (vedi export ARCADEBAD 1.0.0.1)
OPT_PREFIX = 12254     # prefisso dei valori Choice dell'editore Gruppo5BAD
VERSION = "1.0.0.0"


# ---------------------------------------------------------------------------
# Modello: una riga per colonna di schema.sql (47 in tutto)
# ---------------------------------------------------------------------------
def text(name, disp, maxlen, req=False, primary=False, fmt="text"):
    return dict(kind="text", name=name, disp=disp, maxlen=maxlen, req=req, primary=primary, fmt=fmt)

def memo(name, disp, maxlen, req=False):
    return dict(kind="memo", name=name, disp=disp, maxlen=maxlen, req=req)

def dec(name, disp, prec, mn, mx, req=False):
    return dict(kind="decimal", name=name, disp=disp, prec=prec, min=mn, max=mx, req=req)

def whole(name, disp, mn, mx, req=False):
    return dict(kind="int", name=name, disp=disp, min=mn, max=mx, req=req)

def date(name, disp, req=False):
    return dict(kind="date", name=name, disp=disp, req=req)

def yesno(name, disp, req=False):
    return dict(kind="bool", name=name, disp=disp, req=req)

def choice(name, disp, values, req=False):
    return dict(kind="choice", name=name, disp=disp, values=values, req=req)

def lookup(name, disp, target, req=False, cascade_delete=False):
    return dict(kind="lookup", name=name, disp=disp, target=target, req=req, cascade=cascade_delete)

DEC_MAX = 100000000000  # massimo ammesso da Dataverse per il tipo Decimale

TABLES = [
    dict(name="g5_edizione", disp="Edizione", plural="Edizioni", set="g5_edizioni",
         cols=[text("g5_anno", "Anno", 4, True, True),
               date("g5_data_inizio", "Data inizio", True),
               date("g5_data_fine", "Data fine", True),
               text("g5_ora_apertura", "Ora apertura", 5, True),
               text("g5_ora_chiusura", "Ora chiusura", 5, True)],
         keys=[("g5_key_edizione_anno", ["g5_anno"])]),
    dict(name="g5_padiglione", disp="Padiglione", plural="Padiglioni", set="g5_padiglioni",
         cols=[text("g5_codice", "Codice", 2, True, True),
               text("g5_nome", "Nome", 100, True)],
         keys=[("g5_key_padiglione_codice", ["g5_codice"]),
               ("g5_key_padiglione_nome", ["g5_nome"])]),
    dict(name="g5_espositore", disp="Espositore", plural="Espositori", set="g5_espositori",
         cols=[text("g5_id_espositore", "ID espositore", 10, True, True),
               text("g5_ragione_sociale", "Ragione sociale", 200, True),
               text("g5_partita_iva", "Partita IVA", 11, True),
               text("g5_settore", "Settore", 100),
               text("g5_citta", "Città", 100),
               text("g5_referente", "Referente", 200),
               text("g5_email_referente", "Email referente", 200, fmt="email")],
         keys=[("g5_key_espositore_id", ["g5_id_espositore"]),
               ("g5_key_espositore_piva", ["g5_partita_iva"])]),
    dict(name="g5_stand", disp="Stand", plural="Stand", set="g5_stands",
         cols=[text("g5_codice_stand", "Codice stand", 10, True, True),
               lookup("g5_padiglione", "Padiglione", "g5_padiglione", True),
               dec("g5_mq", "Metri quadri", 1, "0.1", "99999.9", True),
               choice("g5_posizione", "Posizione", ["linea", "angolo", "penisola", "isola"], True),
               lookup("g5_attivo_dal", "Attivo dal", "g5_edizione", True)],
         keys=[("g5_key_stand_codice", ["g5_codice_stand"])]),
    dict(name="g5_voce_listino", disp="Voce listino", plural="Voci listino", set="g5_voci_listino",
         cols=[text("g5_codice", "Codice", 20, True, True),
               lookup("g5_edizione", "Edizione", "g5_edizione", True),
               text("g5_descrizione", "Descrizione", 500, True),
               text("g5_unita", "Unità", 50),
               dec("g5_prezzo_unitario", "Prezzo unitario", 2, "-" + str(DEC_MAX), str(DEC_MAX)),
               whole("g5_disponibilita", "Disponibilità", -2147483648, 2147483647),
               memo("g5_note", "Note", 1000)],
         keys=[("g5_key_voce_listino", ["g5_edizione", "g5_codice"])]),
    dict(name="g5_contratto", disp="Contratto", plural="Contratti", set="g5_contratti",
         cols=[text("g5_id_contratto", "ID contratto", 12, True, True),
               lookup("g5_edizione", "Edizione", "g5_edizione", True),
               lookup("g5_espositore", "Espositore", "g5_espositore", True),
               lookup("g5_stand", "Stand", "g5_stand", True),
               choice("g5_stato", "Stato", ["preventivo", "firmato", "annullato"], True),
               date("g5_data_firma", "Data firma"),
               dec("g5_imponibile_listino", "Imponibile a listino", 2, "0", "9999999999.99", True),
               dec("g5_sconto_pct", "Sconto", 4, "0", "1", True),
               dec("g5_imponibile", "Imponibile", 2, "0", "9999999999.99", True),
               date("g5_acconto_scadenza", "Scadenza acconto"),
               date("g5_acconto_pagato_il", "Acconto pagato il"),
               date("g5_saldo_scadenza", "Scadenza saldo"),
               date("g5_saldo_pagato_il", "Saldo pagato il"),
               yesno("g5_rinnovo", "Rinnovo", True)],
         keys=[("g5_key_contratto_id", ["g5_id_contratto"])]),
    dict(name="g5_riga_contratto", disp="Riga contratto", plural="Righe contratto", set="g5_righe_contratto",
         cols=[text("g5_descrizione", "Descrizione", 500, True, True),
               lookup("g5_contratto", "Contratto", "g5_contratto", True, cascade_delete=True),
               whole("g5_riga", "Riga", 1, 32767, True),
               text("g5_codice_voce", "Codice voce", 20, True),
               dec("g5_quantita", "Quantità", 2, "0.01", "99999999.99", True),
               dec("g5_prezzo_unitario", "Prezzo unitario", 2, "-" + str(DEC_MAX), str(DEC_MAX), True),
               dec("g5_importo", "Importo", 2, "-" + str(DEC_MAX), str(DEC_MAX), True)],
         keys=[("g5_key_riga_contratto", ["g5_contratto", "g5_riga"])]),
]


# ---------------------------------------------------------------------------
# XML
# ---------------------------------------------------------------------------
def labels(tag, inner, text_):
    return f"<{tag}><{inner} description={quoteattr(text_)} languagecode=\"{LANG}\" /></{tag}>"

def common_attr(c, custom=True):
    req = "required" if c.get("req") else "none"
    mask = "ValidForAdvancedFind|ValidForForm|ValidForGrid"
    if c.get("primary"):
        mask = "PrimaryName|ValidForAdvancedFind|ValidForForm|ValidForGrid|RequiredForForm"
    return (f"<Name>{c['name']}</Name><LogicalName>{c['name']}</LogicalName>"
            f"<RequiredLevel>{req}</RequiredLevel><DisplayMask>{mask}</DisplayMask>"
            "<ImeMode>auto</ImeMode><ValidForUpdateApi>1</ValidForUpdateApi>"
            "<ValidForReadApi>1</ValidForReadApi><ValidForCreateApi>1</ValidForCreateApi>"
            f"<IsCustomField>{1 if custom else 0}</IsCustomField><IsAuditEnabled>1</IsAuditEnabled>"
            "<IsSecured>0</IsSecured>"
            f"<IntroducedVersion>{VERSION}</IntroducedVersion><IsCustomizable>1</IsCustomizable>"
            "<IsRenameable>1</IsRenameable><CanModifySearchSettings>1</CanModifySearchSettings>"
            "<CanModifyRequirementLevelSettings>1</CanModifyRequirementLevelSettings>"
            "<CanModifyAdditionalSettings>1</CanModifyAdditionalSettings><SourceType>0</SourceType>"
            "<IsGlobalFilterEnabled>0</IsGlobalFilterEnabled><IsSortableEnabled>0</IsSortableEnabled>"
            "<CanModifyGlobalFilterSettings>1</CanModifyGlobalFilterSettings>"
            "<CanModifyIsSortableSettings>1</CanModifyIsSortableSettings>"
            "<IsDataSourceSecret>0</IsDataSourceSecret><AutoNumberFormat></AutoNumberFormat>"
            "<IsSearchable>1</IsSearchable><IsFilterable>0</IsFilterable><IsRetrievable>1</IsRetrievable>"
            "<IsLocalizable>0</IsLocalizable>")

def option_xml(value, label):
    return (f"<option value=\"{value}\" ExternalValue=\"\" IsHidden=\"0\">"
            f"{labels('labels', 'label', label)}</option>")

def attribute_xml(table, c):
    k = c["kind"]
    head = f"<attribute PhysicalName=\"{c['name']}\">"
    names = labels("displaynames", "displayname", c["disp"]) + labels("Descriptions", "Description", "")
    if k == "text":
        body = (f"<Type>nvarchar</Type>{common_attr(c)}<Format>{c['fmt']}</Format>"
                f"<MaxLength>{c['maxlen']}</MaxLength><Length>{c['maxlen'] * 2}</Length>")
    elif k == "memo":
        body = (f"<Type>ntext</Type>{common_attr(c)}<Format>text</Format>"
                f"<MaxLength>{c['maxlen']}</MaxLength>")
    elif k == "decimal":
        body = (f"<Type>decimal</Type>{common_attr(c)}<MinValue>{c['min']}</MinValue>"
                f"<MaxValue>{c['max']}</MaxValue><Accuracy>{c['prec']}</Accuracy>")
    elif k == "int":
        body = (f"<Type>int</Type>{common_attr(c)}<Format>none</Format>"
                f"<MinValue>{c['min']}</MinValue><MaxValue>{c['max']}</MaxValue>")
    elif k == "date":
        # Behavior 2 = "Solo data" (DateOnly): niente fuso orario
        body = (f"<Type>datetime</Type>{common_attr(c)}<Format>date</Format>"
                "<CanChangeDateTimeBehavior>0</CanChangeDateTimeBehavior><Behavior>2</Behavior>")
    elif k == "bool":
        opts = option_xml(1, "Sì") + option_xml(0, "No")
        body = (f"<Type>bit</Type>{common_attr(c)}<AppDefaultValue>0</AppDefaultValue>"
                f"<optionset Name=\"{table['name']}_{c['name']}\"><OptionSetType>bit</OptionSetType>"
                f"<IntroducedVersion>{VERSION}</IntroducedVersion><IsCustomizable>1</IsCustomizable>"
                f"{labels('displaynames', 'displayname', c['disp'])}{labels('Descriptions', 'Description', '')}"
                f"<options>{opts}</options></optionset>")
    elif k == "choice":
        base = OPT_PREFIX * 10000
        opts = "".join(option_xml(base + i, v) for i, v in enumerate(c["values"]))
        body = (f"<Type>picklist</Type>{common_attr(c)}<AppDefaultValue>-1</AppDefaultValue>"
                f"<optionset Name=\"{table['name']}_{c['name']}\"><OptionSetType>picklist</OptionSetType>"
                f"<IsGlobal>0</IsGlobal><IntroducedVersion>{VERSION}</IntroducedVersion>"
                f"<IsCustomizable>1</IsCustomizable>"
                f"{labels('displaynames', 'displayname', c['disp'])}{labels('Descriptions', 'Description', '')}"
                f"<options>{opts}</options></optionset>")
    elif k == "lookup":
        body = (f"<Type>lookup</Type>{common_attr(c)}<LookupStyle>single</LookupStyle>"
                "<LookupTypes />")
    else:
        raise ValueError(k)
    return head + body + names + "</attribute>"

def primarykey_xml(table):
    pk = table["name"] + "id"
    return (f"<attribute PhysicalName=\"{pk}\"><Type>primarykey</Type>"
            f"<Name>{pk}</Name><LogicalName>{pk}</LogicalName>"
            "<RequiredLevel>systemrequired</RequiredLevel>"
            "<DisplayMask>ValidForAdvancedFind|RequiredForGrid</DisplayMask>"
            "<ImeMode>auto</ImeMode><ValidForUpdateApi>0</ValidForUpdateApi>"
            "<ValidForReadApi>1</ValidForReadApi><ValidForCreateApi>1</ValidForCreateApi>"
            "<IsCustomField>0</IsCustomField><IsAuditEnabled>0</IsAuditEnabled>"
            "<IsSecured>0</IsSecured>"
            f"<IntroducedVersion>{VERSION}</IntroducedVersion><IsCustomizable>0</IsCustomizable>"
            "<IsRenameable>0</IsRenameable><CanModifySearchSettings>0</CanModifySearchSettings>"
            "<CanModifyRequirementLevelSettings>0</CanModifyRequirementLevelSettings>"
            "<CanModifyAdditionalSettings>1</CanModifyAdditionalSettings><SourceType>0</SourceType>"
            "<IsGlobalFilterEnabled>0</IsGlobalFilterEnabled><IsSortableEnabled>0</IsSortableEnabled>"
            "<CanModifyGlobalFilterSettings>1</CanModifyGlobalFilterSettings>"
            "<CanModifyIsSortableSettings>1</CanModifyIsSortableSettings>"
            "<IsDataSourceSecret>0</IsDataSourceSecret><AutoNumberFormat></AutoNumberFormat>"
            "<IsSearchable>0</IsSearchable><IsFilterable>1</IsFilterable><IsRetrievable>1</IsRetrievable>"
            "<IsLocalizable>0</IsLocalizable>"
            f"{labels('displaynames', 'displayname', table['disp'])}"
            f"{labels('Descriptions', 'Description', 'Identificatore univoco (GUID di sistema)')}"
            "</attribute>")

def keys_xml(table):
    out = []
    for kname, cols in table["keys"]:
        attrs = "".join(f"<AttributeName>{a}</AttributeName>" for a in cols)
        # ordine degli elementi copiato dall'export reale di Dataverse (ARCADEBAD 1.0.0.1)
        out.append(f"<EntityKey><Name>{kname}</Name><LogicalName>{kname}</LogicalName>"
                   f"<IntroducedVersion>{VERSION}</IntroducedVersion><IsCustomizable>1</IsCustomizable>"
                   f"<EntityKeyAttributes>{attrs}</EntityKeyAttributes>"
                   f"{labels('displaynames', 'displayname', kname)}</EntityKey>")
    return "<EntityKeys>" + "".join(out) + "</EntityKeys>"

ENTITY_FLAGS = """<IsDuplicateCheckSupported>0</IsDuplicateCheckSupported>
<IsBusinessProcessEnabled>0</IsBusinessProcessEnabled><IsRequiredOffline>0</IsRequiredOffline>
<IsInteractionCentricEnabled>0</IsInteractionCentricEnabled><IsCollaboration>0</IsCollaboration>
<AutoRouteToOwnerQueue>0</AutoRouteToOwnerQueue><IsConnectionsEnabled>0</IsConnectionsEnabled>
<EntityColor></EntityColor><IsDocumentManagementEnabled>0</IsDocumentManagementEnabled>
<AutoCreateAccessTeams>0</AutoCreateAccessTeams><IsOneNoteIntegrationEnabled>0</IsOneNoteIntegrationEnabled>
<IsKnowledgeManagementEnabled>0</IsKnowledgeManagementEnabled><IsSLAEnabled>0</IsSLAEnabled>
<IsDocumentRecommendationsEnabled>0</IsDocumentRecommendationsEnabled><IsBPFEntity>0</IsBPFEntity>
<OwnershipTypeMask>OrgOwned</OwnershipTypeMask><IsAuditEnabled>0</IsAuditEnabled>
<IsRetrieveAuditEnabled>0</IsRetrieveAuditEnabled><IsRetrieveMultipleAuditEnabled>0</IsRetrieveMultipleAuditEnabled>
<IsActivity>0</IsActivity><ActivityTypeMask></ActivityTypeMask><IsActivityParty>0</IsActivityParty>
<IsReplicated>0</IsReplicated><IsReplicationUserFiltered>0</IsReplicationUserFiltered>
<IsMailMergeEnabled>0</IsMailMergeEnabled><IsVisibleInMobile>0</IsVisibleInMobile>
<IsVisibleInMobileClient>0</IsVisibleInMobileClient><IsReadOnlyInMobileClient>0</IsReadOnlyInMobileClient>
<IsOfflineInMobileClient>0</IsOfflineInMobileClient><DaysSinceRecordLastModified>0</DaysSinceRecordLastModified>
<MobileOfflineFilters></MobileOfflineFilters><IsMapiGridEnabled>1</IsMapiGridEnabled>
<IsReadingPaneEnabled>1</IsReadingPaneEnabled><IsQuickCreateEnabled>0</IsQuickCreateEnabled>
<SyncToExternalSearchIndex>0</SyncToExternalSearchIndex>"""

ENTITY_TAIL = """<IsCustomizable>1</IsCustomizable><IsRenameable>1</IsRenameable><IsMappable>1</IsMappable>
<CanModifyAuditSettings>1</CanModifyAuditSettings><CanModifyMobileVisibility>1</CanModifyMobileVisibility>
<CanModifyMobileClientVisibility>1</CanModifyMobileClientVisibility><CanModifyMobileClientReadOnly>1</CanModifyMobileClientReadOnly>
<CanModifyMobileClientOffline>1</CanModifyMobileClientOffline><CanModifyConnectionSettings>1</CanModifyConnectionSettings>
<CanModifyDuplicateDetectionSettings>1</CanModifyDuplicateDetectionSettings><CanModifyMailMergeSettings>1</CanModifyMailMergeSettings>
<CanModifyQueueSettings>1</CanModifyQueueSettings><CanCreateAttributes>1</CanCreateAttributes>
<CanCreateForms>1</CanCreateForms><CanCreateCharts>1</CanCreateCharts><CanCreateViews>1</CanCreateViews>
<CanModifyAdditionalSettings>1</CanModifyAdditionalSettings><CanEnableSyncToExternalSearchIndex>1</CanEnableSyncToExternalSearchIndex>
<EnforceStateTransitions>0</EnforceStateTransitions><CanChangeHierarchicalRelationship>1</CanChangeHierarchicalRelationship>
<EntityHelpUrlEnabled>0</EntityHelpUrlEnabled><ChangeTrackingEnabled>1</ChangeTrackingEnabled>
<CanChangeTrackingBeEnabled>1</CanChangeTrackingBeEnabled><IsEnabledForExternalChannels>0</IsEnabledForExternalChannels>
<HasRelatedNotes>False</HasRelatedNotes><HasRelatedActivities>False</HasRelatedActivities>"""

def entity_xml(table, with_keys):
    attrs = primarykey_xml(table) + "".join(attribute_xml(table, c) for c in table["cols"])
    return (f"<Entity><Name LocalizedName={quoteattr(table['disp'])} OriginalName={quoteattr(table['disp'])}>"
            f"{table['name']}</Name><EntityInfo><entity Name=\"{table['name']}\">"
            f"{labels('LocalizedNames', 'LocalizedName', table['disp'])}"
            f"{labels('LocalizedCollectionNames', 'LocalizedCollectionName', table['plural'])}"
            f"{labels('Descriptions', 'Description', 'ARCADE Milano - ricalca arcade.' + table['name'][3:] + ' di db/schema.sql')}"
            f"<attributes>{attrs}</attributes>"
            # le chiavi vanno subito dopo <attributes>: in fondo all'entità l'import le ignora
            f"{keys_xml(table) if with_keys else ''}"
            f"<EntitySetName>{table['set']}</EntitySetName>{ENTITY_FLAGS}"
            f"<IntroducedVersion>{VERSION}</IntroducedVersion>{ENTITY_TAIL}"
            "</entity></EntityInfo></Entity>")

def relationship_xml(table, c):
    rel = f"{c['target']}_{table['name']}_{c['name']}"
    if c["cascade"]:
        # riga_contratto -> contratto: replica ON DELETE CASCADE di schema.sql
        cascade = dict(Assign="NoCascade", Delete="Cascade", Reparent="NoCascade",
                       Share="NoCascade", Unshare="NoCascade")
    else:
        # come una FK senza ON DELETE: non si cancella il padre se ha figli
        cascade = dict(Assign="NoCascade", Delete="Restrict", Reparent="NoCascade",
                       Share="NoCascade", Unshare="NoCascade")
    casc = "".join(f"<Cascade{k}>{v}</Cascade{k}>" for k, v in cascade.items())
    return (f"<EntityRelationship Name=\"{rel}\"><EntityRelationshipType>OneToMany</EntityRelationshipType>"
            f"<IsCustomizable>1</IsCustomizable><IntroducedVersion>{VERSION}</IntroducedVersion>"
            "<IsHierarchical>0</IsHierarchical>"
            f"<ReferencingEntityName>{table['name']}</ReferencingEntityName>"
            f"<ReferencedEntityName>{c['target']}</ReferencedEntityName>"
            f"{casc}<CascadeRollupView>NoCascade</CascadeRollupView>"
            "<IsValidForAdvancedFind>1</IsValidForAdvancedFind>"
            f"<ReferencingAttributeName>{c['name']}</ReferencingAttributeName>"
            f"<RelationshipDescription>{labels('Descriptions', 'Description', '')}</RelationshipDescription>"
            "<EntityRelationshipRoles>"
            "<EntityRelationshipRole><NavPaneDisplayOption>UseCollectionName</NavPaneDisplayOption>"
            "<NavPaneArea>Details</NavPaneArea><NavPaneOrder>10000</NavPaneOrder>"
            f"<NavigationPropertyName>{c['name']}</NavigationPropertyName>"
            "<RelationshipRoleType>1</RelationshipRoleType></EntityRelationshipRole>"
            f"<EntityRelationshipRole><NavigationPropertyName>{rel}</NavigationPropertyName>"
            "<RelationshipRoleType>0</RelationshipRoleType></EntityRelationshipRole>"
            "</EntityRelationshipRoles></EntityRelationship>")

def customizations_xml(with_keys):
    ents = "".join(entity_xml(t, with_keys) for t in TABLES)
    rels = "".join(relationship_xml(t, c) for t in TABLES for c in t["cols"] if c["kind"] == "lookup")
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>"
            "<ImportExportXml xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
            "OrganizationVersion=\"9.2.26104.129\" OrganizationSchemaType=\"Standard\" "
            "CRMServerServiceabilityVersion=\"9.2.26104.00129\">"
            f"<Entities>{ents}</Entities><Roles></Roles><Workflows></Workflows>"
            "<FieldSecurityProfiles></FieldSecurityProfiles><Templates /><EntityMaps />"
            f"<EntityRelationships>{rels}</EntityRelationships><OrganizationSettings /><optionsets />"
            "<CustomControls /><EntityDataProviders />"
            f"<Languages><Language>{LANG}</Language></Languages></ImportExportXml>")

ADDRESS = "".join(
    f"<Address><AddressNumber>{n}</AddressNumber><AddressTypeCode>1</AddressTypeCode>"
    "<City xsi:nil=\"true\"></City><Country xsi:nil=\"true\"></Country><Line1 xsi:nil=\"true\"></Line1>"
    "<Name xsi:nil=\"true\"></Name><PostalCode xsi:nil=\"true\"></PostalCode>"
    "<ShippingMethodCode>1</ShippingMethodCode></Address>" for n in (1, 2))

def solution_xml():
    roots = "".join(f"<RootComponent type=\"1\" schemaName=\"{t['name']}\" behavior=\"0\" />" for t in TABLES)
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>"
            f"<ImportExportXml version=\"9.2.26104.129\" SolutionPackageVersion=\"9.2\" languagecode=\"{LANG}\" "
            "generatedBy=\"CrmLive\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
            "OrganizationVersion=\"9.2.26104.129\" OrganizationSchemaType=\"Standard\" "
            "CRMServerServiceabilityVersion=\"9.2.26104.00129\">"
            "<SolutionManifest><UniqueName>ARCADEBAD</UniqueName>"
            f"{labels('LocalizedNames', 'LocalizedName', 'ARCADE BAD')}<Descriptions />"
            f"<Version>{VERSION}</Version><Managed>0</Managed>"
            "<Publisher><UniqueName>Gruppo5BAD</UniqueName>"
            f"{labels('LocalizedNames', 'LocalizedName', 'Gruppo5BAD')}<Descriptions />"
            "<EMailAddress xsi:nil=\"true\"></EMailAddress><SupportingWebsiteUrl xsi:nil=\"true\"></SupportingWebsiteUrl>"
            f"<CustomizationPrefix>g5</CustomizationPrefix><CustomizationOptionValuePrefix>{OPT_PREFIX}</CustomizationOptionValuePrefix>"
            f"<Addresses>{ADDRESS}</Addresses></Publisher>"
            f"<RootComponents>{roots}</RootComponents><MissingDependencies /></SolutionManifest></ImportExportXml>")

CONTENT_TYPES = ("<?xml version=\"1.0\" encoding=\"utf-8\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
                 "<Default Extension=\"xml\" ContentType=\"application/octet-stream\" /></Types>")


def build(path, with_keys):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("solution.xml", solution_xml())
        z.writestr("customizations.xml", customizations_xml(with_keys))
        z.writestr("[Content_Types].xml", CONTENT_TYPES)


if __name__ == "__main__":
    ncols = sum(len(t["cols"]) for t in TABLES)
    assert ncols == 47, f"attese 47 colonne di schema.sql, trovate {ncols}"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution-build")
    os.makedirs(out, exist_ok=True)
    build(os.path.join(out, "ARCADEBAD_1_0_0_0.zip"), with_keys=True)
    build(os.path.join(out, "ARCADEBAD_1_0_0_0_senza_chiavi.zip"), with_keys=False)
    print(f"OK: 7 tabelle, {ncols} colonne -> {os.path.normpath(out)}")
