"""Skatteguiden.dk — onboarding + paywall.

Theme sampled from konto.skatteguiden.dk and the two app screenshots (no invented colours).
Copy and pricing taken from https://konto.skatteguiden.dk/bliv-medlem/pakker (2026-09-21).
"""
import json
import os
import sys

REF = os.path.expanduser(
    '~/.claude/plugins/cache/adapty/adapty-skills/a9df778bface/skills/flow-generator/references')
sys.path.insert(0, REF)
import flowkit as fk  # noqa: E402
from flowkit import (Ids, Span, Var, close, color, eq, fill, footer, hex_color, icon,  # noqa: E402
                     image, lit, navigate, navigate_back, pad, product, purchase, radius,
                     ref, restore, rich, screen, selectable, stack, switch_rich, text,
                     on_selected, open_url, predeclare)

HERE = os.path.dirname(os.path.abspath(__file__))
I = Ids()
A = Ids('act')
L = 'da'

# ---------------------------------------------------------------- products
# The Demo app catalog has no Skatteguiden products. Both bound products are `monthly`,
# so the period the cards claim ("kr./md") matches the period the store will charge.
P_STANDARD = 'f4088450-45a8-4737-8db0-367e642d7dcb'   # demo placeholder, period: monthly
P_PLUS = 'eb900c21-8404-4693-b956-eda7ce433017'       # demo placeholder, period: monthly

LOGO_URL = 'https://public-media.adapty.io/public/20/75/20754467-dcc4-409f-9b03-a86fb477eff1/asset-logo.png'
LOGO_ID = 534946
HERO_URL = 'https://public-media.adapty.io/public/d9/11/d911e916-0c05-4c8f-804f-0140665d9dfb/asset-hero.png'
HERO_ID = 534947

SCR = ['scr_welcome', 'scr_goal', 'scr_pain', 'scr_method',
       'scr_security', 'scr_plan', 'scr_paywall']

# ---------------------------------------------------------------- theme
# Every hex below was sampled: the site's computed styles, or the app screenshots.
# dark == light on purpose — Skatteguiden's app is light-only, so a dark theme would be invented.
C = [
    ('bg',        'Page',            '#FFFFFF', '#FFFFFF'),
    ('surface',   'Surface',         '#F9F9F9', '#F9F9F9'),
    ('card',      'Card',            '#FFFFFF', '#FFFFFF'),
    ('tint',      'Blue tint',       '#E5EDFF', '#E5EDFF'),
    ('tintPlus',  'Purple tint',     '#EAE0FF', '#EAE0FF'),
    ('primary',   'Skatteguiden blue', '#6B7AFF', '#6B7AFF'),
    ('purple',    'Purple',          '#9563FF', '#9563FF'),
    ('mint',      'Mint',            '#4ED3B4', '#4ED3B4'),
    ('ink',       'Ink',             '#12131A', '#12131A'),
    ('ink2',      'Ink soft',        '#292A35', '#292A35'),
    ('muted',     'Muted',           '#666666', '#666666'),
    ('faint',     'Faint',           '#888888', '#888888'),
    ('border',    'Border',          '#E4E4E9', '#E4E4E9'),
    ('white',     'White',           '#FFFFFF', '#FFFFFF'),
    ('green',     'Check green',     '#2C622C', '#2C622C'),
]

# Poppins is the brand face and cannot be referenced from a config (fonts are builder-only),
# so these presets carry size/weight/leading only.
T = [
    ('h1',      'H1',           28, 'bold',    34),
    ('h2',      'H2',           22, 'bold',    28),
    ('h3',      'H3',           17, 'bold',    23),
    ('body',    'Body',         15, 'regular', 22),
    ('bodyB',   'Body bold',    15, 'bold',    22),
    ('small',   'Small',        13, 'regular', 18),
    ('smallB',  'Small bold',   13, 'bold',    18),
    ('legal',   'Legal',        11, 'regular', 15),
    ('cta',     'CTA',          15, 'bold',    20, 0.6),
    ('price',   'Price',        24, 'bold',    28),
    ('badge',   'Badge',        11, 'bold',    14, 0.4),
    ('step',    'Step number',  15, 'bold',    20),
    ('col',     'Column head',   9, 'bold',    12, 0.3),
]

ICONS = json.load(open(os.path.join(os.path.dirname(HERE), 'assets', 'phosphor-icons.json')))
WANT = {('Check', 'bold'), ('X', 'regular'), ('CheckCircle', 'fill'), ('ShieldCheck', 'regular'),
        ('ChartLine', 'regular'), ('MagnifyingGlass', 'regular'), ('ListChecks', 'regular'),
        ('ArrowLeft', 'regular'), ('Star', 'fill'), ('Sparkle', 'regular')}
ICONS = [i for i in ICONS if (i['name'], i['weight']) in WANT]
assert len(ICONS) == len(WANT), sorted(WANT - {(i['name'], i['weight']) for i in ICONS})


# ---------------------------------------------------------------- helpers
def t(*parts, **kw):
    return text(rich(*parts, locale=L), **kw)


def cta_bar(label, actions, *, sub=None, extra=None):
    """The pinned bottom bar: one pill CTA, optional trust line under it."""
    kids = [stack(
        [t(Span(label, color='white'), preset='cta', align='center', width='fill')],
        height='hug', padding=pad(17, 20, 20, 17), corner=radius(9999),
        fill_=fill('primary'), align_h='center', align_v='center',
        caption='CTA', node_id=I('B'), actions=actions)]
    if sub:
        kids.append(t(Span(sub, color='faint'), preset='legal', align='center'))
    if extra:
        kids.extend(extra)
    return footer(kids, fill_=fill('white'), padding=pad(16, 16, 16, 14), gap=10,
                  caption='Bottom bar', node_id=I('F'))


def tap(*actions):
    return list(actions)


def value_row(icon_name, title, body, *, icon_color='primary', tint='tint'):
    return stack([
        stack([icon(icon_name, size_pt=20, color_id=icon_color, node_id=I('C'))],
              fixed_w=40, fixed_h=40, corner=radius(12), fill_=fill(tint),
              align_h='center', align_v='center', node_id=I('C')),
        stack([t(Span(title, color='ink'), preset='h3'),
               t(Span(body, color='muted'), preset='small')],
              gap=2, node_id=I('C')),
    ], direction='horizontal', gap=14, align_v='center', node_id=I('R'), caption=title)


def step_row(n, icon_name, title, body):
    return stack([
        stack([t(Span(n, color='white'), preset='step', align='center')],
              fixed_w=28, fixed_h=28, corner=radius(9999), fill_=fill('ink'),
              align_h='center', align_v='center', node_id=I('C')),
        stack([
            stack([icon(icon_name, size_pt=18, color_id='primary', node_id=I('C')),
                   t(Span(title, color='ink'), preset='h3', width='hug')],
                  direction='horizontal', gap=8, align_v='center', node_id=I('C')),
            t(Span(body, color='muted'), preset='small'),
        ], gap=4, node_id=I('C')),
    ], direction='horizontal', gap=12, align_v='start', node_id=I('R'), caption=title)


def topbar(step):
    return stack([
        stack([icon('ArrowLeft', size_pt=22, color_id='ink', node_id=I('C'))],
              fixed_w=40, fixed_h=40, align_h='start', align_v='center',
              node_id=I('B'), caption='Tilbage',
              actions=tap(navigate_back(action_id=A('')))),
        stack([t(Span('TRIN ' + str(step) + ' AF 5', color='faint'),
                 preset='col', width='hug')],
              width='hug', padding=pad(6, 10, 10, 6), corner=radius(9999),
              fill_=fill('surface'), node_id=I('C'), caption='Trin ' + str(step)),
    ], direction='horizontal', gap=0, align_v='center', distribution='space-between',
        node_id=I('R'), caption='Topbar')


def bullet(label, *, glyph='CheckCircle', weight='fill', col='mint'):
    return stack([
        icon(glyph, size_pt=18, color_id=col, weight=weight, node_id=I('C')),
        t(Span(label, color='ink2'), preset='body'),
    ], direction='horizontal', gap=10, align_v='center', node_id=I('R'), caption=label)


# ================================================================ 1. welcome
s_welcome = screen(
    SCR[0], [
        stack([
            # No file for the Sg mark — a styled empty box, never a made-up URL.
            image(LOGO_URL, media_id=LOGO_ID, fixed_w=44, height='hug', fit='fit',
                  locale=L, caption='Skatteguiden logo', node_id=I('M')),
            t(Span('Skatteguiden', color='ink'), preset='h3', width='hug'),
        ], direction='horizontal', gap=10, align_v='center', node_id=I('C')),

        stack([
            t(Span('Din skat, på autopilot', color='ink'), preset='h1'),
            t(Span('Få overblik over din indkomst og skat — og lad vores '
                   'skatteteam rette den for dig.', color='muted'), preset='body'),
        ], gap=10, node_id=I('C')),

        stack([
            value_row('ChartLine', 'Overblik hele året',
                      'Se din indkomst, din skat og hvad du får udbetalt.'),
            value_row('MagnifyingGlass', 'Glemte fradrag',
                      'Vi leder efter fradrag, du har til gode — også år tilbage.',
                      icon_color='purple', tint='tintPlus'),
            value_row('ShieldCheck', 'Rigtige skatterådgivere',
                      'Et dansk skatteteam retter og indberetter for dig.'),
        ], gap=18, node_id=I('C')),

        image(HERO_URL, media_id=HERO_ID, height='hug', fit='cover', corner=radius(18),
              locale=L, caption='Hero — Skatteguiden dashboard', node_id=I('M')),
        cta_bar('KOM I GANG', tap(navigate(SCR[1], action_id=A(''))),
                sub='Det tager under et minut.'),
    ],
    caption='Velkommen', fill_=fill('bg'), gap=26, safe_area=True, scrollable=True,
    padding=pad(24, 20, 20, 168), status_bar=True, status_bar_theme='dark')

# ================================================================ 2. goal
GOALS = [
    ('fradrag',  'Glemte fradrag',        'Find penge, jeg har til gode'),
    ('overblik', 'Overblik over min skat', 'Forstå hvad jeg betaler og hvorfor'),
    ('restskat', 'Undgå restskat',         'Betale det rigtige hele året'),
    ('alt',      'Bare styr på det hele',  'Lad jer om det'),
]


def goal_card(cid, title, sub, default=False):
    """Same base look on every card; `propsByState.selected` does the selecting."""
    ring = stack([
        stack([], fixed_w=10, fixed_h=10, corner=radius(9999),
              props_by_state={'selected': {'fill': fill('primary')}},
              states=[], node_id=I('C'), caption='Dot'),
    ], fixed_w=22, fixed_h=22, corner=radius(9999), border='border',
        align_h='center', align_v='center', node_id=I('C'), caption='Radio',
        props_by_state={'selected': {'border': {'color': color('primary'),
                                              'style': 'solid', 'width': 1}}},
        states=[])
    return on_selected(
        selectable([
            stack([t(Span(title, color='ink'), preset='h3'),
                   t(Span(sub, color='muted'), preset='small')], gap=2, node_id=I('C')),
            ring,
        ], group_id='goal', custom_id=cid, default=default,
            direction='horizontal', gap=12, align_v='center',
            distribution='space-between',
            padding=pad(16, 16, 16, 16), corner=radius(14),
            fill_=fill('card'), border='border',
            node_id=I('G'), caption=title),
        fill=fill('tint'),
        border={'color': color('primary'), 'style': 'solid', 'width': 1},
        padding=pad(16, 16, 16, 16), borderRadius=radius(14))


s_goal = screen(
    SCR[1], [
        topbar(1),
        stack([
            t(Span('Hvad vil du helst have styr på?', color='ink'), preset='h1'),
            t(Span('Vi bruger dit svar til at vise dig det rigtige først.',
                   color='muted'), preset='body'),
        ], gap=8, node_id=I('C')),
        stack([goal_card(*g, default=(i == 0)) for i, g in enumerate(GOALS)],
              gap=10, node_id=I('C')),
        cta_bar('FORTSÆT', tap(navigate(SCR[2], action_id=A('')))),
    ],
    caption='Dit mål', fill_=fill('bg'), gap=22, safe_area=True, scrollable=True,
    padding=pad(8, 20, 20, 120), status_bar=True, status_bar_theme='dark',
    selectable_groups=[{'id': 'goal', 'type': 'single_choice'}])

# ================================================================ 3. pain
s_pain = screen(
    SCR[2], [
        topbar(2),
        stack([
            t(Span('Betaler du for meget i skat?', color='ink'), preset='h1'),
            t(Span('Din forskudsopgørelse er et gæt på et helt år. '
                   'Skifter du job, køber bolig eller ændrer din kørsel sig, '
                   'passer den ikke længere.', color='muted'), preset='body'),
        ], gap=10, node_id=I('C')),

        stack([
            t(Span('Uden Skatteguiden', color='faint'), preset='col'),
            bullet('Du opdager først fejlen på årsopgørelsen', glyph='X',
                   weight='regular', col='faint'),
            bullet('Glemte fradrag bliver aldrig indberettet', glyph='X',
                   weight='regular', col='faint'),
            bullet('Restskat kommer som en overraskelse', glyph='X',
                   weight='regular', col='faint'),
        ], gap=12, padding=pad(18, 18, 18, 18), corner=radius(16),
            fill_=fill('surface'), node_id=I('C')),

        stack([
            t(Span('Med Skatteguiden', color='primary'), preset='col'),
            bullet('Du får besked, når din skat ikke passer'),
            bullet('Vi leder efter glemte fradrag år tilbage'),
            bullet('Skatteteamet retter det for dig'),
        ], gap=12, padding=pad(18, 18, 18, 18), corner=radius(16),
            fill_=fill('tint'), node_id=I('C')),

        cta_bar('FORTSÆT', tap(navigate(SCR[3], action_id=A('')))),
    ],
    caption='Problemet', fill_=fill('bg'), gap=20, safe_area=True, scrollable=True,
    padding=pad(8, 20, 20, 120), status_bar=True, status_bar_theme='dark')

# ================================================================ 4. method
s_method = screen(
    SCR[3], [
        topbar(3),
        stack([
            t(Span('Sådan virker det', color='ink'), preset='h1'),
            t(Span('Tre trin. Resten kører af sig selv.', color='muted'), preset='body'),
        ], gap=8, node_id=I('C')),
        stack([
            step_row('1', 'ShieldCheck', 'Forbind til SKAT',
                     'Du logger ind med MitID. Vi henter dine tal fra SKAT.'),
            step_row('2', 'ChartLine', 'Vi holder øje hele året',
                     'Indkomst, fradrag og skattetrin bliver fulgt løbende.'),
            step_row('3', 'ListChecks', 'Skatteteamet retter for dig',
                     'Rigtige skatterådgivere gennemgår og indberetter.'),
        ], gap=22, padding=pad(20, 18, 18, 20), corner=radius(16),
            fill_=fill('surface'), node_id=I('C')),
        cta_bar('FORTSÆT', tap(navigate(SCR[4], action_id=A('')))),
    ],
    caption='Sådan virker det', fill_=fill('bg'), gap=22, safe_area=True, scrollable=True,
    padding=pad(8, 20, 20, 120), status_bar=True, status_bar_theme='dark')

# ================================================================ 5. security
s_security = screen(
    SCR[4], [
        topbar(4),
        stack([
            stack([icon('ShieldCheck', size_pt=30, color_id='primary', node_id=I('C'))],
                  fixed_w=64, fixed_h=64, corner=radius(20), fill_=fill('tint'),
                  align_h='center', align_v='center', node_id=I('C')),
            t(Span('Dine tal bliver hos dig', color='ink'), preset='h1'),
            t(Span('Vi arbejder med danskernes skat. Sikkerhed er ikke en '
                   'ekstrafunktion.', color='muted'), preset='body'),
        ], gap=12, node_id=I('C')),
        stack([
            bullet('Du logger ind med MitID'),
            bullet('Dansk selskab — Skatteguiden ApS, CVR 38531646'),
            bullet('Du ser alt, hvad vi indberetter'),
        ], gap=14, padding=pad(18, 18, 18, 18), corner=radius(16),
            fill_=fill('surface'), node_id=I('C')),
        cta_bar('FORTSÆT', tap(navigate(SCR[5], action_id=A('')))),
    ],
    caption='Sikkerhed', fill_=fill('bg'), gap=22, safe_area=True, scrollable=True,
    padding=pad(8, 20, 20, 120), status_bar=True, status_bar_theme='dark')

# ================================================================ 6. plan (the echo)
# Honest personalization: the flow echoes the answer back. It computes nothing.
GOAL_HEAD = [
    (eq(ref('goal.selectedOptionId'), 'fradrag'),
     [Span('Vi starter med dine ', color='ink'),
      Span('glemte fradrag', color='primary'), Span('.', color='ink')]),
    (eq(ref('goal.selectedOptionId'), 'overblik'),
     [Span('Vi starter med dit ', color='ink'),
      Span('skatteoverblik', color='primary'), Span('.', color='ink')]),
    (eq(ref('goal.selectedOptionId'), 'restskat'),
     [Span('Vi starter med at forebygge ', color='ink'),
      Span('restskat', color='primary'), Span('.', color='ink')]),
]
GOAL_SUB = [
    (eq(ref('goal.selectedOptionId'), 'fradrag'),
     [Span('Du sagde, du vil finde penge, du har til gode. '
           'Så begynder vi der.', color='muted')]),
    (eq(ref('goal.selectedOptionId'), 'overblik'),
     [Span('Du sagde, du vil forstå, hvad du betaler. '
           'Så begynder vi der.', color='muted')]),
    (eq(ref('goal.selectedOptionId'), 'restskat'),
     [Span('Du sagde, du vil betale det rigtige hele året. '
           'Så begynder vi der.', color='muted')]),
]

s_plan = screen(
    SCR[5], [
        topbar(5),
        stack([
            stack([
                icon('Sparkle', size_pt=14, color_id='primary', node_id=I('C')),
                t(Span('DIN PLAN', color='primary'), preset='badge', width='hug'),
            ], direction='horizontal', gap=6, align_v='center', width='hug',
                padding=pad(7, 12, 12, 7), corner=radius(9999), fill_=fill('tint'),
                node_id=I('C')),
            text(switch_rich(GOAL_HEAD,
                             default=[Span('Din plan er klar.', color='ink')], locale=L),
                 preset='h1', node_id=I('T'), caption='Personligt hovedbudskab'),
            text(switch_rich(GOAL_SUB,
                             default=[Span('Lad os få styr på det hele.', color='muted')],
                             locale=L),
                 preset='body', node_id=I('T'), caption='Personlig underrubrik'),
        ], gap=12, node_id=I('C')),
        stack([
            t(Span('Når du er i gang', color='faint'), preset='col'),
            bullet('Du forbinder til SKAT med MitID'),
            bullet('Vi henter din indkomst og dine fradrag'),
            bullet('Skatteteamet gennemgår din skat'),
        ], gap=14, padding=pad(18, 18, 18, 18), corner=radius(16),
            fill_=fill('surface'), node_id=I('C')),
        cta_bar('SE MEDLEMSKABER', tap(navigate(SCR[6], action_id=A('')))),
    ],
    caption='Din plan', fill_=fill('bg'), gap=22, safe_area=True, scrollable=True,
    padding=pad(8, 20, 20, 120), status_bar=True, status_bar_theme='dark')

# ================================================================ 7. paywall
# Rows and prices are verbatim from konto.skatteguiden.dk/bliv-medlem/pakker.
ROWS = [
    ('Overblik over indkomst og skat',    'check', 'check', 'check'),
    ('Først i køen til Tidlig Årsopgørelse', 'x',  'check', 'check'),
    ('Se om du betaler for meget',        'x',     'check', 'check'),
    ('Personlig opdatering hver måned',   'x',     'x',     'check'),
    ('Skatterådgivning inden for 2 hverdage', 'x', 'x',     'check'),
    ('Vi indberetter dine fradrag',       '20%',   '10%',   'Gratis'),
]


def cell(v, *, strong=False):
    if v == 'check':
        kid = icon('Check', size_pt=15, color_id='primary' if strong else 'green',
                   weight='bold', node_id=I('C'))
    elif v == 'x':
        kid = icon('X', size_pt=13, color_id='border', weight='regular', node_id=I('C'))
    else:
        kid = t(Span(v, color='primary' if strong else 'ink2'),
                preset='smallB', align='center')
    return stack([kid], fixed_w=58, align_h='center', align_v='center', node_id=I('C'))


def rule():
    return stack([], fixed_h=1, fill_=fill('border'), node_id=I('C'), caption='Linje')


def table_row(label, a, b, c):
    return stack([
        stack([t(Span(label, color='ink2'), preset='small')], node_id=I('C')),
        cell(a), cell(b), cell(c, strong=True),
    ], direction='horizontal', gap=0, align_v='center',
        padding=pad(10, 0, 0, 10), node_id=I('R'), caption=label)


def table_body():
    out = []
    for i, r in enumerate(ROWS):
        if i:
            out.append(rule())
        out.append(table_row(*r))
    return out


comparison = stack([
    stack([
        stack([], node_id=I('C')),
        stack([t(Span('GRATIS', color='faint'), preset='col', align='center')],
              fixed_w=58, align_h='center', node_id=I('C')),
        stack([t(Span('STANDARD', color='faint'), preset='col', align='center')],
              fixed_w=58, align_h='center', node_id=I('C')),
        stack([t(Span('PLUS', color='primary'), preset='col', align='center')],
              fixed_w=58, align_h='center', node_id=I('C')),
    ], direction='horizontal', gap=0, align_v='end', padding=pad(0, 0, 0, 8), node_id=I('R')),
    rule(),
    *table_body(),
], gap=0, padding=pad(16, 16, 16, 16), corner=radius(16), fill_=fill('surface'),
    node_id=I('C'), caption='Sammenligning')


def plan_card(*, product_id, name, blurb, price, per, yearly, default, badge=None):
    ring = stack([
        stack([], fixed_w=10, fixed_h=10, corner=radius(9999),
              props_by_state={'selected': {'fill': fill('primary')}},
              states=[], node_id=I('C'), caption='Dot'),
    ], fixed_w=22, fixed_h=22, corner=radius(9999), border='border',
        align_h='center', align_v='center', node_id=I('C'), caption='Radio',
        props_by_state={'selected': {'border': {'color': color('primary'),
                                              'style': 'solid', 'width': 1}}},
        states=[])

    head = [t(Span(name, color='ink'), preset='h3', width='hug')]
    if badge:
        head.append(stack(
            [t(Span(badge, color='white'), preset='badge', align='center')],
            width='hug', padding=pad(4, 9, 9, 4), corner=radius(9999),
            fill_=fill('primary'), node_id=I('C'), caption='Badge'))

    return on_selected(
        product([
            stack([
                stack(head, direction='horizontal', gap=8, align_v='center', node_id=I('C')),
                t(Span(blurb, color='muted'), preset='small'),
                stack([
                    t(Span(price, color='ink'), preset='price', width='hug'),
                    t(Span(per, color='muted'), preset='small', width='hug'),
                ], direction='horizontal', gap=5, align_v='end', node_id=I('C')),
                t(Span(yearly, color='faint'), preset='legal'),
            ], gap=5, node_id=I('C')),
            ring,
        ], product_id=product_id, group_id='sgplans', default=default,
            direction='horizontal', gap=12, align_v='center',
            distribution='space-between',
            padding=pad(16, 16, 16, 16), corner=radius(16),
            fill_=fill('card'), border='border',
            node_id=I('P'), caption=name),
        fill=fill('tint'),
        border={'color': color('primary'), 'style': 'solid', 'width': 1},
        padding=pad(16, 16, 16, 16), borderRadius=radius(16))


PAY_HEAD = [
    (eq(ref('goal.selectedOptionId'), 'fradrag'),
     [Span('Få fundet dine ', color='ink'), Span('glemte fradrag', color='primary')]),
    (eq(ref('goal.selectedOptionId'), 'overblik'),
     [Span('Få dit fulde ', color='ink'), Span('skatteoverblik', color='primary')]),
    (eq(ref('goal.selectedOptionId'), 'restskat'),
     [Span('Slip for ', color='ink'), Span('restskat', color='primary')]),
]

TERMS = 'https://www.skatteguiden.dk/juridiske-dokumenter'

s_paywall = screen(
    SCR[6], [
        stack([
            stack([], node_id=I('C')),
            stack([icon('X', size_pt=20, color_id='faint', weight='regular', node_id=I('C'))],
                  fixed_w=36, fixed_h=36, align_h='center', align_v='center',
                  node_id=I('B'), caption='Luk',
                  actions=tap(close(action_id=A('')))),
        ], direction='horizontal', distribution='space-between',
            align_v='center', node_id=I('R')),

        stack([
            stack([
                t(Span('PRØV 1 MÅNED GRATIS', color='primary'), preset='badge',
                  width='hug', align='center'),
            ], width='hug', padding=pad(7, 12, 12, 7), corner=radius(9999),
                fill_=fill('tint'), node_id=I('C')),
            text(switch_rich(PAY_HEAD,
                             default=[Span('Vælg dit medlemskab', color='ink')], locale=L),
                 preset='h1', node_id=I('T'), caption='Overskrift (afspejler målet)'),
            t(Span('Gyldigt én gang. Opsig når som helst.', color='muted'), preset='body'),
        ], gap=10, node_id=I('C')),

        stack([
            plan_card(product_id=P_PLUS, name='Plus', badge='MEST POPULÆR',
                      blurb='Udvidet og hurtigere service — vi indberetter gratis.',
                      price='79 kr.', per='/md', yearly='eller 790 kr./år — spar 158 kr.',
                      default=True),
            plan_card(product_id=P_STANDARD, name='Standard',
                      blurb='Få rettet din skat løbende af vores skatteteam.',
                      price='39 kr.', per='/md', yearly='eller 390 kr./år — spar 78 kr.',
                      default=False),
        ], gap=10, node_id=I('C')),

        t(Span('Hvad får du?', color='ink'), preset='h3'),
        comparison,

        cta_bar(
            'PRØV 1 MÅNED GRATIS',
            tap(purchase('sgplans', action_id=A(''))),
            sub='Derefter fra 39 kr./md. Ingen binding — opsig når som helst.',
            extra=[stack([
                stack([t(Span('Gendan køb', color='faint'), preset='legal',
                         align='center', width='hug')],
                      width='hug', node_id=I('B'), caption='Gendan køb',
                      actions=tap(restore(action_id=A('')))),
                t(Span('·', color='border'), preset='legal', width='hug'),
                stack([t(Span('Vilkår og privatliv', color='faint'), preset='legal',
                         align='center', width='hug')],
                      width='hug', node_id=I('B'), caption='Vilkår',
                      actions=tap(open_url(TERMS, action_id=A('')))),
            ], direction='horizontal', gap=10, align_h='center', align_v='center',
                node_id=I('R'), caption='Juridisk')]),
    ],
    caption='Medlemskab', fill_=fill('bg'), gap=20, safe_area=True, scrollable=True,
    padding=pad(8, 20, 20, 150), status_bar=True, status_bar_theme='dark',
    selectable_groups=[{'id': 'sgplans', 'type': 'product'}])

# ---------------------------------------------------------------- document
cfg = fk.config(
    screens=[s_welcome, s_goal, s_pain, s_method, s_security, s_plan, s_paywall],
    colors=C, typography=T, icons=ICONS,
    locales=((L, 'Dansk'),), default_locale=L,
    meta_screens=predeclare(SCR[6], [P_PLUS, P_STANDARD]),
)

out = os.path.join(os.path.dirname(HERE), 'flows', 'skatteguiden-onboarding.json')
json.dump(cfg, open(out, 'w'), ensure_ascii=False, indent=1)
n = sum(len(s['elements']['map']) for s in cfg['screens'])
print(f'wrote {out}: {len(cfg["screens"])} screens, {n} elements')
