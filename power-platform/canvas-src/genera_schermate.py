"""Genera le schermate dell'app Canvas "FUSIONWORK-BACKOFFICE Commerciale" in formato .pa.yaml.

Le schermate condividono barra laterale, intestazione e tema (App.Formulas), quindi qui sono
definiti una volta sola. Poi `pac canvas pack` crea il .msapp da aprire in Power Apps Studio.

Uso:
    python -I genera_schermate.py
    pac canvas pack --sources backoffice_src --msapp FUSIONWORK-BACKOFFICE_v1.msapp --layout SourceCode

Scelte:
- Controlli classici (Label, Rectangle, Classic/Button, Classic/TextInput, Classic/DropDown, Gallery):
  proprietà stabili e note, così il codice si può spiegare riga per riga.
- I dati arrivano dalle 7 tabelle g5_ già collegate. Contratti e Stand si copiano in collezioni con
  colonne "piatte" (AnnoEd, CodStand, ...): le formule restano corte e non rileggono le lookup ogni volta.
- Libero/venduto non è salvato da nessuna parte: si calcola dai contratti non annullati dell'edizione.
"""
import os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backoffice_src", "Src")
HEADER = "# Generato da power-platform/canvas-src/genera_schermate.py\n"
W, H, SIDE = 1366, 768, 220          # schermo tablet dell'app e larghezza della barra laterale
X0 = SIDE + 28                       # inizio dell'area contenuti


def fx(value, indent):
    """Formula Power Fx come valore YAML: blocco |- per quelle lunghe o con caratteri speciali."""
    s = str(value)
    if "\n" in s or any(c in s for c in ":#{}[]&,'\"") or len(s) > 60:
        pad = " " * (indent + 2)
        return "|-\n" + "\n".join(pad + line for line in ("=" + s).split("\n"))
    return "=" + s


# Etichette per i lettori di schermo (note "Accessibilità" di Verifica app)
ETICHETTE = {
    "hm_galUltimi": "Ultimi contratti firmati", "hm_galPad": "Occupazione per padiglione",
    "st_galStand": "Planimetria degli stand", "nv_galStand": "Stand liberi selezionabili",
    "es_galEsp": "Elenco espositori", "nv_galEsp": "Elenco espositori", "ct_galContratti": "Elenco contratti",
    "ct_galRighe": "Righe del contratto", "nv_galStorico": "Storico contratti dell'espositore",
    "nv_galExtra": "Servizi aggiuntivi del listino", "nv_galRiep": "Servizi selezionati",
    "es_txtCerca": "Cerca espositore", "ct_txtCerca": "Cerca contratto", "nv_txtCerca": "Cerca espositore",
    "es_txtRag": "Ragione sociale", "es_txtPiva": "Partita IVA", "es_txtSett": "Settore", "es_txtCitta": "Città",
    "es_txtRef": "Referente", "es_txtMail": "Email referente",
    "hm_ddEdizione": "Edizione", "ct_ddEdizione": "Edizione",
    "sc_ddEdizione": "Edizione", "sc_txtCerca": "Cerca pagamento", "sc_galPag": "Elenco pagamenti",
    "rn_ddEdizione": "Edizione", "rn_txtCerca": "Cerca espositore", "rn_galRinn": "Espositori da riconfermare",
    "ls_galListino": "Voci di listino", "ls_txtPrezzo": "Prezzo unitario", "ls_txtDisp": "Disponibilità",
    "ls_txtNote": "Note", "ck_galAnom": "Anomalie del controllo selezionato",
}


def control(name, kind, props, children=None, variant=None, indent=6):
    pad = " " * indent
    out = [f"{pad}- {name}:", f"{pad}    Control: {kind}"]
    # accessibilità: proprietà verificate sui controlli salvati da Studio (rettangoli e etichette non sono
    # interattivi: fuori dall'ordine di tabulazione; gallerie, campi e tendine hanno un'etichetta)
    props = dict(props)
    if kind == "Rectangle":
        props.setdefault("AccessibleLabel", '"Elemento grafico"')
        props.setdefault("TabIndex", -1)
    elif kind == "Label":
        props.setdefault("TabIndex", -1)
        props.setdefault("FocusedBorderThickness", 2)
    elif kind == "Gallery":
        props.setdefault("TabIndex", 0)
    if kind in ("Gallery", "Classic/TextInput", "Classic/DropDown"):
        props.setdefault("AccessibleLabel", '"' + ETICHETTE.get(name, "Elenco" if kind == "Gallery" else "Campo") + '"')
    if variant:
        out.append(f"{pad}    Variant: {variant}")
    out.append(f"{pad}    Properties:")
    for k, v in props.items():
        out.append(f"{pad}      {k}: {fx(v, indent + 6)}")
    if children:
        out.append(f"{pad}    Children:")
        out.extend(children)
    return "\n".join(out)


def rect(name, x, y, w, h, fill, border=None, indent=6, extra=None):
    p = {"X": x, "Y": y, "Width": w, "Height": h, "Fill": fill}
    if border:
        p.update({"BorderColor": border, "BorderThickness": 1})
    p.update(extra or {})
    return control(name, "Rectangle", p, indent=indent)


def label(name, text, x, y, w, h, size=12, color="nfTesto", bold=False, align="Align.Left", indent=6, extra=None):
    p = {"Text": text, "X": x, "Y": y, "Width": w, "Height": h, "Size": size, "Color": color,
         "Font": "nfFont", "FontWeight": "FontWeight.Semibold" if bold else "FontWeight.Normal",
         "Align": align, "VerticalAlign": "VerticalAlign.Middle"}
    p.update(extra or {})
    return control(name, "Label", p, indent=indent)


def button(name, text, x, y, w, h, onselect, fill="nfAccento", color="Color.White", indent=6, extra=None):
    p = {"Text": text, "X": x, "Y": y, "Width": w, "Height": h, "OnSelect": onselect, "Fill": fill,
         "Color": color, "HoverFill": f"ColorFade({fill}, -10%)", "PressedFill": f"ColorFade({fill}, -20%)",
         "HoverColor": color, "BorderThickness": 0, "Font": "nfFont", "Size": 12,
         "FontWeight": "FontWeight.Semibold", "RadiusTopLeft": 8, "RadiusTopRight": 8,
         "RadiusBottomLeft": 8, "RadiusBottomRight": 8}
    p.update(extra or {})
    return control(name, "Classic/Button", p, indent=indent)


def sidebar(prefix, active):
    """Barra laterale: logo, voci di menu (quella attiva evidenziata), utente in basso."""
    # le schermate si chiamano scr*: "Stand" ed "Espositori" sono già i nomi delle origini dati
    voci = [("Home", "Panoramica", "Navigate(scrHome, ScreenTransition.None)"),
            ("Stand", "Planimetria stand", "Navigate(scrStand, ScreenTransition.None)"),
            ("Espositori", "Espositori", "Navigate(scrEspositori, ScreenTransition.None)"),
            ("Contratti", "Contratti", "Navigate(scrContratti, ScreenTransition.None)"),
            ("Nuovo", "Nuovo contratto", "Navigate(scrNuovo, ScreenTransition.None)"),
            ("Scadenze", "Scadenze e incassi", "Navigate(scrScadenze, ScreenTransition.None)"),
            ("Rinnovi", "Rinnovi e prelazione", "Navigate(scrRinnovi, ScreenTransition.None)"),
            ("Listino", "Listino 2026", "Navigate(scrListino, ScreenTransition.None)"),
            ("Controlli", "Controlli dati", "Navigate(scrControlli, ScreenTransition.None)")]
    out = [rect(f"{prefix}_recSidebar", 0, 0, SIDE, H, "nfBlu"),
           label(f"{prefix}_lblLogo", '"ARCADE"', 24, 24, 172, 36, size=20, color="Color.White", bold=True),
           label(f"{prefix}_lblLogoSub", '"Back-office commerciale"', 24, 58, 172, 20, size=10, color="ColorValue(\"#94A3B8\")"),
           rect(f"{prefix}_recSep", 24, 96, 172, 1, "nfBlu2")]
    for i, (key, testo, nav) in enumerate(voci):
        attivo = key == active
        abilitata = nav != "false"
        out.append(button(
            f"{prefix}_btnNav{key}", f'"{testo}"', 12, 116 + i * 48, 196, 40,
            nav if abilitata else "false",
            fill="nfAccento" if attivo else "nfBlu",
            color="Color.White" if (attivo or abilitata) else "ColorValue(\"#64748B\")",
            extra={"Align": "Align.Left", "PaddingLeft": 16,
                   "DisplayMode": "DisplayMode.Edit" if abilitata else "DisplayMode.Disabled",
                   "DisabledFill": "nfBlu", "DisabledColor": "ColorValue(\"#64748B\")"}))
    out.append(label(f"{prefix}_lblUtente", "User().FullName", 24, H - 56, 172, 20, size=10, color="Color.White"))
    out.append(label(f"{prefix}_lblEdizioneSide", '"Edizione " & gblAnno', 24, H - 34, 172, 18, size=9,
                     color="ColorValue(\"#94A3B8\")"))
    return out


def header(prefix, titolo, sottotitolo):
    return [label(f"{prefix}_lblTitolo", titolo, X0, 18, 700, 40, size=22, bold=True),
            label(f"{prefix}_lblSottotitolo", sottotitolo, X0, 56, 800, 22, size=11, color="nfTestoSec")]


def screen(name, props, children):
    lines = [HEADER + "Screens:", f"  {name}:", "    Properties:"]
    for k, v in props.items():
        lines.append(f"      {k}: {fx(v, 6)}")
    lines.append("    Children:")
    lines.extend(children)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# App: tema e caricamento dei dati
# ---------------------------------------------------------------------------
# L'app ha "nomi di colonna come identificatori" attivo: in AddColumns i nomi nuovi vanno senza virgolette.
# In Contratti due colonne si chiamano "Stato" (la nostra g5_stato e statecode di sistema): Studio le
# distingue aggiungendo il nome logico, quindi la nostra è 'Stato (g5_stato)'.
CARICA = """ClearCollect(colContratti, AddColumns(Contratti,
    AnnoEd, ThisRecord.Edizione.Anno,
    CodStand, ThisRecord.Stand.'Codice stand',
    IdEsp, ThisRecord.Espositore.'ID espositore',
    RagSoc, ThisRecord.Espositore.'Ragione sociale',
    StatoTxt, Text(ThisRecord.'Stato (g5_stato)')));
ClearCollect(colStand, AddColumns(Stand,
    CodPad, ThisRecord.Padiglione.Codice,
    AnnoAtt, Value(ThisRecord.'Attivo dal'.Anno),
    PosTxt, Text(ThisRecord.Posizione)))"""

APP = HEADER + """App:
  Properties:
    Formulas: |-
      =nfBlu = ColorValue("#0F172A");
      nfBlu2 = ColorValue("#1E293B");
      nfAccento = ColorValue("#7C3AED");
      nfAccentoChiaro = ColorValue("#EDE9FE");
      nfSfondo = ColorValue("#F1F5F9");
      nfCard = ColorValue("#FFFFFF");
      nfBordo = ColorValue("#E2E8F0");
      nfTesto = ColorValue("#0F172A");
      nfTestoSec = ColorValue("#64748B");
      nfVerde = ColorValue("#16A34A");
      nfVerdeChiaro = ColorValue("#DCFCE7");
      nfRosso = ColorValue("#DC2626");
      nfRossoChiaro = ColorValue("#FEE2E2");
      nfAmbra = ColorValue("#D97706");
      nfAmbraChiaro = ColorValue("#FEF3C7");
      nfFont = Font.'Segoe UI';
    OnStart: |-
      =Set(gblAnno, "2026");
""" + "\n".join("      " + l for l in CARICA.split("\n")) + """
    Theme: =PowerAppsTheme
"""

# ---------------------------------------------------------------------------
# Home: indicatori dell'edizione, ultimi contratti, occupazione per padiglione
# ---------------------------------------------------------------------------
def home():
    p = "hm"
    ed = 'Filter(colContratti, AnnoEd = gblAnno && StatoTxt <> "annullato")'
    kpi = [("Stand venduti",
            f'CountRows({ed}) & " / " & CountRows(Filter(colStand, AnnoAtt <= Value(gblAnno)))',
            f'"Occupazione " & Text(CountRows({ed}) / Max(1, CountRows(Filter(colStand, AnnoAtt <= Value(gblAnno)))), "0%")',
            "nfAccento"),
           ("Contratti firmati",
            'CountRows(Filter(colContratti, AnnoEd = gblAnno && StatoTxt = "firmato"))',
            'CountRows(Filter(colContratti, AnnoEd = gblAnno && StatoTxt = "preventivo")) & " preventivi aperti"',
            "nfVerde"),
           ("Imponibile venduto",
            f'Text(Sum({ed}, Imponibile), "[$-it-IT]€ #,##0")',
            # Average su una tabella vuota è un errore (nel 2026 non c'è ancora nessun contratto)
            f'If(CountRows({ed}) = 0, "Nessun contratto ancora", "Sconto medio " & Text(Average({ed}, Sconto), "0.0%"))',
            "nfBlu"),
           ("Acconti da incassare",
            f"CountRows(Filter({ed}, IsBlank('Acconto pagato il')))",
            f"CountRows(Filter({ed}, IsBlank('Saldo pagato il'))) & \" saldi da incassare\"",
            "nfAmbra")]
    ch = sidebar(p, "Home") + header(p, '"Panoramica"', '"ARCADE Milano · edizione " & gblAnno & " · dati Dataverse"')
    ch.append(label(f"{p}_lblEd", '"Edizione"', 1060, 26, 90, 40, size=11, color="nfTestoSec", align="Align.Right"))
    ch.append(control(f"{p}_ddEdizione", "Classic/DropDown", {
        "Items": '["2026", "2025", "2024"]', "Default": "gblAnno", "X": 1160, "Y": 26, "Width": 170, "Height": 40,
        "OnChange": "Set(gblAnno, Self.Selected.Value)", "Font": "nfFont", "Size": 12,
        "BorderColor": "nfBordo", "Fill": "nfCard", "ChevronBackground": "nfCard", "ChevronFill": "nfTesto"}))
    cw, gap = 259, 16
    for i, (cap, val, sub, col) in enumerate(kpi):
        x = X0 + i * (cw + gap)
        ch += [rect(f"{p}_recKpi{i}", x, 104, cw, 116, "nfCard", "nfBordo"),
               rect(f"{p}_recKpiBar{i}", x, 104, cw, 4, col),
               label(f"{p}_lblKpiCap{i}", f'"{cap}"', x + 20, 120, cw - 40, 20, size=11, color="nfTestoSec"),
               label(f"{p}_lblKpiVal{i}", val, x + 20, 144, cw - 40, 40, size=24, bold=True),
               label(f"{p}_lblKpiSub{i}", sub, x + 20, 186, cw - 40, 20, size=10, color="nfTestoSec")]

    # Ultimi contratti
    px, py, pw, ph = X0, 240, 660, 508
    t = 12  # rientro dei figli della galleria
    righe = [
        label(f"{p}_lblCId", "ThisItem.'ID contratto'", 16, 8, 120, 22, size=12, bold=True, indent=t),
        label(f"{p}_lblCEsp", "ThisItem.RagSoc", 16, 30, 330, 20, size=11, color="nfTestoSec", indent=t),
        label(f"{p}_lblCStand", '"Stand " & ThisItem.CodStand', 350, 8, 110, 22, size=11, indent=t),
        label(f"{p}_lblCData", 'Text(ThisItem.\'Data firma\', "dd/mm/yyyy")', 350, 30, 110, 20, size=10,
              color="nfTestoSec", indent=t),
        label(f"{p}_lblCImp", 'Text(ThisItem.Imponibile, "[$-it-IT]€ #,##0")', 460, 8, 120, 22, size=12,
              bold=True, align="Align.Right", indent=t),
        label(f"{p}_lblCStato", "Proper(ThisItem.StatoTxt)", 500, 32, 80, 18, size=9, bold=True,
              align="Align.Center", indent=t, extra={
                  "Fill": 'Switch(ThisItem.StatoTxt, "firmato", nfVerdeChiaro, "preventivo", nfAmbraChiaro, nfRossoChiaro)',
                  "Color": 'Switch(ThisItem.StatoTxt, "firmato", nfVerde, "preventivo", nfAmbra, nfRosso)'}),
        rect(f"{p}_recCSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    ch += [rect(f"{p}_recPanUltimi", px, py, pw, ph, "nfCard", "nfBordo"),
           label(f"{p}_lblPanUltimi", '"Ultimi contratti firmati"', px + 20, py + 14, 400, 28, size=14, bold=True),
           control(f"{p}_galUltimi", "Gallery", {
               "Items": "FirstN(Sort(Filter(colContratti, AnnoEd = gblAnno), 'Data firma', SortOrder.Descending), 7)",
               "X": px + 20, "Y": py + 52, "Width": pw - 40, "Height": ph - 64, "TemplateSize": 60,
               "TemplatePadding": 0, "ShowScrollbar": "false"},
               children=righe, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"),
           label(f"{p}_lblUltimiVuoto", '"Nessun contratto per l\'edizione " & gblAnno & ". Le vendite partiranno dal back-office."',
                 px + 20, py + 60, pw - 40, 40, size=11, color="nfTestoSec",
                 extra={"Visible": "IsEmpty(Filter(colContratti, AnnoEd = gblAnno))"})]

    # Occupazione per padiglione
    qx, qw = px + pw + 16, W - (px + pw + 16) - 32
    tot = "CountRows(Filter(colStand, CodPad = ThisItem.Codice && AnnoAtt <= Value(gblAnno)))"
    ven = ('CountRows(Filter(colContratti, AnnoEd = gblAnno && Left(CodStand, 2) = ThisItem.Codice'
           ' && StatoTxt <> "annullato"))')
    pad = [
        label(f"{p}_lblPCod", 'ThisItem.Codice & " · " & ThisItem.Nome', 0, 6, qw - 40, 24, size=12, bold=True, indent=t),
        label(f"{p}_lblPNum", f'{ven} & " venduti su " & {tot}', 0, 30, qw - 40, 20, size=10, color="nfTestoSec", indent=t),
        rect(f"{p}_recPBg", 0, 58, qw - 40, 10, "nfSfondo", indent=t),
        rect(f"{p}_recPFg", 0, 58, f"(Parent.TemplateWidth) * {ven} / Max(1, {tot})", 10, "nfAccento", indent=t),
    ]
    ch += [rect(f"{p}_recPanPad", qx, py, qw, ph, "nfCard", "nfBordo"),
           label(f"{p}_lblPanPad", '"Occupazione per padiglione"', qx + 20, py + 14, qw - 40, 28, size=14, bold=True),
           control(f"{p}_galPad", "Gallery", {
               "Items": "Sort(Padiglioni, Codice)", "X": qx + 20, "Y": py + 60, "Width": qw - 40, "Height": 290,
               "TemplateSize": 92, "TemplatePadding": 0, "ShowScrollbar": "false"},
               children=pad, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"),
           button(f"{p}_btnAggiorna", '"Aggiorna dati"', qx + 20, py + ph - 60, qw - 40, 40,
                  "Refresh(Contratti); Refresh(Stand);\n" + CARICA, fill="nfAccentoChiaro", color="nfAccento")]
    onvisible = "If(IsEmpty(colStand), Set(gblAnno, Coalesce(gblAnno, \"2026\"));\n" + CARICA + ")"
    return screen("scrHome", {"Fill": "nfSfondo", "OnVisible": onvisible}, ch)


# ---------------------------------------------------------------------------
# Stand: planimetria per padiglione con stato calcolato
# ---------------------------------------------------------------------------
def stand():
    p = "st"
    vend = ('LookUp(colContratti, AnnoEd = gblAnno && CodStand = ThisItem.\'Codice stand\''
            ' && StatoTxt <> "annullato")')
    items = "Sort(Filter(colStand, CodPad = locPad && AnnoAtt <= Value(gblAnno)), 'Codice stand')"
    ch = sidebar(p, "Stand") + header(p, '"Planimetria stand"',
                                      '"Edizione " & gblAnno & " · libero o venduto calcolato dai contratti non annullati"')
    for i, cod in enumerate(["P1", "P2", "P3"]):
        ch.append(button(f"{p}_btnPad{cod}", f'LookUp(Padiglioni, Codice = "{cod}").Nome', X0 + i * 212, 96, 200, 40,
                         f'UpdateContext({{locPad: "{cod}"}})',
                         fill=f'If(locPad = "{cod}", nfAccento, nfCard)',
                         color=f'If(locPad = "{cod}", Color.White, nfTesto)',
                         extra={"BorderColor": "nfBordo", "BorderThickness": 1}))
    tot = f"CountRows({items})"
    venduti = (f'CountRows(Filter(colContratti, AnnoEd = gblAnno && Left(CodStand, 2) = locPad'
               f' && StatoTxt <> "annullato"))')
    ch += [rect(f"{p}_recLegLib", 900, 110, 12, 12, "nfVerde"),
           label(f"{p}_lblLegLib", f'"Liberi " & ({tot} - {venduti})', 918, 100, 110, 32, size=11),
           rect(f"{p}_recLegVen", 1034, 110, 12, 12, "nfRosso"),
           label(f"{p}_lblLegVen", f'"Venduti " & {venduti}', 1052, 100, 110, 32, size=11),
           label(f"{p}_lblLegTot", f'"Totale " & {tot}', 1166, 100, 160, 32, size=11, color="nfTestoSec",
                 align="Align.Right")]
    t = 12
    card = [
        rect(f"{p}_recCard", 6, 6, "Parent.TemplateWidth - 12", "Parent.TemplateHeight - 12",
             f"If(IsBlank({vend}), nfVerdeChiaro, nfRossoChiaro)", indent=t,
             extra={"BorderColor": f"If(IsBlank({vend}), nfVerde, nfRosso)", "BorderThickness": 1}),
        label(f"{p}_lblCod", "ThisItem.'Codice stand'", 16, 12, "Parent.TemplateWidth - 32", 24, size=13,
              bold=True, indent=t),
        label(f"{p}_lblMq", "Text(ThisItem.'Metri quadri') & \" m² · \" & ThisItem.PosTxt", 16, 36,
              "Parent.TemplateWidth - 32", 20, size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblStato", f'If(IsBlank({vend}), "Libero", {vend}.RagSoc)', 16, 62,
              "Parent.TemplateWidth - 32", 22, size=10, bold=True, indent=t,
              extra={"Color": f"If(IsBlank({vend}), nfVerde, nfRosso)"}),
    ]
    ch.append(control(f"{p}_galStand", "Gallery", {
        "Items": items, "X": X0, "Y": 152, "Width": W - X0 - 24, "Height": H - 168, "WrapCount": 6,
        "TemplateSize": 100, "TemplatePadding": 0, "ShowScrollbar": "true"},
        # griglia a 6 colonne: serve WrapCount, che la variante "Flexible" non ha (errore PA2108)
        children=card, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
    onvisible = 'If(IsBlank(locPad), UpdateContext({locPad: "P1"}))'
    return screen("scrStand", {"Fill": "nfSfondo", "OnVisible": onvisible}, ch)


# ---------------------------------------------------------------------------
# Espositori: elenco con ricerca e scheda modificabile (controllo partita IVA, regola R3)
# ---------------------------------------------------------------------------
def espositori():
    p = "es"
    sel = f"{p}_galEsp.Selected"
    cerca = f"{p}_txtCerca.Text"
    ch = sidebar(p, "Espositori") + header(p, '"Espositori"',
                                           'CountRows(Espositori) & " aziende in anagrafica · dati Dataverse"')
    ch.append(control(f"{p}_txtCerca", "Classic/TextInput", {
        "Default": '""', "HintText": '"Cerca per ragione sociale, ID o città"', "DelayOutput": "true",
        "X": X0, "Y": 96, "Width": 520,
        "Height": 40, "Font": "nfFont", "Size": 12, "BorderColor": "nfBordo", "Fill": "nfCard",
        "RadiusTopLeft": 8, "RadiusTopRight": 8, "RadiusBottomLeft": 8, "RadiusBottomRight": 8}))
    ch.append(button(f"{p}_btnNuovo", '"+ Nuovo espositore"', W - 24 - 200, 96, 200, 40,
                     "UpdateContext({locNuovo: true})"))
    t = 12
    riga = [
        rect(f"{p}_recRiga", 0, 0, "Parent.TemplateWidth", "Parent.TemplateHeight",
             "If(ThisItem.IsSelected && !locNuovo, nfAccentoChiaro, nfCard)", indent=t),
        label(f"{p}_lblRag", "ThisItem.'Ragione sociale'", 16, 8, 380, 24, size=12, bold=True, indent=t),
        label(f"{p}_lblInfo", "ThisItem.'ID espositore' & \" · \" & ThisItem.Settore & \" · \" & ThisItem.Città",
              16, 32, 470, 20, size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblNContr", "CountRows(Filter(colContratti, IdEsp = ThisItem.'ID espositore'))", 420, 8, 64, 24,
              size=11, bold=True, align="Align.Right", color="nfAccento", indent=t),
        rect(f"{p}_recRigaSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    lx, lw = X0, 520
    ch += [rect(f"{p}_recLista", lx, 152, lw, H - 168, "nfCard", "nfBordo"),
           control(f"{p}_galEsp", "Gallery", {
               "Items": (f"Sort(Filter(Espositori, IsBlank({cerca}) || {cerca} in 'Ragione sociale'"
                         f" || {cerca} in 'ID espositore' || {cerca} in Città), 'Ragione sociale')"),
               "X": lx + 1, "Y": 153, "Width": lw - 2, "Height": H - 170, "TemplateSize": 60,
               "TemplatePadding": 0, "ShowScrollbar": "true", "OnSelect": "UpdateContext({locNuovo: false})"},
               children=riga, variant="BrowseLayout_Flexible_SocialFeed_ver5.0")]

    # Scheda di dettaglio
    dx = lx + lw + 16
    dw = W - dx - 24
    ch += [rect(f"{p}_recScheda", dx, 152, dw, H - 168, "nfCard", "nfBordo"),
           label(f"{p}_lblSchedaTit", f"If(locNuovo, \"Nuovo espositore\", {sel}.'Ragione sociale')",
                 dx + 24, 168, dw - 48, 32, size=16, bold=True),
           label(f"{p}_lblSchedaSub",
                 (f"If(locNuovo, \"L'ID viene assegnato al salvataggio\", {sel}.'ID espositore' & \" · \" & "
                  f"CountRows(Filter(colContratti, IdEsp = {sel}.'ID espositore')) & \" contratti · \" & "
                  f"CountRows(Filter(colContratti, IdEsp = {sel}.'ID espositore' && Rinnovo)) & \" rinnovi\")"),
                 dx + 24, 200, dw - 48, 20, size=10, color="nfTestoSec")]
    campi = [("Rag", "Ragione sociale", "'Ragione sociale'"), ("Piva", "Partita IVA", "'Partita IVA'"),
             ("Sett", "Settore", "Settore"), ("Citta", "Città", "Città"),
             ("Ref", "Referente", "Referente"), ("Mail", "Email referente", "'Email referente'")]
    fw = (dw - 48 - 16) // 2
    for i, (key, cap, col) in enumerate(campi):
        x = dx + 24 + (i % 2) * (fw + 16)
        y = 236 + (i // 2) * 84
        ch.append(label(f"{p}_lblCap{key}", f'"{cap}"', x, y, fw, 20, size=10, color="nfTestoSec"))
        extra = {}
        if key == "Piva":
            extra = {"BorderColor": f'If(IsMatch({p}_txtPiva.Text, "\\d{{11}}"), nfBordo, nfRosso)'}
        ch.append(control(f"{p}_txt{key}", "Classic/TextInput", {
            "Default": f'If(locNuovo, "", {sel}.{col})', "X": x, "Y": y + 22, "Width": fw, "Height": 40,
            "Font": "nfFont", "Size": 12, "BorderColor": "nfBordo", "Fill": "nfCard",
            "RadiusTopLeft": 6, "RadiusTopRight": 6, "RadiusBottomLeft": 6, "RadiusBottomRight": 6, **extra}))
    ch.append(label(f"{p}_lblPivaErr", '"La partita IVA deve avere esattamente 11 cifre"', dx + 24, 236 + 84 + 64,
                    fw * 2, 18, size=9, color="nfRosso",
                    extra={"Visible": f'!IsBlank({p}_txtPiva.Text) && !IsMatch({p}_txtPiva.Text, "\\d{{11}}")'}))
    valori = (f"'Ragione sociale': {p}_txtRag.Text, 'Partita IVA': {p}_txtPiva.Text, Settore: {p}_txtSett.Text,"
              f" Città: {p}_txtCitta.Text, Referente: {p}_txtRef.Text, 'Email referente': {p}_txtMail.Text")
    # L'ID espositore (ESP<nnn>) lo assegna Dataverse con la numerazione automatica di g5_id_espositore
    salva = f"""If(
    IsBlank({p}_txtRag.Text), Notify("La ragione sociale è obbligatoria", NotificationType.Error),
    !IsMatch({p}_txtPiva.Text, "\\d{{11}}"), Notify("La partita IVA deve avere esattamente 11 cifre", NotificationType.Error),
    IfError(
        If(locNuovo,
            With({{nuovo: Patch(Espositori, Defaults(Espositori), {{{valori}}})}},
                Notify("Espositore " & nuovo.'ID espositore' & " salvato", NotificationType.Success)),
            Patch(Espositori, {sel}, {{{valori}}});
            Notify("Espositore salvato", NotificationType.Success)
        );
        UpdateContext({{locNuovo: false}}),
        Notify("Salvataggio non riuscito: " & FirstError.Message, NotificationType.Error)
    )
)"""
    ch.append(button(f"{p}_btnSalva", '"Salva"', dx + 24, H - 80, 160, 44, salva))
    ch.append(button(f"{p}_btnAnnulla", '"Annulla"', dx + 200, H - 80, 160, 44,
                     f"UpdateContext({{locNuovo: false}}); Reset({p}_txtRag); Reset({p}_txtPiva)",
                     fill="nfCard", color="nfTesto", extra={"BorderColor": "nfBordo", "BorderThickness": 1}))
    return screen("scrEspositori", {"Fill": "nfSfondo", "OnVisible": "UpdateContext({locNuovo: false})"}, ch)


# ---------------------------------------------------------------------------
# Contratti: elenco, importi, pagamenti e righe; firma, annullo, pagamenti e sollecito
# ---------------------------------------------------------------------------
# Dopo ogni scrittura le due collezioni si ricaricano: Dataverse resta la fonte, la collezione è solo una copia.
RICARICA = "Refresh(Contratti);\n" + CARICA
EURO = '"[$-it-IT]€ #,##0"'
EURO2 = '"[$-it-IT]€ #,##0.00"'
# Le righe contratto sono 950, oltre il limite di 500 righe delle query che Power Apps non delega a Dataverse.
# Filtrare per contratto (lookup) non è delegabile, quindi si caricano per numero di riga: ogni query
# (Riga = 1, Riga = 2, ...) è un'uguaglianza su un numero, che Dataverse esegue lui e restituisce meno di 500 righe.
# Una riga ha al massimo 14 numeri (spazio, maggiorazione e 12 servizi): 16 passaggi bastano.
CARICA_RIGHE = """If(IsEmpty(colRighe),
    ForAll(Sequence(16) As n,
        Collect(colRighe, AddColumns(Filter('Righe contratto', Riga = n.Value), IdC, ThisRecord.Contratto.'ID contratto'))))"""
# Ordine fisso dei servizi del listino: serve un numero perché i testi non si confrontano con <= (ErrBadType)
ORD_SERVIZI = ('Switch(Codice, "EX-ARR", 1, "EX-EL3", 2, "EX-EL6", 3, "EX-FIBRA", 4, "EX-PARK", 5, "EX-PASS", 6,'
               ' "SP-BADGE", 7, "SP-COSPLAY", 8, "SP-INDIE", 9, "SP-SOCIAL", 10, "SP-STAGE", 11, "SP-TORNEO", 12, 99)')


def stato_pagamento(sel, pag, scad):
    """Testo dello stato di un pagamento: attesa firma, annullato, pagato, in ritardo, scaduto, da pagare."""
    return (f'If({sel}.StatoTxt = "preventivo", "In attesa di firma", If({sel}.StatoTxt = "annullato", "Annullato", '
            f"If(!IsBlank({sel}.'{pag}'), If({sel}.'{pag}' > {sel}.'{scad}', \"Pagato in ritardo\", \"Pagato\"), "
            f"If({sel}.'{scad}' < Today(), \"Scaduto da \" & DateDiff({sel}.'{scad}', Today(), TimeUnit.Days) & \" gg\", "
            f'"Da pagare"))))')


def contratti():
    p = "ct"
    sel = f"{p}_galContratti.Selected"
    cerca = f"{p}_txtCerca.Text"
    # un'unica definizione del filtro: la usano la galleria, il sottotitolo e il messaggio "nessun contratto"
    filtro = ('Filter(colContratti, AnnoEd = gblAnno && (locStato = "Tutti" || StatoTxt = locStato)'
              f" && (IsBlank({cerca}) || {cerca} in 'ID contratto' || {cerca} in RagSoc || {cerca} in CodStand))")

    def S(formula):
        return formula.replace("§", sel)

    ch = sidebar(p, "Contratti") + header(
        p, '"Contratti"',
        f'CountRows(Filter(colContratti, AnnoEd = gblAnno)) & " contratti nell\'edizione " & gblAnno'
        f' & " · " & CountRows({filtro}) & " mostrati"')
    ch.append(label(f"{p}_lblEd", '"Edizione"', 1060, 26, 90, 40, size=11, color="nfTestoSec", align="Align.Right"))
    ch.append(control(f"{p}_ddEdizione", "Classic/DropDown", {
        "Items": '["2026", "2025", "2024"]', "Default": "gblAnno", "X": 1160, "Y": 26, "Width": 170, "Height": 40,
        "OnChange": "Set(gblAnno, Self.Selected.Value)", "Font": "nfFont", "Size": 12,
        "BorderColor": "nfBordo", "Fill": "nfCard", "ChevronBackground": "nfCard", "ChevronFill": "nfTesto"}))
    ch.append(control(f"{p}_txtCerca", "Classic/TextInput", {
        "Default": '""', "HintText": '"Cerca per contratto, espositore o stand"', "DelayOutput": "true",
        "X": X0, "Y": 96, "Width": 300,
        "Height": 40, "Font": "nfFont", "Size": 12, "BorderColor": "nfBordo", "Fill": "nfCard",
        "RadiusTopLeft": 8, "RadiusTopRight": 8, "RadiusBottomLeft": 8, "RadiusBottomRight": 8}))
    for i, (val, testo) in enumerate([("Tutti", "Tutti"), ("firmato", "Firmati"),
                                      ("preventivo", "Preventivi"), ("annullato", "Annullati")]):
        ch.append(button(f"{p}_btnFiltro{i}", f'"{testo}"', X0 + 316 + i * 104, 96, 96, 40,
                         f'UpdateContext({{locStato: "{val}"}})',
                         fill=f'If(locStato = "{val}", nfAccento, nfCard)',
                         color=f'If(locStato = "{val}", Color.White, nfTesto)',
                         extra={"BorderColor": "nfBordo", "BorderThickness": 1}))

    # --- elenco a sinistra
    t = 12
    badge_fill = 'Switch(ThisItem.StatoTxt, "firmato", nfVerdeChiaro, "preventivo", nfAmbraChiaro, nfRossoChiaro)'
    badge_col = 'Switch(ThisItem.StatoTxt, "firmato", nfVerde, "preventivo", nfAmbra, nfRosso)'
    riga = [
        rect(f"{p}_recRiga", 0, 0, "Parent.TemplateWidth", "Parent.TemplateHeight",
             "If(ThisItem.IsSelected, nfAccentoChiaro, nfCard)", indent=t),
        label(f"{p}_lblCId", "ThisItem.'ID contratto'", 16, 8, 160, 22, size=12, bold=True, indent=t),
        label(f"{p}_lblCEsp", 'ThisItem.RagSoc & " · stand " & ThisItem.CodStand', 16, 34, 330, 20, size=10,
              color="nfTestoSec", indent=t),
        label(f"{p}_lblCImp", f"Text(ThisItem.Imponibile, {EURO})", 360, 8, 140, 22, size=12, bold=True,
              align="Align.Right", indent=t),
        label(f"{p}_lblCStato", "Proper(ThisItem.StatoTxt)", 420, 34, 80, 18, size=9, bold=True,
              align="Align.Center", indent=t, extra={"Fill": badge_fill, "Color": badge_col}),
        rect(f"{p}_recRigaSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    items = f"Sort({filtro}, 'ID contratto', SortOrder.Descending)"
    lx, lw = X0, 520
    ch += [rect(f"{p}_recLista", lx, 152, lw, H - 168, "nfCard", "nfBordo"),
           control(f"{p}_galContratti", "Gallery", {
               "Items": items, "X": lx + 1, "Y": 153, "Width": lw - 2, "Height": H - 170, "TemplateSize": 64,
               "TemplatePadding": 0, "ShowScrollbar": "true", "OnSelect": "UpdateContext({locConf: false})"},
               children=riga, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"),
           label(f"{p}_lblVuoto", '"Nessun contratto con questi filtri per l\'edizione " & gblAnno', lx + 24, 190,
                 lw - 48, 40, size=11, color="nfTestoSec", align="Align.Center",
                 extra={"Visible": f"IsEmpty({filtro})"})]

    # --- dettaglio a destra
    dx = lx + lw + 16
    dw = W - dx - 24
    iw = dw - 48                                  # larghezza interna del pannello
    ch += [rect(f"{p}_recDettaglio", dx, 152, dw, H - 168, "nfCard", "nfBordo"),
           label(f"{p}_lblDetId", S("§.'ID contratto'"), dx + 24, 166, 300, 32, size=18, bold=True),
           label(f"{p}_lblDetStato", S("Proper(§.StatoTxt)"), dx + dw - 24 - 110, 172, 110, 22, size=10, bold=True,
                 align="Align.Center", extra={
                     "Fill": S('Switch(§.StatoTxt, "firmato", nfVerdeChiaro, "preventivo", nfAmbraChiaro, nfRossoChiaro)'),
                     "Color": S('Switch(§.StatoTxt, "firmato", nfVerde, "preventivo", nfAmbra, nfRosso)')}),
           label(f"{p}_lblDetSub",
                 S('§.RagSoc & " · stand " & §.CodStand & " · edizione " & §.AnnoEd'
                   ' & If(§.Rinnovo, " · rinnovo", "")'),
                 dx + 24, 198, iw, 22, size=11, color="nfTestoSec")]
    cw3 = (iw - 32) // 3
    cards = [("Totale a listino", S(f"Text(§.'Imponibile a listino', {EURO})")),
             ("Sconto", S('Text(§.Sconto, "0%")')),
             ("Imponibile", S(f"Text(§.Imponibile, {EURO})"))]
    for i, (cap, val) in enumerate(cards):
        x = dx + 24 + i * (cw3 + 16)
        ch += [rect(f"{p}_recCard{i}", x, 232, cw3, 64, "nfSfondo"),
               label(f"{p}_lblCardCap{i}", f'"{cap}"', x + 12, 238, cw3 - 24, 18, size=10, color="nfTestoSec"),
               label(f"{p}_lblCardVal{i}", val, x + 12, 258, cw3 - 24, 30, size=16, bold=True)]

    # pagamenti: acconto 30% e saldo 70% (importi derivati dal listino COND-ACCONTO, non salvati)
    ch.append(label(f"{p}_lblPagTit", '"Pagamenti"', dx + 24, 308, 200, 24, size=13, bold=True))
    acc = S("Round(§.Imponibile * 0.3, 2)")
    pagamenti = [("Acconto (30%)", "Acconto pagato il", "Scadenza acconto", f"Text({acc}, {EURO2})", "Acconto"),
                 ("Saldo (70%)", "Saldo pagato il", "Scadenza saldo", S(f"Text(§.Imponibile - Round(§.Imponibile * 0.3, 2), {EURO2})"), "Saldo")]
    for k, (nome, pag, scad, importo, key) in enumerate(pagamenti):
        y0 = 336 + k * 60
        st = f"{p}_lblPagStato{k}"
        ch += [rect(f"{p}_recPag{k}", dx + 24, y0, iw, 52, "nfSfondo"),
               label(f"{p}_lblPagNome{k}", f'"{nome}"', dx + 36, y0 + 6, 150, 20, size=12, bold=True),
               label(f"{p}_lblPagImp{k}", importo, dx + 36, y0 + 28, 150, 18, size=11, color="nfTestoSec"),
               label(f"{p}_lblPagScad{k}",
                     S(f"If(IsBlank(§.'{scad}'), \"Scadenza da fissare\", \"Scadenza \" & Text(§.'{scad}', \"dd/mm/yyyy\"))"),
                     dx + 190, y0 + 6, 150, 20, size=11),
               label(f"{p}_lblPagData{k}",
                     S(f"If(IsBlank(§.'{pag}'), \"Non ancora pagato\", \"Pagato il \" & Text(§.'{pag}', \"dd/mm/yyyy\"))"),
                     dx + 190, y0 + 28, 150, 18, size=10, color="nfTestoSec"),
               label(st, S(stato_pagamento("§", pag, scad)), dx + 346, y0 + 6, 172, 18, size=9, bold=True,
                     align="Align.Center", extra={
                         "Fill": f'If(StartsWith({st}.Text, "Pagato in"), nfAmbraChiaro, If(StartsWith({st}.Text, "Pagato"), nfVerdeChiaro, If(StartsWith({st}.Text, "Scaduto"), nfRossoChiaro, nfBordo)))',
                         "Color": f'If(StartsWith({st}.Text, "Pagato in"), nfAmbra, If(StartsWith({st}.Text, "Pagato"), nfVerde, If(StartsWith({st}.Text, "Scaduto"), nfRosso, nfTestoSec)))'}),
               button(f"{p}_btnPagato{k}", '"Segna come pagato"', dx + 346, y0 + 28, 172, 20,
                      S(f"""IfError(
    Patch(Contratti, LookUp(Contratti, 'ID contratto' = §.'ID contratto'), {{'{pag}': Today()}});
    Notify("{key} registrato", NotificationType.Success);
    {RICARICA},
    Notify("Registrazione non riuscita: " & FirstError.Message, NotificationType.Error)
)"""),
                      fill="nfCard", color="nfAccento",
                      extra={"Size": 10, "BorderColor": "nfBordo", "BorderThickness": 1,
                             "Visible": S(f"§.StatoTxt = \"firmato\" && IsBlank(§.'{pag}')")})]

    # righe del contratto: il filtro sul contratto lo esegue Dataverse (le righe sono 950, oltre il limite di 500)
    ch.append(label(f"{p}_lblRigheTit", '"Righe del contratto"', dx + 24, 458, 400, 24, size=13, bold=True))
    colonne = [("Voce", 0, 96, "Align.Left"), ("Descrizione", 96, 190, "Align.Left"), ("Qtà", 286, 50, "Align.Right"),
               ("Prezzo", 336, 80, "Align.Right"), ("Importo", 416, 94, "Align.Right")]
    for nome, off, w, al in colonne:
        ch.append(label(f"{p}_lblRH{nome}", f'"{nome}"', dx + 24 + off, 484, w, 18, size=9, color="nfTestoSec", align=al))
    righe = [
        label(f"{p}_lblRV", "ThisItem.'Codice voce'", 0, 4, 96, 20, size=10, bold=True, indent=t),
        label(f"{p}_lblRD", "ThisItem.Descrizione", 96, 4, 190, 20, size=10, indent=t),
        label(f"{p}_lblRQ", 'Text(ThisItem.Quantità, "#,##0.##")', 286, 4, 50, 20, size=10, align="Align.Right", indent=t),
        label(f"{p}_lblRP", f"Text(ThisItem.'Prezzo unitario', {EURO2})", 336, 4, 80, 20, size=10, align="Align.Right", indent=t),
        label(f"{p}_lblRI", f"Text(ThisItem.Importo, {EURO2})", 416, 4, 94, 20, size=10, bold=True, align="Align.Right", indent=t),
        rect(f"{p}_recRSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    ch.append(control(f"{p}_galRighe", "Gallery", {
        # le lookup si confrontano per identificativo (GUID): confrontare i due record dava ErrIncompatibleTypesForEquality
        "Items": S("Sort(Filter(colRighe, IdC = §.'ID contratto'), Riga)"),
        "X": dx + 24, "Y": 504, "Width": iw, "Height": 184, "TemplateSize": 28, "TemplatePadding": 0,
        "ShowScrollbar": "true"},
        children=righe, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"))

    # azioni
    firma = S(f"""IfError(
    Patch(Contratti, LookUp(Contratti, 'ID contratto' = §.'ID contratto'),
        {{'Stato (g5_stato)': 'Stato (Contratti)'.firmato, 'Data firma': Today(),
          'Scadenza acconto': DateAdd(Today(), 15, TimeUnit.Days),
          'Scadenza saldo': DateAdd(LookUp(Edizioni, Anno = §.AnnoEd).'Data inizio', -30, TimeUnit.Days)}});
    Notify("Contratto firmato", NotificationType.Success);
    {RICARICA},
    Notify("Firma non riuscita: " & FirstError.Message, NotificationType.Error)
)""")
    annulla = S(f"""If(locConf,
    IfError(
        Patch(Contratti, LookUp(Contratti, 'ID contratto' = §.'ID contratto'), {{'Stato (g5_stato)': 'Stato (Contratti)'.annullato}});
        UpdateContext({{locConf: false}});
        Notify("Contratto annullato", NotificationType.Success);
        {RICARICA};
        true,
        Notify("Annullamento non riuscito: " & FirstError.Message, NotificationType.Error)
    ),
    UpdateContext({{locConf: true}})
)""")
    scaduto = S("§.StatoTxt = \"firmato\" && ((IsBlank(§.'Acconto pagato il') && §.'Scadenza acconto' < Today())"
                " || (IsBlank(§.'Saldo pagato il') && §.'Scadenza saldo' < Today()))")
    sollecito = S("""With({em: LookUp(Espositori, 'ID espositore' = §.IdEsp),
      acc: §.StatoTxt = "firmato" && IsBlank(§.'Acconto pagato il') && §.'Scadenza acconto' < Today()},
    Launch("mailto:" & em.'Email referente' & "?subject=" & EncodeUrl("Sollecito di pagamento - contratto " & §.'ID contratto')
        & "&body=" & EncodeUrl("Gentile " & em.Referente & "," & Char(10) & Char(10)
        & "ci risulta ancora da incassare " & If(acc, "l'acconto del 30%", "il saldo") & " del contratto " & §.'ID contratto'
        & " (stand " & §.CodStand & "), pari a € "
        & Text(If(acc, Round(§.Imponibile * 0.3, 2), §.Imponibile - Round(§.Imponibile * 0.3, 2)), "#,##0.00")
        & ", con scadenza " & Text(If(acc, §.'Scadenza acconto', §.'Scadenza saldo'), "dd/mm/yyyy") & "."
        & Char(10) & Char(10) & "Cordiali saluti," & Char(10) & "Ufficio commerciale ARCADE Milano")))""")
    disab = {"DisabledFill": "nfBordo", "DisabledColor": "nfTestoSec"}
    ch += [button(f"{p}_btnFirma", '"Firma contratto"', dx + 24, H - 64, 160, 40, firma,
                  extra={**disab, "DisplayMode": S('If(§.StatoTxt = "preventivo", DisplayMode.Edit, DisplayMode.Disabled)')}),
           button(f"{p}_btnAnnulla", 'If(locConf, "Conferma annullamento", "Annulla contratto")', dx + 194, H - 64, 170, 40,
                  annulla, fill="If(locConf, nfRosso, nfCard)", color="If(locConf, Color.White, nfRosso)",
                  extra={**disab, "BorderColor": "nfRosso", "BorderThickness": 1,
                         "DisplayMode": S('If(§.StatoTxt <> "annullato" && !IsBlank(§.\'ID contratto\'), DisplayMode.Edit, DisplayMode.Disabled)')}),
           button(f"{p}_btnSollecito", '"Invia sollecito"', dx + 374, H - 64, 160, 40, sollecito,
                  fill="nfAccentoChiaro", color="nfAccento",
                  extra={**disab, "DisplayMode": f"If({scaduto}, DisplayMode.Edit, DisplayMode.Disabled)"})]
    onvisible = ('If(IsBlank(locStato), UpdateContext({locStato: "Tutti"}));\nUpdateContext({locConf: false});\n'
                 + CARICA_RIGHE)
    return screen("scrContratti", {"Fill": "nfSfondo", "OnVisible": onvisible}, ch)


# ---------------------------------------------------------------------------
# Nuovo contratto: procedura guidata in 4 passi -> preventivo dell'edizione 2026
# Regole prese dai 198 contratti storici (verificate): prezzo area = mq x prezzo del padiglione,
# maggiorazione sull'area per posizione, imponibile = listino x (1 - sconto), acconto 30% e saldo 70%,
# numero contratto progressivo su tutte le edizioni, rinnovo = espositore presente nell'edizione precedente.
# ---------------------------------------------------------------------------
def nuovo():
    p = "nv"
    PW = W - X0 - 24                       # larghezza del pannello dei contenuti
    cerca = f"{p}_txtCerca.Text"
    anno_prec = 'Text(Value(gblAnno) - 1, "0")'
    prec = ("LookUp(colContratti, IdEsp = locEsp.'ID espositore' && AnnoEd = " + anno_prec +
            ' && StatoTxt <> "annullato")')
    area = "(locStand.'Metri quadri' * locPrezzoMq)"
    magg = f"Round({area} * locPct, 2)"
    extra = "Sum(colExtra, Qta * 'Prezzo unitario')"
    totale = f"({area} + {magg} + {extra})"
    imponib = f"Round({totale} * (1 - locSconto), 2)"
    acconto = f"Round({imponib} * 0.3, 2)"
    liberi = ("Filter(colStand As s, s.CodPad = locPad && s.AnnoAtt <= Value(gblAnno)"
              " && IsBlank(LookUp(colContratti, AnnoEd = gblAnno && CodStand = s.'Codice stand'"
              ' && StatoTxt <> "annullato")))')
    t = 12

    def v(n):
        return {"Visible": f"locPasso = {n}"}

    ch = sidebar(p, "Nuovo") + header(
        p, '"Nuovo contratto"', '"Preventivo per l\'edizione " & gblAnno & " · la firma si registra dalla schermata Contratti"')
    for i, nome in enumerate(["Espositore", "Stand", "Servizi", "Riepilogo"], start=1):
        ch.append(label(f"{p}_lblPasso{i}", f'"{i}  ·  {nome}"', X0 + (i - 1) * 278, 96, 260, 40, size=12, bold=True,
                        align="Align.Center", extra={
                            "Fill": f"If(locPasso = {i}, nfAccento, If(locPasso > {i}, nfVerdeChiaro, nfCard))",
                            "Color": f"If(locPasso = {i}, Color.White, If(locPasso > {i}, nfVerde, nfTestoSec))",
                            "BorderColor": "nfBordo", "BorderThickness": 1}))
    ch.append(rect(f"{p}_recPannello", X0, 152, PW, H - 168, "nfCard", "nfBordo"))

    # ---- passo 1: espositore
    ch.append(control(f"{p}_txtCerca", "Classic/TextInput", {
        "Default": '""', "HintText": '"Cerca espositore per nome, ID o città"', "DelayOutput": "true",
        "X": X0 + 24, "Y": 168, "Width": 440, "Height": 40, "Font": "nfFont", "Size": 12, "BorderColor": "nfBordo",
        "Fill": "nfCard", "RadiusTopLeft": 8, "RadiusTopRight": 8, "RadiusBottomLeft": 8, "RadiusBottomRight": 8,
        **v(1)}))
    esp_riga = [
        rect(f"{p}_recEsp", 0, 0, "Parent.TemplateWidth", "Parent.TemplateHeight",
             "If(locEsp.'ID espositore' = ThisItem.'ID espositore', nfAccentoChiaro, nfCard)", indent=t),
        label(f"{p}_lblEspRag", "ThisItem.'Ragione sociale'", 12, 6, 400, 24, size=12, bold=True, indent=t),
        label(f"{p}_lblEspInfo", "ThisItem.'ID espositore' & \" · \" & ThisItem.Settore & \" · \" & ThisItem.Città",
              12, 30, 410, 20, size=10, color="nfTestoSec", indent=t),
        rect(f"{p}_recEspSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
        # pulsante trasparente sopra la riga (ultimo = in primo piano): il clic arriva sempre al suo OnSelect
        button(f"{p}_btnEspSel", '""', 0, 0, "Parent.TemplateWidth", "Parent.TemplateHeight",
               "UpdateContext({locEsp: ThisItem})", fill="Color.Transparent", color="Color.Transparent", indent=t,
               extra={"HoverFill": "ColorFade(nfAccento, 92%)", "PressedFill": "ColorFade(nfAccento, 85%)",
                      "RadiusTopLeft": 0, "RadiusTopRight": 0, "RadiusBottomLeft": 0, "RadiusBottomRight": 0}),
    ]
    ch.append(control(f"{p}_galEsp", "Gallery", {
        "Items": (f"Sort(Filter(Espositori, IsBlank({cerca}) || {cerca} in 'Ragione sociale'"
                  f" || {cerca} in 'ID espositore' || {cerca} in Città), 'Ragione sociale')"),
        "X": X0 + 24, "Y": 220, "Width": 440, "Height": 468, "TemplateSize": 56, "TemplatePadding": 0,
        "ShowScrollbar": "true", "OnSelect": "UpdateContext({locEsp: ThisItem})", **v(1)},
        children=esp_riga, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"))
    rx, rw = X0 + 488, PW - 512
    ch += [label(f"{p}_lblEspTit", "If(IsBlank(locEsp), \"Seleziona un espositore dall'elenco\", locEsp.'Ragione sociale')",
                 rx, 168, rw, 30, size=16, bold=True, extra=v(1)),
           label(f"{p}_lblEspSub", "If(IsBlank(locEsp), \"\", locEsp.'ID espositore' & \" · \" & locEsp.Settore & \" · \" & locEsp.Città)",
                 rx, 200, rw, 22, size=11, color="nfTestoSec", extra=v(1)),
           label(f"{p}_lblEspRef", "If(IsBlank(locEsp), \"\", \"Referente: \" & locEsp.Referente)",
                 rx, 222, rw, 22, size=11, color="nfTestoSec", extra=v(1)),
           rect(f"{p}_recPrel", rx, 256, rw, 84, f"If(IsBlank({prec}), nfSfondo, nfAmbraChiaro)",
                extra={"Visible": "locPasso = 1 && !IsBlank(locEsp)"}),
           label(f"{p}_lblPrel",
                 (f'If(IsBlank({prec}), "Nessun contratto nel " & {anno_prec} & ": nuovo espositore, non è un rinnovo.", '
                  f'"Rinnovo: nel " & {anno_prec} & " era sullo stand " & {prec}.CodStand & ". Prelazione: " & '
                  f'LookUp(colListino, Codice = "COND-PRELAZ").Note & " (dal listino). Lo stand resta proponibile.")'),
                 rx + 14, 262, rw - 28, 72, size=11, extra={"Visible": "locPasso = 1 && !IsBlank(locEsp)"}),
           label(f"{p}_lblStorico", '"Storico contratti"', rx, 354, rw, 24, size=13, bold=True, extra=v(1))]
    stor = [
        label(f"{p}_lblStA", "ThisItem.AnnoEd & \" · stand \" & ThisItem.CodStand & If(ThisItem.Rinnovo, \" · rinnovo\", \"\")",
              0, 8, 360, 24, size=11, indent=t),
        label(f"{p}_lblStI", f"Text(ThisItem.Imponibile, {EURO})", 360, 8, 200, 24, size=11, bold=True,
              align="Align.Right", indent=t),
        rect(f"{p}_recStSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    ch.append(control(f"{p}_galStorico", "Gallery", {
        "Items": ("Sort(Filter(colContratti, IdEsp = locEsp.'ID espositore' && StatoTxt <> \"annullato\"), "
                  "AnnoEd, SortOrder.Descending)"),
        "X": rx, "Y": 382, "Width": rw, "Height": 300, "TemplateSize": 40, "TemplatePadding": 0,
        "ShowScrollbar": "true", **v(1)},
        children=stor, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"))

    # ---- passo 2: stand libero
    for i, cod in enumerate(["P1", "P2", "P3"]):
        ch.append(button(f"{p}_btnPad{cod}", f'LookUp(Padiglioni, Codice = "{cod}").Nome', X0 + 24 + i * 212, 168, 200, 40,
                         f'UpdateContext({{locPad: "{cod}"}})',
                         fill=f'If(locPad = "{cod}", nfAccento, nfCard)',
                         color=f'If(locPad = "{cod}", Color.White, nfTesto)',
                         extra={"BorderColor": "nfBordo", "BorderThickness": 1, **v(2)}))
    ch += [label(f"{p}_lblLiberi", f'CountRows({liberi}) & " stand liberi in questo padiglione"',
                 X0 + PW - 24 - 360, 168, 360, 40, size=11, color="nfTestoSec", align="Align.Right", extra=v(2)),
           label(f"{p}_lblStand25",
                 (f'If(IsBlank({prec}), "", "Nel " & {anno_prec} & " " & locEsp.\'Ragione sociale\' & " era sullo stand " & '
                  f'{prec}.CodStand & If(IsBlank(LookUp(colContratti, AnnoEd = gblAnno && CodStand = {prec}.CodStand'
                  f' && StatoTxt <> "annullato")), " (libero: è il suo stand storico)", " (già venduto per il " & gblAnno & ")"))'),
                 X0 + 24, 214, PW - 48, 24, size=11, color="nfAmbra", extra=v(2))]
    card = [
        rect(f"{p}_recCard", 6, 6, "Parent.TemplateWidth - 12", "Parent.TemplateHeight - 12",
             "If(ThisItem.'Codice stand' = locStand.'Codice stand', nfAccentoChiaro, nfVerdeChiaro)", indent=t,
             extra={"BorderColor": "If(ThisItem.'Codice stand' = locStand.'Codice stand', nfAccento, nfVerde)",
                    "BorderThickness": 2}),
        label(f"{p}_lblCCod", "ThisItem.'Codice stand'", 16, 12, "Parent.TemplateWidth - 32", 24, size=13, bold=True, indent=t),
        label(f"{p}_lblCMq", "Text(ThisItem.'Metri quadri') & \" m² · \" & ThisItem.PosTxt", 16, 36,
              "Parent.TemplateWidth - 32", 20, size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblCArea",
              f"\"Area \" & Text(ThisItem.'Metri quadri' * LookUp(colListino, Codice = \"SPAZIO-\" & ThisItem.CodPad).'Prezzo unitario', {EURO})",
              16, 58, "Parent.TemplateWidth - 32", 20, size=10, bold=True, indent=t),
        label(f"{p}_lblCStorico", f'"Stand " & {anno_prec}', 16, 78, "Parent.TemplateWidth - 32", 16, size=9, bold=True,
              color="nfAmbra", indent=t, extra={"Visible": f"ThisItem.'Codice stand' = {prec}.CodStand"}),
        button(f"{p}_btnStandSel", '""', 0, 0, "Parent.TemplateWidth", "Parent.TemplateHeight",
               "UpdateContext({locStand: ThisItem})", fill="Color.Transparent", color="Color.Transparent", indent=t,
               extra={"HoverFill": "ColorFade(nfAccento, 92%)", "PressedFill": "ColorFade(nfAccento, 85%)",
                      "RadiusTopLeft": 0, "RadiusTopRight": 0, "RadiusBottomLeft": 0, "RadiusBottomRight": 0}),
    ]
    ch.append(control(f"{p}_galStand", "Gallery", {
        "Items": f"Sort({liberi}, 'Codice stand')", "X": X0 + 24, "Y": 246, "Width": PW - 48, "Height": 442,
        "WrapCount": 6, "TemplateSize": 100, "TemplatePadding": 0, "ShowScrollbar": "true",
        "OnSelect": "UpdateContext({locStand: ThisItem})", **v(2)},
        children=card, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))

    # ---- passo 3: servizi aggiuntivi dal listino
    lw3 = 420
    ch += [rect(f"{p}_recSpazio", X0 + 24, 164, lw3, 524, "nfSfondo", extra=v(3)),
           label(f"{p}_lblSpTit", "\"Stand \" & locStand.'Codice stand'", X0 + 40, 176, lw3 - 32, 30, size=16, bold=True, extra=v(3)),
           label(f"{p}_lblSpSub",
                 "Text(locStand.'Metri quadri') & \" m² · \" & locStand.PosTxt & \" · \" & LookUp(Padiglioni, Codice = locStand.CodPad).Nome",
                 X0 + 40, 206, lw3 - 32, 22, size=11, color="nfTestoSec", extra=v(3)),
           label(f"{p}_lblSpArea", f"\"Area: \" & Text(locStand.'Metri quadri') & \" m² × \" & Text(locPrezzoMq, {EURO})",
                 X0 + 40, 252, 250, 24, size=11, extra=v(3)),
           label(f"{p}_lblSpAreaV", f"Text({area}, {EURO2})", X0 + 290, 252, lw3 - 282, 24, size=11, bold=True,
                 align="Align.Right", extra=v(3)),
           label(f"{p}_lblSpMagg", "\"Maggiorazione \" & locStand.PosTxt & \" (\" & Text(locPct, \"0%\") & \" sull'area)\"",
                 X0 + 40, 284, 250, 24, size=11, extra={"Visible": "locPasso = 3 && locPct > 0"}),
           label(f"{p}_lblSpMaggV", f"Text({magg}, {EURO2})", X0 + 290, 284, lw3 - 282, 24, size=11, bold=True,
                 align="Align.Right", extra={"Visible": "locPasso = 3 && locPct > 0"}),
           label(f"{p}_lblSpExtra", '"Servizi aggiuntivi"', X0 + 40, 316, 250, 24, size=11, extra=v(3)),
           label(f"{p}_lblSpExtraV", f"Text({extra}, {EURO2})", X0 + 290, 316, lw3 - 282, 24, size=11, bold=True,
                 align="Align.Right", extra=v(3)),
           rect(f"{p}_recSpSep", X0 + 40, 356, lw3 - 32, 1, "nfBordo", extra=v(3)),
           label(f"{p}_lblSpTot", '"Totale a listino"', X0 + 40, 368, 200, 30, size=13, bold=True, extra=v(3)),
           label(f"{p}_lblSpTotV", f"Text({totale}, {EURO2})", X0 + 220, 366, lw3 - 212, 34, size=18, bold=True,
                 align="Align.Right", color="nfAccento", extra=v(3)),
           label(f"{p}_lblSpNota",
                 '"Prezzi dal listino " & gblAnno & ". Passi espositore ed energia elettrica sono preimpostati come nei contratti precedenti."',
                 X0 + 40, 420, lw3 - 32, 60, size=10, color="nfTestoSec", extra=v(3)),
           label(f"{p}_lblExTit", '"Servizi aggiuntivi dal listino"', X0 + 468, 164, PW - 492, 26, size=14, bold=True, extra=v(3))]
    passo = "If(ThisItem.Unità = \"m²\", locStand.'Metri quadri', 1)"
    ex_riga = [
        label(f"{p}_lblExD", "ThisItem.Descrizione", 12, 8, 270, 24, size=12, bold=True, indent=t),
        label(f"{p}_lblExP", f"Text(ThisItem.'Prezzo unitario', {EURO}) & \" \" & Coalesce(ThisItem.Unità, \"\")", 12, 34, 270, 20,
              size=10, color="nfTestoSec", indent=t),
        button(f"{p}_btnExMeno", '"-"', 290, 14, 34, 36,
               f"Patch(colExtra, ThisItem, {{Qta: Max(0, ThisItem.Qta - {passo})}})",
               fill="nfCard", color="nfTesto", indent=t, extra={"Size": 16, "BorderColor": "nfBordo", "BorderThickness": 1}),
        label(f"{p}_lblExQ", 'Text(ThisItem.Qta, "#,##0.##")', 326, 14, 56, 36, size=13, bold=True, align="Align.Center",
              indent=t, extra={"Fill": "If(ThisItem.Qta > 0, nfAccentoChiaro, nfSfondo)"}),
        button(f"{p}_btnExPiu", '"+"', 384, 14, 34, 36,
               f"Patch(colExtra, ThisItem, {{Qta: Min(Coalesce(ThisItem.Disponibilità, 9999), ThisItem.Qta + {passo})}})",
               indent=t, extra={"Size": 16}),
        label(f"{p}_lblExT", f"If(ThisItem.Qta > 0, Text(ThisItem.Qta * ThisItem.'Prezzo unitario', {EURO}), \"-\")",
              430, 14, 150, 36, size=12, bold=True, align="Align.Right", indent=t),
        rect(f"{p}_recExSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    ch.append(control(f"{p}_galExtra", "Gallery", {
        "Items": "colExtra", "X": X0 + 468, "Y": 194, "Width": PW - 492, "Height": 494, "TemplateSize": 64,
        "TemplatePadding": 0, "ShowScrollbar": "true", **v(3)},
        children=ex_riga, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"))

    # ---- passo 4: riepilogo, sconto, salvataggio
    lw4 = 520
    ch += [rect(f"{p}_recRiep", X0 + 24, 164, lw4, 524, "nfSfondo", extra=v(4)),
           label(f"{p}_lblRiTit", '"Riepilogo"', X0 + 40, 176, lw4 - 32, 28, size=16, bold=True, extra=v(4)),
           label(f"{p}_lblRiEsp", "locEsp.'Ragione sociale' & \" · \" & locEsp.'ID espositore'", X0 + 40, 208, lw4 - 32, 24,
                 size=12, bold=True, extra=v(4)),
           label(f"{p}_lblRiStand",
                 "\"Stand \" & locStand.'Codice stand' & \" · \" & Text(locStand.'Metri quadri') & \" m² · \" & locStand.PosTxt & \" · edizione \" & gblAnno",
                 X0 + 40, 232, lw4 - 32, 22, size=11, color="nfTestoSec", extra=v(4)),
           label(f"{p}_lblRiRinn",
                 f'If(IsBlank({prec}), "Primo anno: non è un rinnovo", "Rinnovo (presente anche nel " & {anno_prec} & ")")',
                 X0 + 40, 254, lw4 - 32, 22, size=11, color="nfTestoSec", extra=v(4)),
           label(f"{p}_lblRiArea", f"\"Area espositiva  \" & Text(locStand.'Metri quadri') & \" m² × \" & Text(locPrezzoMq, {EURO})",
                 X0 + 40, 292, 330, 24, size=11, extra=v(4)),
           label(f"{p}_lblRiAreaV", f"Text({area}, {EURO2})", X0 + 370, 292, lw4 - 362, 24, size=11, bold=True,
                 align="Align.Right", extra=v(4)),
           label(f"{p}_lblRiMagg", "\"Maggiorazione \" & locStand.PosTxt", X0 + 40, 318, 330, 24, size=11,
                 extra={"Visible": "locPasso = 4 && locPct > 0"}),
           label(f"{p}_lblRiMaggV", f"Text({magg}, {EURO2})", X0 + 370, 318, lw4 - 362, 24, size=11, bold=True,
                 align="Align.Right", extra={"Visible": "locPasso = 4 && locPct > 0"})]
    ri_riga = [
        label(f"{p}_lblRiD", "ThisItem.Descrizione", 0, 4, 250, 24, size=11, indent=t),
        label(f"{p}_lblRiQ", "Text(ThisItem.Qta, \"#,##0.##\") & \" × \" & Text(ThisItem.'Prezzo unitario', \"#,##0\")", 250, 4, 120, 24,
              size=10, color="nfTestoSec", align="Align.Right", indent=t),
        label(f"{p}_lblRiT", f"Text(ThisItem.Qta * ThisItem.'Prezzo unitario', {EURO2})", 370, 4, 118, 24, size=11,
              bold=True, align="Align.Right", indent=t),
    ]
    ch.append(control(f"{p}_galRiep", "Gallery", {
        "Items": "Filter(colExtra, Qta > 0)", "X": X0 + 40, "Y": 350, "Width": lw4 - 32, "Height": 330,
        "TemplateSize": 32, "TemplatePadding": 0, "ShowScrollbar": "true", **v(4)},
        children=ri_riga, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"))
    rx4, rw4 = X0 + 24 + lw4 + 24, PW - 24 - lw4 - 24 - 24
    ch.append(label(f"{p}_lblScTit", '"Sconto commerciale"', rx4, 176, rw4, 26, size=14, bold=True, extra=v(4)))
    for i, sc in enumerate([0, 0.05, 0.10, 0.15, 0.20]):
        val = f"{sc:g}"
        ch.append(button(f"{p}_btnSc{i}", f'"{int(sc * 100)}%"', rx4 + i * ((rw4 - 4 * 8) // 5 + 8), 208,
                         (rw4 - 4 * 8) // 5, 40, f"UpdateContext({{locSconto: {val}}})",
                         fill=f"If(locSconto = {val}, nfAccento, nfCard)", color=f"If(locSconto = {val}, Color.White, nfTesto)",
                         extra={"BorderColor": "nfBordo", "BorderThickness": 1, **v(4)}))
    righe_tot = [("Totale a listino", f"Text({totale}, {EURO2})", 276, False),
                 ("Sconto", f"\"- \" & Text({totale} - {imponib}, {EURO2})", 308, False),
                 ("Imponibile", f"Text({imponib}, {EURO2})", 346, True),
                 ("Acconto alla firma (30%)", f"Text({acconto}, {EURO2})", 400, False),
                 ("Saldo (70%)", f"Text({imponib} - {acconto}, {EURO2})", 432, False)]
    for k, (cap, val, y, forte) in enumerate(righe_tot):
        ch += [label(f"{p}_lblTotC{k}", f'"{cap}"', rx4, y, rw4 - 200, 30, size=15 if forte else 12, bold=forte, extra=v(4)),
               label(f"{p}_lblTotV{k}", val, rx4 + rw4 - 200, y, 200, 30, size=18 if forte else 12, bold=True,
                     align="Align.Right", color="nfAccento" if forte else "nfTesto", extra=v(4))]
    ch.append(label(f"{p}_lblNota",
                    ("\"Il contratto si salva come preventivo. Alla firma si fissano la scadenza dell'acconto (15 giorni) e quella del saldo (\" & "
                     "Text(DateAdd(LookUp(Edizioni, Anno = gblAnno).'Data inizio', -30, TimeUnit.Days), \"dd/mm/yyyy\") & \", 30 giorni prima della fiera).\""),
                    rx4, 480, rw4, 84, size=10, color="nfTestoSec", extra=v(4)))

    # ---- navigazione tra i passi
    pronto2 = ("LookUp(colListino, Codice = \"SPAZIO-\" & locStand.CodPad).'Prezzo unitario'")
    vai3 = f"""UpdateContext({{locPasso: 3, locPrezzoMq: {pronto2},
    locPct: If(locStand.PosTxt = "linea", 0, LookUp(colListino, Codice = "MAGG-" & Upper(locStand.PosTxt)).'Prezzo unitario')}});
ClearCollect(colExtra, AddColumns(Filter(colListino, StartsWith(Codice, "EX-") || StartsWith(Codice, "SP-")),
    Qta, Switch(Codice, "EX-PASS", 5, "EX-EL3", 1, 0), Ord, {ORD_SERVIZI}))"""
    rinn = f"!IsBlank({prec})"
    riga_sp = ("{Contratto: gblNuovo, Riga: 1, 'Codice voce': \"SPAZIO\", Descrizione: \"Area espositiva \" & locStand.'Codice stand', "
               f"Quantità: locStand.'Metri quadri', 'Prezzo unitario': locPrezzoMq, Importo: Round({area}, 2)}}")
    riga_mg = ("{Contratto: gblNuovo, Riga: 2, 'Codice voce': \"MAGG\", Descrizione: \"Maggiorazione \" & locStand.PosTxt, "
               f"Quantità: 1, 'Prezzo unitario': {magg}, Importo: {magg}}}")
    riga_ex = ("{Contratto: gblNuovo, Riga: If(locPct > 0, 2, 1) + CountRows(Filter(colExtra, Qta > 0 && Ord <= ex.Ord)), "
               "'Codice voce': ex.Codice, Descrizione: ex.Descrizione, Quantità: ex.Qta, "
               "'Prezzo unitario': ex.'Prezzo unitario', Importo: Round(ex.Qta * ex.'Prezzo unitario', 2)}")
    # Il numero del contratto lo assegna Dataverse (numerazione automatica di g5_id_contratto, formato
    # C<anno>-<nnnn>): l'app non lo calcola, così due salvataggi insieme non possono avere lo stesso numero.
    # Se il contratto è stato creato ma una riga non si salva, il contratto si annulla (non resta senza righe).
    salva = f"""Set(gblNuovo, Blank());
IfError(
    UpdateContext({{locSalva: true}});
    Refresh(Contratti);
    {CARICA};
    If(!IsBlank(LookUp(colContratti, AnnoEd = gblAnno && CodStand = locStand.'Codice stand' && StatoTxt <> "annullato")),
        Notify("Lo stand " & locStand.'Codice stand' & " risulta già venduto: sceglierne un altro", NotificationType.Error);
        UpdateContext({{locSalva: false, locPasso: 2}}),
        Set(gblNuovo, Patch(Contratti, Defaults(Contratti),
            {{Edizione: LookUp(Edizioni, Anno = gblAnno), Espositore: locEsp,
              Stand: LookUp(Stand, 'Codice stand' = locStand.'Codice stand'),
              'Stato (g5_stato)': 'Stato (Contratti)'.preventivo,
              'Imponibile a listino': {totale}, Sconto: locSconto, Imponibile: {imponib}, Rinnovo: {rinn}}}));
        Patch('Righe contratto', Defaults('Righe contratto'), {riga_sp});
        If(locPct > 0, Patch('Righe contratto', Defaults('Righe contratto'), {riga_mg}));
        ForAll(Filter(colExtra, Qta > 0) As ex, Patch('Righe contratto', Defaults('Righe contratto'), {riga_ex}));
        {CARICA};
        Notify("Preventivo " & gblNuovo.'ID contratto' & " creato", NotificationType.Success);
        UpdateContext({{locSalva: false}});
        Clear(colRighe);
        Navigate(scrContratti, ScreenTransition.None, {{locStato: "Tutti", locConf: false}})
    ),
    UpdateContext({{locSalva: false}});
    If(!IsBlank(gblNuovo),
        IfError(Patch(Contratti, gblNuovo, {{'Stato (g5_stato)': 'Stato (Contratti)'.annullato}}); true, false);
        Notify("Righe non salvate: il contratto " & gblNuovo.'ID contratto' & " è stato annullato. Riprovare.", NotificationType.Error),
        Notify("Salvataggio non riuscito: " & FirstError.Message, NotificationType.Error))
)"""
    ch += [label(f"{p}_lblHint",
                 ('If(locPasso = 1, If(IsBlank(locEsp), "Seleziona un espositore per continuare", '
                  '"Selezionato: " & locEsp.\'Ragione sociale\'), If(locPasso = 2, If(IsBlank(locStand), '
                  '"Seleziona uno stand libero per continuare", "Selezionato: stand " & locStand.\'Codice stand\'), ""))'),
                 X0 + 180, H - 64, 600, 40, size=11, color="nfTestoSec"),
           button(f"{p}_btnIndietro", '"Indietro"', X0 + 24, H - 64, 140, 40, "UpdateContext({locPasso: locPasso - 1})",
                  fill="nfCard", color="nfTesto",
                  extra={"BorderColor": "nfBordo", "BorderThickness": 1, "Visible": "locPasso > 1"}),
           button(f"{p}_btnAvanti1", '"Avanti"', X0 + PW - 24 - 200, H - 64, 200, 40, "UpdateContext({locPasso: 2})",
                  extra={"DisabledFill": "nfBordo", "DisabledColor": "nfTestoSec",
                         "DisplayMode": "If(IsBlank(locEsp), DisplayMode.Disabled, DisplayMode.Edit)", **v(1)}),
           button(f"{p}_btnAvanti2", '"Avanti"', X0 + PW - 24 - 200, H - 64, 200, 40, vai3,
                  extra={"DisabledFill": "nfBordo", "DisabledColor": "nfTestoSec",
                         "DisplayMode": "If(IsBlank(locStand), DisplayMode.Disabled, DisplayMode.Edit)", **v(2)}),
           button(f"{p}_btnAvanti3", '"Avanti"', X0 + PW - 24 - 200, H - 64, 200, 40, "UpdateContext({locPasso: 4})",
                  extra=v(3)),
           button(f"{p}_btnSalva", 'If(locSalva, "Salvataggio...", "Salva preventivo")', X0 + PW - 24 - 200, H - 64, 200, 40,
                  salva, fill="nfVerde",
                  extra={"DisabledFill": "nfBordo", "DisabledColor": "nfTestoSec",
                         "DisplayMode": "If(locSalva, DisplayMode.Disabled, DisplayMode.Edit)", **v(4)})]
    # Se si arriva da "Rinnovi e prelazione" (gblEspIniz) l'espositore è già scelto: si parte dal passo 2, con lo stand
    # storico preselezionato solo se è ancora libero (prelazione come informazione, non come blocco).
    onvisible = f"""Set(gblAnno, "2026");
UpdateContext({{locPasso: If(IsBlank(gblEspIniz), 1, 2),
    locEsp: If(IsBlank(gblEspIniz), LookUp(Espositori, 'ID espositore' = ""), gblEspIniz),
    locStand: If(!IsBlank(gblStandIniz) && IsBlank(LookUp(colContratti, AnnoEd = "2026" && CodStand = gblStandIniz.'Codice stand' && StatoTxt <> "annullato")),
        gblStandIniz, LookUp(colStand, 'Codice stand' = "")),
    locSconto: 0, locPad: If(IsBlank(gblStandIniz), "P1", gblStandIniz.CodPad), locSalva: false, locPrezzoMq: 0, locPct: 0}});
Set(gblEspIniz, Blank());
Set(gblStandIniz, Blank());
ClearCollect(colListino, 'Voci listino');
ClearCollect(colExtra, AddColumns(Filter(colListino, StartsWith(Codice, "EX-") || StartsWith(Codice, "SP-")),
    Qta, 0, Ord, {ORD_SERVIZI}))"""
    return screen("scrNuovo", {"Fill": "nfSfondo", "OnVisible": onvisible}, ch)


# ---------------------------------------------------------------------------
# Scadenze e incassi: tutti gli acconti e i saldi dei contratti firmati, per urgenza
# Nessuna tabella nuova: acconto e saldo sono colonne di Contratti; gli importi (30% / 70%) si calcolano.
# ---------------------------------------------------------------------------
# colPag ha una riga per pagamento (due per contratto firmato). Lo stato si calcola alla lettura:
# pagato / pagato in ritardo / scaduto / in scadenza (entro 30 giorni) / da pagare.
CARICA_PAG = """ClearCollect(colPagBase, ForAll(Filter(colContratti, StatoTxt = "firmato") As c,
    {IdC: c.'ID contratto', RagSoc: c.RagSoc, CodStand: c.CodStand, IdEsp: c.IdEsp, AnnoEd: c.AnnoEd,
     Tipo: "Acconto", Importo: Round(c.Imponibile * 0.3, 2), Scad: c.'Scadenza acconto', Pagato: c.'Acconto pagato il'}));
Collect(colPagBase, ForAll(Filter(colContratti, StatoTxt = "firmato") As c,
    {IdC: c.'ID contratto', RagSoc: c.RagSoc, CodStand: c.CodStand, IdEsp: c.IdEsp, AnnoEd: c.AnnoEd,
     Tipo: "Saldo", Importo: c.Imponibile - Round(c.Imponibile * 0.3, 2), Scad: c.'Scadenza saldo', Pagato: c.'Saldo pagato il'}));
ClearCollect(colPag, AddColumns(colPagBase,
    Esito, If(!IsBlank(Pagato), If(Pagato > Scad, "Pagato in ritardo", "Pagato"),
              If(Scad < Today(), "Scaduto", If(Scad <= DateAdd(Today(), 30, TimeUnit.Days), "In scadenza", "Da pagare"))),
    Giorni, If(IsBlank(Pagato), DateDiff(Scad, Today(), TimeUnit.Days), 0)))"""


def scadenze():
    p = "sc"
    cerca = f"{p}_txtCerca.Text"
    base = 'Filter(colPag, locEdiz = "Tutte" || AnnoEd = locEdiz)'
    filtro = (f'Filter({base}, (locEsito = "Tutti" || (locEsito = "Aperti" && IsBlank(Pagato))'
              ' || (locEsito = "Pagati" && !IsBlank(Pagato)) || Esito = locEsito)'
              f" && (IsBlank({cerca}) || {cerca} in IdC || {cerca} in RagSoc || {cerca} in CodStand))")
    t = 12
    ch = sidebar(p, "Scadenze") + header(
        p, '"Scadenze e incassi"', '"Acconti e saldi dei contratti firmati · oggi " & Text(Today(), "dd/mm/yyyy")')
    ch.append(label(f"{p}_lblEd", '"Edizione"', 1060, 26, 90, 40, size=11, color="nfTestoSec", align="Align.Right"))
    ch.append(control(f"{p}_ddEdizione", "Classic/DropDown", {
        "Items": '["Tutte", "2026", "2025", "2024"]', "Default": "locEdiz", "X": 1160, "Y": 26, "Width": 170, "Height": 40,
        "OnChange": "UpdateContext({locEdiz: Self.Selected.Value})", "Font": "nfFont", "Size": 12,
        "BorderColor": "nfBordo", "Fill": "nfCard", "ChevronBackground": "nfCard", "ChevronFill": "nfTesto"}))

    # indicatori: seguono l'edizione scelta, non il filtro di stato
    aperti = f"Filter({base}, IsBlank(Pagato))"
    kpi = [("Da incassare", f"Text(Sum({aperti}, Importo), {EURO})", f'CountRows({aperti}) & " pagamenti aperti"', "nfBlu"),
           ("In ritardo", f'Text(Sum(Filter({base}, Esito = "Scaduto"), Importo), {EURO})',
            f'CountRows(Filter({base}, Esito = "Scaduto")) & " pagamenti scaduti"', "nfRosso"),
           ("In scadenza entro 30 giorni", f'Text(Sum(Filter({base}, Esito = "In scadenza"), Importo), {EURO})',
            f'CountRows(Filter({base}, Esito = "In scadenza")) & " pagamenti"', "nfAmbra"),
           ("Incassato", f"Text(Sum(Filter({base}, !IsBlank(Pagato)), Importo), {EURO})",
            f'CountRows(Filter({base}, !IsBlank(Pagato))) & " pagati · " & CountRows(Filter({base}, Esito = "Pagato in ritardo")) & " in ritardo"',
            "nfVerde")]
    cw, gap = 259, 16
    for i, (cap, val, sub, col) in enumerate(kpi):
        x = X0 + i * (cw + gap)
        ch += [rect(f"{p}_recKpi{i}", x, 96, cw, 104, "nfCard", "nfBordo"),
               rect(f"{p}_recKpiBar{i}", x, 96, cw, 4, col),
               label(f"{p}_lblKpiCap{i}", f'"{cap}"', x + 20, 110, cw - 40, 20, size=11, color="nfTestoSec"),
               label(f"{p}_lblKpiVal{i}", val, x + 20, 132, cw - 40, 36, size=22, bold=True),
               label(f"{p}_lblKpiSub{i}", sub, x + 20, 170, cw - 40, 20, size=10, color="nfTestoSec")]

    # filtri
    ch.append(control(f"{p}_txtCerca", "Classic/TextInput", {
        "Default": '""', "HintText": '"Cerca per espositore, contratto o stand"', "DelayOutput": "true",
        "X": X0, "Y": 214, "Width": 300, "Height": 40, "Font": "nfFont", "Size": 12, "BorderColor": "nfBordo",
        "Fill": "nfCard", "RadiusTopLeft": 8, "RadiusTopRight": 8, "RadiusBottomLeft": 8, "RadiusBottomRight": 8}))
    for i, (val, testo) in enumerate([("Aperti", "Da incassare"), ("Scaduto", "Scaduti"), ("In scadenza", "In scadenza"),
                                      ("Pagati", "Pagati"), ("Tutti", "Tutti")]):
        ch.append(button(f"{p}_btnFiltro{i}", f'"{testo}"', X0 + 316 + i * 138, 214, 130, 40,
                         f'UpdateContext({{locEsito: "{val}"}})',
                         fill=f'If(locEsito = "{val}", nfAccento, nfCard)',
                         color=f'If(locEsito = "{val}", Color.White, nfTesto)',
                         extra={"BorderColor": "nfBordo", "BorderThickness": 1}))

    # elenco
    py, ph = 270, H - 270 - 16
    ch += [rect(f"{p}_recLista", X0, py, PW_SC, ph, "nfCard", "nfBordo")]
    for nome, off, w, al in [("Espositore · contratto", 20, 360, "Align.Left"), ("Pagamento", 390, 120, "Align.Left"),
                             ("Scadenza", 520, 130, "Align.Left"), ("Stato", 660, 170, "Align.Left")]:
        ch.append(label(f"{p}_lblH{off}", f'"{nome}"', X0 + 1 + off, py + 6, w, 20, size=9, color="nfTestoSec", align=al))
    ch.append(label(f"{p}_lblConta", f'CountRows({filtro}) & " pagamenti · " & Text(Sum({filtro}, Importo), {EURO})',
                    X0 + 840, py + 6, 240, 20, size=10, bold=True, align="Align.Right", color="nfAccento"))
    badge_fill = ('Switch(ThisItem.Esito, "Scaduto", nfRossoChiaro, "In scadenza", nfAmbraChiaro, "Pagato", nfVerdeChiaro,'
                  ' "Pagato in ritardo", nfAmbraChiaro, nfBordo)')
    badge_col = ('Switch(ThisItem.Esito, "Scaduto", nfRosso, "In scadenza", nfAmbra, "Pagato", nfVerde,'
                 ' "Pagato in ritardo", nfAmbra, nfTestoSec)')
    badge_txt = ('Switch(ThisItem.Esito, "Scaduto", "Scaduto da " & ThisItem.Giorni & " gg",'
                 ' "In scadenza", If(ThisItem.Giorni = 0, "Scade oggi", "Scade tra " & Abs(ThisItem.Giorni) & " gg"), ThisItem.Esito)')
    aperto = "IsBlank(ThisItem.Pagato)"
    segna = f"""IfError(
    With({{rec: LookUp(Contratti, 'ID contratto' = ThisItem.IdC)}},
        If(ThisItem.Tipo = "Acconto",
            Patch(Contratti, rec, {{'Acconto pagato il': Today()}}),
            Patch(Contratti, rec, {{'Saldo pagato il': Today()}})));
    Notify(ThisItem.Tipo & " registrato", NotificationType.Success);
    {RICARICA};
    {CARICA_PAG},
    Notify("Registrazione non riuscita: " & FirstError.Message, NotificationType.Error)
)"""
    sollecito = """With({em: LookUp(Espositori, 'ID espositore' = ThisItem.IdEsp)},
    Launch("mailto:" & em.'Email referente' & "?subject="
        & EncodeUrl(If(ThisItem.Esito = "Scaduto", "Sollecito di pagamento", "Promemoria di pagamento") & " - contratto " & ThisItem.IdC)
        & "&body=" & EncodeUrl("Gentile " & em.Referente & "," & Char(10) & Char(10)
        & If(ThisItem.Esito = "Scaduto", "ci risulta ancora da incassare ", "ricordiamo che sta per scadere ")
        & If(ThisItem.Tipo = "Acconto", "l'acconto del 30%", "il saldo") & " del contratto " & ThisItem.IdC
        & " (stand " & ThisItem.CodStand & "), pari a € " & Text(ThisItem.Importo, "#,##0.00")
        & ", con scadenza " & Text(ThisItem.Scad, "dd/mm/yyyy") & "." & Char(10) & Char(10)
        & "Cordiali saluti," & Char(10) & "Ufficio commerciale ARCADE Milano")))"""
    riga = [
        rect(f"{p}_recRiga", 0, 0, "Parent.TemplateWidth", "Parent.TemplateHeight", "nfCard", indent=t),
        label(f"{p}_lblRag", "ThisItem.RagSoc", 20, 6, 360, 22, size=12, bold=True, indent=t),
        label(f"{p}_lblIdc", 'ThisItem.IdC & " · stand " & ThisItem.CodStand & " · ed. " & ThisItem.AnnoEd', 20, 30, 360, 20,
              size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblTipo", "ThisItem.Tipo", 390, 6, 120, 22, size=12, bold=True, indent=t),
        label(f"{p}_lblImp", f"Text(ThisItem.Importo, {EURO2})", 390, 30, 120, 20, size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblScad", 'Text(ThisItem.Scad, "dd/mm/yyyy")', 520, 6, 130, 22, size=12, indent=t),
        label(f"{p}_lblPag", 'If(IsBlank(ThisItem.Pagato), "Non pagato", "Pagato il " & Text(ThisItem.Pagato, "dd/mm/yyyy"))',
              520, 30, 130, 20, size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblBadge", badge_txt, 660, 14, 170, 26, size=10, bold=True, align="Align.Center", indent=t,
              extra={"Fill": badge_fill, "Color": badge_col}),
        button(f"{p}_btnPagato", '"Segna pagato"', 840, 12, 120, 30, segna, indent=t,
               extra={"Size": 11, "Visible": aperto}),
        button(f"{p}_btnSollecito", 'If(ThisItem.Esito = "Scaduto", "Sollecito", "Promemoria")', 970, 12, 110, 30, sollecito,
               fill="nfAccentoChiaro", color="nfAccento", indent=t,
               extra={"Size": 11, "Visible": f'{aperto} && (ThisItem.Esito = "Scaduto" || ThisItem.Esito = "In scadenza")'}),
        rect(f"{p}_recRigaSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    ch += [control(f"{p}_galPag", "Gallery", {
               "Items": f"Sort({filtro}, Scad)", "X": X0 + 1, "Y": py + 30, "Width": PW_SC - 2, "Height": ph - 32,
               "TemplateSize": 56, "TemplatePadding": 0, "ShowScrollbar": "true"},
               children=riga, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"),
           label(f"{p}_lblVuoto", '"Nessun pagamento con questi filtri"', X0 + 24, py + 70, PW_SC - 48, 40, size=12,
                 color="nfTestoSec", align="Align.Center", extra={"Visible": f"IsEmpty({filtro})"})]
    onvisible = ('If(IsBlank(locEdiz), UpdateContext({locEdiz: "Tutte", locEsito: "Aperti"}));\n' + CARICA_PAG)
    return screen("scrScadenze", {"Fill": "nfSfondo", "OnVisible": onvisible}, ch)


PW_SC = W - X0 - 24                       # larghezza dell'area contenuti

# ---------------------------------------------------------------------------
# Rinnovi e prelazione: chi ha comprato nell'edizione precedente e non ha ancora un contratto in questa
# Nessuna tabella nuova: tutto si calcola da Contratti, Stand ed Espositori.
# Indice di rinnovo = punti 0-3 (spiegabile): presente anche due edizioni prima (fedele), pagamenti entro 30 giorni
# dalla scadenza (puntuale), sconto contenuto (<= 5%). Soglia dei 30 giorni scelta sui dati 2025:
# 40 espositori alta (3 punti), 50 media (2), 20 bassa (<= 1).
# ---------------------------------------------------------------------------
CARICA_RINN = """ClearCollect(colRinnBase, ForAll(Filter(colContratti, AnnoEd = Text(Value(gblAnno) - 1, "0") && StatoTxt <> "annullato") As c,
    {IdEsp: c.IdEsp, RagSoc: c.RagSoc, StandPrec: c.CodStand, ImpPrec: c.Imponibile, ScoPrec: c.Sconto,
     Fedele: !IsBlank(LookUp(colContratti, IdEsp = c.IdEsp && AnnoEd = Text(Value(gblAnno) - 2, "0") && StatoTxt <> "annullato")),
     Puntuale: !IsBlank(c.'Acconto pagato il') && !IsBlank(c.'Saldo pagato il')
         && c.'Acconto pagato il' <= DateAdd(c.'Scadenza acconto', 30, TimeUnit.Days)
         && c.'Saldo pagato il' <= DateAdd(c.'Scadenza saldo', 30, TimeUnit.Days)}));
ClearCollect(colRinn, AddColumns(colRinnBase, Punti, If(Fedele, 1, 0) + If(Puntuale, 1, 0) + If(ScoPrec <= 0.05, 1, 0)))"""


def rinnovi():
    p = "rn"
    cerca = f"{p}_txtCerca.Text"
    ha_contratto = "LookUp(colContratti, IdEsp = r.IdEsp && AnnoEd = gblAnno && StatoTxt <> \"annullato\")"
    da_contattare = f"Filter(colRinn As r, IsBlank({ha_contratto}))"
    rinnovati = f"Filter(colRinn As r, !IsBlank({ha_contratto}))"
    filtro = (f'Filter(colRinn As r, (locRin = "Tutti" || (locRin = "Da contattare" && IsBlank({ha_contratto}))'
              f' || (locRin = "Rinnovati" && !IsBlank({ha_contratto})))'
              ' && (locIdx = "Tutti" || Switch(r.Punti, 3, "Alta", 2, "Media", "Bassa") = locIdx)'
              f" && (IsBlank({cerca}) || {cerca} in r.RagSoc || {cerca} in r.IdEsp || {cerca} in r.StandPrec))")
    t = 12
    prec_anno = 'Text(Value(gblAnno) - 1, "0")'
    ch = sidebar(p, "Rinnovi") + header(
        p, '"Rinnovi e prelazione"',
        f'"Espositori " & {prec_anno} & " da riconfermare per il " & gblAnno'
        ' & " · prelazione " & Coalesce(LookUp(colListino, Codice = "COND-PRELAZ").Note, "")')
    ch.append(label(f"{p}_lblEd", '"Edizione"', 1060, 26, 90, 40, size=11, color="nfTestoSec", align="Align.Right"))
    ch.append(control(f"{p}_ddEdizione", "Classic/DropDown", {
        "Items": '["2026", "2025"]', "Default": "gblAnno", "X": 1160, "Y": 26, "Width": 170, "Height": 40,
        "OnChange": "Set(gblAnno, Self.Selected.Value);\n" + CARICA_RINN, "Font": "nfFont", "Size": 12,
        "BorderColor": "nfBordo", "Fill": "nfCard", "ChevronBackground": "nfCard", "ChevronFill": "nfTesto"}))
    kpi = [("Da riconfermare", "CountRows(colRinn)", f'"Contratti " & {prec_anno} & " non annullati"', "nfBlu"),
           ("Già rinnovati", f"CountRows({rinnovati})",
            f'Text(CountRows({rinnovati}) / Max(1, CountRows(colRinn)), "0%") & " del totale"', "nfVerde"),
           ("Da contattare", f"CountRows({da_contattare})",
            f'CountRows(Filter({da_contattare}, Punti = 3)) & " con indice di rinnovo alto"', "nfAmbra"),
           ("Valore da rinnovare", f"Text(Sum({da_contattare}, ImpPrec), {EURO})",
            '"imponibile dei contratti " & ' + prec_anno, "nfAccento")]
    cw, gap = 259, 16
    for i, (cap, val, sub, col) in enumerate(kpi):
        x = X0 + i * (cw + gap)
        ch += [rect(f"{p}_recKpi{i}", x, 96, cw, 104, "nfCard", "nfBordo"),
               rect(f"{p}_recKpiBar{i}", x, 96, cw, 4, col),
               label(f"{p}_lblKpiCap{i}", f'"{cap}"', x + 20, 110, cw - 40, 20, size=11, color="nfTestoSec"),
               label(f"{p}_lblKpiVal{i}", val, x + 20, 132, cw - 40, 36, size=22, bold=True),
               label(f"{p}_lblKpiSub{i}", sub, x + 20, 170, cw - 40, 20, size=10, color="nfTestoSec")]
    ch.append(control(f"{p}_txtCerca", "Classic/TextInput", {
        "Default": '""', "HintText": '"Cerca espositore o stand"', "DelayOutput": "true",
        "X": X0, "Y": 214, "Width": 300, "Height": 40, "Font": "nfFont", "Size": 12, "BorderColor": "nfBordo",
        "Fill": "nfCard", "RadiusTopLeft": 8, "RadiusTopRight": 8, "RadiusBottomLeft": 8, "RadiusBottomRight": 8}))
    gruppi = [("locRin", ["Da contattare", "Rinnovati", "Tutti"]), ("locIdx", ["Alta", "Media", "Bassa", "Tutti"])]
    k = 0
    x = X0 + 316
    for var, valori in gruppi:
        for val in valori:
            testo = val if var == "locRin" else ("Indice " + val.lower() if val != "Tutti" else "Ogni indice")
            w = 118 if var == "locRin" else 104
            ch.append(button(f"{p}_btnFiltro{k}", f'"{testo}"', x, 214, w, 40, f'UpdateContext({{{var}: "{val}"}})',
                             fill=f'If({var} = "{val}", nfAccento, nfCard)', color=f'If({var} = "{val}", Color.White, nfTesto)',
                             extra={"Size": 11, "BorderColor": "nfBordo", "BorderThickness": 1}))
            x += w + 6
            k += 1
        x += 12

    py, ph = 270, H - 270 - 16
    ch.append(rect(f"{p}_recLista", X0, py, PW_SC, ph, "nfCard", "nfBordo"))
    for nome, off, w in [("Espositore", 20, 300), ("Stand storico", 330, 130), ("Valore", 470, 110),
                         ("Indice di rinnovo", 590, 220), ("Azione", 840, 200)]:
        ch.append(label(f"{p}_lblH{off}", f'"{nome}"', X0 + 1 + off, py + 6, w, 20, size=9, color="nfTestoSec"))
    ch.append(label(f"{p}_lblConta", f'CountRows({filtro}) & " espositori"', X0 + PW_SC - 24 - 180, py + 6, 180, 20, size=10,
                    bold=True, align="Align.Right", color="nfAccento"))
    rinn = "LookUp(colContratti, IdEsp = ThisItem.IdEsp && AnnoEd = gblAnno && StatoTxt <> \"annullato\")"
    stand_libero = "IsBlank(LookUp(colContratti, AnnoEd = gblAnno && CodStand = ThisItem.StandPrec && StatoTxt <> \"annullato\"))"
    indice = 'Switch(ThisItem.Punti, 3, "Alta", 2, "Media", "Bassa")'
    prepara = ("Set(gblEspIniz, LookUp(Espositori, 'ID espositore' = ThisItem.IdEsp));\n"
               "Set(gblStandIniz, LookUp(colStand, 'Codice stand' = ThisItem.StandPrec));\n"
               "Navigate(scrNuovo, ScreenTransition.None)")
    riga = [
        rect(f"{p}_recRiga", 0, 0, "Parent.TemplateWidth", "Parent.TemplateHeight", "nfCard", indent=t),
        label(f"{p}_lblRag", "ThisItem.RagSoc", 20, 6, 300, 22, size=12, bold=True, indent=t),
        label(f"{p}_lblInfo", f'ThisItem.IdEsp & " · " & If(ThisItem.Fedele, "presente anche nel " & Text(Value(gblAnno) - 2, "0"), "prima volta nel " & {prec_anno})',
              20, 30, 300, 20, size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblStand", '"Stand " & ThisItem.StandPrec', 330, 6, 130, 22, size=12, bold=True, indent=t),
        label(f"{p}_lblLibero", f'If({stand_libero}, "Libero: prelazione", "Già venduto")', 330, 30, 130, 20, size=10, bold=True,
              indent=t, extra={"Color": f"If({stand_libero}, nfVerde, nfRosso)"}),
        label(f"{p}_lblImp", f"Text(ThisItem.ImpPrec, {EURO})", 470, 6, 110, 22, size=12, bold=True, indent=t),
        label(f"{p}_lblSco", '"sconto " & Text(ThisItem.ScoPrec, "0%")', 470, 30, 110, 20, size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblIdx", indice, 590, 8, 80, 22, size=10, bold=True, align="Align.Center", indent=t, extra={
            "Fill": 'Switch(ThisItem.Punti, 3, nfVerdeChiaro, 2, nfAmbraChiaro, nfBordo)',
            "Color": 'Switch(ThisItem.Punti, 3, nfVerde, 2, nfAmbra, nfTestoSec)'}),
        label(f"{p}_lblMotivi",
              'If(ThisItem.Fedele, "Fedele", "Nuovo") & " · " & If(ThisItem.Puntuale, "Puntuale", "Ritardi") & " · " & If(ThisItem.ScoPrec <= 0.05, "Sconto basso", "Sconto alto")',
              590, 32, 240, 18, size=9, color="nfTestoSec", indent=t),
        button(f"{p}_btnPrepara", '"Prepara preventivo"', 840, 14, 200, 32, prepara, indent=t,
               extra={"Size": 11, "Visible": f'gblAnno = "2026" && IsBlank({rinn})'}),
        label(f"{p}_lblRinn", f'"Rinnovato · " & {rinn}.\'ID contratto\'', 840, 14, 220, 32, size=11, bold=True, indent=t,
              extra={"Color": "nfVerde", "Visible": f"!IsBlank({rinn})"}),
        rect(f"{p}_recRigaSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    ch += [control(f"{p}_galRinn", "Gallery", {
               "Items": f'SortByColumns({filtro}, "Punti", SortOrder.Descending, "ImpPrec", SortOrder.Descending)',
               "X": X0 + 1, "Y": py + 30, "Width": PW_SC - 2, "Height": ph - 32, "TemplateSize": 60,
               "TemplatePadding": 0, "ShowScrollbar": "true"},
               children=riga, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"),
           label(f"{p}_lblVuoto", '"Nessun espositore con questi filtri"', X0 + 24, py + 70, PW_SC - 48, 40, size=12,
                 color="nfTestoSec", align="Align.Center", extra={"Visible": f"IsEmpty({filtro})"})]
    onvisible = ('If(IsBlank(locRin), UpdateContext({locRin: "Da contattare", locIdx: "Tutti"}));\n'
                 "If(IsEmpty(colListino), ClearCollect(colListino, 'Voci listino'));\n" + CARICA_RINN)
    return screen("scrRinnovi", {"Fill": "nfSfondo", "OnVisible": onvisible}, ch)


# ---------------------------------------------------------------------------
# Listino 2026: elenco delle voci e modifica di prezzo, disponibilità e note
# Nessuna tabella nuova: legge e scrive 'Voci listino'. I contratti già creati non cambiano
# (ogni riga contratto conserva il prezzo con cui è stata venduta).
# ---------------------------------------------------------------------------
def listino():
    p = "ls"
    sel = f"{p}_galListino.Selected"
    categorie = [("Spazio", "SPAZIO"), ("Maggiorazioni", "MAGG"), ("Servizi", "EX-"), ("Sponsor", "SP-"), ("Condizioni", "COND")]
    conds = " || ".join(f'(locCat = "{n}" && StartsWith(Codice, "{pre}"))' for n, pre in categorie)
    filtro = f'Filter(colListino, locCat = "Tutte" || {conds})'
    ch = sidebar(p, "Listino") + header(
        p, '"Listino 2026"',
        'CountRows(colListino) & " voci · prezzi e disponibilità usati dai nuovi preventivi · i contratti già creati non cambiano"')
    for i, nome in enumerate(["Tutte"] + [n for n, _ in categorie]):
        ch.append(button(f"{p}_btnCat{i}", f'"{nome}"', X0 + i * 106, 96, 100, 40, f'UpdateContext({{locCat: "{nome}"}})',
                         fill=f'If(locCat = "{nome}", nfAccento, nfCard)', color=f'If(locCat = "{nome}", Color.White, nfTesto)',
                         extra={"Size": 11, "BorderColor": "nfBordo", "BorderThickness": 1}))
    t, lw = 12, 640
    riga = [
        rect(f"{p}_recRiga", 0, 0, "Parent.TemplateWidth", "Parent.TemplateHeight",
             "If(ThisItem.IsSelected, nfAccentoChiaro, nfCard)", indent=t),
        label(f"{p}_lblCod", "ThisItem.Codice", 16, 6, 260, 22, size=12, bold=True, indent=t),
        label(f"{p}_lblDesc", "ThisItem.Descrizione", 16, 30, 380, 20, size=10, color="nfTestoSec", indent=t),
        label(f"{p}_lblPrezzo", "If(IsBlank(ThisItem.'Prezzo unitario'), \"-\", Text(ThisItem.'Prezzo unitario', \"#,##0.00\") & \" \" & Coalesce(ThisItem.Unità, \"\"))",
              400, 6, 210, 22, size=12, bold=True, align="Align.Right", indent=t),
        label(f"{p}_lblDisp", "If(IsBlank(ThisItem.Disponibilità), \"disponibilità illimitata\", \"disponibili: \" & ThisItem.Disponibilità)",
              400, 30, 210, 20, size=10, color="nfTestoSec", align="Align.Right", indent=t),
        rect(f"{p}_recRigaSep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=t),
    ]
    ch += [rect(f"{p}_recLista", X0, 152, lw, H - 168, "nfCard", "nfBordo"),
           control(f"{p}_galListino", "Gallery", {
               "Items": f"Sort({filtro}, Codice)", "X": X0 + 1, "Y": 153, "Width": lw - 2, "Height": H - 170,
               "TemplateSize": 58, "TemplatePadding": 0, "ShowScrollbar": "true", "OnSelect": "UpdateContext({locConfL: false})"},
               children=riga, variant="BrowseLayout_Flexible_SocialFeed_ver5.0")]
    rx, rw = X0 + lw + 16, PW_SC - lw - 16
    tp, td, tn = f"{p}_txtPrezzo.Text", f"{p}_txtDisp.Text", f"{p}_txtNote.Text"
    valido = f"(IsBlank({tp}) || (IsNumeric({tp}) && Value({tp}) >= 0)) && (IsBlank({td}) || (IsNumeric({td}) && Value({td}) >= 0))"
    stile = {"Font": "nfFont", "Size": 12, "BorderColor": "nfBordo", "Fill": "nfCard",
             "RadiusTopLeft": 6, "RadiusTopRight": 6, "RadiusBottomLeft": 6, "RadiusBottomRight": 6}
    ch += [rect(f"{p}_recScheda", rx, 152, rw, H - 168, "nfCard", "nfBordo"),
           label(f"{p}_lblSchTit", S_(sel, "§.Codice"), rx + 24, 166, rw - 48, 30, size=16, bold=True),
           label(f"{p}_lblSchDesc", S_(sel, "§.Descrizione"), rx + 24, 198, rw - 48, 40, size=11, color="nfTestoSec"),
           label(f"{p}_lblCapP", S_(sel, "\"Prezzo unitario (\" & Coalesce(§.Unità, \"-\") & \")\""), rx + 24, 250, rw - 48, 20,
                 size=10, color="nfTestoSec"),
           control(f"{p}_txtPrezzo", "Classic/TextInput", {
               "Default": S_(sel, "If(IsBlank(§.'Prezzo unitario'), \"\", Text(§.'Prezzo unitario', \"0.00\"))"),
               "X": rx + 24, "Y": 272, "Width": rw - 48, "Height": 40, **stile}),
           label(f"{p}_lblCapD", '"Disponibilità (vuoto = illimitata)"', rx + 24, 326, rw - 48, 20, size=10, color="nfTestoSec"),
           control(f"{p}_txtDisp", "Classic/TextInput", {
               "Default": S_(sel, "If(IsBlank(§.Disponibilità), \"\", Text(§.Disponibilità))"),
               "X": rx + 24, "Y": 348, "Width": rw - 48, "Height": 40, **stile}),
           label(f"{p}_lblCapN", '"Note"', rx + 24, 402, rw - 48, 20, size=10, color="nfTestoSec"),
           control(f"{p}_txtNote", "Classic/TextInput", {
               "Default": S_(sel, "Coalesce(§.Note, \"\")"), "X": rx + 24, "Y": 424, "Width": rw - 48, "Height": 40, **stile}),
           label(f"{p}_lblErr", '"Prezzo e disponibilità devono essere numeri positivi (decimali con la virgola)"', rx + 24, 472,
                 rw - 48, 36, size=10, color="nfRosso", extra={"Visible": f"!({valido})"}),
           label(f"{p}_lblInfo",
                 '"Il nuovo prezzo vale per i prossimi preventivi. I contratti già creati restano invariati: ogni riga conserva il prezzo con cui è stata venduta."',
                 rx + 24, 520, rw - 48, 60, size=10, color="nfTestoSec")]
    salva = S_(sel, f"""If(locConfL,
    IfError(
        Patch('Voci listino', LookUp('Voci listino', Codice = §.Codice),
            {{'Prezzo unitario': If(IsBlank({tp}), Blank(), Value({tp})),
              Disponibilità: If(IsBlank({td}), Blank(), Value({td})),
              Note: {tn}}});
        UpdateContext({{locConfL: false}});
        Notify("Voce di listino aggiornata", NotificationType.Success);
        ClearCollect(colListino, 'Voci listino');
        true,
        Notify("Aggiornamento non riuscito: " & FirstError.Message, NotificationType.Error)
    ),
    UpdateContext({{locConfL: true}})
)""")
    ch += [button(f"{p}_btnSalva", 'If(locConfL, "Conferma modifica", "Salva modifica")', rx + 24, H - 64, 200, 40, salva,
                  fill="If(locConfL, nfRosso, nfAccento)",
                  extra={"DisabledFill": "nfBordo", "DisabledColor": "nfTestoSec",
                         "DisplayMode": f"If({valido}, DisplayMode.Edit, DisplayMode.Disabled)"}),
           button(f"{p}_btnRipristina", '"Ripristina"', rx + 238, H - 64, 140, 40,
                  f"UpdateContext({{locConfL: false}}); Reset({p}_txtPrezzo); Reset({p}_txtDisp); Reset({p}_txtNote)",
                  fill="nfCard", color="nfTesto", extra={"BorderColor": "nfBordo", "BorderThickness": 1})]
    onvisible = ("If(IsEmpty(colListino), ClearCollect(colListino, 'Voci listino'));\n"
                 'If(IsBlank(locCat), UpdateContext({locCat: "Tutte"}));\nUpdateContext({locConfL: false})')
    return screen("scrListino", {"Fill": "nfSfondo", "OnVisible": onvisible}, ch)


def S_(sel, formula):
    """Sostituisce il segnaposto § con il controllo selezionato."""
    return formula.replace("§", sel)


# ---------------------------------------------------------------------------
# NB: con l'alias (`As a`) i campi si scrivono sempre `a.Campo`: `StatoTxt` da solo dà ErrInvalidName.
# Controlli dati: le regole del progetto (R1-R3 di docs/wiki/schema-dataverse.md e altre verificate in storico)
# calcolate in tempo reale sui dati di Dataverse. Sui 198 contratti storici tutti i controlli danno 0 anomalie.
# ---------------------------------------------------------------------------
CARICA_CONTROLLI = """Clear(colAnom);
Collect(colAnom, ForAll(Filter(colContratti As a, a.StatoTxt <> "annullato" && CountRows(Filter(colContratti, AnnoEd = a.AnnoEd && CodStand = a.CodStand && StatoTxt <> "annullato")) > 1) As x,
    {Chk: "1", Rif: x.'ID contratto', Dett: "Stand " & x.CodStand & " venduto più volte nell'edizione " & x.AnnoEd}));
Collect(colAnom, ForAll(Filter(colContratti, StatoTxt = "firmato" && IsBlank('Data firma')) As x,
    {Chk: "2", Rif: x.'ID contratto', Dett: "Contratto firmato senza data di firma"}));
Collect(colAnom, ForAll(Filter(Espositori, !IsMatch('Partita IVA', "\\d{11}")) As x,
    {Chk: "3", Rif: x.'ID espositore', Dett: "Partita IVA non valida: " & x.'Partita IVA'}));
Collect(colAnom, ForAll(Filter(colContratti As a, a.StatoTxt <> "annullato" && Abs(Sum(Filter(colRighe, IdC = a.'ID contratto'), Importo) - a.'Imponibile a listino') > 0.01) As x,
    {Chk: "4", Rif: x.'ID contratto', Dett: "Somma righe " & Text(Sum(Filter(colRighe, IdC = x.'ID contratto'), Importo), "#,##0.00") & " diversa dal totale a listino " & Text(x.'Imponibile a listino', "#,##0.00")}));
Collect(colAnom, ForAll(Filter(colContratti, Abs('Imponibile a listino' * (1 - Sconto) - Imponibile) > 0.01) As x,
    {Chk: "5", Rif: x.'ID contratto', Dett: "Imponibile " & Text(x.Imponibile, "#,##0.00") & " diverso da listino meno sconto"}));
Collect(colAnom, ForAll(Filter(colContratti, !IsBlank('Data firma') && ((!IsBlank('Acconto pagato il') && 'Acconto pagato il' < 'Data firma') || (!IsBlank('Saldo pagato il') && 'Saldo pagato il' < 'Data firma'))) As x,
    {Chk: "6", Rif: x.'ID contratto', Dett: "Pagamento registrato prima della firma"}));
Collect(colAnom, ForAll(Filter(colContratti, StatoTxt = "firmato" && (IsBlank('Scadenza acconto') || IsBlank('Scadenza saldo'))) As x,
    {Chk: "7", Rif: x.'ID contratto', Dett: "Contratto firmato senza scadenza di acconto o saldo"}));
Collect(colAnom, ForAll(Filter(colContratti As a, a.StatoTxt <> "annullato" && LookUp(colStand, 'Codice stand' = a.CodStand).AnnoAtt > Value(a.AnnoEd)) As x,
    {Chk: "8", Rif: x.'ID contratto', Dett: "Stand " & x.CodStand & " non ancora attivo nel " & x.AnnoEd}))"""

CONTROLLI = [("1", "R1 · Stand venduto una sola volta per edizione", "Due contratti non annullati sullo stesso stand e nella stessa edizione"),
             ("2", "R2 · Contratto firmato con data di firma", "Ogni contratto firmato deve avere la data di firma"),
             ("3", "R3 · Partita IVA di 11 cifre", "Tutti gli espositori hanno una partita IVA valida"),
             ("4", "Righe uguali al totale a listino", "La somma delle righe coincide con l'imponibile a listino"),
             ("5", "Imponibile = listino meno sconto", "Imponibile uguale a totale a listino per (1 - sconto)"),
             ("6", "Pagamenti non prima della firma", "Acconto e saldo non sono pagati prima di firmare"),
             ("7", "Scadenze sui contratti firmati", "Acconto e saldo hanno una scadenza fissata"),
             ("8", "Stand attivo nell'edizione venduta", "Lo stand esisteva nell'edizione del contratto")]


def controlli():
    p = "ck"
    n_anom = lambda c: f'CountRows(Filter(colAnom, Chk = "{c}"))'
    superati = " + ".join(f"If({n_anom(c)} = 0, 1, 0)" for c, _, _ in CONTROLLI)
    ch = sidebar(p, "Controlli") + header(
        p, '"Controlli dati"', '"Regole del progetto verificate sui dati di Dataverse · controllo del " & Text(Now(), "dd/mm/yyyy hh:mm")')
    kpi = [("Controlli superati", f'({superati}) & " / {len(CONTROLLI)}"', '"regole senza anomalie"', "nfVerde"),
           ("Anomalie trovate", "CountRows(colAnom)", '"da correggere prima della sincronizzazione"', "nfRosso"),
           ("Contratti verificati", "CountRows(colContratti)", '"tutte le edizioni, compresi gli annullati"', "nfBlu")]
    cw = 259
    for i, (cap, val, sub, col) in enumerate(kpi):
        x = X0 + i * (cw + 16)
        ch += [rect(f"{p}_recKpi{i}", x, 96, cw, 92, "nfCard", "nfBordo"), rect(f"{p}_recKpiBar{i}", x, 96, cw, 4, col),
               label(f"{p}_lblKpiCap{i}", f'"{cap}"', x + 20, 108, cw - 40, 20, size=11, color="nfTestoSec"),
               label(f"{p}_lblKpiVal{i}", val, x + 20, 128, cw - 40, 34, size=22, bold=True),
               label(f"{p}_lblKpiSub{i}", sub, x + 20, 162, cw - 40, 20, size=10, color="nfTestoSec")]
    ch.append(button(f"{p}_btnRicontrolla", '"Ricontrolla"', X0 + 3 * (cw + 16), 112, 190, 44,
                     "Refresh(Contratti);\n" + CARICA + ";\nClear(colRighe);\n" + CARICA_RIGHE + ";\n" + CARICA_CONTROLLI))
    # elenco dei controlli
    for i, (c, titolo, desc) in enumerate(CONTROLLI):
        y = 204 + i * 68
        ch += [rect(f"{p}_recChk{i}", X0, y, 520, 62, f'If(locChk = "{c}", nfAccentoChiaro, nfCard)', "nfBordo"),
               label(f"{p}_lblChkT{i}", f'"{titolo}"', X0 + 16, y + 8, 380, 22, size=12, bold=True),
               label(f"{p}_lblChkD{i}", f'"{desc}"', X0 + 16, y + 32, 400, 22, size=10, color="nfTestoSec"),
               label(f"{p}_lblChkN{i}", f'If({n_anom(c)} = 0, "OK", {n_anom(c)} & " anomalie")', X0 + 420, y + 18, 84, 26,
                     size=10, bold=True, align="Align.Center",
                     extra={"Fill": f"If({n_anom(c)} = 0, nfVerdeChiaro, nfRossoChiaro)",
                            "Color": f"If({n_anom(c)} = 0, nfVerde, nfRosso)"}),
               button(f"{p}_btnChk{i}", '""', X0, y, 520, 62, f'UpdateContext({{locChk: "{c}"}})', fill="Color.Transparent",
                      color="Color.Transparent",
                      extra={"HoverFill": "ColorFade(nfAccento, 92%)", "PressedFill": "ColorFade(nfAccento, 85%)",
                             "RadiusTopLeft": 0, "RadiusTopRight": 0, "RadiusBottomLeft": 0, "RadiusBottomRight": 0})]
    # dettaglio del controllo scelto
    dx, dw = X0 + 536, PW_SC - 536
    titoli = "Switch(locChk, " + ", ".join(f'"{c}", "{t}"' for c, t, _ in CONTROLLI) + ', "")'
    ch += [rect(f"{p}_recDett", dx, 204, dw, 544, "nfCard", "nfBordo"),
           label(f"{p}_lblDetT", titoli, dx + 20, 216, dw - 40, 28, size=14, bold=True),
           label(f"{p}_lblDetN", f'Switch(CountRows(Filter(colAnom, Chk = locChk)), 0, "Nessuna anomalia: controllo superato", CountRows(Filter(colAnom, Chk = locChk)) & " anomalie da correggere")',
                 dx + 20, 246, dw - 40, 22, size=11, color="nfTestoSec")]
    righe = [
        label(f"{p}_lblARif", "ThisItem.Rif", 0, 8, 130, 24, size=11, bold=True, indent=12),
        label(f"{p}_lblADett", "ThisItem.Dett", 130, 8, 380, 24, size=11, indent=12),
        rect(f"{p}_recASep", 0, "Parent.TemplateHeight - 1", "Parent.TemplateWidth", 1, "nfBordo", indent=12),
    ]
    ch.append(control(f"{p}_galAnom", "Gallery", {
        "Items": "Filter(colAnom, Chk = locChk)", "X": dx + 20, "Y": 280, "Width": dw - 40, "Height": 456,
        "TemplateSize": 40, "TemplatePadding": 0, "ShowScrollbar": "true"},
        children=righe, variant="BrowseLayout_Flexible_SocialFeed_ver5.0"))
    onvisible = ('If(IsBlank(locChk), UpdateContext({locChk: "1"}));\n' + CARICA_RIGHE + ";\n" + CARICA_CONTROLLI)
    return screen("scrControlli", {"Fill": "nfSfondo", "OnVisible": onvisible}, ch)


def main():
    os.makedirs(SRC, exist_ok=True)
    old = os.path.join(SRC, "Screen1.pa.yaml")
    if os.path.exists(old):
        os.remove(old)   # la schermata vuota iniziale viene sostituita da Home
    files = {"App.pa.yaml": APP, "scrHome.pa.yaml": home(), "scrStand.pa.yaml": stand(),
             "scrEspositori.pa.yaml": espositori(), "scrContratti.pa.yaml": contratti(),
             "scrNuovo.pa.yaml": nuovo(), "scrScadenze.pa.yaml": scadenze(), "scrRinnovi.pa.yaml": rinnovi(),
             "scrListino.pa.yaml": listino(), "scrControlli.pa.yaml": controlli(),
             "_EditorState.pa.yaml": ("EditorState:\n  ScreensOrder:\n    - scrHome\n    - scrStand\n"
                                      "    - scrEspositori\n    - scrContratti\n    - scrNuovo\n    - scrScadenze\n"
                                      "    - scrRinnovi\n    - scrListino\n    - scrControlli\n")}
    for name, text in files.items():
        with open(os.path.join(SRC, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print("Schermate generate:", ", ".join(files))


if __name__ == "__main__":
    main()
