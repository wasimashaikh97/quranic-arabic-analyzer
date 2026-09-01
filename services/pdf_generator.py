# -*- coding: utf-8 -*-
"""Printable Sarf sheets.

Two layouts:

``generate_one_page_sheet``
    A single **A4 landscape** wall chart: the four mandatory gardaans side by
    side (14 صیغے each), the باب / وزن / مادہ header, and a bottom strip with
    امر، نہی، مصدر، اسم فاعل، اسم مفعول.  Designed to be printed once and
    used at the desk — everything about the verb on one sheet of paper.

``generate_study_sheet``
    The detailed multi-page booklet (bigger type, Urdu + English gloss for
    every صیغہ, derivatives, related افعال, Quranic usage).
"""

import io
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

try:
    from arabic_reshaper import ArabicReshaper
    from bidi.algorithm import get_display
    # CRITICAL: arabic_reshaper deletes all harakat by default, which would
    # strip exactly the information a Sarf sheet exists to show
    # (أَنْزَلَ would print as أنزل).  Keep every diacritic.
    _RESHAPER = ArabicReshaper(configuration={
        'delete_harakat': False,
        'support_ligatures': True,
        'shift_harakat_position': False,
    })
    HAS_ARABIC_SUPPORT = True
except ImportError:                                    # pragma: no cover
    _RESHAPER = None
    HAS_ARABIC_SUPPORT = False

ASSET_FONTS = Path(__file__).resolve().parent.parent / 'assets' / 'fonts'

NA_UR = 'قابلِ اطلاق نہیں'

BRAND = colors.HexColor('#14532d')
BRAND_LIGHT = colors.HexColor('#dcfce7')
ACCENT = colors.HexColor('#92400e')
GREY = colors.HexColor('#6b7280')
ROW_ALT = colors.HexColor('#f3f4f6')

# Amiri has no arrow glyphs, so use guillemets (which already point the way
# Arabic reads) instead of ← / ↓ — otherwise the PDF shows empty boxes.
CHAIN_SEP = ' « '
CHAIN_DOWN = '«'


#: characters the Arabic fonts do not carry, mapped to ones they do, so a
#: stray arrow can never print as an empty box
_GLYPH_SUBSTITUTES = {
    '→': '»', '←': '«', '↓': '«', '⟶': '»', '⟵': '«',
    '➜': '»', '⇒': '»', '‑': '-',
}


def reshape(text) -> str:
    """Shape Arabic/Urdu glyphs and apply the bidi algorithm for PDF output."""
    if text is None:
        return ''
    text = str(text)
    for src, dst in _GLYPH_SUBSTITUTES.items():
        if src in text:
            text = text.replace(src, dst)
    if not HAS_ARABIC_SUPPORT or not text.strip():
        return text
    try:
        return get_display(_RESHAPER.reshape(text))
    except Exception:                                  # pragma: no cover
        return text


# Backwards-compatible alias (older call-sites imported this name)
reshape_arabic = reshape


class PDFGenerator:
    """Builds the printable sheets."""

    def __init__(self):
        self._register_fonts()
        self.styles = self._create_styles()

    # ------------------------------------------------------------------
    def _register_fonts(self):
        """Prefer the bundled Amiri (full Arabic + Urdu coverage)."""
        self.arabic_font = 'Helvetica'
        self.arabic_bold = 'Helvetica-Bold'
        self.english_font = 'Helvetica'

        bundled = [
            ('Amiri', ASSET_FONTS / 'Amiri-Regular.ttf',
             'Amiri-Bold', ASSET_FONTS / 'Amiri-Bold.ttf'),
            ('NotoNaskhArabic', ASSET_FONTS / 'NotoNaskhArabic-Regular.ttf',
             None, None),
        ]
        for name, regular, bold_name, bold_path in bundled:
            if not regular.exists():
                continue
            try:
                pdfmetrics.registerFont(TTFont(name, str(regular)))
                self.arabic_font = name
                self.arabic_bold = name
                if bold_name and bold_path and bold_path.exists():
                    pdfmetrics.registerFont(TTFont(bold_name, str(bold_path)))
                    self.arabic_bold = bold_name
                self.english_font = name
                return
            except Exception:
                continue

        # last resort: a system font that carries Arabic glyphs
        for path in ('C:/Windows/Fonts/arial.ttf',
                     'C:/Windows/Fonts/arialuni.ttf',
                     '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                     '/Library/Fonts/Arial Unicode.ttf'):
            if os.path.exists(path):
                try:
                    name = Path(path).stem
                    pdfmetrics.registerFont(TTFont(name, path))
                    self.arabic_font = self.arabic_bold = self.english_font = name
                    return
                except Exception:
                    continue

    # ------------------------------------------------------------------
    def _create_styles(self, scale: float = 1.0) -> dict:
        base = getSampleStyleSheet()

        def st(name, size, align=TA_RIGHT, font=None, colour=colors.black,
               leading=None, bold=False, space_after=0):
            size = size * scale
            return ParagraphStyle(
                name, parent=base['Normal'],
                fontName=font or (self.arabic_bold if bold else self.arabic_font),
                fontSize=size, leading=(leading * scale) if leading
                else size * 1.55,
                alignment=align, textColor=colour, spaceAfter=space_after)

        return {
            'title': st('title', 21, TA_CENTER, bold=True, colour=BRAND,
                        space_after=4),
            'subtitle': st('subtitle', 13, TA_CENTER, colour=GREY, space_after=6),
            'section': st('section', 13.5, TA_RIGHT, bold=True, colour=BRAND,
                          space_after=4),
            'tense_head': st('tense_head', 11.5, TA_CENTER, bold=True,
                             colour=colors.white),
            'arabic': st('arabic', 13, TA_RIGHT, colour=ACCENT, bold=True),
            'arabic_big': st('arabic_big', 26, TA_CENTER, bold=True, colour=ACCENT),
            'arabic_cell': st('arabic_cell', 13.5, TA_CENTER, colour=ACCENT,
                              bold=True, leading=18.5),
            'arabic_strip': st('arabic_strip', 12.5, TA_CENTER, colour=ACCENT,
                               bold=True, leading=18),
            'pronoun_cell': st('pronoun_cell', 11, TA_CENTER, colour=colors.black,
                               leading=16),
            'num_cell': st('num_cell', 9, TA_CENTER, font=self.english_font,
                           colour=GREY, leading=13),
            'na_cell': st('na_cell', 10.5, TA_CENTER, colour=GREY, leading=18.5),
            'urdu': st('urdu', 10.5, TA_RIGHT, leading=17),
            'urdu_cell': st('urdu_cell', 9.5, TA_RIGHT, leading=15),
            'label': st('label', 10, TA_RIGHT, colour=GREY),
            'english': st('english', 9.5, TA_LEFT, font=self.english_font),
            'english_cell': st('english_cell', 9, TA_LEFT, font=self.english_font,
                               leading=13),
            'small': st('small', 8.5, TA_CENTER, colour=GREY),
            'note': st('note', 10, TA_RIGHT, colour=ACCENT, leading=16),
            'note_small': st('note_small', 8.5, TA_RIGHT, colour=ACCENT, leading=12),
        }

    # ==================================================================
    # ONE-PAGE PRINT SHEET
    # ==================================================================
    def generate_one_page_sheet(self, verb: dict, conjugations: dict,
                                baab: dict = None, root_info: dict = None) -> bytes:
        """A4 landscape: the whole verb on a single printable page.

        Type is scaled down in small steps until the sheet genuinely fits one
        page, so an unusually long verb (اِسْتَكْتَبَ, with its long مشتقات) can
        never silently spill onto a second sheet.
        """
        page = landscape(A4)
        margins = dict(leftMargin=9 * mm, rightMargin=9 * mm,
                       topMargin=8 * mm, bottomMargin=7 * mm)
        frame_w = page[0] - margins['leftMargin'] - margins['rightMargin']
        frame_h = page[1] - margins['topMargin'] - margins['bottomMargin']
        gaps = 3 * (2 * mm)

        original_styles = self.styles
        try:
            for scale in (1.0, 0.95, 0.9, 0.85, 0.8, 0.75):
                self.styles = self._create_styles(scale)
                blocks = [self._identity_band(verb, baab),
                          self._four_gardaan_block(conjugations),
                          self._bottom_strip(verb, conjugations),
                          self._hierarchy_line(verb)]
                height = gaps + sum(b.wrap(frame_w, frame_h)[1] for b in blocks)
                # nested auto-width tables measure a little short, so keep a
                # safety margin rather than trusting wrap() to the millimetre
                if height <= frame_h - 5 * mm:
                    break

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, pagesize=page, **margins,
                title='%s — مکمل صرف' % verb.get('arabic', ''),
                author='قرآنی عربی فعل تجزیہ')

            story = []
            for i, block in enumerate([
                    self._identity_band(verb, baab),
                    self._four_gardaan_block(conjugations),
                    self._bottom_strip(verb, conjugations),
                    self._hierarchy_line(verb)]):
                if i:
                    story.append(Spacer(1, 2 * mm))
                story.append(block)
            doc.build(story)

            pdf = buffer.getvalue()
            buffer.close()
            return pdf
        finally:
            self.styles = original_styles

    # -- one-page pieces -----------------------------------------------
    def _identity_band(self, verb: dict, baab: dict) -> Table:
        baab = baab or {}
        baab_name = verb.get('baab_name_arabic') or baab.get('name_ar', '')
        # right-to-left reading order: verb on the RIGHT, meanings on the left
        cells = [
            [self._meaning_table(verb),
             self._kv_table([
                 ('مصدر', verb.get('masdar', '—')),
                 ('اسم فاعل', verb.get('ism_fail', '—')),
                 ('اسم مفعول', verb.get('ism_mafool') or NA_UR),
                 ('متعدی / لازم', verb.get('transitivity', '')),
             ]),
             self._kv_table([
                 ('مادہ', verb.get('root', '')),
                 ('باب', baab_name),
                 ('وزن', verb.get('wazn', '')),
                 ('قسم', self._type_label(verb)),
             ]),
             Paragraph(reshape(verb.get('arabic', '')), self.styles['arabic_big'])],
        ]
        table = Table(cells, colWidths=[96 * mm, 68 * mm, 62 * mm, 52 * mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.1, BRAND),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('BACKGROUND', (-1, 0), (-1, 0), BRAND_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        return table

    def _kv_table(self, pairs) -> Table:
        rows = [[Paragraph(reshape(str(value or '—')), self.styles['arabic']),
                 Paragraph(reshape(label), self.styles['label'])]
                for label, value in pairs]
        t = Table(rows, colWidths=None)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 0.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))
        return t

    def _meaning_table(self, verb: dict) -> Table:
        rows = [
            [Paragraph(reshape('اردو معنی: ' + (verb.get('meaning_urdu') or '—')),
                       self.styles['urdu'])],
            [Paragraph('English: ' + (verb.get('meaning_english') or '—'),
                       self.styles['english'])],
        ]
        note = verb.get('unavailable_note')
        if note:
            rows.append([Paragraph(reshape('نوٹ: ' + note),
                                   self.styles['note_small'])])
        t = Table(rows)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        return t

    #: the four mandatory tenses, in the order the student learns them
    FOUR = [
        ('past_active', 'ماضی معروف'),
        ('present_active', 'مضارع معروف'),
        ('past_passive', 'ماضی مجہول'),
        ('present_passive', 'مضارع مجہول'),
    ]

    #: the reference book's grid: rows are person/gender, columns are number
    GRID_ROWS = [
        ('غائب مذکر', '3rd m.', 0, 1, 2),
        ('غائب مؤنث', '3rd f.', 3, 4, 5),
        ('حاضر مذکر', '2nd m.', 6, 7, 8),
        ('حاضر مؤنث', '2nd f.', 9, 10, 11),
        ('متکلم', '1st', 12, None, 13),
    ]

    def _four_gardaan_block(self, conjugations: dict) -> Table:
        """The four gardaans, each as the book's واحد | مثنی | جمع grid.

        Five rows instead of fourteen, so the four tenses sit two-by-two and
        the Arabic can be printed much larger.
        """
        blocks = [[self._one_grid(conjugations, self.FOUR[1]),
                   self._one_grid(conjugations, self.FOUR[0])],
                  [self._one_grid(conjugations, self.FOUR[3]),
                   self._one_grid(conjugations, self.FOUR[2])]]
        table = Table(blocks, colWidths=[139 * mm, 139 * mm])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return table

    def _one_grid(self, conjugations: dict, spec) -> Table:
        key, title = spec
        rows = conjugations.get(key) or []

        # Column order must match the data rows below, which are built
        # plural, dual, singular, label — i.e. right-to-left as the book prints
        # it: the row label on the right, جمع furthest left.
        data = [[Paragraph(reshape('جمع'), self.styles['tense_head']),
                 Paragraph(reshape('مثنی'), self.styles['tense_head']),
                 Paragraph(reshape('واحد'), self.styles['tense_head']),
                 Paragraph(reshape(title), self.styles['tense_head'])]]

        def cell(index):
            if index is None or index >= len(rows):
                return Paragraph('×', self.styles['na_cell'])
            return Paragraph(reshape(rows[index]['arabic']),
                             self.styles['arabic_cell'])

        for label_ur, label_en, single, dual, plural in self.GRID_ROWS:
            label = Paragraph(reshape('%s' % label_ur), self.styles['pronoun_cell'])
            if dual is None:
                merged = cell(plural)
                data.append([merged, merged, cell(single), label])
            else:
                data.append([cell(plural), cell(dual), cell(single), label])

        widths = [33 * mm, 33 * mm, 33 * mm, 38 * mm]
        table = Table(data, colWidths=widths)
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), BRAND),
            ('BOX', (0, 0), (-1, -1), 0.9, BRAND),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('BACKGROUND', (-1, 1), (-1, -1), BRAND_LIGHT),
        ]
        if not rows:
            style.append(('BACKGROUND', (0, 1), (-2, -1),
                          colors.HexColor('#fafafa')))
        # the first person has no dual, so the book merges those two cells
        style.append(('SPAN', (0, 5), (1, 5)))
        table.setStyle(TableStyle(style))
        return table


    def _bottom_strip(self, verb: dict, conjugations: dict) -> Table:
        imperative = conjugations.get('imperative') or []
        prohibition = conjugations.get('prohibition') or []

        def joined(rows):
            if not rows:
                return NA_UR
            return '   ·   '.join(r['arabic'] for r in rows)

        cells = [
            [Paragraph(reshape(joined(imperative)), self.styles['arabic_strip']),
             Paragraph(reshape('امر'), self.styles['label'])],
            [Paragraph(reshape(joined(prohibition)), self.styles['arabic_strip']),
             Paragraph(reshape('نہی'), self.styles['label'])],
            [Paragraph(reshape(self._derivatives_line(verb)),
                       self.styles['arabic_strip']),
             Paragraph(reshape('مشتقات'), self.styles['label'])],
        ]
        table = Table(cells, colWidths=[254 * mm, 24 * mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.0, BRAND),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
            ('BACKGROUND', (-1, 0), (-1, -1), BRAND_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ]))
        return table

    def _hierarchy_line(self, verb: dict) -> Table:
        """The شجری خاکہ compressed into one printable strip."""
        chain = [
            verb.get('root', ''),
            verb.get('arabic', ''),
            verb.get('baab_name_arabic', ''),
            verb.get('wazn', ''),
            verb.get('past_3ms') or '—',
            verb.get('present_3ms') or '—',
            # the long «قابلِ اطلاق نہیں» would wrap this strip onto a second
            # line and push the sheet to two pages; the note above explains it
            verb.get('past_passive_3ms') or '—',
            verb.get('present_passive_3ms') or '—',
        ]
        labels = ['مادہ', 'فعل', 'باب', 'وزن',
                  'ماضی معروف', 'مضارع معروف', 'ماضی مجہول', 'مضارع مجہول']
        # right-to-left: first link on the right
        text = CHAIN_SEP.join(reversed(
            ['%s: %s' % (lbl, val) for lbl, val in zip(labels, chain)]))
        cells = [[Paragraph(reshape(text), self.styles['arabic_strip']),
                  Paragraph(reshape('شجری خاکہ'), self.styles['label'])]]
        table = Table(cells, colWidths=[254 * mm, 24 * mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.0, BRAND),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
            ('BACKGROUND', (-1, 0), (-1, -1), BRAND_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        return table

    @staticmethod
    def _derivatives_line(verb: dict) -> str:
        parts = []
        if verb.get('masdar'):
            parts.append('مصدر: ' + verb['masdar'])
        if verb.get('masdar2'):
            parts.append('مصدر: ' + verb['masdar2'])
        if verb.get('ism_fail'):
            parts.append('اسم فاعل: ' + verb['ism_fail'])
        parts.append('اسم مفعول: ' + (verb.get('ism_mafool') or NA_UR))
        return '   ·   '.join(parts)

    @staticmethod
    def _type_label(verb: dict) -> str:
        try:
            from core.morphology import ArabicMorphology
            info = ArabicMorphology.get_verb_type_info(
                verb.get('verb_type', 'sound'))
            return info.get('title_ar', '')
        except Exception:
            return verb.get('verb_type', '')

    # ==================================================================
    # DETAILED BOOKLET
    # ==================================================================
    def generate_study_sheet(self, verb_data: dict, conjugations: dict,
                             quranic_data: list = None, root_info: dict = None,
                             baab: dict = None, afaal: list = None,
                             include_quranic: bool = True,
                             include_english: bool = True,
                             include_urdu: bool = True,
                             include_graph: bool = False) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=14 * mm, rightMargin=14 * mm,
            topMargin=13 * mm, bottomMargin=13 * mm,
            title='%s — مکمل صرف' % verb_data.get('arabic', ''),
            author='قرآنی عربی فعل تجزیہ')

        story = []
        self._add_cover(story, verb_data, baab, include_urdu, include_english)
        self._add_hierarchy(story, verb_data, baab)

        for key, title in self.FOUR:
            rows = conjugations.get(key) or []
            story.append(PageBreak())
            story.append(Paragraph(reshape('%s — %s' % (verb_data.get('arabic', ''), title)),
                                   self.styles['title']))
            story.append(HRFlowable(width='100%', thickness=1, color=BRAND,
                                    spaceAfter=6))
            if rows:
                self._add_conjugation_table(story, title, rows,
                                            include_urdu, include_english)
            else:
                self._add_unavailable(story, title, verb_data)

        story.append(PageBreak())
        story.append(Paragraph(reshape('امر، نہی اور مشتقات'), self.styles['title']))
        story.append(HRFlowable(width='100%', thickness=1, color=BRAND, spaceAfter=6))
        for key, title in (('imperative', 'امر (Imperative)'),
                           ('prohibition', 'نہی (Prohibition)')):
            rows = conjugations.get(key) or []
            if rows:
                self._add_conjugation_table(story, title, rows,
                                            include_urdu, include_english)
                story.append(Spacer(1, 5 * mm))
            else:
                self._add_unavailable(story, title, verb_data)
        self._add_derivatives(story, verb_data, include_urdu, include_english)

        if afaal:
            story.append(PageBreak())
            self._add_afaal(story, verb_data, afaal)

        if include_quranic and quranic_data:
            story.append(PageBreak())
            self._add_quranic(story, quranic_data, include_urdu, include_english)

        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    # -- booklet pieces ------------------------------------------------
    def _add_cover(self, story, verb, baab, include_urdu, include_english):
        baab = baab or {}
        story.append(Paragraph(reshape('فعل کی مکمل صرفی معلومات'),
                               self.styles['title']))
        story.append(Paragraph(reshape('Complete Sarf of one verb'),
                               self.styles['subtitle']))
        story.append(Paragraph(reshape(verb.get('arabic', '')),
                               self.styles['arabic_big']))
        story.append(Spacer(1, 4 * mm))

        pairs = [
            ('فعل (ماضی معروف)', verb.get('past_3ms')),
            ('مضارع معروف', verb.get('present_3ms')),
            ('ماضی مجہول', verb.get('past_passive_3ms') or NA_UR),
            ('مضارع مجہول', verb.get('present_passive_3ms') or NA_UR),
            ('مادہ', verb.get('root')),
            ('باب', verb.get('baab_name_arabic') or baab.get('name_ar', '')),
            ('وزن', verb.get('wazn')),
            ('فعل کی قسم', self._type_label(verb)),
            ('متعدی / لازم', verb.get('transitivity')),
            ('مصدر', verb.get('masdar')),
            ('اسم فاعل', verb.get('ism_fail')),
            ('اسم مفعول', verb.get('ism_mafool') or NA_UR),
        ]
        if include_urdu:
            pairs.append(('اردو معنی', verb.get('meaning_urdu')))

        data = [[Paragraph(reshape(str(v or '—')), self.styles['arabic']),
                 Paragraph(reshape(k), self.styles['label'])] for k, v in pairs]
        if include_english:
            data.append([Paragraph(verb.get('meaning_english', '') or '—',
                                   self.styles['english']),
                         Paragraph('English meaning', self.styles['label'])])

        table = Table(data, colWidths=[110 * mm, 62 * mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, BRAND),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
            ('BACKGROUND', (1, 0), (1, -1), BRAND_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(table)

        note = verb.get('unavailable_note')
        if note:
            story.append(Spacer(1, 3 * mm))
            story.append(Paragraph(reshape('نوٹ: ' + note), self.styles['note']))

    def _add_hierarchy(self, story, verb, baab):
        baab = baab or {}
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(reshape('شجری خاکہ (Hierarchy)'),
                               self.styles['section']))
        chain = [
            ('مادہ', verb.get('root', '')),
            ('فعل', verb.get('arabic', '')),
            ('باب', verb.get('baab_name_arabic') or baab.get('name_ar', '')),
            ('وزن', verb.get('wazn', '')),
            ('ماضی معروف', verb.get('past_3ms') or '—'),
            ('مضارع معروف', verb.get('present_3ms') or '—'),
            ('ماضی مجہول', verb.get('past_passive_3ms') or NA_UR),
            ('مضارع مجہول', verb.get('present_passive_3ms') or NA_UR),
            ('مکمل گردان', '۵۶ + ۱۲ صیغے'),
        ]
        rows = [[Paragraph(reshape(value), self.styles['arabic']),
                 Paragraph(reshape(CHAIN_DOWN if i else ''), self.styles['small']),
                 Paragraph(reshape(label), self.styles['label'])]
                for i, (label, value) in enumerate(chain)]
        table = Table(rows, colWidths=[96 * mm, 12 * mm, 64 * mm])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.8, BRAND),
            ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#e5e7eb')),
            ('BACKGROUND', (2, 0), (2, -1), BRAND_LIGHT),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(table)

    def _add_conjugation_table(self, story, title, rows,
                               include_urdu, include_english):
        story.append(Paragraph(reshape(title), self.styles['section']))

        # RTL column order: English | اردو | عربی | صیغہ | ضمیر | #
        header, widths = [], []
        if include_english:
            header.append(Paragraph('English', self.styles['tense_head']))
            widths.append(32 * mm)
        if include_urdu:
            header.append(Paragraph(reshape('اردو معنی'), self.styles['tense_head']))
            widths.append(46 * mm)
        header += [Paragraph(reshape('عربی'), self.styles['tense_head']),
                   Paragraph(reshape('صیغہ'), self.styles['tense_head']),
                   Paragraph(reshape('ضمیر'), self.styles['tense_head']),
                   Paragraph(reshape('#'), self.styles['tense_head'])]
        widths += [40 * mm, 34 * mm, 22 * mm, 8 * mm]

        data = [header]
        for i, row in enumerate(rows, start=1):
            cells = []
            if include_english:
                cells.append(Paragraph(row.get('meaning_english', ''),
                                       self.styles['english_cell']))
            if include_urdu:
                cells.append(Paragraph(reshape(row.get('meaning_urdu', '')),
                                       self.styles['urdu_cell']))
            cells += [
                Paragraph(reshape(row.get('arabic', '')),
                          self.styles['arabic_cell']),
                Paragraph(reshape(row.get('sigha_urdu', '')),
                          self.styles['urdu_cell']),
                Paragraph(reshape(row.get('pronoun_arabic', '')),
                          self.styles['pronoun_cell']),
                Paragraph(str(i), self.styles['small']),
            ]
            data.append(cells)

        table = Table(data, colWidths=widths, repeatRows=1)
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), BRAND),
            ('BOX', (0, 0), (-1, -1), 0.9, BRAND),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ]
        for r in range(1, len(data)):
            if r % 2 == 0:
                style.append(('BACKGROUND', (0, r), (-1, r), ROW_ALT))
        table.setStyle(TableStyle(style))
        story.append(table)

    def _add_unavailable(self, story, title, verb):
        story.append(Paragraph(reshape(title), self.styles['section']))
        text = '%s — %s' % (NA_UR, verb.get('unavailable_note')
                            or 'اس فعل کے لیے یہ صورت مستند طور پر دستیاب نہیں۔')
        box = Table([[Paragraph(reshape(text), self.styles['note'])]],
                    colWidths=[172 * mm])
        box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.8, ACCENT),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(box)
        story.append(Spacer(1, 4 * mm))

    def _add_derivatives(self, story, verb, include_urdu, include_english):
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(reshape('مشتقات (Derived words)'),
                               self.styles['section']))
        nouns = verb.get('derived_nouns') or {}
        if not nouns:
            story.append(Paragraph(reshape(NA_UR), self.styles['note']))
            return

        header, widths = [], []
        if include_urdu:
            header.append(Paragraph(reshape('اردو'), self.styles['tense_head']))
            widths.append(52 * mm)
        header += [Paragraph(reshape('وزن'), self.styles['tense_head']),
                   Paragraph(reshape('عربی'), self.styles['tense_head']),
                   Paragraph(reshape('قسم'), self.styles['tense_head'])]
        widths += [40 * mm, 40 * mm, 40 * mm]

        data = [header]
        for info in nouns.values():
            if not isinstance(info, dict):
                continue
            cells = []
            if include_urdu:
                cells.append(Paragraph(reshape(info.get('meaning_urdu', '')),
                                       self.styles['urdu_cell']))
            cells += [
                Paragraph(reshape(info.get('pattern', '')), self.styles['urdu_cell']),
                Paragraph(reshape(info.get('arabic', '')), self.styles['arabic_cell']),
                Paragraph(reshape(info.get('label_ur', '')), self.styles['urdu_cell']),
            ]
            data.append(cells)

        table = Table(data, colWidths=widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND),
            ('BOX', (0, 0), (-1, -1), 0.9, BRAND),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(table)

    def _add_afaal(self, story, verb, afaal):
        story.append(Paragraph(
            reshape('مادہ %s — تمام مستند افعال' % verb.get('root', '')),
            self.styles['title']))
        story.append(HRFlowable(width='100%', thickness=1, color=BRAND,
                                spaceAfter=6))

        # RTL column order
        data = [[Paragraph(reshape(h), self.styles['tense_head'])
                 for h in ('اردو معنی', 'مصدر', 'مضارع', 'فعل', 'وزن', 'باب')]]
        for entry in afaal:
            info = entry['baab_info']
            if entry['available']:
                for v in entry['verbs']:
                    data.append([
                        Paragraph(reshape(v.get('meaning_urdu', '')), self.styles['urdu_cell']),
                        Paragraph(reshape(v.get('masdar', '')), self.styles['arabic_cell']),
                        Paragraph(reshape(v.get('present_3ms', '')), self.styles['arabic_cell']),
                        Paragraph(reshape(v.get('arabic', '')), self.styles['arabic_cell']),
                        Paragraph(reshape(info['wazn_past']), self.styles['urdu_cell']),
                        Paragraph(reshape(info['name_ar']), self.styles['urdu_cell']),
                    ])
            else:
                data.append([
                    Paragraph(reshape('اس باب میں اس مادہ کا مستند فعل دستیاب نہیں'),
                              self.styles['urdu_cell']),
                    Paragraph(reshape('—'), self.styles['arabic_cell']),
                    Paragraph(reshape('—'), self.styles['arabic_cell']),
                    Paragraph(reshape('—'), self.styles['arabic_cell']),
                    Paragraph(reshape(info['wazn_past']), self.styles['urdu_cell']),
                    Paragraph(reshape(info['name_ar']), self.styles['urdu_cell']),
                ])

        table = Table(data, colWidths=[34 * mm, 26 * mm, 30 * mm, 30 * mm,
                                       26 * mm, 26 * mm], repeatRows=1)
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), BRAND),
            ('BOX', (0, 0), (-1, -1), 0.9, BRAND),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ]
        table.setStyle(TableStyle(style))
        story.append(table)

    def _add_quranic(self, story, quranic_data, include_urdu, include_english):
        story.append(Paragraph(reshape('قرآن مجید میں استعمال'), self.styles['title']))
        story.append(HRFlowable(width='100%', thickness=1, color=BRAND, spaceAfter=6))

        for item in quranic_data:
            ref = 'سورۃ %s (%s:%s)' % (
                item.get('surah_name_arabic', item.get('surah_name', '')),
                item.get('surah_number', item.get('surah_no', '')),
                item.get('ayah_number', item.get('ayah_no', '')))
            block = [Paragraph(reshape(ref), self.styles['section']),
                     Paragraph(reshape(item.get('arabic_text', item.get('arabic', ''))),
                               self.styles['arabic'])]
            if include_urdu:
                block.append(Paragraph(
                    reshape(item.get('translation_urdu', item.get('urdu', ''))),
                    self.styles['urdu']))
            if include_english:
                block.append(Paragraph(
                    item.get('translation_english', item.get('english', '')),
                    self.styles['english']))
            note = item.get('grammatical_note')
            if note:
                block.append(Paragraph('Note: ' + note, self.styles['english']))
            block.append(Spacer(1, 4 * mm))
            story.append(KeepTogether(block))
