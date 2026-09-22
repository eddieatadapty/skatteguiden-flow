"""Assemble the clickable prototype: real phosphor icons + the uploaded assets, inlined."""
import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = {(i['name'], i['weight']): i['raw']
         for i in json.load(open(os.path.join(os.path.dirname(HERE), 'assets', 'phosphor-icons.json')))}


def ico(name, px, weight='regular', cls=''):
    raw = ICONS[(name, weight)]
    raw = re.sub(r'width="\d+"', 'width="%d"' % px, raw, count=1)
    raw = re.sub(r'height="\d+"', 'height="%d"' % px, raw, count=1)
    if cls:
        raw = raw.replace('<svg ', '<svg class="%s" ' % cls, 1)
    return raw


def data_uri(path):
    with open(path, 'rb') as fh:
        return 'data:image/png;base64,' + base64.b64encode(fh.read()).decode()


CHECK = lambda cls='': ico('Check', 15, 'bold', cls)
CROSS = lambda cls='': ico('X', 13, 'regular', cls)


def topbar(step, back=True):
    left = ('<button class="iconbtn" type="button" data-back aria-label="Tilbage">%s</button>'
            % ico('ArrowLeft', 21)) if back else '<span></span>'
    return ('<div class="topbar">%s<span class="pill">Trin %d af 5</span></div>'
            % (left, step))


def footer(label, go=None, sub=None, buy=False, extra=''):
    act = 'data-buy' if buy else 'data-go="%s"' % go
    sub_html = '<p class="legal">%s</p>' % sub if sub else ''
    return ('<div class="footerbar"><button class="cta" type="button" %s>%s</button>%s%s</div>'
            % (act, label, sub_html, extra))


def bullet(txt, on=True):
    if on:
        return ('<div class="bullet mint">%s<span>%s</span></div>'
                % (ico('CheckCircle', 17, 'fill'), txt))
    return '<div class="bullet off">%s<span>%s</span></div>' % (ico('X', 15), txt)


# ---------------------------------------------------------------- 1 welcome
VALUE_ROWS = [
    ('ChartLine', '', 'Overblik hele året',
     'Se din indkomst, din skat og hvad du får udbetalt.'),
    ('MagnifyingGlass', 'plum', 'Glemte fradrag',
     'Vi leder efter fradrag, du har til gode — også år tilbage.'),
    ('ShieldCheck', '', 'Rigtige skatterådgivere',
     'Et dansk skatteteam retter og indberetter for dig.'),
]
rows = ''.join(
    '<div class="vrow"><span class="vico %s">%s</span>'
    '<span><p class="h3">%s</p><p class="small">%s</p></span></div>'
    % (cls, ico(n, 19), t, b) for n, cls, t, b in VALUE_ROWS)

welcome = f'''<div class="pane" data-id="welcome"><div class="scroll">
  <div class="vrow" style="gap:10px">
    <img src="{{{{LOGO}}}}" alt="Skatteguiden" style="width:42px;height:auto">
    <p class="h3">Skatteguiden</p>
  </div>
  <div class="group" style="gap:10px">
    <h2 class="h1">Din skat, på autopilot</h2>
    <p class="sub">Få overblik over din indkomst og skat — og lad vores skatteteam rette den for dig.</p>
  </div>
  <div class="group" style="gap:17px">{rows}</div>
  <img class="hero" src="{{{{HERO}}}}" alt="Skatteguiden-appen: din skat på et overblik">
</div>{footer('Kom i gang', go='goal', sub='Det tager under et minut.')}</div>'''

# ---------------------------------------------------------------- 2 goal
GOALS = [
    ('fradrag', 'Glemte fradrag', 'Find penge, jeg har til gode'),
    ('overblik', 'Overblik over min skat', 'Forstå hvad jeg betaler og hvorfor'),
    ('restskat', 'Undgå restskat', 'Betale det rigtige hele året'),
    ('alt', 'Bare styr på det hele', 'Lad jer om det'),
]
choices = ''.join(
    '<button class="choice" type="button" role="radio" aria-checked="false" data-goal="%s">'
    '<span><p class="h3">%s</p><p class="small">%s</p></span>'
    '<span class="ring"><i></i></span></button>' % (k, t, s) for k, t, s in GOALS)

goal = f'''<div class="pane" data-id="goal"><div class="scroll">
  {topbar(1)}
  <div class="group" style="gap:8px">
    <h2 class="h1">Hvad vil du helst have styr på?</h2>
    <p class="sub">Vi bruger dit svar til at vise dig det rigtige først.</p>
  </div>
  <div class="group" role="radiogroup" aria-label="Dit mål">{choices}</div>
</div>{footer('Fortsæt', go='pain')}</div>'''

# ---------------------------------------------------------------- 3 pain
pain = f'''<div class="pane" data-id="pain"><div class="scroll">
  {topbar(2)}
  <div class="group" style="gap:10px">
    <h2 class="h1">Betaler du for meget i skat?</h2>
    <p class="sub">Din forskudsopgørelse er et gæt på et helt år. Skifter du job, køber bolig
      eller ændrer din kørsel sig, passer den ikke længere.</p>
  </div>
  <div class="panel grey">
    <p class="colhead">Uden Skatteguiden</p>
    {bullet('Du opdager først fejlen på årsopgørelsen', False)}
    {bullet('Glemte fradrag bliver aldrig indberettet', False)}
    {bullet('Restskat kommer som en overraskelse', False)}
  </div>
  <div class="panel tinted">
    <p class="colhead" style="color:var(--sg-primary)">Med Skatteguiden</p>
    {bullet('Du får besked, når din skat ikke passer')}
    {bullet('Vi leder efter glemte fradrag år tilbage')}
    {bullet('Skatteteamet retter det for dig')}
  </div>
</div>{footer('Fortsæt', go='method')}</div>'''

# ---------------------------------------------------------------- 4 method
STEPS = [
    ('ShieldCheck', 'Forbind til SKAT',
     'Du logger ind med MitID. Vi henter dine tal fra SKAT.'),
    ('ChartLine', 'Vi holder øje hele året',
     'Indkomst, fradrag og skattetrin bliver fulgt løbende.'),
    ('ListChecks', 'Skatteteamet retter for dig',
     'Rigtige skatterådgivere gennemgår og indberetter.'),
]
steps = ''.join(
    '<div class="step3"><span class="n">%d</span><span>'
    '<span class="ttl">%s<span class="h3">%s</span></span>'
    '<p class="small" style="margin-top:4px">%s</p></span></div>'
    % (i, ico(n, 17), t, b) for i, (n, t, b) in enumerate(STEPS, 1))

method = f'''<div class="pane" data-id="method"><div class="scroll">
  {topbar(3)}
  <div class="group" style="gap:8px">
    <h2 class="h1">Sådan virker det</h2>
    <p class="sub">Tre trin. Resten kører af sig selv.</p>
  </div>
  <div class="panel grey" style="gap:21px;padding:19px 17px">{steps}</div>
</div>{footer('Fortsæt', go='security')}</div>'''

# ---------------------------------------------------------------- 5 security
security = f'''<div class="pane" data-id="security"><div class="scroll">
  {topbar(4)}
  <div class="group" style="gap:12px">
    <span class="shieldwrap">{ico('ShieldCheck', 29)}</span>
    <h2 class="h1">Dine tal bliver hos dig</h2>
    <p class="sub">Vi arbejder med danskernes skat. Sikkerhed er ikke en ekstrafunktion.</p>
  </div>
  <div class="panel grey" style="gap:13px">
    {bullet('Du logger ind med MitID')}
    {bullet('Dansk selskab — Skatteguiden ApS, CVR 38531646')}
    {bullet('Du ser alt, hvad vi indberetter')}
  </div>
</div>{footer('Fortsæt', go='plan')}</div>'''

# ---------------------------------------------------------------- 6 plan
plan = f'''<div class="pane" data-id="plan"><div class="scroll">
  {topbar(5)}
  <div class="group" style="gap:12px">
    <span class="badge">{ico('Sparkle', 13)}Din plan</span>
    <h2 class="h1" id="plan-head">Din plan er klar.</h2>
    <p class="sub" id="plan-sub">Lad os få styr på det hele.</p>
  </div>
  <div class="panel grey" style="gap:13px">
    <p class="colhead">Når du er i gang</p>
    {bullet('Du forbinder til SKAT med MitID')}
    {bullet('Vi henter din indkomst og dine fradrag')}
    {bullet('Skatteteamet gennemgår din skat')}
  </div>
</div>{footer('Se medlemskaber', go='paywall')}</div>'''

# ---------------------------------------------------------------- 7 paywall
ROWS = [
    ('Overblik over indkomst og skat', 1, 1, 1),
    ('Først i køen til Tidlig Årsopgørelse', 0, 1, 1),
    ('Se om du betaler for meget', 0, 1, 1),
    ('Personlig opdatering hver måned', 0, 0, 1),
    ('Skatterådgivning inden for 2 hverdage', 0, 0, 1),
    ('Vi indberetter dine fradrag', '20%', '10%', 'Gratis'),
]


def tcell(v, plus=False):
    if v == 1:
        return '<td class="v">%s</td>' % CHECK('yes plus' if plus else 'yes')
    if v == 0:
        return '<td class="v">%s</td>' % CROSS('no')
    return '<td class="v"><span class="fee%s">%s</span></td>' % (' plus' if plus else '', v)


trs = ''.join('<tr><td>%s</td>%s%s%s</tr>'
              % (lbl, tcell(a), tcell(b), tcell(c, True)) for lbl, a, b, c in ROWS)

PLAN_CARDS = [
    ('plus', 'Plus', 'Mest populær', 'Udvidet og hurtigere service — vi indberetter gratis.',
     '79 kr.', 'eller 790 kr./år — spar 158 kr.'),
    ('standard', 'Standard', None, 'Få rettet din skat løbende af vores skatteteam.',
     '39 kr.', 'eller 390 kr./år — spar 78 kr.'),
]
cards = ''.join(
    '<button class="plan" type="button" role="radio" aria-checked="false" data-plan="%s">'
    '<span class="body"><span class="name"><span class="h3">%s</span>%s</span>'
    '<p class="small">%s</p>'
    '<span class="price"><b>%s</b><span>/md</span></span>'
    '<p class="peryear">%s</p></span>'
    '<span class="ring"><i></i></span></button>'
    % (k, nm, ('<span class="tag">%s</span>' % tag) if tag else '', blurb, pr, yr)
    for k, nm, tag, blurb, pr, yr in PLAN_CARDS)

legal = ('<div class="legalrow">'
         '<button class="linky" type="button" data-link="Gendanner tidligere køb fra App Store.">'
         'Gendan køb</button><span class="legal">·</span>'
         '<button class="linky" type="button" '
         'data-link="Åbner skatteguiden.dk/juridiske-dokumenter.">Vilkår og privatliv</button>'
         '</div>')

paywall = f'''<div class="pane" data-id="paywall"><div class="scroll">
  <div class="topbar"><span></span>
    <button class="iconbtn right" type="button" data-close aria-label="Luk">{ico('X', 19)}</button>
  </div>
  <div class="group" style="gap:10px">
    <span class="badge">Prøv 1 måned gratis</span>
    <h2 class="h1" id="pay-head">Vælg dit medlemskab</h2>
    <p class="sub">Gyldigt én gang. Opsig når som helst.</p>
  </div>
  <div class="group" role="radiogroup" aria-label="Medlemskab">{cards}</div>
  <p class="h3">Hvad får du?</p>
  <div class="cmp"><table>
    <thead><tr><th></th><th>Gratis</th><th>Standard</th><th class="plus">Plus</th></tr></thead>
    <tbody>{trs}</tbody>
  </table></div>
</div>{footer('Prøv 1 måned gratis', buy=True,
              sub='Derefter fra 39 kr./md. Ingen binding — opsig når som helst.',
              extra=legal)}</div>'''


# ---------------------------------------------------------------- 8 offer (own flow)
TL = [
    ('Check', 'I dag', 'Fuld adgang til Plus. Du betaler 0 kr.', 'now', 'bold'),
    ('Bell', 'Undervejs', 'Du kan opsige når som helst i App Store.', '', 'regular'),
    ('CalendarBlank', 'Efter 1 måned', '790 kr./år, hvis du ikke har opsagt.', '', 'regular'),
]
tl = ''.join(
    '<div class="tlrow %s"><span class="chip">%s</span>'
    '<span class="txt"><p class="h3">%s</p><p class="small">%s</p></span></div>'
    % (cls, ico(n, 17, w), t, b) for n, t, b, cls, w in TL)

PLUS_BULLETS = ['Få rettet din skat automatisk', 'Vi indberetter dine fradrag gratis',
                'Skatterådgivning inden for 2 hverdage', 'En personlig opdatering hver måned']

offer_legal = ('<div class="legalrow">'
               '<button class="linky" type="button" '
               'data-link="Gendanner tidligere køb fra App Store.">Gendan køb</button>'
               '<span class="legal">·</span>'
               '<button class="linky" type="button" '
               'data-link="Åbner skatteguiden.dk/juridiske-dokumenter.">'
               'Vilkår og privatliv</button></div>')

offer = f"""<div class="pane" data-id="offer"><div class="scroll">
  <div class="topbar"><span></span>
    <button class="iconbtn right" type="button" data-close aria-label="Luk">{ico('X', 19)}</button>
  </div>
  <div class="group" style="gap:10px">
    <span class="badge">{ico('Sparkle', 13)}Spar 2 måneder</span>
    <h2 class="h1">Betal årligt. Få 2 måneder gratis.</h2>
    <p class="sub">Fuld adgang til Plus — til prisen for 10 måneder.</p>
  </div>
  <div class="save">
    <span class="big"><b>790 kr.</b><span>/år</span></span>
    <p class="a">I stedet for 948 kr. ved månedlig betaling.</p>
    <p class="b">Svarer til ca. 66 kr./md — du sparer 158 kr. om året.</p>
  </div>
  <div class="timeline">{tl}</div>
  <div class="panel grey" style="gap:13px">
    <p class="colhead">Det får du med Plus</p>
    {''.join(bullet(x) for x in PLUS_BULLETS)}
  </div>
</div><div class="footerbar">
  <p class="offerline">0 kr. i dag<i>·</i><span>derefter 790 kr./år</span></p>
  <button class="cta" type="button" data-buy>Start min gratis måned</button>
  <p class="legal">Ingen binding. Opsig når som helst i App Store.</p>
  {offer_legal}
</div></div>"""


# ---------------------------------------------------------------- assemble
html = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
html = html.replace('<!--PANES-->',
                    '\n'.join([welcome, goal, pain, method, security, plan, paywall, offer]))
html = html.replace('__ICON_CheckCircle_34__', ico('CheckCircle', 34, 'fill'))
html = html.replace('{{LOGO}}', data_uri(os.path.join(os.path.dirname(HERE), 'assets', 'asset-logo.png')))
html = html.replace('{{HERO}}', data_uri(os.path.join(os.path.dirname(HERE), 'assets', 'asset-hero.png')))

assert '{{' not in html and '__ICON' not in html, 'unsubstituted token left'
out = os.path.join(os.path.dirname(HERE), 'index.html')
open(out, 'w', encoding='utf-8').write(html)
print('wrote %s  (%.0f KB)' % (out, len(html.encode()) / 1024))
