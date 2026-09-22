"""Skatteguiden — annual membership offer. One offer, no choice.

The saving is exact arithmetic on their own published prices: 790 = 10 x 79,
so annual is twelve months for the price of ten. Copy and pricing from
https://konto.skatteguiden.dk/bliv-medlem/pakker ("Prøv 1 måned gratis - gyldigt én gang").
"""
import json
import os
import sys

REF = os.path.expanduser(
    '~/.claude/plugins/cache/adapty/adapty-skills/a9df778bface/skills/flow-generator/references')
sys.path.insert(0, REF)
import flowkit as fk  # noqa: E402
from flowkit import (Ids, Span, absolute, attach_point, close, color, fill, footer,  # noqa: E402
                     gradient, icon, image, open_url, pad, purchase, radius, relative,
                     restore, rich, screen, size, stack, text, predeclare)

HERE = os.path.dirname(os.path.abspath(__file__))
I, A = Ids(), Ids('act')
L = 'da'

SCREEN = 'scr_annual'
# The one product this screen steers to. ANNUAL, because the offer IS the annual price —
# a monthly product here would contradict the "790 kr./år" the screen promises.
P_PLUS = 'da22cffe-64c4-487e-ade1-e229d76b5aa7'   # "1 year", period: annual

HERO_URL = ('https://public-media.adapty.io/public/d9/11/'
            'd911e916-0c05-4c8f-804f-0140665d9dfb/asset-hero.png')
HERO_ID = 534947

# Identical theme to the main flow, so the two screens cannot drift apart.
C = [
    ('bg',        'Page',              '#FFFFFF', '#FFFFFF'),
    ('surface',   'Surface',           '#F9F9F9', '#F9F9F9'),
    ('card',      'Card',              '#FFFFFF', '#FFFFFF'),
    ('tint',      'Blue tint',         '#E5EDFF', '#E5EDFF'),
    ('tintPlus',  'Purple tint',       '#EAE0FF', '#EAE0FF'),
    ('primary',   'Skatteguiden blue', '#6B7AFF', '#6B7AFF'),
    ('purple',    'Purple',            '#9563FF', '#9563FF'),
    ('mint',      'Mint',              '#4ED3B4', '#4ED3B4'),
    ('ink',       'Ink',               '#12131A', '#12131A'),
    ('ink2',      'Ink soft',          '#292A35', '#292A35'),
    ('muted',     'Muted',             '#666666', '#666666'),
    ('faint',     'Faint',             '#888888', '#888888'),
    ('border',    'Border',            '#E4E4E9', '#E4E4E9'),
    ('white',     'White',             '#FFFFFF', '#FFFFFF'),
    ('green',     'Check green',       '#2C622C', '#2C622C'),
]
T = [
    ('h1',     'H1',          28, 'bold',    34),
    ('h3',     'H3',          17, 'bold',    23),
    ('body',   'Body',        15, 'regular', 22),
    ('small',  'Small',       13, 'regular', 18),
    ('legal',  'Legal',       11, 'regular', 15),
    ('cta',    'CTA',         15, 'bold',    20, 0.6),
    ('price',  'Price',       30, 'bold',    34),
    ('badge',  'Badge',       11, 'bold',    14, 0.4),
    ('col',    'Column head',  9, 'bold',    12, 0.3),
    ('offer',  'Offer line',  15, 'bold',    20),
]

_lib = json.load(open(os.path.join(os.path.dirname(HERE), 'assets', 'phosphor-icons.json')))
WANT = {('Check', 'bold'), ('X', 'regular'), ('CheckCircle', 'fill'), ('Bell', 'regular'),
        ('CalendarBlank', 'regular'), ('Sparkle', 'regular')}
ICONS = [i for i in _lib if (i['name'], i['weight']) in WANT]
assert len(ICONS) == len(WANT), sorted(WANT - {(i['name'], i['weight']) for i in ICONS})

PRIMARY_HEX = '#6B7AFF'
TERMS = 'https://www.skatteguiden.dk/juridiske-dokumenter'


def t(*parts, **kw):
    return text(rich(*parts, locale=L), **kw)


# ---------------------------------------------------------------- timeline
# Row = [chip, rail, text]; only the text is in flow. The rail is anchored top AND bottom
# with height 'auto' so it follows however tall the copy turns out to be, and a negative
# bottom carries its tail under the next chip. Geometry derived from the chip:
#   chip 32 = icon 18 + 2x7 · rail left = (32-4)/2 = 14 · text inset = 32+10 = 42
ROW_GAP = 18


def tl_row(icon_name, title, body, *, first=False, last=False, weight='regular'):
    chip = stack(
        [icon(icon_name, size_pt=18, weight=weight,
              color_id='white' if first else 'primary', node_id=I('C'))],
        width='hug', height='hug', padding=pad(7, 7, 7, 7), corner=radius(100),
        fill_=fill('primary' if first else 'tint'),
        align_h='center', align_v='center',
        position=absolute(top=0, left=0), node_id=I('C'), caption='Chip')
    kids = [chip]
    if not last:
        # Fade on ALPHA, not toward the page colour — a stop that IS the background
        # renders the tail invisible and reads as a short connector (trap 12).
        kids.append(stack(
            [], fixed_w=4, height='auto',
            fill_=gradient(180, (PRIMARY_HEX, 0, 100), (PRIMARY_HEX, 1, 22)),
            position=absolute(top=20, left=14, bottom=-(ROW_GAP + 6), z=-10),
            node_id=I('C'), caption='Connector'))
    kids.append(stack([
        t(Span(title, color='ink'), preset='h3'),
        t(Span(body, color='muted'), preset='small'),
    ], gap=4, padding=pad(0, 42, 0, 0), node_id=I('C')))
    return stack(kids, direction='horizontal', gap=16, align_v='start',
                 node_id=I('R'), caption=title)


timeline = stack([
    tl_row('Check', 'I dag',
           'Fuld adgang til Plus. Du betaler 0 kr.', first=True, weight='bold'),
    tl_row('Bell', 'Undervejs',
           'Du kan opsige når som helst i App Store.'),
    tl_row('CalendarBlank', 'Efter 1 måned',
           '790 kr./år, hvis du ikke har opsagt.', last=True),
], gap=ROW_GAP, node_id=I('C'), caption='Prøveperiode')


def bullet(label):
    return stack([
        icon('CheckCircle', size_pt=18, color_id='mint', weight='fill', node_id=I('C')),
        t(Span(label, color='ink2'), preset='body'),
    ], direction='horizontal', gap=10, align_v='center', node_id=I('R'), caption=label)


# ---------------------------------------------------------------- screen
offer = screen(
    SCREEN, [
        stack([
            stack([], node_id=I('C')),
            stack([icon('X', size_pt=20, color_id='faint', node_id=I('C'))],
                  fixed_w=36, fixed_h=36, align_h='center', align_v='center',
                  node_id=I('B'), caption='Luk', actions=[close(action_id=A(''))]),
        ], direction='horizontal', distribution='space-between', align_v='center',
            node_id=I('R')),

        stack([
            stack([
                icon('Sparkle', size_pt=13, color_id='primary', node_id=I('C')),
                t(Span('SPAR 2 MÅNEDER', color='primary'), preset='badge', width='hug'),
            ], direction='horizontal', gap=6, align_v='center', width='hug',
                padding=pad(7, 12, 12, 7), corner=radius(9999), fill_=fill('tint'),
                node_id=I('C'), caption='Badge'),
            t(Span('Betal årligt. Få 2 måneder gratis.', color='ink'), preset='h1'),
            t(Span('Fuld adgang til Plus — til prisen for 10 måneder.',
                   color='muted'), preset='body'),
        ], gap=10, node_id=I('C')),

        stack([
            stack([
                t(Span('790 kr.', color='ink'), preset='price', width='hug'),
                t(Span('/år', color='muted'), preset='body', width='hug'),
            ], direction='horizontal', gap=5, align_v='end', node_id=I('C')),
            t(Span('I stedet for 948 kr. ved månedlig betaling.', color='ink2'),
              preset='small'),
            t(Span('Svarer til ca. 66 kr./md — du sparer 158 kr. om året.',
                   color='muted'), preset='small'),
        ], gap=5, padding=pad(17, 18, 18, 17), corner=radius(16), fill_=fill('tint'),
            node_id=I('C'), caption='Besparelse'),

        timeline,

        stack([
            t(Span('Det får du med Plus', color='faint'), preset='col'),
            bullet('Få rettet din skat automatisk'),
            bullet('Vi indberetter dine fradrag gratis'),
            bullet('Skatterådgivning inden for 2 hverdage'),
            bullet('En personlig opdatering hver måned'),
        ], gap=13, padding=pad(18, 18, 18, 18), corner=radius(16),
            fill_=fill('surface'), node_id=I('C')),

        # One product means nothing to pick: the card is hidden and exists only so the
        # product is attached (and a price variable could resolve). The CTA buys by const.
        attach_point(product_id=P_PLUS, group_id='sgoffer', element_id=I('P')),

        footer([
            t(Span('0 kr. i dag', color='ink'), Span('  ·  ', color='border'),
              Span('derefter 790 kr./år', color='muted'),
              preset='offer', align='center'),
            stack([t(Span('START MIN GRATIS MÅNED', color='white'), preset='cta',
                     align='center', width='fill')],
                  height='hug', padding=pad(17, 20, 20, 17), corner=radius(9999),
                  fill_=fill('primary'), align_h='center', align_v='center',
                  node_id=I('B'), caption='CTA',
                  actions=[purchase('sgoffer', action_id=A(''))]),
            t(Span('Ingen binding. Opsig når som helst i App Store.', color='faint'),
              preset='legal', align='center'),
            stack([
                stack([t(Span('Gendan køb', color='faint'), preset='legal',
                         align='center', width='hug')],
                      width='hug', node_id=I('B'), caption='Gendan køb',
                      actions=[restore(action_id=A(''))]),
                t(Span('·', color='border'), preset='legal', width='hug'),
                stack([t(Span('Vilkår og privatliv', color='faint'), preset='legal',
                         align='center', width='hug')],
                      width='hug', node_id=I('B'), caption='Vilkår',
                      actions=[open_url(TERMS, action_id=A(''))]),
            ], direction='horizontal', gap=10, align_h='center', align_v='center',
                node_id=I('R'), caption='Juridisk'),
        ], fill_=fill('white'), padding=pad(16, 16, 16, 14), gap=10,
            node_id=I('F'), caption='Bottom bar'),
    ],
    caption='Førstegangstilbud', fill_=fill('bg'), gap=20, safe_area=True, scrollable=True,
    padding=pad(8, 20, 20, 196), status_bar=True, status_bar_theme='dark',
    selectable_groups=[{'id': 'sgoffer', 'type': 'product'}])

cfg = fk.config(screens=[offer], colors=C, typography=T, icons=ICONS,
                locales=((L, 'Dansk'),), default_locale=L,
                meta_screens=predeclare(SCREEN, [P_PLUS]))

out = os.path.join(os.path.dirname(HERE), 'flows', 'skatteguiden-annual-offer.json')
json.dump(cfg, open(out, 'w'), ensure_ascii=False, indent=1)
print('wrote %s: %d elements' % (out, len(cfg['screens'][0]['elements']['map'])))
