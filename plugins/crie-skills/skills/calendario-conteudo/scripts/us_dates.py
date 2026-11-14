#!/usr/bin/env python3
"""US marketing calendar: computes movable US holidays, retail dates and tax deadlines for any year.

Stdlib only. Usage:
    python3 -I us_dates.py --year 2027 [--year 2028] [--lang en|pt] [--brazil] [--month 11]

Lunar/lunisolar dates that need astronomy or moon sighting (Lunar New Year, Ramadan, Eid, Diwali)
are NOT computed: the script prints a reminder to look them up. Hanukkah, Rosh Hashanah and
Yom Kippur are computed with the arithmetic Hebrew calendar.
"""
import argparse
import sys
from datetime import date, timedelta

MSG = {
    "en": {
        "header": "US marketing calendar {y}",
        "lookup": "Look up every year (lunar, not computed): Lunar New Year, Ramadan / Eid al-Fitr, Diwali.",
        "observed": "observed",
        "bad_year": "Year must be between 1900 and 2200.",
        "bad_month": "Month must be between 1 and 12.",
    },
    "pt": {
        "header": "Calendário de marketing dos EUA {y}",
        "lookup": "Consulte todo ano (lunares, não calculadas): Ano-Novo Lunar, Ramadã / Eid al-Fitr, Diwali.",
        "observed": "folga observada",
        "bad_year": "O ano deve estar entre 1900 e 2200.",
        "bad_month": "O mês deve estar entre 1 e 12.",
    },
}

# name -> (en, pt)
N = {
    "newyear": ("New Year's Day (federal)", "Ano-Novo (feriado federal)"),
    "mlk": ("Martin Luther King Jr. Day (federal, 3rd Mon Jan)", "Dia de Martin Luther King Jr. (federal, 3ª seg. de jan.)"),
    "superbowl": ("Super Bowl Sunday (estimate: 2nd Sun Feb; confirm with the NFL)", "Domingo do Super Bowl (estimativa: 2º dom. de fev.; confirme com a NFL)"),
    "valentine": ("Valentine's Day", "Valentine's Day (Dia dos Namorados dos EUA)"),
    "presidents": ("Presidents' Day (federal, 3rd Mon Feb)", "Presidents' Day (federal, 3ª seg. de fev.)"),
    "mardigras": ("Mardi Gras / Carnival Tuesday", "Terça de Carnaval / Mardi Gras"),
    "ashwed": ("Ash Wednesday", "Quarta-feira de Cinzas"),
    "dst_start": ("Daylight saving time starts (2nd Sun Mar)", "Início do horário de verão (2º dom. de mar.)"),
    "stpatrick": ("St. Patrick's Day", "St. Patrick's Day"),
    "goodfriday": ("Good Friday", "Sexta-feira Santa"),
    "easter": ("Easter Sunday", "Domingo de Páscoa"),
    "taxday": ("Tax Day: individual returns + Q1 estimated tax (Form 1040-ES)", "Prazo do imposto de renda pessoa física + 1ª parcela estimada (1040-ES)"),
    "pship": ("Partnership / S-corp returns due (Forms 1065 / 1120-S)", "Prazo das declarações de partnership / S-corp (1065 / 1120-S)"),
    "admin": ("Administrative Professionals' Day (Wed of last full week of Apr)", "Dia do Profissional Administrativo (qua. da última semana cheia de abr.)"),
    "cinco": ("Cinco de Mayo", "Cinco de Mayo"),
    "teacher": ("Teacher Appreciation Week starts (1st full week of May)", "Início da Semana de Valorização do Professor (1ª semana cheia de maio)"),
    "nsbw": ("National Small Business Week starts (SBA; usually 1st week of May; confirm on sba.gov)", "Início da National Small Business Week (SBA; costuma ser a 1ª semana de maio; confirme no sba.gov)"),
    "mother": ("Mother's Day (2nd Sun May)", "Dia das Mães (2º dom. de maio; igual ao Brasil)"),
    "memorial": ("Memorial Day (federal, last Mon May)", "Memorial Day (federal, última seg. de maio)"),
    "q2": ("Q2 estimated tax due", "2ª parcela do imposto estimado"),
    "juneteenth": ("Juneteenth (federal)", "Juneteenth (feriado federal)"),
    "father": ("Father's Day (3rd Sun June)", "Dia dos Pais dos EUA (3º dom. de junho)"),
    "july4": ("Independence Day (federal)", "Independence Day / 4 de Julho (federal)"),
    "labor": ("Labor Day (federal, 1st Mon Sep)", "Labor Day (federal, 1ª seg. de set.)"),
    "grandparents": ("Grandparents Day (1st Sun after Labor Day)", "Dia dos Avós dos EUA (1º dom. após o Labor Day)"),
    "q3": ("Q3 estimated tax due + extended partnership / S-corp returns", "3ª parcela do imposto estimado + prazo estendido de partnership / S-corp"),
    "hhm": ("Hispanic Heritage Month (Sep 15 - Oct 15)", "Mês da Herança Hispânica (15/09 a 15/10)"),
    "rosh": ("Rosh Hashanah (begins at sundown the evening before)", "Rosh Hashaná (começa ao pôr do sol da véspera)"),
    "yomkippur": ("Yom Kippur (begins at sundown the evening before)", "Yom Kippur (começa ao pôr do sol da véspera)"),
    "columbus": ("Columbus Day / Indigenous Peoples' Day (federal, 2nd Mon Oct)", "Columbus Day / Dia dos Povos Indígenas (federal, 2ª seg. de out.)"),
    "extension": ("Extended individual returns due (Oct 15)", "Prazo da declaração pessoa física com extensão (15/10)"),
    "halloween": ("Halloween", "Halloween"),
    "dst_end": ("Daylight saving time ends (1st Sun Nov)", "Fim do horário de verão (1º dom. de nov.)"),
    "election": ("Election Day (Tue after 1st Mon Nov; avoid partisan posts)", "Dia da eleição (ter. após a 1ª seg. de nov.; evite posts partidários)"),
    "veterans": ("Veterans Day (federal)", "Veterans Day (federal)"),
    "thanksgiving": ("Thanksgiving (federal, 4th Thu Nov)", "Thanksgiving / Ação de Graças (federal, 4ª qui. de nov.)"),
    "blackfriday": ("Black Friday", "Black Friday"),
    "sbs": ("Small Business Saturday", "Small Business Saturday (compre no comércio local)"),
    "cyber": ("Cyber Monday", "Cyber Monday"),
    "giving": ("Giving Tuesday", "Giving Tuesday (dia de doações)"),
    "hanukkah": ("Hanukkah, first night (candle at sundown; ends 8 nights later)", "Hanukkah, primeira noite (vela ao pôr do sol; 8 noites)"),
    "supersat": ("Super Saturday (last Saturday before Christmas)", "Super Saturday (último sábado antes do Natal)"),
    "xmaseve": ("Christmas Eve", "Véspera de Natal"),
    "xmas": ("Christmas Day (federal)", "Natal (feriado federal)"),
    "kwanzaa": ("Kwanzaa begins (Dec 26 - Jan 1)", "Início do Kwanzaa (26/12 a 01/01)"),
    "nye": ("New Year's Eve", "Réveillon"),
    "q4": ("Q4 estimated tax (previous year) due", "4ª parcela do imposto estimado (do ano anterior)"),
    "finlit": ("Financial Literacy Month (April)", "Mês da Educação Financeira (abril)"),
    "homeown": ("National Homeownership Month (June) + Atlantic hurricane season starts", "Mês Nacional da Casa Própria (junho) + início da temporada de furacões do Atlântico"),
    "lifeins": ("Life Insurance Awareness Month (September)", "Mês de Conscientização do Seguro de Vida (setembro)"),
    "aep_mkt": ("Medicare AEP marketing may begin (CMS)", "Início permitido do marketing do AEP do Medicare (CMS)"),
    "aep": ("Medicare Annual Enrollment Period opens (to Dec 7)", "Abre o período anual de inscrição do Medicare (até 07/12)"),
    "aca": ("ACA Marketplace Open Enrollment opens (end date varies by state; check HealthCare.gov)", "Abre a inscrição do ACA/Obamacare (fim varia por estado; confira no HealthCare.gov)"),
    "aep_end": ("Medicare Annual Enrollment Period ends", "Fim do período anual de inscrição do Medicare"),
    "maoep": ("Medicare Advantage Open Enrollment (Jan 1 - Mar 31)", "Open Enrollment do Medicare Advantage (01/01 a 31/03)"),
    # Brazilian community
    "br_carnaval": ("Carnaval (Saturday to Tuesday)", "Carnaval (sábado a terça)"),
    "br_namorados": ("Dia dos Namorados (Brazilian Valentine's Day)", "Dia dos Namorados"),
    "br_sjoao": ("Festa Junina peak (São João); parties run all June", "São João (auge das festas juninas, que vão o mês todo)"),
    "br_pais": ("Dia dos Pais in Brazil (2nd Sun Aug, differs from US)", "Dia dos Pais no Brasil (2º dom. de agosto, diferente dos EUA)"),
    "br_brday": ("Brazilian Day NYC (estimate: Sunday before Labor Day; confirm)", "Brazilian Day NYC (estimativa: domingo antes do Labor Day; confirme)"),
    "br_sete": ("Brazilian Independence Day (Sete de Setembro)", "Independência do Brasil (7 de Setembro)"),
    "br_criancas": ("Dia das Crianças + Nossa Senhora Aparecida", "Dia das Crianças + Nossa Senhora Aparecida"),
}


def nth_weekday(y, m, weekday, n):
    """n-th weekday (Mon=0) of month; n=-1 means last."""
    if n > 0:
        d = date(y, m, 1)
        d += timedelta(days=(weekday - d.weekday()) % 7)
        return d + timedelta(weeks=n - 1)
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    d = nxt - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def easter(y):
    """Western (Gregorian) Easter, anonymous algorithm."""
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(y, month, day)


# --- Hebrew calendar (Reingold & Dershowitz, arithmetic) ---
HEBREW_EPOCH = -1373427  # R.D. of 1 Tishri AM 1 (Python ordinal == R.D.)


def _elapsed(y):
    months = (235 * y - 234) // 19
    parts = 12084 + 13753 * months
    day = 29 * months + parts // 25920
    return day + 1 if (3 * (day + 1)) % 7 < 3 else day


def _correction(y):
    ny0, ny1, ny2 = _elapsed(y - 1), _elapsed(y), _elapsed(y + 1)
    if ny2 - ny1 == 356:
        return 2
    if ny1 - ny0 == 382:
        return 1
    return 0


def hebrew_new_year(y):
    return HEBREW_EPOCH + _elapsed(y) + _correction(y)


def rosh_hashanah(greg_year):
    return date.fromordinal(hebrew_new_year(greg_year + 3761))


def hanukkah_first_day(greg_year):
    """25 Kislev of the Hebrew year that starts in autumn of greg_year (first candle the evening before)."""
    hy = greg_year + 3761
    ny = hebrew_new_year(hy)
    length = hebrew_new_year(hy + 1) - ny
    marheshvan = 30 if length in (355, 385) else 29
    return date.fromordinal(ny + 30 + marheshvan + 24)


def federal_observed(y):
    """Federal holidays as observed (Sat -> Fri, Sun -> Mon), used for tax deadline shifts."""
    fixed = [date(y, 1, 1), date(y, 6, 19), date(y, 7, 4), date(y, 11, 11), date(y, 12, 25)]
    obs = set()
    for d in fixed:
        if d.weekday() == 5:
            obs.add(d - timedelta(days=1))
        elif d.weekday() == 6:
            obs.add(d + timedelta(days=1))
        else:
            obs.add(d)
    obs |= {nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3), nth_weekday(y, 5, 0, -1),
            nth_weekday(y, 9, 0, 1), nth_weekday(y, 10, 0, 2), nth_weekday(y, 11, 3, 4)}
    # Jan 1 of next year observed on Dec 31 when it falls on Saturday
    if date(y + 1, 1, 1).weekday() == 5:
        obs.add(date(y, 12, 31))
    # DC Emancipation Day (Apr 16) also moves federal tax deadlines
    em = date(y, 4, 16)
    obs.add(em - timedelta(days=1) if em.weekday() == 5 else em + timedelta(days=1) if em.weekday() == 6 else em)
    return obs


def tax_due(d):
    """IRS rule: a deadline on a weekend or legal holiday moves to the next business day."""
    hol = federal_observed(d.year)
    while d.weekday() >= 5 or d in hol:
        d += timedelta(days=1)
    return d


def observed_note(d, lang):
    if d.weekday() == 5:
        return f" ({MSG[lang]['observed']}: {fmt(d - timedelta(days=1), lang)})"
    if d.weekday() == 6:
        return f" ({MSG[lang]['observed']}: {fmt(d + timedelta(days=1), lang)})"
    return ""


WD = {"en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      "pt": ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]}


def fmt(d, lang):
    return d.strftime("%m/%d/%Y") if lang == "en" else d.strftime("%d/%m/%Y")


def build(y, lang, brazil):
    ev = []
    add = lambda d, key, extra="": ev.append((d, N[key][0 if lang == "en" else 1] + extra))
    e = easter(y)
    thanks = nth_weekday(y, 11, 3, 4)
    labor = nth_weekday(y, 9, 0, 1)
    xmas = date(y, 12, 25)

    add(date(y, 1, 1), "newyear", observed_note(date(y, 1, 1), lang))
    add(tax_due(date(y, 1, 15)), "q4")
    add(date(y, 1, 1), "maoep")
    add(nth_weekday(y, 1, 0, 3), "mlk")
    add(nth_weekday(y, 2, 6, 2), "superbowl")
    add(date(y, 2, 14), "valentine")
    add(nth_weekday(y, 2, 0, 3), "presidents")
    add(e - timedelta(days=47), "mardigras")
    add(e - timedelta(days=46), "ashwed")
    add(nth_weekday(y, 3, 6, 2), "dst_start")
    add(tax_due(date(y, 3, 15)), "pship")
    add(date(y, 3, 17), "stpatrick")
    add(e - timedelta(days=2), "goodfriday")
    add(e, "easter")
    add(date(y, 4, 1), "finlit")
    add(tax_due(date(y, 4, 15)), "taxday")
    last_sat_apr = nth_weekday(y, 4, 5, -1)  # last full week ends on a Saturday
    add(last_sat_apr - timedelta(days=3), "admin")
    first_mon_may = nth_weekday(y, 5, 0, 1)
    add(first_mon_may, "teacher")
    add(nth_weekday(y, 5, 6, 1), "nsbw")
    add(date(y, 5, 5), "cinco")
    add(nth_weekday(y, 5, 6, 2), "mother")
    add(nth_weekday(y, 5, 0, -1), "memorial")
    add(date(y, 6, 1), "homeown")
    add(tax_due(date(y, 6, 15)), "q2")
    add(date(y, 6, 19), "juneteenth", observed_note(date(y, 6, 19), lang))
    add(nth_weekday(y, 6, 6, 3), "father")
    add(date(y, 7, 4), "july4", observed_note(date(y, 7, 4), lang))
    add(date(y, 9, 1), "lifeins")
    add(labor, "labor")
    add(labor + timedelta(days=6), "grandparents")
    add(tax_due(date(y, 9, 15)), "q3")
    add(date(y, 9, 15), "hhm")
    rh = rosh_hashanah(y)
    add(rh, "rosh")
    add(rh + timedelta(days=9), "yomkippur")
    add(date(y, 10, 1), "aep_mkt")
    add(date(y, 10, 15), "aep")
    add(nth_weekday(y, 10, 0, 2), "columbus")
    add(tax_due(date(y, 10, 15)), "extension")
    add(date(y, 10, 31), "halloween")
    add(date(y, 11, 1), "aca")
    add(nth_weekday(y, 11, 6, 1), "dst_end")
    add(nth_weekday(y, 11, 0, 1) + timedelta(days=1), "election")
    add(date(y, 11, 11), "veterans", observed_note(date(y, 11, 11), lang))
    add(thanks, "thanksgiving")
    add(thanks + timedelta(days=1), "blackfriday")
    add(thanks + timedelta(days=2), "sbs")
    add(thanks + timedelta(days=4), "cyber")
    add(thanks + timedelta(days=5), "giving")
    hk = hanukkah_first_day(y)
    if hk.year == y:
        add(hk - timedelta(days=1), "hanukkah")
    add(date(y, 12, 7), "aep_end")
    sat = xmas - timedelta(days=(xmas.weekday() - 5) % 7 or 7)
    add(sat, "supersat")
    add(date(y, 12, 24), "xmaseve")
    add(xmas, "xmas", observed_note(xmas, lang))
    add(date(y, 12, 26), "kwanzaa")
    add(date(y, 12, 31), "nye")

    if brazil:
        add(e - timedelta(days=50), "br_carnaval")
        add(date(y, 6, 12), "br_namorados")
        add(date(y, 6, 24), "br_sjoao")
        add(nth_weekday(y, 8, 6, 2), "br_pais")
        add(labor - timedelta(days=1), "br_brday")
        add(date(y, 9, 7), "br_sete")
        add(date(y, 10, 12), "br_criancas")
    ev.sort(key=lambda t: t[0])
    return ev


def main(argv=None):
    p = argparse.ArgumentParser(description="US marketing calendar / Calendário de marketing dos EUA")
    p.add_argument("--year", type=int, action="append", required=True)
    p.add_argument("--lang", choices=["en", "pt"], default="en")
    p.add_argument("--brazil", action="store_true", help="add Brazilian-community dates / datas da comunidade brasileira")
    p.add_argument("--month", type=int, help="only this month / só este mês")
    a = p.parse_args(argv)
    t = MSG[a.lang]
    if a.month is not None and not 1 <= a.month <= 12:
        print(t["bad_month"], file=sys.stderr)
        return 2
    for y in a.year:
        if not 1900 <= y <= 2200:
            print(t["bad_year"], file=sys.stderr)
            return 2
        print(f"# {t['header'].format(y=y)}")
        for d, name in build(y, a.lang, a.brazil):
            if a.month and d.month != a.month:
                continue
            print(f"{fmt(d, a.lang)}  {WD[a.lang][d.weekday()]}  {name}")
        print(t["lookup"])
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
