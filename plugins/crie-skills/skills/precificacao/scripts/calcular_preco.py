#!/usr/bin/env python3
"""Selling-price calculator for US small businesses (product, service, menu, business). Stdlib only.

Percentages are given as % (6 = 6%). Numbers accept US or Brazilian style and symbols:
8.50 | 8,50 | 1,234.56 | 1.234,56 | "$8.50" | 6%. A lone separator followed by exactly 3 digits is a
thousands separator (12,000 = 12.000 = twelve thousand). Output is in USD. --lang pt|en (default en).

Taxes, the US way:
  * Sales tax is added ON TOP of the price at checkout and is not revenue: it never enters the price divisor.
    --sales-tax 7 only shows what the customer pays.
  * Income tax and self-employment tax are on PROFIT: --margin is a PRE-TAX profit margin and --tax-setaside 30
    shows how much of that profit to set aside (estimate; confirm with a CPA).
  * --revenue-taxes is only for gross-receipts taxes charged on revenue (some states/cities). Usually 0.

Single-product business (fixed costs spread over total monthly units):
  python3 calcular_preco.py product --direct-cost 8.50 --variable-pct 3 --fee-per-sale 0.30 \
      --fixed-costs 12000 --volume 3000 --margin 15 [--current-price 14.99] [--sales-tax 7] [--tax-setaside 30]

One item of a menu/catalog (fixed costs as % of revenue):
  python3 calcular_preco.py product --direct-cost 3.30 --variable-pct 3 --fixed-cost-pct 30 --margin 15

Whole menu (CSV name,direct_cost,current_price,volume — last two optional; `,` `;` or tab; EN or PT headers):
  python3 calcular_preco.py menu --file items.csv --variable-pct 3 --margin 15 --fixed-costs 35000 \
      [--fixed-cost-pct 37] [--output result.csv]

Business break-even (fixed costs / weighted contribution margin %):
  python3 calcular_preco.py business --fixed-costs 35000 --avg-cm-pct 45 [--monthly-revenue 95000]

Service (hourly and project price):
  python3 calcular_preco.py service --fixed-costs 2500 --owner-pay 6000 --billable-hours 100 \
      --variable-pct 3 --margin 20 [--current-price 85] [--labor-rate 20 --payroll-burden 15] \
      [--project-hours 30] [--direct-cost 200] [--upfront-discount 5] [--deposit-pct 50] \
      [--installment-fee 4 --installments 3] [--sqft 2000] [--visits-per-month 4 --recurring-discount 10]

Contractor job estimate (markup method "10 and 10", or margin method --overhead-pct/--margin):
  python3 calcular_preco.py job --materials 9800 --crew-hours 120 --labor-rate 32 --payroll-burden 25 \
      --subcontractors 6500 --equipment 350 --permits 600 --dumpster 650 --contingency 8 \
      --overhead-markup 10 --profit-markup 10 [--schedule 33/33/34] [--change-order-cost 1200]

Commission income plan (insurance agents, loan brokers: you don't set the premium):
  python3 calcular_preco.py commission --target-income 90000 --fixed-costs 1200 --avg-premium 1500 \
      --first-year-pct 50 --renewal-pct 5 --payout-pct 80 --cost-per-lead 35 --close-rate 10

Portuguese mode names and flags also work (produto/servico/cardapio/empresa/obra/comissao, --custo-direto, --margem ...).
--json prints the result as JSON.
"""
import argparse
import csv
import json
import math
import re
import sys
import unicodedata


# ---------------------------------------------------------------- language
def _detect_lang(argv):
    for i, a in enumerate(argv):
        if a == "--lang" and i + 1 < len(argv):
            return "pt" if argv[i + 1].lower().startswith("pt") else "en"
        if a.startswith("--lang="):
            return "pt" if a.split("=", 1)[1].lower().startswith("pt") else "en"
    return "en"


LANG = _detect_lang(sys.argv[1:])


def T(en, pt):
    return pt if LANG == "pt" else en


_PT_ARGPARSE = {
    "usage: ": "uso: ",
    "options": "opções",
    "optional arguments": "opções",
    "positional arguments": "argumentos posicionais",
    "show this help message and exit": "mostra esta ajuda e sai",
    "the following arguments are required: %s": "faltou informar: %s",
    "invalid choice: %(value)r (choose from %(choices)s)": "opção inválida: %(value)r (escolha entre %(choices)s)",
    "unrecognized arguments: %s": "argumentos não reconhecidos: %s",
    "expected one argument": "faltou o valor",
    "argument %(argument_name)s: %(message)s": "%(argument_name)s: %(message)s",
    "invalid %(type)s value: %(value)r": "valor inválido: %(value)r",
    "ambiguous option: %(option)s could match %(matches)s": "opção ambígua: %(option)s pode ser %(matches)s",
}
if LANG == "pt":
    argparse._ = lambda s: _PT_ARGPARSE.get(s, s)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        message = re.sub(r"^argument \{[^}]*\}: ", T("mode: ", "modo: "), message)
        message = re.sub(r"^argument ", "", message).rstrip(".")
        print(T(f"Error: {message}. Use --help to see the options.",
                f"Erro: {message}. Use --help para ver as opções."), file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------- numbers
_NUM = re.compile(r"[-+]?(\d+(\.\d*)?|\.\d+)")
_EXAMPLES = "8.50 | 8,50 | 1,234.56 | 1.234,56 | $8.50 | 6%"


def number(txt, percent=False):
    """Parse US or Brazilian style ('1,234.56', '1.234,56', '$8.50', 'R$ 8,50', '6%'). Rejects negative/inf/nan.
    percent=True: a lone separator is always decimal (8.875 = 8,875 = 8.875%, NYC sales tax)."""
    raw = str(txt)
    s = raw.strip()
    for sym in ("US$", "R$", "USD", "$", "%", " ", " ", " "):
        s = s.replace(sym, "")
    bad = ValueError(T(f"'{raw}' is not a valid number (examples: {_EXAMPLES})",
                       f"'{raw}' não é um número válido (exemplos: {_EXAMPLES})"))
    if s.lower().lstrip("+-") in ("inf", "infinity", "nan"):
        raise ValueError(T(f"'{raw}' is not a valid number (use a finite value)",
                           f"'{raw}' não é um número válido (informe um valor finito)"))
    sign = ""
    if s and s[0] in "+-":
        sign, s = s[0], s[1:]
    if "," in s and "." in s:
        dec = "," if s.rfind(",") > s.rfind(".") else "."
        th = "." if dec == "," else ","
        intpart, _, frac = s.rpartition(dec)
        if not re.fullmatch(r"\d{1,3}(" + re.escape(th) + r"\d{3})*", intpart) or not re.fullmatch(r"\d*", frac):
            raise bad
        s = intpart.replace(th, "") + "." + frac
    elif "," in s or "." in s:
        sep = "," if "," in s else "."
        if s.count(sep) > 1:
            if not re.fullmatch(r"\d{1,3}(" + re.escape(sep) + r"\d{3})+", s):
                raise bad
            s = s.replace(sep, "")
        elif not percent and re.fullmatch(r"[1-9]\d{0,2}" + re.escape(sep) + r"\d{3}", s):  # 12,000 = 12.000 = 12000
            s = s.replace(sep, "")
        else:
            s = s.replace(sep, ".")
    s = sign + s
    if not _NUM.fullmatch(s):
        raise bad
    v = float(s)
    if not math.isfinite(v):
        raise bad
    if v < 0:
        raise ValueError(T(f"'{raw}' is negative; use a positive value or zero",
                           f"'{raw}' é negativo; informe um valor positivo ou zero"))
    return v + 0.0


def arg_num(txt):
    try:
        return number(txt)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def arg_pct(txt):
    try:
        return number(txt, percent=True)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


# ---------------------------------------------------------------- formatting
def r2(v):
    """Round to cents without -0.0."""
    return round(v, 2) + 0.0


def usd(v):
    return ("-$" if round(v, 2) < 0 else "$") + f"{abs(v):,.2f}"


def pct(v):
    s = f"{v:.2f}".rstrip("0")
    s = s + "0" if s.endswith(".") else s
    return ("0.0" if s in ("-0.0", "-0.00") else s) + "%"


def g(v):
    return f"{v:,.10g}" if v != int(v) else f"{int(v):,}"


def ceil_int(x):
    return int(math.ceil(x - 1e-9))


def price_by_divisor(base, pct_sum):
    divisor = 1 - pct_sum / 100
    if divisor <= 0:
        raise ValueError(T(
            f"The percentages (revenue taxes, variable fees, fixed cost %, margin) add up to {pct(pct_sum)}. "
            "They must stay below 100%. Lower the margin or review the percentages.",
            f"A soma dos percentuais (impostos sobre receita, taxas variáveis, custo fixo % e margem) chegou a "
            f"{pct(pct_sum)}. Precisa ficar abaixo de 100%. Reduza a margem ou revise os percentuais."))
    return base / divisor


def compose(price, parts):
    """Round each part to cents; the last one (profit) absorbs rounding so the sum equals the rounded price."""
    items = [(k, v) for k, v in parts.items() if v is not None]
    out = {k: r2(v) for k, v in items[:-1]}
    out[items[-1][0]] = r2(round(price, 2) - sum(out.values()))
    return out


def scenarios(base, pct_without_margin):
    c = {}
    for m in (10, 15, 20, 25, 30):
        try:
            c[f"{m}%"] = round(price_by_divisor(base, pct_without_margin + m), 2)
        except ValueError:
            c[f"{m}%"] = None
    return c


def charm_price(p):
    """Charm price at or above p: under $10 the next price ending in 9 cents ($1.22 -> $1.29);
    from $10 up the next price ending in .99 ($15.61 -> $15.99)."""
    cents = round(p * 100)
    if cents < 1000:
        c = math.ceil((cents + 1) / 10) * 10 - 1
    else:
        c = math.ceil((cents + 1) / 100) * 100 - 1
    return round(c / 100, 2)


def round_up(p, step=5):
    """Next round price (services): multiple of `step` at or above p."""
    return float(math.ceil(round(p, 2) / step - 1e-9) * step)


def setaside(profit, rate):
    """Split a (rounded) pre-tax profit into tax set-aside + after-tax profit, summing exactly."""
    if rate is None:
        return None
    base = max(profit, 0.0)
    s = r2(base * rate / 100)
    return {"rate_pct": rate, "set_aside": s, "after_tax": r2(round(profit, 2) - s)}


def sales_tax_info(price, rate):
    if not rate:
        return None
    p = round(price, 2)
    t = r2(p * rate / 100)
    return {"rate_pct": rate, "price": p, "sales_tax": t, "customer_pays": r2(p + t)}


def net_of_sales_tax(p, a):
    """If current prices already include sales tax, the business keeps only p / (1 + rate)."""
    if getattr(a, "price_includes_sales_tax", False) and a.sales_tax:
        return p / (1 + a.sales_tax / 100)
    return p


def common_checks(a, notes, warnings):
    for name, val in (("--margin", a.margin), ("--tax-setaside", a.tax_setaside), ("--sales-tax", a.sales_tax)):
        if val is not None and val > 100:
            raise ValueError(T(f"{name} must be at most 100%.", f"{name} precisa ser no máximo 100%."))
    if a.sales_tax and a.sales_tax > 15:
        warnings.append(T(f"Sales tax of {pct(a.sales_tax)} is unusually high (combined US rates are usually 0–11%). "
                          "Check the rate for your city/county.",
                          f"Sales tax de {pct(a.sales_tax)} é alto demais (nos EUA a taxa combinada costuma ficar entre "
                          "0 e 11%). Confira a taxa da sua cidade/condado."))
    if a.sales_tax:
        notes.append(T("Sales tax is added on top of the price and passed to the state; it is not your revenue. "
                       "On Amazon, Etsy, eBay, DoorDash, Uber Eats and Grubhub, marketplace-facilitator laws in most "
                       "states make the platform collect and remit it: do not add it again on those orders.",
                       "O sales tax é somado por cima do preço e repassado ao estado; não é receita sua. Na Amazon, "
                       "Etsy, eBay, DoorDash, Uber Eats e Grubhub, as leis de marketplace facilitator da maioria dos "
                       "estados fazem a plataforma cobrar e recolher: não some de novo nesses pedidos."))
    if getattr(a, "price_includes_sales_tax", False) and not a.sales_tax:
        warnings.append(T("--price-includes-sales-tax has no effect without --sales-tax.",
                          "--price-includes-sales-tax não tem efeito sem --sales-tax."))
    if a.tax_setaside is None:
        notes.append(T("The margin is PRE-TAX profit. Income tax + self-employment tax are paid on profit: pass "
                       "--tax-setaside (a rough planning range for sole props/single-member LLCs is 25–35% for federal "
                       "+ state + SE tax; estimate only, confirm with your CPA).",
                       "A margem é lucro ANTES do imposto de renda. Income tax + self-employment tax incidem sobre o "
                       "lucro: use --tax-setaside (faixa de planejamento para sole prop/LLC de um sócio: 25–35% somando "
                       "federal + estadual + SE tax; é estimativa, confirme com seu CPA)."))


# ---------------------------------------------------------------- product
def calc_product(a):
    warnings, notes = [], []
    common_checks(a, notes, warnings)
    pct_costs = a.revenue_taxes + a.variable_pct
    if a.fixed_cost_pct is not None:
        fixed_unit = 0.0
        total_pct = pct_costs + a.fixed_cost_pct + a.margin
        method = T("fixed costs as % of revenue", "custo fixo como % do faturamento")
        if a.volume:
            warnings.append(T("You passed --fixed-cost-pct and --volume: the fixed cost % was used for the price; "
                              "volume is used only for the monthly profit.",
                              "Você informou --fixed-cost-pct e --volume: prevaleceu o custo fixo em %; "
                              "o volume foi usado só para o lucro do mês."))
    elif a.volume:
        fixed_unit = a.fixed_costs / a.volume
        total_pct = pct_costs + a.margin
        method = T("fixed costs spread per unit", "custo fixo rateado por unidade")
        notes.append(T("Spreading fixed costs per unit only works for a single-product business: --volume must be the "
                       "TOTAL units the business sells per month. For a menu or catalog use --fixed-cost-pct or menu mode.",
                       "Rateio por unidade só vale para negócio de 1 produto principal: --volume precisa ser o volume "
                       "TOTAL do negócio no mês. Para cardápio ou catálogo, use --fixed-cost-pct ou o modo menu."))
    else:
        raise ValueError(T("Pass --volume (units per month, single-product business) or --fixed-cost-pct "
                           "(menu/catalog; use --fixed-cost-pct 0 if you have no fixed costs).",
                           "Informe --volume (unidades por mês, negócio de 1 produto) ou --fixed-cost-pct "
                           "(cardápio/catálogo; use --fixed-cost-pct 0 se não houver custo fixo)."))
    base = a.direct_cost + fixed_unit + a.fee_per_sale
    if base <= 0:
        raise ValueError(T("Direct cost, fixed cost per unit and fee per sale add up to zero: there is no base for a "
                           "price. Pass --direct-cost (cost per unit) and/or fixed costs.",
                           "Custo direto, custo fixo por unidade e taxa fixa por venda somam zero: não há base para o "
                           "preço. Informe --direct-cost (custo por unidade) e/ou o custo fixo."))
    price = price_by_divisor(base, total_pct)
    fixed_v = fixed_unit if a.fixed_cost_pct is None else price * a.fixed_cost_pct / 100
    cm_unit = price - a.direct_cost - a.fee_per_sale - price * pct_costs / 100

    comp = compose(price, {
        "direct_cost": a.direct_cost,
        "fixed_cost_per_unit": fixed_v,
        "revenue_taxes": price * a.revenue_taxes / 100 if a.revenue_taxes else None,
        "variable_fees": price * a.variable_pct / 100,
        "fee_per_sale": a.fee_per_sale if a.fee_per_sale else None,
        "pre_tax_profit": price * a.margin / 100,
    })
    r = {
        "mode": "product",
        "method": method,
        "suggested_price": round(price, 2),
        "charm_price": charm_price(price),
        "markup_on_direct_cost": round(price / a.direct_cost, 3) if a.direct_cost else None,
        "composition": comp,
        "contribution_margin_per_unit": r2(cm_unit),
        "contribution_margin_pct": round(cm_unit / price * 100, 1) + 0.0,
    }
    tx = setaside(comp["pre_tax_profit"], a.tax_setaside)
    if tx:
        r["tax_setaside_per_unit"] = tx
    st = sales_tax_info(price, a.sales_tax)
    if st:
        r["sales_tax_on_suggested"] = st
    if a.fixed_cost_pct is None and a.fixed_costs and cm_unit > 0:
        r["break_even_units_month"] = ceil_int(a.fixed_costs / cm_unit)
        r["break_even_revenue_month"] = round(r["break_even_units_month"] * price, 2)
    elif a.fixed_cost_pct is not None:
        notes.append(T("With fixed costs as %, there is no per-item break-even: use the business break-even "
                       "(business or menu mode) = fixed costs / weighted contribution margin %.",
                       "Com custo fixo em %, não há ponto de equilíbrio por item: calcule o da empresa "
                       "(modo business ou menu) = custo fixo ÷ margem de contribuição % média."))
    r["margin_scenarios"] = scenarios(base, total_pct - a.margin)
    if a.current_price:
        shelf = a.current_price
        p = net_of_sales_tax(shelf, a)
        fixed_at = p * a.fixed_cost_pct / 100 if a.fixed_cost_pct is not None else fixed_unit
        cm_cur = p - a.direct_cost - a.fee_per_sale - p * pct_costs / 100
        profit_cur = cm_cur - fixed_at
        cp = {
            "price": shelf,
            "net_price_excl_sales_tax": r2(p) if p != shelf else None,
            "profit_per_unit": r2(profit_cur),
            "net_margin_pct": round(profit_cur / p * 100, 1) + 0.0,
            "contribution_margin_per_unit": r2(cm_cur),
        }
        if cp["net_price_excl_sales_tax"] is None:
            del cp["net_price_excl_sales_tax"]
        if a.fixed_cost_pct is None and a.fixed_costs:
            if cm_cur > 0:
                cp["break_even_units_month"] = ceil_int(a.fixed_costs / cm_cur)
                cp["break_even_revenue_month"] = round(cp["break_even_units_month"] * p, 2)
            else:
                cp["break_even_units_month"] = None
                warnings.append(T("At the current price each unit does not even cover direct cost + fees: no volume "
                                  "can pay the fixed costs.",
                                  "No preço atual cada unidade não cobre nem o custo direto + taxas: não existe volume "
                                  "que pague o custo fixo."))
        if a.volume:
            cp["volume"] = a.volume
            cp["profit_month"] = r2(profit_cur * a.volume)
            t2 = setaside(cp["profit_month"], a.tax_setaside)
            if t2:
                cp["tax_setaside_month"] = t2
        r["current_price"] = cp
    r["warnings"], r["notes"] = warnings, notes
    return r


# ---------------------------------------------------------------- business
def calc_business(a):
    warnings, notes = [], []
    if a.avg_cm_pct <= 0 or a.avg_cm_pct >= 100:
        raise ValueError(T("--avg-cm-pct must be between 0 and 100 (weighted contribution margin as % of revenue).",
                           "--avg-cm-pct precisa ficar entre 0 e 100 (margem de contribuição média em % do faturamento)."))
    if a.tax_setaside is not None and a.tax_setaside > 100:
        raise ValueError(T("--tax-setaside must be at most 100%.", "--tax-setaside precisa ser no máximo 100%."))
    be = a.fixed_costs / (a.avg_cm_pct / 100)
    r = {"mode": "business", "fixed_costs_month": r2(a.fixed_costs), "avg_cm_pct": a.avg_cm_pct,
         "break_even_revenue_month": r2(be)}
    if a.monthly_revenue:
        f = a.monthly_revenue
        r["monthly_revenue"] = r2(f)
        r["pre_tax_profit_month"] = r2(f * a.avg_cm_pct / 100 - a.fixed_costs)
        r["safety_margin_pct"] = round((f - be) / f * 100, 1) + 0.0
        tx = setaside(r["pre_tax_profit_month"], a.tax_setaside)
        if tx:
            r["tax_setaside_month"] = tx
    notes.append(T("Use revenue WITHOUT sales tax collected (sales tax belongs to the state).",
                   "Use o faturamento SEM o sales tax cobrado (o sales tax é do estado)."))
    r["warnings"], r["notes"] = warnings, notes
    return r


# ---------------------------------------------------------------- menu
_HEADERS = {
    "name": {"name", "item", "product", "nome", "produto", "descricao", "description"},
    "direct_cost": {"direct_cost", "cost", "unit_cost", "custo_direto", "custo", "custo_unitario"},
    "current_price": {"current_price", "price", "preco_atual", "preco", "preco_venda"},
    "volume": {"volume", "monthly_volume", "units", "units_month", "volume_mensal", "qtd", "quantidade"},
}
_ORDER = ["name", "direct_cost", "current_price", "volume"]


def _norm(h):
    h = unicodedata.normalize("NFKD", h).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"[\s\-/]+", "_", h)


def _is_num(x):
    try:
        number(x)
        return True
    except ValueError:
        return False


def read_menu(path):
    fmt = T("Format: name,direct_cost,current_price,volume (or ; separated)",
            "Formato: nome;custo_direto;preco_atual;volume_mensal (ou separado por vírgula)")
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            text = fh.read()
    except OSError as e:
        raise ValueError(T(f"Could not open {path}: {e.strerror}", f"Não consegui abrir {path}: {e.strerror}"))
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        raise ValueError(T(f"The file {path} is empty.", f"O arquivo {path} está vazio."))
    sep = ";" if ";" in lines[0] else ("\t" if "\t" in lines[0] else ",")
    rows = list(csv.reader(lines, delimiter=sep))
    first = [c.strip() for c in rows[0]]
    cols = _ORDER
    start = 0
    normed = [_norm(c) for c in first]
    known = {k: i for i, h in enumerate(normed) for k, names in _HEADERS.items() if h in names}
    if known or (len(first) > 1 and not _is_num(first[1])):
        start = 1
        if "name" in known and "direct_cost" in known:
            cols = [None] * len(first)
            for k, i in known.items():
                cols[i] = k
        elif known:
            raise ValueError(T(f"{path}: the header needs at least a name and a direct_cost column. {fmt}",
                               f"{path}: o cabeçalho precisa de pelo menos as colunas nome e custo_direto. {fmt}"))
    items = []
    for n, fields in enumerate(rows[start:], start=start + 1):
        fields = [c.strip() for c in fields]
        extra = [c for c in fields[len(cols):] if c]
        try:
            if extra:
                raise ValueError(T("more columns than expected (with comma-separated files, write decimals as 3.30 "
                                   "or quote them, or use ; as separator)",
                                   "mais colunas que o esperado (em arquivo separado por vírgula, escreva decimais "
                                   "como 3.30 ou entre aspas, ou use ; como separador)"))
            rec = {k: "" for k in _ORDER}
            for i, k in enumerate(cols):
                if k and i < len(fields):
                    rec[k] = fields[i]
            if not rec["name"] or not rec["direct_cost"]:
                raise ValueError(T("missing name or direct_cost", "faltou nome ou custo_direto"))
            items.append({
                "name": rec["name"],
                "direct_cost": number(rec["direct_cost"]),
                "current_price": number(rec["current_price"]) if rec["current_price"] else None,
                "volume": number(rec["volume"]) if rec["volume"] else None,
            })
        except ValueError as e:
            raise ValueError(T(f"{path}, line {n}: {e}. {fmt}", f"{path}, linha {n}: {e}. {fmt}"))
    if not items:
        raise ValueError(T(f"No items found in {path}.", f"Nenhum item encontrado em {path}."))
    return items


def calc_menu(a):
    warnings, notes = [], []
    common_checks(a, notes, warnings)
    items = read_menu(a.file)
    pct_costs = a.revenue_taxes + a.variable_pct
    all_vol = all(i["current_price"] and i["volume"] for i in items)
    cur_rev = sum(net_of_sales_tax(i["current_price"], a) * i["volume"] for i in items) if all_vol else None
    cfp = a.fixed_cost_pct
    if cfp is None:
        if not (a.fixed_costs and cur_rev):
            raise ValueError(T("Pass --fixed-cost-pct, or --fixed-costs with current price and volume for every item "
                               "(then the % is computed on current revenue).",
                               "Informe --fixed-cost-pct, ou --fixed-costs com preço atual e volume de todos os itens "
                               "(aí o % é calculado sobre o faturamento atual)."))
        cfp = a.fixed_costs / cur_rev * 100
        notes.append(T(f"Fixed cost % computed: {usd(a.fixed_costs)} / current revenue {usd(cur_rev)} = {pct(cfp)}.",
                       f"Custo fixo em % calculado: {usd(a.fixed_costs)} ÷ faturamento atual {usd(cur_rev)} = {pct(cfp)}."))
    total_pct = pct_costs + cfp + a.margin
    if a.fee_per_sale:
        notes.append(T("--fee-per-sale is applied per item here; for a per-order fee use the average per item.",
                       "--fee-per-sale entra por item aqui; se a taxa é por pedido, use a média por item."))
    rows, cm_tot, rev_tot, cm_pcts = [], 0.0, 0.0, []
    for i in items:
        cd, shelf, v = i["direct_cost"], i["current_price"], i["volume"]
        base = cd + a.fee_per_sale
        if base <= 0:
            raise ValueError(T(f"Item '{i['name']}': direct cost is zero; enter the cost per unit.",
                               f"Item '{i['name']}': custo direto zero; informe o custo por unidade."))
        sug = price_by_divisor(base, total_pct)
        l = {"item": i["name"], "direct_cost": r2(cd), "suggested_price": round(sug, 2), "charm_price": charm_price(sug),
             "current_price": shelf}
        if shelf:
            p = net_of_sales_tax(shelf, a)
            cm = p - cd - a.fee_per_sale - p * pct_costs / 100
            profit = cm - p * cfp / 100
            l.update(contribution_margin_per_unit=r2(cm), contribution_margin_pct=round(cm / p * 100, 1) + 0.0,
                     profit_per_unit=r2(profit), net_margin_pct=round(profit / p * 100, 1) + 0.0,
                     price_change_pct=round((sug / p - 1) * 100, 1) + 0.0,
                     status="profit" if round(profit, 2) >= 0 else "loss")
            cm_pcts.append(cm / p * 100)
            if v:
                l.update(volume=v, profit_month=r2(profit * v))
                cm_tot += cm * v
                rev_tot += p * v
        rows.append(l)
    r = {"mode": "menu", "fixed_cost_pct": round(cfp, 2), "items": rows}
    avg = None
    if all_vol and rev_tot > 0:
        avg = cm_tot / rev_tot * 100
        r["avg_cm_pct"] = round(avg, 1)
        r["avg_cm_type"] = "weighted"
        r["current_revenue_month"] = r2(rev_tot)
        if a.fixed_costs:
            r["pre_tax_profit_month"] = r2(cm_tot - a.fixed_costs)
            tx = setaside(r["pre_tax_profit_month"], a.tax_setaside)
            if tx:
                r["tax_setaside_month"] = tx
    elif cm_pcts:
        avg = sum(cm_pcts) / len(cm_pcts)
        r["avg_cm_pct"] = round(avg, 1)
        r["avg_cm_type"] = "simple"
        notes.append(T("Without volume for every item the average contribution margin is a simple average; with "
                       "volumes it is weighted by revenue and more accurate.",
                       "Sem volume de todos os itens, a margem de contribuição média é simples; com volumes, fica "
                       "ponderada pelo faturamento e mais fiel."))
    if a.fixed_costs and avg is not None:
        if avg > 0:
            r["break_even_revenue_month"] = r2(a.fixed_costs / (avg / 100))
        else:
            warnings.append(T("Average contribution margin is zero or negative: the business loses money on every sale.",
                              "Margem de contribuição média negativa ou zero: a empresa perde dinheiro em cada venda."))
    elif not a.fixed_costs:
        notes.append(T("Pass --fixed-costs to see the business break-even.",
                       "Informe --fixed-costs para ver o ponto de equilíbrio da empresa."))
    losers = [l["item"] for l in rows if l.get("status") == "loss"]
    if losers:
        warnings.append(T(f"Items losing money at the current price: {', '.join(losers)}.",
                          f"Itens no prejuízo no preço atual: {', '.join(losers)}."))
    if a.output:
        save_csv(a.output, rows)
        r["output_file"] = a.output
    r["warnings"], r["notes"] = warnings, notes
    return r


def save_csv(path, rows):
    cols = ["item", "direct_cost", "current_price", "volume", "suggested_price", "charm_price", "price_change_pct",
            "contribution_margin_per_unit", "contribution_margin_pct", "profit_per_unit", "net_margin_pct",
            "profit_month", "status"]
    head = cols if LANG == "en" else ["item", "custo_direto", "preco_atual", "volume_mensal", "preco_sugerido",
                                      "preco_psicologico", "reajuste_pct", "margem_contribuicao_unitaria",
                                      "margem_contribuicao_pct", "lucro_unitario", "margem_liquida_pct", "lucro_mes",
                                      "status"]
    status = {"profit": T("profit", "lucro"), "loss": T("loss", "prejuízo")}
    try:
        with open(path, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(head)
            for l in rows:
                out = []
                for c in cols:
                    v = l.get(c, "")
                    if c == "status":
                        v = status.get(v, "")
                    elif c == "volume" and isinstance(v, float):
                        v = f"{v:g}"
                    elif isinstance(v, float):
                        v = f"{v:.1f}" if c.endswith("_pct") else f"{v:.2f}"
                    out.append(v)
                w.writerow(out)
    except OSError as e:
        raise ValueError(T(f"Could not write {path}: {e.strerror}", f"Não consegui gravar {path}: {e.strerror}"))


# ---------------------------------------------------------------- service
def calc_service(a):
    warnings, notes = [], []
    common_checks(a, notes, warnings)
    if not a.billable_hours:
        raise ValueError(T("Pass --billable-hours (billable hours per month; usually 60–70% of hours worked).",
                           "Informe --billable-hours (horas faturáveis por mês; em geral 60–70% das horas trabalhadas)."))
    if a.installment_fee >= 100 or a.upfront_discount > 100 or a.recurring_discount > 100 or a.deposit_pct > 100:
        raise ValueError(T("Discounts and deposit must be at most 100% and --installment-fee below 100%.",
                           "Descontos e sinal precisam ser no máximo 100% e --installment-fee abaixo de 100%."))
    if a.installments < 1 or a.installments != int(a.installments):
        raise ValueError(T("--installments must be a whole number of 1 or more.",
                           "--installments precisa ser um número inteiro de 1 ou mais."))
    overhead_month = a.fixed_costs + a.owner_pay
    overhead_hour = overhead_month / a.billable_hours
    labor_hour = a.labor_rate * (1 + a.payroll_burden / 100)
    cost_hour = overhead_hour + labor_hour
    if cost_hour <= 0:
        warnings.append(T("Fixed costs, owner's pay and labor add up to zero: the hourly price comes out $0.00. "
                          "Pass --fixed-costs and --owner-pay for a real price.",
                          "Custo fixo, pró-labore e mão de obra somam zero: o preço da hora sai $0.00. "
                          "Informe --fixed-costs e --owner-pay para um preço real."))
    pct_costs = a.revenue_taxes + a.variable_pct
    total_pct = pct_costs + a.margin
    price_hour = price_by_divisor(cost_hour, total_pct)
    comp = compose(price_hour, {
        "overhead": overhead_hour,
        "labor": labor_hour if labor_hour else None,
        "revenue_taxes": price_hour * a.revenue_taxes / 100 if a.revenue_taxes else None,
        "variable_fees": price_hour * a.variable_pct / 100,
        "pre_tax_profit": price_hour * a.margin / 100,
    })
    r = {
        "mode": "service",
        "cost_per_hour": round(cost_hour, 2),
        "suggested_hourly_price": round(price_hour, 2),
        "rounded_hourly_price": round_up(price_hour),
        "composition_per_hour": comp,
        "target_revenue_month": round(price_hour * a.billable_hours, 2),
        "pre_tax_profit_month": r2(price_hour * a.margin / 100 * a.billable_hours),
        "margin_scenarios": scenarios(cost_hour, pct_costs),
    }
    if a.tax_setaside is not None:
        taxable = r["pre_tax_profit_month"] + a.owner_pay
        s = r2(max(taxable, 0) * a.tax_setaside / 100)
        r["tax_setaside_month"] = {"rate_pct": a.tax_setaside, "taxable_base": r2(taxable), "set_aside": s}
        if a.owner_pay:
            notes.append(T("Tax set-aside is on owner's pay + profit: for a sole prop or single-member LLC the owner's "
                           "draw is not a deductible expense. If you are an S-corp paying yourself W-2 wages, payroll "
                           "withholding covers the salary and you set aside only on the profit.",
                           "A reserva de impostos é sobre pró-labore + lucro: em sole prop ou LLC de um sócio, a "
                           "retirada do dono não é despesa dedutível. Se você é S-corp e se paga salário W-2, a "
                           "retenção na folha cobre o salário e a reserva fica só sobre o lucro."))
    st = sales_tax_info(price_hour, a.sales_tax)
    if st:
        r["sales_tax_on_hourly"] = st
    if a.fee_per_sale and not a.project_hours:
        notes.append(T("--fee-per-sale is a per-payment fee: it enters the project price (use --project-hours), "
                       "not the hourly rate.",
                       "--fee-per-sale é por pagamento: entra no preço do projeto (use --project-hours), não na hora."))
    if a.current_price:
        p = a.current_price
        cm_hour = p * (1 - pct_costs / 100) - labor_hour
        profit_hour = cm_hour - overhead_hour
        cp = {"hourly_price": p, "profit_per_hour": r2(profit_hour),
              "net_margin_pct": round(profit_hour / p * 100, 1) + 0.0,
              "profit_month": r2(profit_hour * a.billable_hours)}
        if cm_hour > 0:
            cp["break_even_hours_month"] = ceil_int(overhead_month / cm_hour)
            if cp["break_even_hours_month"] > a.billable_hours:
                warnings.append(T(f"At the current price you must bill {cp['break_even_hours_month']} h/month to break "
                                  f"even, more than your {g(a.billable_hours)} billable hours.",
                                  f"No preço atual você precisa faturar {cp['break_even_hours_month']} h/mês para "
                                  f"empatar, mais que as {g(a.billable_hours)} h faturáveis disponíveis."))
        else:
            cp["break_even_hours_month"] = None
        r["current_price"] = cp
    if a.project_hours:
        base = cost_hour * a.project_hours + a.direct_cost + a.fee_per_sale
        price = price_by_divisor(base, total_pct)
        keep = 1 - pct_costs / 100
        upfront = price * (1 - a.upfront_discount / 100)
        profit_upfront = upfront * keep - base
        n = int(a.installments)
        inst_total = price / (1 - a.installment_fee / 100)
        each = round(inst_total / n, 2)
        pj = {
            "hours": a.project_hours,
            "direct_costs": r2(a.direct_cost),
            "suggested_price": round(price, 2),
            "rounded_price": round_up(price),
            "composition": compose(price, {
                "labor_and_overhead": cost_hour * a.project_hours,
                "direct_costs": a.direct_cost if a.direct_cost else None,
                "fee_per_sale": a.fee_per_sale if a.fee_per_sale else None,
                "revenue_taxes": price * a.revenue_taxes / 100 if a.revenue_taxes else None,
                "variable_fees": price * a.variable_pct / 100,
                "pre_tax_profit": price * a.margin / 100,
            }),
        }
        if a.upfront_discount:
            pj.update(upfront_discount_pct=a.upfront_discount, upfront_price=round(upfront, 2),
                      upfront_profit=r2(profit_upfront))
            if profit_upfront < 0:
                warnings.append(T(f"The {pct(a.upfront_discount)} upfront discount puts the project at a loss "
                                  f"({usd(profit_upfront)}). Keep the discount below your margin.",
                                  f"O desconto à vista de {pct(a.upfront_discount)} deixa o projeto no prejuízo "
                                  f"({usd(profit_upfront)}). Mantenha o desconto abaixo da margem."))
        if a.deposit_pct:
            dep = r2(round(price, 2) * a.deposit_pct / 100)
            pj.update(deposit_pct=a.deposit_pct, deposit=dep, balance=r2(round(price, 2) - dep))
        if n > 1 or a.installment_fee:
            pj.update(installment_fee_pct=a.installment_fee, installments=n, installments_total=round(inst_total, 2),
                      installment_amount=each, last_installment=r2(round(inst_total, 2) - each * (n - 1)))
        if a.sqft:
            pj["sqft"] = a.sqft
            pj["price_per_sqft"] = round(price / a.sqft, 3)
        st = sales_tax_info(price, a.sales_tax)
        if st:
            pj["sales_tax"] = st
        if a.visits_per_month:
            rec = price * (1 - a.recurring_discount / 100)
            rec_profit = rec * keep - base
            pj["recurring"] = {"visits_per_month": a.visits_per_month, "discount_pct": a.recurring_discount,
                               "price_per_visit": round(rec, 2), "profit_per_visit": r2(rec_profit),
                               "revenue_month": r2(round(rec, 2) * a.visits_per_month),
                               "profit_month": r2(rec_profit * a.visits_per_month)}
            if rec_profit < 0:
                warnings.append(T(f"The {pct(a.recurring_discount)} recurring discount makes each visit lose money "
                                  f"({usd(rec_profit)}). Lower the discount or the hours per recurring visit.",
                                  f"O desconto recorrente de {pct(a.recurring_discount)} faz cada visita dar prejuízo "
                                  f"({usd(rec_profit)}). Reduza o desconto ou as horas por visita recorrente."))
        r["project"] = pj
    else:
        if a.direct_cost:
            notes.append(T("--direct-cost in service mode only enters the project price (use with --project-hours).",
                           "--direct-cost no serviço só entra no preço do projeto (use com --project-hours)."))
        if a.sqft or a.visits_per_month or a.deposit_pct:
            notes.append(T("--sqft, --visits-per-month and --deposit-pct need --project-hours (hours per job/visit).",
                           "--sqft, --visits-per-month e --deposit-pct precisam de --project-hours (horas por serviço/visita)."))
    r["warnings"], r["notes"] = warnings, notes
    return r


# ---------------------------------------------------------------- job (contractor estimate)
def parse_schedule(txt):
    parts = [p for p in re.split(r"[/;|\s]+|,(?=\s*\d)", str(txt).strip()) if p]
    try:
        vals = [number(p, percent=True) for p in parts]
    except ValueError:
        vals = []
    if not vals or abs(sum(vals) - 100) > 0.01 or any(v <= 0 for v in vals):
        raise ValueError(T(f"--schedule must be percentages that add up to 100 (e.g. 33/33/34); got '{txt}'.",
                           f"--schedule precisa ser percentuais que somam 100 (ex.: 33/33/34); recebi '{txt}'."))
    return vals


def calc_job(a):
    warnings, notes = [], []
    for name, val in (("--margin", a.margin), ("--tax-setaside", a.tax_setaside)):
        if val is not None and val > 100:
            raise ValueError(T(f"{name} must be at most 100%.", f"{name} precisa ser no máximo 100%."))
    labor = a.labor_cost + a.crew_hours * a.labor_rate * (1 + a.payroll_burden / 100)
    lines = {"materials": a.materials, "labor": labor, "subcontractors": a.subcontractors,
             "equipment_rental": a.equipment, "permits": a.permits, "dumpster_disposal": a.dumpster,
             "other_direct": a.other_costs}
    direct = sum(lines.values())
    if direct <= 0:
        raise ValueError(T("Job direct costs add up to zero: pass --materials, --crew-hours with --labor-rate, "
                           "--subcontractors etc.",
                           "Os custos diretos da obra somam zero: informe --materials, --crew-hours com --labor-rate, "
                           "--subcontractors etc."))
    contingency = direct * a.contingency / 100
    cost = direct + contingency
    use_markup = a.overhead_markup is not None or a.profit_markup is not None
    if use_markup and (a.overhead_pct is not None or a.margin is not None):
        raise ValueError(T("Use either the markup pair (--overhead-markup/--profit-markup, % on cost) or the margin pair "
                           "(--overhead-pct/--margin, % of price), not both.",
                           "Use o par de markup (--overhead-markup/--profit-markup, % sobre o custo) ou o de margem "
                           "(--overhead-pct/--margin, % do preço), não os dois."))
    if use_markup:
        om, pm = a.overhead_markup or 0.0, a.profit_markup or 0.0
        overhead = cost * om / 100
        profit_before_fees = (cost + overhead) * pm / 100
        sub = cost + overhead + profit_before_fees + a.fee_per_sale
        price = price_by_divisor(sub, a.variable_pct)
        method = "markup"
        profit = profit_before_fees
    else:
        if a.margin is None:
            raise ValueError(T("Pass --margin (profit % of price) with --overhead-pct, or --overhead-markup and "
                               "--profit-markup (the classic 10 and 10).",
                               "Informe --margin (lucro % do preço) com --overhead-pct, ou --overhead-markup e "
                               "--profit-markup (o clássico 10 e 10)."))
        op = a.overhead_pct or 0.0
        price = price_by_divisor(cost + a.fee_per_sale, op + a.margin + a.variable_pct)
        overhead = price * op / 100
        profit = price * a.margin / 100
        method = "margin"
    fees = price * a.variable_pct / 100
    parts = {k: (v if v else None) for k, v in lines.items()}
    parts.update(contingency=contingency or None, overhead=overhead or None, variable_fees=fees or None,
                 fee_per_sale=a.fee_per_sale or None, pre_tax_profit=profit)
    comp = compose(price, parts)
    r = {"mode": "job", "method": method, "direct_costs": r2(direct), "cost_with_contingency": r2(cost),
         "suggested_price": round(price, 2), "rounded_price": round_up(price, 10 if price < 10000 else 50),
         "composition": comp,
         "markup_on_cost_pct": round((price / cost - 1) * 100, 1) + 0.0,
         "gross_margin_pct": round((price - cost) / price * 100, 1) + 0.0,
         "net_margin_pct": round(comp["pre_tax_profit"] / round(price, 2) * 100, 1) + 0.0}
    if use_markup:
        p2 = round(price, 2)
        op_share = round((comp.get("overhead", 0) + comp["pre_tax_profit"]) / p2 * 100, 1) + 0.0
        fee_share = round((comp.get("variable_fees", 0) + comp.get("fee_per_sale", 0)) / p2 * 100, 1) + 0.0
        r["overhead_profit_share_pct"], r["fees_share_pct"] = op_share, fee_share
        fee_en = f"; card/payment fees take another {pct(fee_share)}" if fee_share else ""
        fee_pt = f"; as taxas de cartão/pagamento levam outros {pct(fee_share)}" if fee_share else ""
        notes.append(T(f"Markup is not margin: {pct(a.overhead_markup or 0)} overhead + {pct(a.profit_markup or 0)} "
                       f"profit on cost = {pct(r['markup_on_cost_pct'])} total markup, but only "
                       f"{pct(op_share)} of the price is overhead + profit (net margin "
                       f"{pct(r['net_margin_pct'])}){fee_en}.",
                       f"Markup não é margem: {pct(a.overhead_markup or 0)} de overhead + {pct(a.profit_markup or 0)} "
                       f"de lucro sobre o custo = markup total de {pct(r['markup_on_cost_pct'])}, mas só "
                       f"{pct(op_share)} do preço é overhead + lucro (margem líquida "
                       f"{pct(r['net_margin_pct'])}){fee_pt}."))
    if a.labor_rate and not a.payroll_burden:
        notes.append(T("--labor-rate has no --payroll-burden: for W-2 crews add employer payroll costs (FICA 7.65% + "
                       "FUTA/SUTA + workers' comp; often 15–35% in construction, estimate).",
                       "--labor-rate sem --payroll-burden: para equipe W-2 some os encargos do empregador (FICA 7,65% + "
                       "FUTA/SUTA + workers' comp; em construção costuma dar 15–35%, estimativa)."))
    tx = setaside(comp["pre_tax_profit"], a.tax_setaside)
    if tx:
        r["tax_setaside"] = tx
    if a.change_order_cost:
        factor = price / (cost + a.fee_per_sale)
        r["change_order"] = {"cost": r2(a.change_order_cost), "price": round(a.change_order_cost * factor, 2),
                             "factor": round(factor, 4)}
        notes.append(T("Change orders are priced with the same markup as the job; get them signed (scope, price, "
                       "schedule impact) before doing the work.",
                       "Change orders usam o mesmo markup da obra; colha a assinatura (escopo, preço, impacto no prazo) "
                       "antes de executar."))
    if a.schedule:
        vals = parse_schedule(a.schedule)
        total = r["rounded_price"]          # the schedule follows the quoted (rounded) price
        r["schedule_base"] = total
        amts = [r2(total * v / 100) for v in vals[:-1]]
        amts.append(r2(total - sum(amts)))
        r["payment_schedule"] = [{"pct": v, "amount": m} for v, m in zip(vals, amts)]
        if vals[0] > 100 / 3 + 0.01:
            warnings.append(T(f"The first payment is {pct(vals[0])}. Several states cap home-improvement deposits "
                              "(e.g. Massachusetts HIC law: generally up to 1/3 of the price unless special-order "
                              "materials; California: 10% or $1,000, whichever is less). Verify your state's rule.",
                              f"A primeira parcela é {pct(vals[0])}. Vários estados limitam o sinal de reforma "
                              "residencial (ex.: Massachusetts, lei HIC: em geral até 1/3 do preço, salvo material sob "
                              "encomenda; Califórnia: 10% ou $1,000, o que for menor). Confira a regra do seu estado."))
    notes.append(T("Contractors usually pay sales tax on materials when buying them (in many states, e.g. "
                   "Massachusetts, the contractor is the consumer): include it in --materials, don't add it on top.",
                   "Em geral o empreiteiro paga o sales tax do material na compra (em muitos estados, como "
                   "Massachusetts, ele é o consumidor final): inclua em --materials, não some por cima."))
    r["warnings"], r["notes"] = warnings, notes
    return r


# ---------------------------------------------------------------- commission (insurance agents, loan brokers)
def calc_commission(a):
    warnings, notes = [], []
    for name, val in (("--close-rate", a.close_rate), ("--payout-pct", a.payout_pct),
                      ("--chargeback-pct", a.chargeback_pct), ("--tax-setaside", a.tax_setaside)):
        if val is not None and val > 100:
            raise ValueError(T(f"{name} must be at most 100%.", f"{name} precisa ser no máximo 100%."))
    if a.avg_commission is not None:
        gross = a.avg_commission
    elif a.avg_premium and a.first_year_pct is not None:
        gross = a.avg_premium * a.first_year_pct / 100
    else:
        raise ValueError(T("Pass --avg-commission ($ per sale), or --avg-premium with --first-year-pct.",
                           "Informe --avg-commission ($ por venda), ou --avg-premium com --first-year-pct."))
    net = gross * a.payout_pct / 100 * (1 - a.chargeback_pct / 100)
    if a.cost_per_lead and not a.close_rate:
        raise ValueError(T("--cost-per-lead needs --close-rate (% of leads that buy).",
                           "--cost-per-lead precisa de --close-rate (% dos leads que compram)."))
    lead_cost_sale = a.cost_per_lead / (a.close_rate / 100) if a.close_rate else 0.0
    per_sale = net - lead_cost_sale
    need = a.target_income + a.fixed_costs * 12 - a.renewal_income
    r = {"mode": "commission", "gross_commission_per_sale": r2(gross), "net_commission_per_sale": r2(net),
         "lead_cost_per_sale": r2(lead_cost_sale), "contribution_per_sale": r2(per_sale),
         "income_needed_from_new_sales_year": r2(max(need, 0))}
    if need <= 0:
        r["sales_needed_year"] = 0
        notes.append(T("Renewals already cover the target income and expenses.",
                       "As renovações já cobrem a renda-alvo e as despesas."))
    elif per_sale <= 0:
        raise ValueError(T(f"Each sale costs {usd(lead_cost_sale)} in leads but pays {usd(net)} in commission: "
                           "lower the cost per lead, raise the close rate or sell higher-commission products.",
                           f"Cada venda custa {usd(lead_cost_sale)} em leads e paga {usd(net)} de comissão: reduza o "
                           "custo por lead, aumente a taxa de fechamento ou venda produtos de comissão maior."))
    else:
        sales = ceil_int(need / per_sale)
        r["sales_needed_year"] = sales
        r["sales_needed_month"] = ceil_int(sales / 12)
        r["sales_needed_week"] = ceil_int(sales / 52)
        if a.close_rate:
            leads = ceil_int(sales / (a.close_rate / 100))
            r["leads_needed_year"] = leads
            r["leads_needed_month"] = ceil_int(leads / 12)
            r["marketing_budget_year"] = r2(leads * a.cost_per_lead)
            r["marketing_budget_month"] = r2(leads * a.cost_per_lead / 12)
        r["commission_revenue_year"] = r2(sales * net + a.renewal_income)
        if a.renewal_pct and a.avg_premium:
            r["renewal_added_per_year"] = r2(sales * a.avg_premium * a.renewal_pct / 100 * a.payout_pct / 100)
            notes.append(T("Each year of new sales adds renewal commissions to next year's income (if policies stay "
                           "in force).",
                           "Cada ano de vendas novas soma comissões de renovação à renda do ano seguinte (se as apólices "
                           "continuarem ativas)."))
    if a.tax_setaside is not None:
        r["tax_setaside_year"] = {"rate_pct": a.tax_setaside, "taxable_base": r2(a.target_income),
                                  "set_aside": r2(a.target_income * a.tax_setaside / 100)}
    notes.append(T("You don't set the premium or the commission rate: this plans sales, leads and marketing "
                   "budget. Insurance anti-rebating laws in most states forbid giving part of your commission back to "
                   "the client, and charging fees on top of commissions is prohibited or regulated in many states. "
                   "Financial advisors' fee models (AUM %, flat, hourly) follow SEC/state adviser rules; loan "
                   "originator pay follows the CFPB LO compensation rule. Check with your compliance or state "
                   "regulator.",
                   "Você não define o prêmio nem a comissão: aqui o plano é de vendas, leads e verba de marketing. As "
                   "leis anti-rebating da maioria dos estados proíbem devolver parte da comissão ao cliente, e cobrar "
                   "taxa além da comissão é proibido ou regulado em muitos estados. Modelos de honorário de consultor "
                   "financeiro (% AUM, fixo, por hora) seguem as regras da SEC/estaduais; a remuneração de loan "
                   "originator segue a regra de LO compensation do CFPB. Confirme com o compliance ou o regulador."))
    r["warnings"], r["notes"] = warnings, notes
    return r


def show_job(r, L):
    L.append(T(f"Job estimate: {usd(r['suggested_price'])} (round {usd(r['rounded_price'])}; {r['method']} method)",
               f"Orçamento da obra: {usd(r['suggested_price'])} (redondo {usd(r['rounded_price'])}; método {r['method']})"))
    L.append(T(f"Direct costs {usd(r['direct_costs'])}; with contingency {usd(r['cost_with_contingency'])}",
               f"Custos diretos {usd(r['direct_costs'])}; com contingência {usd(r['cost_with_contingency'])}"))
    L.append(T("Breakdown:", "Composição:"))
    for k, v in r["composition"].items():
        L.append(f"  - {L_(k)}: {usd(v)}")
    L.append(T(f"Markup on cost {pct(r['markup_on_cost_pct'])} | gross margin {pct(r['gross_margin_pct'])} | "
               f"net margin {pct(r['net_margin_pct'])} (pre-tax)",
               f"Markup sobre o custo {pct(r['markup_on_cost_pct'])} | margem bruta {pct(r['gross_margin_pct'])} | "
               f"margem líquida {pct(r['net_margin_pct'])} (antes do IR)"))
    if "tax_setaside" in r:
        L.append(tax_line(r["tax_setaside"], ""))
    if "change_order" in r:
        c = r["change_order"]
        L.append(T(f"Change order: cost {usd(c['cost'])} -> price {usd(c['price'])} (x{c['factor']:.4f})",
                   f"Change order: custo {usd(c['cost'])} -> preço {usd(c['price'])} (x{c['factor']:.4f})"))
    if "payment_schedule" in r:
        names = T(["Deposit", "Progress", "Final"], ["Sinal", "Etapa", "Final"])
        L.append(T(f"Payment schedule (on the quoted price {usd(r['schedule_base'])}):",
                   f"Cronograma de pagamento (sobre o preço orçado {usd(r['schedule_base'])}):"))
        n = len(r["payment_schedule"])
        for i, s in enumerate(r["payment_schedule"]):
            nm = names[0] if i == 0 else (names[2] if i == n - 1 else f"{names[1]} {i}")
            L.append(f"  - {nm} ({pct(s['pct'])}): {usd(s['amount'])}")


def show_commission(r, L):
    L.append(T(f"Commission per sale: gross {usd(r['gross_commission_per_sale'])}, net {usd(r['net_commission_per_sale'])}"
               f" (after split/chargebacks); lead cost per sale {usd(r['lead_cost_per_sale'])}",
               f"Comissão por venda: bruta {usd(r['gross_commission_per_sale'])}, líquida {usd(r['net_commission_per_sale'])}"
               f" (após split/estornos); custo de leads por venda {usd(r['lead_cost_per_sale'])}"))
    L.append(T(f"Needed from new sales this year: {usd(r['income_needed_from_new_sales_year'])}",
               f"Necessário de vendas novas no ano: {usd(r['income_needed_from_new_sales_year'])}"))
    if r.get("sales_needed_year"):
        L.append(T(f"Sales needed: {r['sales_needed_year']:,}/year = {r['sales_needed_month']:,}/month = "
                   f"{r['sales_needed_week']:,}/week",
                   f"Vendas necessárias: {r['sales_needed_year']:,}/ano = {r['sales_needed_month']:,}/mês = "
                   f"{r['sales_needed_week']:,}/semana"))
        if "leads_needed_year" in r:
            L.append(T(f"Leads needed: {r['leads_needed_year']:,}/year ({r['leads_needed_month']:,}/month); marketing "
                       f"budget {usd(r['marketing_budget_year'])}/year ({usd(r['marketing_budget_month'])}/month)",
                       f"Leads necessários: {r['leads_needed_year']:,}/ano ({r['leads_needed_month']:,}/mês); verba de "
                       f"marketing {usd(r['marketing_budget_year'])}/ano ({usd(r['marketing_budget_month'])}/mês)"))
        L.append(T(f"Commission income (new after split + renewals, before marketing and expenses): "
                   f"{usd(r['commission_revenue_year'])}/year",
                   f"Renda de comissões (novas após split + renovações, antes de marketing e despesas): "
                   f"{usd(r['commission_revenue_year'])}/ano"))
        if "renewal_added_per_year" in r:
            L.append(T(f"  Renewals these sales add next year: {usd(r['renewal_added_per_year'])}",
                       f"  Renovações que essas vendas somam no ano seguinte: {usd(r['renewal_added_per_year'])}"))
    if "tax_setaside_year" in r:
        t = r["tax_setaside_year"]
        L.append(T(f"  Set aside for income/SE tax ({pct(t['rate_pct'])} of {usd(t['taxable_base'])}, estimate): "
                   f"{usd(t['set_aside'])}/year",
                   f"  Reservar para income/SE tax ({pct(t['rate_pct'])} de {usd(t['taxable_base'])}, estimativa): "
                   f"{usd(t['set_aside'])}/ano"))


# ---------------------------------------------------------------- text output
LABELS = {
    "direct_cost": ("direct cost", "custo direto"),
    "fixed_cost_per_unit": ("fixed cost per unit", "custo fixo por unidade"),
    "revenue_taxes": ("revenue (gross receipts) taxes", "impostos sobre a receita"),
    "variable_fees": ("variable fees (card, app, marketplace, commission)",
                      "taxas variáveis (cartão, app, marketplace, comissão)"),
    "fee_per_sale": ("fixed fee per sale", "taxa fixa por venda"),
    "pre_tax_profit": ("pre-tax profit", "lucro antes do imposto de renda"),
    "overhead": ("overhead (fixed costs incl. owner's pay)", "overhead/estrutura (custo fixo + pró-labore)"),
    "labor": ("labor (wage + payroll costs)", "mão de obra (salário + encargos)"),
    "labor_and_overhead": ("labor and overhead", "mão de obra e estrutura"),
    "materials": ("materials (incl. sales tax paid)", "material (com sales tax pago)"),
    "subcontractors": ("subcontractors", "subempreiteiros"),
    "equipment_rental": ("equipment rental", "aluguel de equipamento"),
    "permits": ("permits", "licenças (permits)"),
    "dumpster_disposal": ("dumpster / disposal", "caçamba / descarte"),
    "other_direct": ("other direct costs", "outros custos diretos"),
    "contingency": ("contingency", "contingência"),
    "direct_costs": ("direct costs (materials, supplies, travel)", "custos diretos (material, insumos, deslocamento)"),
}


def L_(k):
    return T(*LABELS[k])


def tax_line(tx, per):
    return T(f"  Set aside for income/SE tax ({pct(tx['rate_pct'])}, estimate): {usd(tx['set_aside'])}{per}"
             f" -> after-tax profit {usd(tx['after_tax'])}{per}",
             f"  Reservar para income/SE tax ({pct(tx['rate_pct'])}, estimativa): {usd(tx['set_aside'])}{per}"
             f" -> lucro depois do imposto {usd(tx['after_tax'])}{per}")


def st_line(st, what):
    return T(f"  With sales tax {pct(st['rate_pct'])}: {what} {usd(st['price'])} + {usd(st['sales_tax'])} tax = "
             f"customer pays {usd(st['customer_pays'])} (the tax goes to the state)",
             f"  Com sales tax de {pct(st['rate_pct'])}: {what} {usd(st['price'])} + {usd(st['sales_tax'])} de imposto = "
             f"cliente paga {usd(st['customer_pays'])} (o imposto vai para o estado)")


def show(r):
    L = []
    m = r["mode"]
    if m in ("job", "commission"):
        (show_job if m == "job" else show_commission)(r, L)
        for n in r.get("notes", []):
            L.append(T("Note: ", "Nota: ") + n)
        for w in r.get("warnings", []):
            L.append(T("Warning: ", "Aviso: ") + w)
        print("\n".join(L))
        return
    unit, month = T("/unit", "/un"), T("/month", "/mês")
    if m == "product":
        L.append(T(f"Suggested price: {usd(r['suggested_price'])}  ({r['method']}); charm price {usd(r['charm_price'])}",
                   f"Preço sugerido: {usd(r['suggested_price'])}  ({r['method']}); preço psicológico {usd(r['charm_price'])}"))
        if r.get("markup_on_direct_cost"):
            L.append(T(f"Markup on direct cost: {r['markup_on_direct_cost']:.3f}x",
                       f"Markup sobre o custo direto: {r['markup_on_direct_cost']:.3f}x"))
        L.append(T("Price breakdown:", "Composição do preço:"))
        for k, v in r["composition"].items():
            L.append(f"  - {L_(k)}: {usd(v)}")
        if "tax_setaside_per_unit" in r:
            L.append(tax_line(r["tax_setaside_per_unit"], unit))
        if "sales_tax_on_suggested" in r:
            L.append(st_line(r["sales_tax_on_suggested"], T("price", "preço")))
        L.append(T(f"Contribution margin: {usd(r['contribution_margin_per_unit'])} per unit ({pct(r['contribution_margin_pct'])})",
                   f"Margem de contribuição: {usd(r['contribution_margin_per_unit'])} por unidade ({pct(r['contribution_margin_pct'])})"))
        if "break_even_units_month" in r:
            L.append(T(f"Break-even at the suggested price: {r['break_even_units_month']:,} units/month "
                       f"({usd(r['break_even_revenue_month'])})",
                       f"Ponto de equilíbrio no preço sugerido: {r['break_even_units_month']:,} unidades/mês "
                       f"({usd(r['break_even_revenue_month'])})"))
        if "current_price" in r:
            cp = r["current_price"]
            ok = cp["profit_per_unit"] >= 0
            net = ""
            if "net_price_excl_sales_tax" in cp:
                net = T(f" (tax included; you keep {usd(cp['net_price_excl_sales_tax'])})",
                        f" (imposto incluso; fica com você {usd(cp['net_price_excl_sales_tax'])})")
            L.append(T(f"Current price {usd(cp['price'])}{net}: {'profit' if ok else 'loss'} of "
                       f"{usd(abs(cp['profit_per_unit']))} per unit ({pct(cp['net_margin_pct'])}, pre-tax)",
                       f"Preço atual {usd(cp['price'])}{net}: {'lucro' if ok else 'prejuízo'} de "
                       f"{usd(abs(cp['profit_per_unit']))} por unidade ({pct(cp['net_margin_pct'])}, antes do IR)"))
            if cp.get("break_even_units_month"):
                L.append(T(f"  Break-even at the current price: {cp['break_even_units_month']:,} units/month "
                           f"({usd(cp['break_even_revenue_month'])})",
                           f"  Ponto de equilíbrio no preço atual: {cp['break_even_units_month']:,} unidades/mês "
                           f"({usd(cp['break_even_revenue_month'])})"))
            if "profit_month" in cp:
                ok = cp["profit_month"] >= 0
                L.append(T(f"  {'Profit' if ok else 'Loss'} for the month ({g(cp['volume'])} units, pre-tax): "
                           f"{usd(abs(cp['profit_month']))}",
                           f"  {'Lucro' if ok else 'Prejuízo'} no mês ({g(cp['volume'])} unidades, antes do IR): "
                           f"{usd(abs(cp['profit_month']))}"))
                if "tax_setaside_month" in cp and ok:
                    L.append(tax_line(cp["tax_setaside_month"], month))
    elif m == "business":
        L.append(T(f"Business break-even: {usd(r['break_even_revenue_month'])} of revenue/month "
                   f"(fixed costs {usd(r['fixed_costs_month'])} / contribution margin {pct(r['avg_cm_pct'])})",
                   f"Ponto de equilíbrio da empresa: {usd(r['break_even_revenue_month'])} de faturamento/mês "
                   f"(custo fixo {usd(r['fixed_costs_month'])} ÷ margem de contribuição {pct(r['avg_cm_pct'])})"))
        if "pre_tax_profit_month" in r:
            ok = r["pre_tax_profit_month"] >= 0
            L.append(T(f"Revenue of {usd(r['monthly_revenue'])}: {'profit' if ok else 'loss'} of "
                       f"{usd(abs(r['pre_tax_profit_month']))} for the month, pre-tax (safety margin {pct(r['safety_margin_pct'])})",
                       f"Faturamento de {usd(r['monthly_revenue'])}: {'lucro' if ok else 'prejuízo'} de "
                       f"{usd(abs(r['pre_tax_profit_month']))} no mês, antes do IR (margem de segurança {pct(r['safety_margin_pct'])})"))
            if "tax_setaside_month" in r and ok:
                L.append(tax_line(r["tax_setaside_month"], month))
    elif m == "menu":
        L.append(T(f"Menu with fixed costs at {pct(r['fixed_cost_pct'])} of revenue:",
                   f"Cardápio com custo fixo de {pct(r['fixed_cost_pct'])} do faturamento:"))
        for l in r["items"]:
            s = T(f"  - {l['item']}: cost {usd(l['direct_cost'])} | suggested {usd(l['suggested_price'])} "
                  f"(charm {usd(l['charm_price'])})",
                  f"  - {l['item']}: custo {usd(l['direct_cost'])} | sugerido {usd(l['suggested_price'])} "
                  f"(psicológico {usd(l['charm_price'])})")
            if l.get("current_price"):
                st = T("profit", "lucro") if l["status"] == "profit" else T("loss", "prejuízo")
                s += T(f" | current {usd(l['current_price'])} ({st} {usd(abs(l['profit_per_unit']))}/unit, "
                       f"CM {pct(l['contribution_margin_pct'])})",
                       f" | atual {usd(l['current_price'])} ({st} {usd(abs(l['profit_per_unit']))}/un, "
                       f"MC {pct(l['contribution_margin_pct'])})")
                if "profit_month" in l:
                    s += T(f" | month {usd(l['profit_month'])}", f" | mês {usd(l['profit_month'])}")
            L.append(s)
        if "avg_cm_pct" in r:
            kind = T("weighted by current revenue", "ponderada pelo faturamento atual") if r["avg_cm_type"] == "weighted" \
                else T("simple average, volumes missing", "média simples, sem volume de todos os itens")
            L.append(T(f"Average contribution margin ({kind}): {pct(r['avg_cm_pct'])}",
                       f"Margem de contribuição média ({kind}): {pct(r['avg_cm_pct'])}"))
        if "break_even_revenue_month" in r:
            L.append(T(f"Business break-even: {usd(r['break_even_revenue_month'])} of revenue/month",
                       f"Ponto de equilíbrio da empresa: {usd(r['break_even_revenue_month'])} de faturamento/mês"))
        if "pre_tax_profit_month" in r:
            ok = r["pre_tax_profit_month"] >= 0
            L.append(T(f"{'Profit' if ok else 'Loss'} for the month (total contribution margin - fixed costs, pre-tax), "
                       f"revenue {usd(r['current_revenue_month'])}: {usd(abs(r['pre_tax_profit_month']))}",
                       f"{'Lucro' if ok else 'Prejuízo'} do mês (margem de contribuição total − custo fixo, antes do IR), "
                       f"faturamento {usd(r['current_revenue_month'])}: {usd(abs(r['pre_tax_profit_month']))}"))
            if "tax_setaside_month" in r and ok:
                L.append(tax_line(r["tax_setaside_month"], month))
        if "output_file" in r:
            L.append(T(f"Table saved to {r['output_file']}", f"Tabela salva em {r['output_file']}"))
    else:
        L.append(T(f"Cost per hour: {usd(r['cost_per_hour'])}", f"Custo da hora: {usd(r['cost_per_hour'])}"))
        L.append(T(f"Suggested hourly price: {usd(r['suggested_hourly_price'])} (round price {usd(r['rounded_hourly_price'])})",
                   f"Preço da hora sugerido: {usd(r['suggested_hourly_price'])} (preço redondo {usd(r['rounded_hourly_price'])})"))
        L.append(T("Breakdown per hour:", "Composição da hora:"))
        for k, v in r["composition_per_hour"].items():
            L.append(f"  - {L_(k)}: {usd(v)}")
        if "sales_tax_on_hourly" in r:
            L.append(st_line(r["sales_tax_on_hourly"], T("hour", "hora")))
        L.append(T(f"Target revenue per month (all billable hours sold): {usd(r['target_revenue_month'])}; "
                   f"pre-tax profit {usd(r['pre_tax_profit_month'])}",
                   f"Faturamento-alvo no mês (todas as horas faturáveis vendidas): {usd(r['target_revenue_month'])}; "
                   f"lucro antes do IR {usd(r['pre_tax_profit_month'])}"))
        if "tax_setaside_month" in r:
            t = r["tax_setaside_month"]
            L.append(T(f"  Set aside for income/SE tax ({pct(t['rate_pct'])} of {usd(t['taxable_base'])}, estimate): "
                       f"{usd(t['set_aside'])}/month",
                       f"  Reservar para income/SE tax ({pct(t['rate_pct'])} de {usd(t['taxable_base'])}, estimativa): "
                       f"{usd(t['set_aside'])}/mês"))
        if "current_price" in r:
            cp = r["current_price"]
            ok = cp["profit_per_hour"] >= 0
            L.append(T(f"Current rate {usd(cp['hourly_price'])}: {'profit' if ok else 'loss'} of "
                       f"{usd(abs(cp['profit_per_hour']))} per hour ({pct(cp['net_margin_pct'])}); per month with every "
                       f"billable hour sold: {usd(cp['profit_month'])}",
                       f"Hora atual {usd(cp['hourly_price'])}: {'lucro' if ok else 'prejuízo'} de "
                       f"{usd(abs(cp['profit_per_hour']))} por hora ({pct(cp['net_margin_pct'])}); no mês, com todas "
                       f"as horas vendidas: {usd(cp['profit_month'])}"))
            if cp.get("break_even_hours_month"):
                L.append(T(f"  Break-even at the current rate: {cp['break_even_hours_month']:,} hours/month",
                           f"  Ponto de equilíbrio no preço atual: {cp['break_even_hours_month']:,} horas/mês"))
            else:
                L.append(T("  At the current rate, fees and labor eat the whole hour: there is no break-even.",
                           "  No preço atual, taxas e mão de obra comem a hora inteira: não há ponto de equilíbrio."))
        if "project" in r:
            p = r["project"]
            L.append(T(f"Job/project of {g(p['hours'])} h: {usd(p['suggested_price'])} (round price {usd(p['rounded_price'])})",
                       f"Serviço/projeto de {g(p['hours'])} h: {usd(p['suggested_price'])} (preço redondo {usd(p['rounded_price'])})"))
            for k, v in p["composition"].items():
                L.append(f"  - {L_(k)}: {usd(v)}")
            if "upfront_price" in p:
                L.append(T(f"  Paid in full upfront (-{pct(p['upfront_discount_pct'])}): {usd(p['upfront_price'])}, "
                           f"profit {usd(p['upfront_profit'])}",
                           f"  Pagamento à vista/antecipado (-{pct(p['upfront_discount_pct'])}): {usd(p['upfront_price'])}, "
                           f"lucro {usd(p['upfront_profit'])}"))
            if "deposit" in p:
                L.append(T(f"  Deposit {pct(p['deposit_pct'])}: {usd(p['deposit'])} to book; balance {usd(p['balance'])}",
                           f"  Sinal de {pct(p['deposit_pct'])}: {usd(p['deposit'])} para reservar; saldo {usd(p['balance'])}"))
            if "installments" in p:
                last = "" if p["last_installment"] == p["installment_amount"] else \
                    T(f" (last {usd(p['last_installment'])})", f" (última {usd(p['last_installment'])})")
                L.append(T(f"  {p['installments']} payments of {usd(p['installment_amount'])}{last} = "
                           f"{usd(p['installments_total'])} (financing/card fee {pct(p['installment_fee_pct'])})",
                           f"  {p['installments']}x de {usd(p['installment_amount'])}{last} = "
                           f"{usd(p['installments_total'])} (taxa de parcelamento {pct(p['installment_fee_pct'])})"))
            if "price_per_sqft" in p:
                L.append(T(f"  {g(p['sqft'])} sq ft: ${p['price_per_sqft']:.3f} per sq ft",
                           f"  {g(p['sqft'])} pés²: ${p['price_per_sqft']:.3f} por pé² (sq ft)"))
            if "sales_tax" in p:
                L.append(st_line(p["sales_tax"], T("job", "serviço")))
            if "recurring" in p:
                q = p["recurring"]
                L.append(T(f"  Recurring ({g(q['visits_per_month'])} visits/month, -{pct(q['discount_pct'])}): "
                           f"{usd(q['price_per_visit'])}/visit, profit {usd(q['profit_per_visit'])}/visit; "
                           f"{usd(q['revenue_month'])}/month, profit {usd(q['profit_month'])}/month",
                           f"  Recorrente ({g(q['visits_per_month'])} visitas/mês, -{pct(q['discount_pct'])}): "
                           f"{usd(q['price_per_visit'])}/visita, lucro {usd(q['profit_per_visit'])}/visita; "
                           f"{usd(q['revenue_month'])}/mês, lucro {usd(q['profit_month'])}/mês"))
    if "margin_scenarios" in r:
        L.append(T("Price by desired pre-tax margin:", "Preço por margem de lucro desejada (antes do IR):"))
        for k, v in r["margin_scenarios"].items():
            L.append(f"  - {k}: {usd(v) if v is not None else T('not feasible (percentages exceed 100%)', 'inviável (percentuais passam de 100%)')}")
    for n in r.get("notes", []):
        L.append(T("Note: ", "Nota: ") + n)
    for w in r.get("warnings", []):
        L.append(T("Warning: ", "Aviso: ") + w)
    print("\n".join(L))


# ---------------------------------------------------------------- CLI
def main():
    ap = Parser(description=T("Selling-price calculator (USD)", "Calculadora de preço de venda (USD)"),
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=T("Numbers accept ", "Números aceitam ") + _EXAMPLES)
    ap.add_argument("--lang", choices=["en", "pt"], default="en", help=T("output language", "idioma da saída"))
    sub = ap.add_subparsers(dest="mode", metavar="{product,service,menu,business,job,commission}", parser_class=Parser)
    sub.required = True

    def common(p, fixed_pct=True):
        p.add_argument("--margin", "--margem", dest="margin", type=arg_pct, required=True,
                       help=T("desired PRE-TAX profit, %% of price", "lucro desejado ANTES do IR, %% do preço"))
        p.add_argument("--variable-pct", "--variaveis", "--fees-pct", dest="variable_pct", type=arg_pct, default=0.0,
                       help=T("%% of price: card processing, app/marketplace commission, sales commission",
                              "%% do preço: cartão, comissão de app/marketplace, comissão de venda"))
        p.add_argument("--fee-per-sale", "--taxa-fixa-venda", dest="fee_per_sale", type=arg_num, default=0.0,
                       help=T("fixed $ per sale (e.g. card $0.30, Etsy listing $0.20)",
                              "$ fixo por venda (ex.: cartão $0.30, listagem Etsy $0.20)"))
        p.add_argument("--revenue-taxes", "--impostos-receita", dest="revenue_taxes", type=arg_pct, default=0.0,
                       help=T("%% gross-receipts taxes on revenue (usually 0)", "%% de imposto sobre a receita bruta (em geral 0)"))
        p.add_argument("--fixed-costs", "--custo-fixo-mensal", dest="fixed_costs", type=arg_num, default=0.0,
                       help=T("$ fixed costs per month", "$ de custos fixos por mês"))
        if fixed_pct:
            p.add_argument("--fixed-cost-pct", "--custo-fixo-pct", dest="fixed_cost_pct", type=arg_pct,
                           help=T("fixed costs as %% of revenue", "custo fixo como %% do faturamento"))
            p.add_argument("--price-includes-sales-tax", "--preco-com-imposto", dest="price_includes_sales_tax",
                           action="store_true",
                           help=T("current prices already include sales tax", "preços atuais já incluem o sales tax"))
        p.add_argument("--sales-tax", "--imposto-venda", dest="sales_tax", type=arg_pct, default=0.0,
                       help=T("%% sales tax added at checkout (display only)", "%% de sales tax somado no caixa (só exibição)"))
        p.add_argument("--tax-setaside", "--reserva-impostos", dest="tax_setaside", type=arg_pct,
                       help=T("%% of profit to set aside for income + SE tax (estimate)",
                              "%% do lucro a reservar para income + SE tax (estimativa)"))
        p.add_argument("--lang", choices=["en", "pt"], default=argparse.SUPPRESS, help=argparse.SUPPRESS)
        p.add_argument("--json", action="store_true", help=T("JSON output", "saída em JSON"))

    pp = sub.add_parser("product", aliases=["produto"], help=T("price of a product", "preço de um produto"))
    common(pp)
    pp.add_argument("--direct-cost", "--custo-direto", dest="direct_cost", type=arg_num, default=0.0,
                    help=T("cost per unit (ingredients, packaging, goods)", "custo por unidade (insumos, embalagem, mercadoria)"))
    pp.add_argument("--volume", "--volume-mensal", dest="volume", type=arg_num,
                    help=T("units/month (single-product business)", "unidades/mês (negócio de 1 produto principal)"))
    pp.add_argument("--current-price", "--preco-atual", dest="current_price", type=arg_num)
    pp.set_defaults(func=calc_product)

    pc = sub.add_parser("menu", aliases=["cardapio"], help=T("many items from a CSV", "vários itens a partir de um CSV"))
    common(pc)
    pc.add_argument("--file", "--arquivo", dest="file", required=True,
                    help=T("CSV name,direct_cost,current_price,volume", "CSV nome;custo_direto;preco_atual;volume_mensal"))
    pc.add_argument("--output", "--saida", dest="output", help=T("save the table as CSV", "salva a tabela em CSV"))
    pc.set_defaults(func=calc_menu)

    pe = sub.add_parser("business", aliases=["empresa"], help=T("business break-even", "ponto de equilíbrio da empresa"))
    pe.add_argument("--fixed-costs", "--custo-fixo-mensal", dest="fixed_costs", type=arg_num, required=True)
    pe.add_argument("--avg-cm-pct", "--mc-media-pct", dest="avg_cm_pct", type=arg_pct, required=True,
                    help=T("weighted contribution margin, %% of revenue", "margem de contribuição média, %% do faturamento"))
    pe.add_argument("--monthly-revenue", "--faturamento-mensal", dest="monthly_revenue", type=arg_num)
    pe.add_argument("--tax-setaside", "--reserva-impostos", dest="tax_setaside", type=arg_pct)
    pe.add_argument("--lang", choices=["en", "pt"], default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    pe.add_argument("--json", action="store_true", help=T("JSON output", "saída em JSON"))
    pe.set_defaults(func=calc_business)

    ps = sub.add_parser("service", aliases=["servico"], help=T("hourly and project price", "preço da hora e do projeto"))
    common(ps, fixed_pct=False)
    ps.add_argument("--owner-pay", "--pro-labore", dest="owner_pay", type=arg_num, default=0.0,
                    help=T("owner's pay target per month", "pró-labore desejado por mês"))
    ps.add_argument("--billable-hours", "--horas-produtivas", dest="billable_hours", type=arg_num,
                    help=T("billable hours per month", "horas faturáveis por mês"))
    ps.add_argument("--current-price", "--preco-atual", dest="current_price", type=arg_num,
                    help=T("hourly rate charged today", "preço da hora cobrado hoje"))
    ps.add_argument("--labor-rate", "--salario-hora", dest="labor_rate", type=arg_num, default=0.0,
                    help=T("$ wage per labor hour of employees/contractors doing the work",
                           "$ por hora pago a funcionários/terceiros que executam"))
    ps.add_argument("--payroll-burden", "--encargos", dest="payroll_burden", type=arg_pct, default=0.0,
                    help=T("%% employer payroll costs on wages (FICA, FUTA/SUTA, workers' comp)",
                           "%% de encargos do empregador sobre o salário (FICA, FUTA/SUTA, workers' comp)"))
    ps.add_argument("--project-hours", "--horas-projeto", dest="project_hours", type=arg_num,
                    help=T("labor hours of the job/visit (crew size x hours)", "horas de trabalho do serviço (equipe x horas)"))
    ps.add_argument("--direct-cost", "--custo-direto", dest="direct_cost", type=arg_num, default=0.0,
                    help=T("job direct costs (supplies, travel, subcontractors)", "custos diretos do serviço"))
    ps.add_argument("--upfront-discount", "--deposit-discount", "--desconto-avista", dest="upfront_discount",
                    type=arg_pct, default=0.0, help=T("%% discount for paying in full upfront", "%% de desconto à vista"))
    ps.add_argument("--deposit-pct", "--sinal-pct", dest="deposit_pct", type=arg_pct, default=0.0,
                    help=T("%% deposit to book the job", "%% de sinal para reservar"))
    ps.add_argument("--installment-fee", "--taxa-parcelamento", dest="installment_fee", type=arg_pct, default=0.0,
                    help=T("%% fee for paying in installments (BNPL/financing)", "%% de taxa do parcelamento"))
    ps.add_argument("--installments", "--parcelas", dest="installments", type=arg_num, default=1.0)
    ps.add_argument("--sqft", "--pes-quadrados", dest="sqft", type=arg_num, help=T("square feet of the job", "pés² do serviço"))
    ps.add_argument("--visits-per-month", "--visitas-mes", dest="visits_per_month", type=arg_num)
    ps.add_argument("--recurring-discount", "--desconto-recorrente", dest="recurring_discount", type=arg_pct, default=0.0,
                    help=T("%% discount for recurring visits (weekly/biweekly)", "%% de desconto para visitas recorrentes"))
    ps.set_defaults(func=calc_service)

    pj = sub.add_parser("job", aliases=["obra"], help=T("contractor job estimate", "orçamento de obra/empreitada"))
    for flag, pt_, dest, h in (
            ("--materials", "--materiais", "materials", T("$ materials (incl. sales tax you pay)", "$ de material")),
            ("--labor-cost", "--mao-de-obra", "labor_cost", T("$ labor already totaled", "$ de mão de obra já somada")),
            ("--crew-hours", "--horas-equipe", "crew_hours", T("total labor hours (crew size x hours)", "horas totais da equipe")),
            ("--labor-rate", "--salario-hora", "labor_rate", T("$ wage per labor hour", "$ de salário por hora")),
            ("--subcontractors", "--subempreiteiros", "subcontractors", T("$ subcontractors", "$ de subempreiteiros")),
            ("--equipment", "--equipamentos", "equipment", T("$ equipment rental", "$ de aluguel de equipamento")),
            ("--permits", "--licencas", "permits", T("$ permits and inspections", "$ de licenças e vistorias")),
            ("--dumpster", "--cacamba", "dumpster", T("$ dumpster/disposal", "$ de caçamba/descarte")),
            ("--other-costs", "--outros-custos", "other_costs", T("$ other direct costs", "$ de outros custos diretos")),
            ("--fee-per-sale", "--taxa-fixa-venda", "fee_per_sale", T("$ fixed payment fee", "$ de taxa fixa")),
            ("--change-order-cost", "--custo-aditivo", "change_order_cost", T("$ direct cost of a change order", "$ de custo de um aditivo"))):
        pj.add_argument(flag, pt_, dest=dest, type=arg_num, default=0.0, help=h)
    for flag, pt_, dest, h, d in (
            ("--payroll-burden", "--encargos", "payroll_burden", T("%% payroll costs on wages", "%% de encargos sobre salário"), 0.0),
            ("--contingency", "--contingencia", "contingency", T("%% contingency on direct costs", "%% de contingência"), 0.0),
            ("--variable-pct", "--variaveis", "variable_pct", T("%% card/financing fee on price", "%% de taxa de cartão/financiamento"), 0.0),
            ("--overhead-markup", "--markup-overhead", "overhead_markup", T("%% overhead ON COST (markup method)", "%% de overhead SOBRE O CUSTO"), None),
            ("--profit-markup", "--markup-lucro", "profit_markup", T("%% profit on cost + overhead (markup method)", "%% de lucro sobre custo + overhead"), None),
            ("--overhead-pct", "--overhead-pct-preco", "overhead_pct", T("%% overhead OF PRICE (margin method)", "%% de overhead DO PREÇO"), None),
            ("--margin", "--margem", "margin", T("%% pre-tax profit OF PRICE (margin method)", "%% de lucro DO PREÇO"), None),
            ("--tax-setaside", "--reserva-impostos", "tax_setaside", T("%% of profit for income/SE tax", "%% do lucro para income/SE tax"), None)):
        pj.add_argument(flag, pt_, dest=dest, type=arg_pct, default=d, help=h)
    pj.add_argument("--schedule", "--cronograma", dest="schedule",
                    help=T("payment schedule in %%, e.g. 33/33/34", "cronograma em %%, ex.: 33/33/34"))
    pj.add_argument("--lang", choices=["en", "pt"], default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    pj.add_argument("--json", action="store_true", help=T("JSON output", "saída em JSON"))
    pj.set_defaults(func=calc_job)

    pk = sub.add_parser("commission", aliases=["comissao"],
                        help=T("income plan for commission sellers (insurance, loans)", "plano de renda para quem vive de comissão"))
    for flag, pt_, dest, h, d in (
            ("--target-income", "--renda-alvo", "target_income", T("$ pre-tax income goal per YEAR", "$ de renda-alvo por ANO, antes do IR"), None),
            ("--fixed-costs", "--custo-fixo-mensal", "fixed_costs", T("$ business expenses per MONTH", "$ de despesas por MÊS"), 0.0),
            ("--avg-premium", "--premio-medio", "avg_premium", T("$ average annual premium per policy", "$ de prêmio anual médio"), None),
            ("--avg-commission", "--comissao-media", "avg_commission", T("$ average commission per sale", "$ de comissão média por venda"), None),
            ("--renewal-income", "--renda-renovacoes", "renewal_income", T("$ renewal commissions expected this year", "$ de renovações esperadas no ano"), 0.0),
            ("--cost-per-lead", "--custo-por-lead", "cost_per_lead", T("$ per lead", "$ por lead"), 0.0)):
        pk.add_argument(flag, pt_, dest=dest, type=arg_num, default=d, required=(dest == "target_income"), help=h)
    for flag, pt_, dest, h, d in (
            ("--first-year-pct", "--comissao-1o-ano", "first_year_pct", T("%% first-year commission on premium", "%% de comissão do 1º ano"), None),
            ("--renewal-pct", "--comissao-renovacao", "renewal_pct", T("%% renewal commission on premium", "%% de comissão de renovação"), 0.0),
            ("--payout-pct", "--repasse-pct", "payout_pct", T("%% of the commission you keep (agency split)", "%% da comissão que fica com você"), 100.0),
            ("--chargeback-pct", "--estorno-pct", "chargeback_pct", T("%% of commissions lost to lapses/chargebacks", "%% perdido em cancelamentos/estornos"), 0.0),
            ("--close-rate", "--taxa-fechamento", "close_rate", T("%% of leads that buy", "%% dos leads que compram"), None),
            ("--tax-setaside", "--reserva-impostos", "tax_setaside", T("%% of income for income/SE tax", "%% da renda para income/SE tax"), None)):
        pk.add_argument(flag, pt_, dest=dest, type=arg_pct, default=d, help=h)
    pk.add_argument("--lang", choices=["en", "pt"], default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    pk.add_argument("--json", action="store_true", help=T("JSON output", "saída em JSON"))
    pk.set_defaults(func=calc_commission)

    a = ap.parse_args()
    try:
        r = a.func(a)
        out = json.dumps(r, ensure_ascii=False, indent=2, allow_nan=False) if a.json else None
    except ValueError as e:
        print(T("Error: ", "Erro: ") + str(e), file=sys.stderr)
        sys.exit(1)
    if out is not None:
        print(out)
    else:
        show(r)


if __name__ == "__main__":
    main()
