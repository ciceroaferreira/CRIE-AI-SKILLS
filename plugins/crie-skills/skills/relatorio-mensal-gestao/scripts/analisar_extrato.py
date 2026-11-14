#!/usr/bin/env python3
"""Monthly management report from bank and credit-card exports (CSV, TXT, OFX/QFX, XLSX). Stdlib only.

Usage:
  python3 -I analisar_extrato.py checking.csv card.csv [more files] [--lang en|pt] [--month 2026-10]
      [--rules rules.json] [--out-csv categorized.csv] [--out-json summary.json] [--no-descriptions]
      [--card amex.csv] [--not-card file.csv] [--date-order mdy|dmy] [--industry "construction"]

US banks are the default (Chase, Bank of America, Wells Fargo, Capital One, Amex, Citi, TD, Discover, QuickBooks
exports, OFX/QFX). Brazilian exports (Itau, BB, Bradesco, Santander, Caixa, Inter, Nubank, C6) are still read.
The report goes to stdout as Markdown. --out-csv writes every transaction with its category for review.
--card FILE: FILE is a credit-card export where charges are POSITIVE (signs are flipped). Amex/Discover layouts and
card files with "PAYMENT - THANK YOU" rows are detected automatically; --not-card FILE turns detection off.
--no-descriptions: no transaction descriptions or payer names in the report or the JSON (alerts included); the
--out-csv review file still lists every transaction. --industry: optional business type used to word alerts (the
job-deposit alert is for construction/trades; it never fires for insurance commission income).
Portuguese aliases still work: --mes, --regras, --saida-csv, --saida-json, --sem-descricoes, --setor.
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, date, timedelta

LANG = "en"

# ---------------------------------------------------------------- categories
# key: (English label, Portuguese label, cost type). Cost type: fixed | variable | out (excluded from the result) |
# draw (owner draws, shown apart from the operating result) | in (cash in).
CATS = {
    "card_payment": ("Credit card payments (transfer, not an expense)",
                     "Pagamentos de cartão de crédito (transferência, não é despesa)", "out"),
    "transfer": ("Transfers between your own accounts", "Transferências entre contas próprias", "out"),
    "loan_in": ("Loans and owner contributions received (not revenue)",
                "Empréstimos e aportes recebidos (não é receita)", "out"),
    "owner_draw": ("Owner draws/distributions", "Retiradas/distribuições do dono", "draw"),
    "payroll_tax": ("Payroll taxes", "Impostos sobre a folha (payroll taxes)", "fixed"),
    "payroll": ("Payroll (wages)", "Folha de pagamento (salários)", "fixed"),
    "sales_tax": ("Sales tax paid to the state", "Sales tax pago ao estado", "variable"),
    "taxes": ("Taxes (IRS, state, franchise, property)", "Impostos (IRS, estado, franchise, propriedade)", "variable"),
    "loan_pay": ("Loan payments (SBA, MCA, vehicle, equipment)",
                 "Parcelas de empréstimos (SBA, MCA, veículo, equipamento)", "fixed"),
    "insurance": ("Insurance", "Seguros", "fixed"),
    "rent": ("Rent and occupancy", "Aluguel e ocupação", "fixed"),
    "utilities": ("Utilities, phone and internet", "Luz, gás, água, telefone e internet", "fixed"),
    "vehicle": ("Vehicle, fuel and tolls", "Veículo, combustível e pedágios", "variable"),
    "marketing": ("Marketing and advertising", "Marketing e anúncios", "variable"),
    "software": ("Software and subscriptions", "Software e assinaturas", "fixed"),
    "licenses": ("Licenses, permits, registrations and CE (state, FINRA, NMLS, building dept)",
                 "Licenças, alvarás, registros e CE (estado, FINRA, NMLS, prefeitura)", "variable"),
    "leads": ("Lead purchases (EverQuote, SmartFinancial, QuoteWizard...)",
              "Compra de leads (EverQuote, SmartFinancial, QuoteWizard...)", "variable"),
    "equipment": ("Equipment rental, dumpsters and disposal", "Aluguel de equipamentos, caçambas e descarte", "variable"),
    "chargebacks": ("Chargebacks and commission reversals (negative revenue)",
                    "Chargebacks e estornos de comissão (receita negativa)", "contra"),
    "professional": ("Professional services (CPA, legal)", "Serviços profissionais (contador, advogado)", "fixed"),
    "fees": ("Bank and merchant fees", "Tarifas bancárias e de maquininha", "variable"),
    "contractors": ("Contractors/subcontractors (1099)", "Prestadores/subempreiteiros (1099)", "variable"),
    "supplies": ("Supplies, materials and inventory", "Insumos, materiais e estoque", "variable"),
    "travel": ("Travel and meals", "Viagens e refeições", "variable"),
    "people_review": ("Zelle/Venmo/Cash App to people (review)",
                      "Zelle/Venmo/Cash App para pessoas (revisar)", "variable"),
    "other_out": ("Other expenses (review)", "Outras despesas (revisar)", "variable"),
    "commissions": ("Commissions and advisory fees (carriers, IMOs/FMOs, broker-dealers)",
                    "Comissões e taxas de assessoria (seguradoras, IMOs/FMOs, corretoras)", "in"),
    "cust_deposits": ("Customer deposits, down payments, progress payments, retainage (may be unearned)",
                      "Sinais, entradas, medições e retenções de clientes (podem não estar ganhos)", "in"),
    "sales_card": ("Card/POS deposits (Square, Stripe, Clover, Toast...)",
                   "Depósitos de cartão/POS (Square, Stripe, Clover, Toast...)", "in"),
    "sales_apps": ("Delivery apps and marketplaces (DoorDash, Uber Eats, Amazon, Etsy...)",
                   "Apps de entrega e marketplaces (DoorDash, Uber Eats, Amazon, Etsy...)", "in"),
    "sales_p2p": ("Zelle/Venmo/Cash App/PayPal received", "Zelle/Venmo/Cash App/PayPal recebidos", "in"),
    "sales_deposit": ("Check, cash and mobile deposits", "Depósitos de cheque, dinheiro e mobile", "in"),
    "sales_ach": ("Customer ACH/wire payments", "Pagamentos de clientes por ACH/wire", "in"),
    "refunds": ("Refunds, reversals and rebates (not sales)", "Estornos, reembolsos e cashback (não é venda)", "in"),
    "interest": ("Interest earned", "Juros recebidos", "in"),
    "other_in": ("Other income (review)", "Outras entradas (revisar)", "in"),
}
OUT_OF_RESULT = {"card_payment", "transfer", "loan_in"}
SALES_KEYS = {"commissions", "cust_deposits", "sales_card", "sales_apps", "sales_p2p", "sales_deposit", "sales_ach"}
REVIEW_KEYS = {"other_out", "people_review"}
LABOR_KEYS = {"payroll", "payroll_tax"}
ALIASES = {  # other names users (or the old Brazilian version) give to the built-in categories
    "transfers": "transfer", "transferencias": "transfer", "transferencias entre contas": "transfer",
    "card payments": "card_payment", "credit card payment": "card_payment", "pagamento de cartao": "card_payment",
    "loans received": "loan_in", "owner contributions": "loan_in", "aportes e emprestimos nao e receita": "loan_in",
    "aportes": "loan_in", "owner draws": "owner_draw", "draws": "owner_draw", "distributions": "owner_draw",
    "pro labore retiradas dos socios": "owner_draw", "retiradas": "owner_draw", "pessoal": "payroll",
    "salarios": "payroll", "impostos e taxas": "taxes", "impostos": "taxes", "tarifas bancarias e de cartao": "fees",
    "marketing e vendas": "marketing", "sistemas e assinaturas": "software", "contabilidade e servicos": "professional",
    "emprestimos e financiamentos": "loan_pay", "fornecedores e mercadorias": "supplies", "fornecedores": "supplies",
    "contractors": "contractors", "subcontractors": "contractors", "prestadores": "contractors",
    "contractors 1099": "contractors", "supplies and inventory": "supplies", "supplies": "supplies",
    "materials": "supplies", "leads": "leads", "commissions": "commissions", "comissoes": "commissions",
    "customer deposits": "cust_deposits", "chargebacks": "chargebacks", "permits": "licenses", "licenses": "licenses",
}

# Terms are matched as whole words on the description with accents and punctuation removed ("AT&T" = "at t").
# "word*" matches a prefix; "word #" means the word followed by a number ("shell #" matches "SHELL 57442").
CARD_PAY_OUT = ["credit crd autopay", "credit crd epay", "crd epay", "credit card payment", "credit card pmt",
                "credit card pymt", "cc payment", "payment to crd", "pmt to crd", "payment to chase card",
                "chase credit crd", "applecard gsbank", "apple card payment", "amex epayment", "american express ach pmt",
                "amex ach pmt", "american express payment", "capital one mobile pmt", "capital one online pmt",
                "capital one mobile pymt", "capital one online pymt", "capital one crcardpmt", "citi card online",
                "citi autopay", "citicard payment", "citi card payment", "discover e payment", "discover payment",
                "bank of america credit card", "bk of amer card", "wf credit card", "wells fargo card", "barclaycard",
                "synchrony bank payment", "synchrony payment", "brex payment", "pagamento fatura", "pagto fatura"]
CARD_PAY_IN = ["payment thank*", "payment received thank*", "pymt thank*", "pmt thank*", "autopay auto pmt", "auto pmt",
               "directpay full balance", "capital one mobile pymt", "capital one online pymt", "capital one mobile pmt",
               "capital one online pmt"]
TRANSFER = ["online transfer", "online banking transfer", "online xfer", "transfer to chk*", "transfer from chk*",
            "transfer to sav*", "transfer from sav*", "transfer to checking", "transfer from checking",
            "transfer to savings", "transfer from savings", "xfer to chk*", "xfer from chk*", "xfer to sav*",
            "xfer from sav*", "internal transfer", "between accounts", "acct xfer", "account transfer",
            "transfer to share", "transfer from share", "money market", "sweep", "transferencia entre contas",
            "entre contas", "mesma titularidade", "conta propria", "contas proprias", "aplicacao", "aplic aut*",
            "resgate", "resg aut*", "cdb", "poupanca"]
LOAN_IN = ["loan proceeds", "loan advance", "loan disbursement", "loan funding", "loan deposit", "sba loan*", "sba eidl",
           "eidl", "ppp loan", "mca funding", "merchant cash advance", "ondeck", "kabbage", "bluevine loan",
           "bluevine capital", "fundbox", "credibly", "square capital", "square loan*", "shopify capital",
           "paypal working capital", "line of credit", "loc advance", "loc draw", "owner contribution",
           "owner investment", "capital contribution", "owner deposit", "transfer from personal", "from personal",
           "aporte*", "emprestimo recebido", "credito emprestimo", "liberacao de credito"]

RULES_OUT = [
    ["owner_draw", ["owner draw*", "owners draw*", "owner s draw*", "draw", "distribution", "distributions",
                    "shareholder dist*", "member dist*", "transfer to personal", "to personal", "personal account",
                    "retirada*", "pro labore", "prolabore"]],
    ["payroll_tax", ["payroll tax*", "gusto tax", "adp tax", "paychex tps", "paychex tax*", "intuit tax", "qbooks tax",
                     "quickbooks payroll tax", "suta", "futa", "unemployment tax*", "unemployment ins*",
                     "reemployment tax", "dept of unemployment", "department of unemployment", "ma dua", "edd",
                     "dept of labor", "inss", "fgts"]],
    ["software", ["payroll fee*", "gusto fee*", "adp fee*", "adp payroll fee*", "paychex eib"]],
    ["payroll", ["payroll", "gusto", "adp", "adp wage*", "paychex", "intuit payroll*", "qbooks payroll",
                 "quickbooks payroll", "qb payroll", "rippling", "onpay", "justworks", "trinet", "patriot payroll",
                 "surepayroll", "wages", "wage pay", "salary", "salario*", "folha"]],
    ["sales_tax", ["sales tax", "sales and use tax", "sales use tax", "sales tx", "dept revenue sales*", "dor sales*"]],
    ["taxes", ["irs usataxpymt", "usataxpymt", "irs", "eftps", "us treasury", "franchise tax*", "franchise tax bd",
               "ca ftb", "dept of revenue", "department of revenue", "dept revenue", "dept of rev*", "mass dor",
               "ma dor", "masstaxconnect", "nys dtf", "ny state dtf", "comptroller", "state tax*", "estimated tax*",
               "tax payment", "property tax*", "tax collector", "county tax*", "annual report fee", "sunbiz",
               "secretary of state", "imposto*", "darf"]],
    ["loan_pay", ["loan payment", "loan pmt", "loan pymt", "sba loan*", "sba eidl", "eidl", "sba", "ondeck",
                  "kabbage", "bluevine loan", "fundbox", "credibly", "mca", "merchant cash advance", "square capital",
                  "square loan*", "shopify capital", "paypal working capital", "pp working capital", "lendio",
                  "funding circle", "equipment financ*", "auto loan", "car payment", "ally payment", "ally pmt",
                  "toyota financial", "toyota motor credit", "ford credit", "gm financial", "honda financial",
                  "mortgage", "line of credit", "loc payment", "heloc", "emprestimo*", "financiamento*"]],
    ["chargebacks", ["chargeback*", "charge back", "commission chargeback*", "comm chargeback*", "chgbk",
                     "commission reversal*", "comm reversal*", "comm rev", "advance recovery", "unearned commission*",
                     "clawback*", "commission debit*", "debit balance recovery"]],
    ["insurance", ["e o insurance", "e o ins*", "errors and omissions", "errors omissions", "calsurance", "eando",
                   "insurance", "ins prem*", "insur*", "next insurance", "hiscox", "the hartford", "hartford",
                   "state farm", "geico", "progressive ins*", "progressive", "liberty mutual", "travelers ins*",
                   "nationwide", "allstate", "workers comp*", "biberk", "thimble", "pie insurance", "simply business",
                   "coverwallet", "general liability", "blue cross", "bcbs", "florida blue", "aetna", "cigna",
                   "united healthcare", "harvard pilgrim", "tufts health", "seguro*"]],
    ["rent", ["rent", "rent payment", "office rent", "lease", "lease payment", "lease pmt", "property mgmt",
              "property management", "realty", "landlord", "public storage", "extra space storage", "cubesmart",
              "self storage", "regus", "wework", "commissary", "aluguel", "condominio"]],
    ["utilities", ["con ed", "con edison", "coned", "eversource", "national grid", "ngrid", "pg e", "pge", "fpl",
                   "florida power", "duke energy", "duke energ*", "teco", "tampa electric", "jea", "ouc",
                   "southern california edison", "socalgas", "sdg e", "pseg", "dominion energy", "xcel energy",
                   "georgia power", "alabama power", "entergy", "ameren", "comed", "peco", "bge", "pepco",
                   "dte energy", "consumers energy", "unitil", "columbia gas", "nicor gas", "atmos energy",
                   "piedmont natural gas", "peoples gas", "nv energy", "txu energy", "reliant energy",
                   "constellation energy", "comcast", "xfinity", "spectrum", "charter comm*", "cox comm*",
                   "cox cable", "optimum", "altice", "verizon", "vz wireless", "vzwrlss", "at t", "att", "t mobile",
                   "tmobile", "sprint", "frontier comm*", "centurylink", "lumen", "starlink", "google fi",
                   "mint mobile", "cricket wireless", "metro by t mobile", "metropcs", "boost mobile",
                   "electric", "electricity", "electric co", "power light", "natural gas", "gas company", "water",
                   "sewer", "water dept", "trash", "waste management", "republic services", "utility", "utilities",
                   "internet", "phone bill", "wireless", "energia", "conta de luz", "telefone"]],
    ["vehicle", ["costco gas", "sams club fuel", "sam s club fuel", "bj s fuel", "shell oil", "shell service*",
                 "shell station", "shell #", "exxon*", "exxonmobil", "mobil #", "mobil oil", "chevron", "texaco",
                 "bp #", "bp products", "sunoco", "speedway", "racetrac", "race trac", "marathon petro*", "valero",
                 "citgo", "circle k", "quiktrip", "qt #", "pilot travel", "pilot flying j", "flying j",
                 "love s travel", "loves travel", "wawa", "sheetz", "gulf oil", "cumberland farms", "irving oil",
                 "murphy usa", "murphy oil", "kwik trip", "casey s", "holiday station*", "fuel", "gasoline", "diesel",
                 "gas station", "e zpass", "ezpass*", "sunpass", "fastrak", "ipass", "txtag", "peach pass", "tolls",
                 "toll", "parking", "parkmobile", "park mobile", "spothero", "jiffy lube", "valvoline", "autozone",
                 "advance auto", "o reilly", "napa auto*", "pep boys", "midas", "firestone", "goodyear",
                 "discount tire", "car wash", "auto repair", "dmv", "rmv", "combustive*", "pedagio", "posto"]],
    ["licenses", ["license*", "licensing", "nipr", "sircon", "pearson vue", "prometric", "continuing education",
                  "ce credits", "webce", "kaplan financial", "finra", "nmls", "iard", "crd renewal", "sec registration",
                  "state registration", "dept of insurance", "department of insurance", "dept of financial services",
                  "division of insurance", "permit*", "building dept", "building department", "building permit*",
                  "inspection fee*", "alvara"]],
    ["leads", ["everquote", "smartfinancial", "smart financial", "quotewizard", "quote wizard", "lendingtree",
               "lending tree", "mediaalpha", "datalot", "assurance iq", "naaip", "benepath", "leads", "lead purchase",
               "lead vendor", "leadgen", "lead gen", "angi leads", "homeadvisor", "home advisor"]],
    ["marketing", ["facebk", "facebook", "fb ads", "meta ads", "meta platforms", "instagram", "google ads*",
                   "googleads", "google adwords", "yelp", "yelp inc", "thumbtack", "angi", "angi leads", "angies list",
                   "angie s list", "homeadvisor", "home advisor", "nextdoor", "groupon", "mailchimp",
                   "constant contact", "vistaprint", "tiktok ads", "tiktok", "linkedin", "microsoft ads", "bing ads",
                   "pinterest", "snapchat", "the knot", "weddingwire", "bark com", "networx", "advertising",
                   "marketing", "anuncio*", "publicidade"]],
    ["software", ["intuit", "quickbooks", "qbooks", "qbo", "google workspace", "google gsuite", "gsuite",
                  "google storage", "google one", "google cloud", "google", "microsoft", "msft", "office 365",
                  "adobe", "canva", "shopify", "squarespace", "wix", "godaddy", "namecheap", "zoom", "zoom us",
                  "slack", "dropbox", "apple com bill", "icloud", "notion", "openai", "chatgpt", "anthropic",
                  "claude ai", "jobber", "housecall pro", "housecall", "servicetitan", "toasttab", "toast inc",
                  "docusign", "calendly", "hubspot", "salesforce", "zapier", "amazon web services", "aws", "twilio",
                  "ringcentral", "grasshopper", "openphone", "vonage", "1password", "lastpass", "xero", "freshbooks",
                  "wave apps", "bill com", "expensify", "redtail", "wealthbox", "zoho", "agencybloc", "radiusbob",
                  "ipipeline", "experian", "equifax", "transunion", "myfico", "factual data", "meridianlink",
                  "encompass", "ellie mae", "docmagic", "orion advisor", "emoney", "riskalyze", "nitrogen wealth",
                  "morningstar", "smarsh", "global relay", "procore", "buildertrend", "coconstruct", "jobtread",
                  "companycam", "houzz pro", "software", "subscription", "assinatura*"]],
    ["professional", ["cpa", "cpas", "accounting", "accountant", "bookkeep*", "tax prep*", "tax service*",
                      "h r block", "hr block", "jackson hewitt", "legal", "law office*", "law firm", "law group",
                      "attorney*", "esq", "legalzoom", "registered agent", "northwest registered", "zenbusiness",
                      "incfile", "consulting", "consultant", "contador*", "contabil*", "advogad*", "honorario*"]],
    ["fees", ["monthly service fee", "service fee", "service charge*", "svc charge*", "svc chg", "maintenance fee",
              "monthly maintenance", "account fee", "overdraft*", "od fee", "nsf", "insufficient funds",
              "returned item*", "return item*", "wire fee", "wire trans svc*", "wire transfer fee", "fee", "fees",
              "atm fee", "non chase atm*", "foreign transaction*", "intl transaction*", "interest charge*",
              "finance charge*", "custodial fee*", "custody fee*", "platform fee*", "clearing fee*",
              "ticket charge*", "late fee", "late payment fee", "annual fee", "annual membership fee",
              "square inc", "square fee*", "sq fee*", "stripe", "paypal fee*", "clover", "merchant fee*",
              "merchant service*", "merchant svc*", "bankcard fee*", "tarifa*", "juros", "iof"]],
    ["equipment", ["united rentals", "sunbelt rentals", "sunbelt rental*", "herc rentals", "ahern rentals",
                   "home depot rental", "home depot tool rental", "tool rental", "equipment rental", "equip rental",
                   "dumpster*", "roll off", "rolloff", "junk removal", "landfill", "transfer station", "cacamba*"]],
    ["contractors", ["contractor*", "subcontract*", "1099", "upwork", "fiverr", "labor", "freelance*"]],
    ["supplies", ["costco", "costco whse", "sam s club", "sams club", "samsclub", "restaurant depot", "jetro",
                  "bj s wholesale", "bjs wholesale", "bj s whls*", "home depot", "the home depot", "homedepot",
                  "lowe s", "lowes", "menards", "sysco", "us foods", "usfoods", "gordon food*", "gfs",
                  "chef s warehouse", "chefs warehouse", "webstaurant*", "katom", "uline", "staples", "office depot",
                  "officemax", "walmart", "wal mart", "wm supercenter", "amazon", "amzn", "amzn mktp*", "amazon com",
                  "amazon mktpl*", "amazon business", "dollar tree", "dollar general", "family dollar", "publix",
                  "kroger", "aldi", "whole foods", "trader joe s", "market basket", "stop shop", "harbor freight",
                  "grainger", "ferguson", "sherwin williams", "ace hardware", "true value", "sally beauty",
                  "cosmoprof", "cintas", "ecolab", "zep", "janitorial", "supply", "supplies", "wholesale",
                  "inventory", "packaging", "abc supply", "84 lumber", "builders firstsource", "lumber*",
                  "beacon roofing", "srs distribution", "fastenal", "white cap", "hd supply", "floor decor",
                  "benjamin moore", "kelly moore", "plumbing supply", "electrical supply", "ready mix", "concrete",
                  "drywall", "roofing supply", "material*", "fornecedor*", "atacad*", "mercadoria*", "embalage*"]],
    ["travel", ["uber", "lyft", "airbnb", "hotel", "marriott", "hilton", "hyatt", "holiday inn", "expedia",
                "booking com", "delta air*", "american air*", "united air*", "southwest air*", "jetblue",
                "spirit air*", "frontier air*", "amtrak", "doordash", "grubhub", "uber eats", "starbucks", "dunkin",
                "mcdonald s", "restaurant", "pizza", "chipotle", "panera", "chick fil a", "wendy s", "burger king",
                "taco bell", "restaurante"]],
    ["people_review", ["zelle", "venmo", "cash app", "square cash", "paypal inst xfer", "apple cash"]],
]
RULES_IN = [
    ["refunds", ["refund", "refunds", "return", "returned", "reversal", "reversed", "credit adjustment",
                 "fee reversal", "rebate", "cashback", "cash back", "cash reward*", "rewards", "statement credit",
                 "tax refund", "tax ref", "treas 310", "dispute credit", "provisional credit", "estorno*"]],
    ["interest", ["interest payment", "interest paid", "interest earned", "interest credit", "int earned", "interest",
                  "dividend*", "rendimento*"]],
    ["cust_deposits", ["down payment", "downpayment", "deposit for", "job deposit", "project deposit", "retainer",
                       "progress payment", "progress billing", "draw request", "construction draw", "retainage",
                       "retention release", "sinal"]],
    ["commissions", ["commission*", "comm pymt", "comm pmt", "comm pay*", "comm dep*", "comm adv*", "adv comm*", "advance comm*",
                     "advisory fee*",
                     "renewal comm*", "override comm*", "new york life", "nylic", "northwestern mutual", "nwmlic",
                     "prudential", "pruco", "metlife", "transamerica", "mutual of omaha", "pacific life",
                     "lincoln national", "lincoln financial", "lincoln life", "aig", "corebridge", "american general",
                     "national life", "f g annuities", "f g life", "fidelity guaranty", "americo", "globe life",
                     "foresters", "john hancock", "principal life", "allianz life", "athene", "north american co",
                     "sammons", "nationwide life", "protective life", "banner life", "symetra", "securian",
                     "minnesota life", "mass mutual", "massmutual", "guardian life", "penn mutual", "national western",
                     "senior life", "royal neighbors", "liberty bankers", "sbli", "integrity marketing", "amerilife",
                     "lpl financial", "raymond james", "ameriprise", "commonwealth financial", "osaic", "cetera",
                     "pershing", "comissao", "comissoes"]],
    ["sales_p2p", ["zelle", "venmo", "cash app", "square cash", "paypal", "apple cash"]],
    ["sales_apps", ["doordash", "door dash", "uber eats", "ubereats", "uber", "grubhub", "postmates", "caviar",
                    "ezcater", "seamless", "chownow", "slice", "amazon", "amzn", "etsy", "ebay", "shopify",
                    "walmart marketplace", "tiktok shop", "faire", "poshmark", "mercari", "instacart"]],
    ["sales_card", ["square", "square inc", "stripe", "clover", "toast inc", "toast dep*", "toasttab", "heartland",
                    "fiserv", "first data", "worldpay", "elavon", "global payments", "tsys", "paysafe",
                    "chase paymentech", "paymentech", "bankcard", "bnkcd", "mtot dep", "merchant dep*", "merch dep",
                    "merchant services", "merchant svc*", "intuit pymt*", "intuit payment*", "quickbooks payments",
                    "qb payments", "authorize net", "braintree", "helcim", "lightspeed", "spoton", "shift4", "revel",
                    "payanywhere", "sumup", "zettle", "settlement", "settlemt", "stone", "cielo", "getnet",
                    "pagseguro", "mercado pago"]],
    ["sales_ach", ["wire in", "incoming wire", "wire transfer in", "fedwire credit", "wire type wire in", "ach credit",
                   "ach deposit", "invoice*", "remittance", "ted recebida", "pix recebido"]],
    ["sales_deposit", ["deposit", "deposits", "mobile deposit", "remote deposit", "remote online deposit",
                       "counter credit", "edeposit", "branch deposit", "atm deposit", "check deposit", "cash deposit",
                       "deposito*"]],
]
# The bank's own category column (Chase/Capital One/Amex card exports) is used only when no rule matched.
HINTS = [("advertis", "marketing"), ("fuel", "vehicle"), ("gas", "vehicle"), ("automotive", "vehicle"),
         ("insurance", "insurance"), ("utilit", "utilities"), ("phone", "utilities"), ("cable", "utilities"),
         ("internet", "utilities"), ("communication", "utilities"), ("restaurant", "travel"),
         ("dining", "travel"), ("food drink", "travel"), ("travel", "travel"), ("lodging", "travel"),
         ("airline", "travel"), ("fee", "fees"), ("interest charge", "fees"), ("professional", "professional"),
         ("software", "software"), ("hardware", "supplies"), ("supplies", "supplies"), ("groceries", "supplies"),
         ("merchandise", "supplies"), ("office", "supplies"), ("home improvement", "supplies"), ("home", "supplies")]

OVERDRAFT_RE = re.compile(r"\b(overdraft|nsf|insufficient funds|od fee|returned item|return item)")
PAY_THANK_RE = re.compile(r"\b(payment|pymt|pmt)( received)? thank")

# ---------------------------------------------------------------- messages (en / pt)
MSG = {
    "err": ("Error", "Erro"),
    "no_dir": ("the folder for {p} does not exist. Create it first (e.g. mkdir -p {d}).",
               "a pasta de destino de {p} não existe. Crie antes (ex.: mkdir -p {d})."),
    "bad_month": ("use --month as YYYY-MM (e.g. 2026-10).", "use --month no formato AAAA-MM (ex.: 2026-10)."),
    "rules_open": ("could not open the rules file {p}: {e}", "não consegui abrir o arquivo de regras {p}: {e}"),
    "rules_json": ("the rules file {p} is not valid JSON (line {l}, column {c}: {m}). See references/regras-exemplo.json.",
                   "o arquivo de regras {p} não é um JSON válido (linha {l}, coluna {c}: {m}). Veja references/regras-exemplo.json."),
    "rules_obj": ("{p}: the rules JSON must be an object with \"expenses\" and/or \"income\" keys.",
                  "{p}: o JSON de regras deve ser um objeto com as chaves \"expenses\"/\"despesas\" e/ou \"income\"/\"receitas\"."),
    "rules_item": ("{p}: in \"{k}\", each rule must be [\"Category\", [\"term\", ...]]. Found: {i}",
                   "{p}: em \"{k}\", cada regra deve ser [\"Categoria\", [\"termo\", ...]]. Encontrei: {i}"),
    "rules_terms": ("{p}: the terms for '{c}' must be a list of text strings.",
                    "{p}: os termos da categoria '{c}' devem ser uma lista de textos."),
    "no_cols": ("{f}: could not find date and amount columns. Header seen: {h}",
                "{f}: não encontrei colunas de data e valor. Cabeçalho visto: {h}"),
    "binary": ("{f}: looks like a binary file (spreadsheet or PDF), not CSV. Export the statement as CSV or OFX/QFX, or save the spreadsheet as CSV.",
               "{f}: parece um arquivo binário (planilha ou PDF), não CSV. Exporte o extrato em CSV ou OFX/QFX, ou salve a planilha como CSV."),
    "pdf": ("{f}: the script does not read PDFs. Download the CSV or QFX/OFX instead (or extract the PDF text with the pdf skill and build a CSV).",
            "{f}: o script não lê PDF. Baixe o CSV ou QFX/OFX (ou extraia o texto do PDF com a skill pdf e monte um CSV)."),
    "xls": ("{f}: old Excel (.xls) is not read. Export CSV or OFX/QFX, or save it as CSV or .xlsx.",
            "{f}: Excel antigo (.xls) não é lido. Exporte CSV ou OFX/QFX, ou salve como CSV ou .xlsx."),
    "xlsx_bad": ("{f}: could not read the spreadsheet ({e}). Save it as CSV or export CSV/OFX.",
                 "{f}: não consegui ler a planilha ({e}). Salve como CSV ou exporte CSV/OFX."),
    "ofx_none": ("{f}: no OFX/QFX transactions found.", "{f}: nenhum lançamento OFX/QFX encontrado."),
    "no_txn": ("no transactions found.", "nenhum lançamento encontrado."),
    "month_missing": ("month {m} is not in the files. Months found: {ms}", "o mês {m} não está nos arquivos. Meses encontrados: {ms}"),
    "w_noheader": ("{f}: no header row; columns inferred from content (date = column {d}, amount = column {v}). Check the totals.",
                   "{f}: arquivo sem cabeçalho; colunas deduzidas pelo conteúdo (data = coluna {d}, valor = coluna {v}). Confira os totais."),
    "w_dropped": ("{f}: {n} dated row(s) were skipped because the amount could not be read. Check the original file.",
                  "{f}: {n} linha(s) com data foram ignoradas porque o valor não pôde ser lido. Confira no arquivo original."),
    "w_dup": ("{f}: {n} transaction(s) repeated from {o} were ignored (the same period seems to have been exported twice). If these are different accounts, check the totals.",
              "{f}: {n} lançamento(s) repetidos de {o} foram ignorados (o mesmo período parece exportado duas vezes). Se forem contas diferentes, confira os totais."),
    "w_dup_fitid": ("earlier file(s) with the same FITID", "arquivo(s) anterior(es) com o mesmo FITID"),
    "w_incomplete": ("Month {m} looks incomplete in the files (transactions from {a} to {b}). Make sure the whole month was exported. Month-over-month alerts were turned off.",
                     "O mês {m} parece incompleto nos arquivos (lançamentos de {a} a {b}). Confira se exportou o mês inteiro. Alertas de variação entre meses foram desativados."),
    "w_noprev": ("No transactions for {p} (the month before {m}); the comparison will come with the next close.",
                 "Não há lançamentos de {p} (mês anterior a {m}); a comparação fica para o próximo fechamento."),
    "w_date_amb": ("{f}: every date has day and month ≤ 12, so the order is ambiguous; read as {o}. If that is wrong, rerun with --date-order {x}.",
                   "{f}: todas as datas têm dia e mês ≤ 12, então a ordem é ambígua; li como {o}. Se estiver errado, rode de novo com --date-order {x}."),
    "w_card_auto": ("{f}: looks like a credit-card export where charges are positive (Amex/Discover style); signs were flipped so charges count as spending. If that is wrong, rerun with --not-card {b}.",
                    "{f}: parece exportação de cartão de crédito com compras positivas (estilo Amex/Discover); os sinais foram invertidos para as compras contarem como gasto. Se estiver errado, rode com --not-card {b}."),
    "w_card_forced": ("{f}: signs flipped (--card): charges count as spending, payments and refunds as money in.",
                      "{f}: sinais invertidos (--card): compras contam como gasto; pagamentos e estornos como entrada."),
    "w_card_pos": ("{f}: most transactions are positive. If this is a credit-card statement that lists charges as positive numbers, rerun with --card {b}.",
                   "{f}: a maioria dos lançamentos é positiva. Se for fatura de cartão que mostra compras como números positivos, rode de novo com --card {b}."),
    "w_hint": ("{n} transaction(s) were categorized from the bank's own category column (no rule matched). Check them in the CSV.",
               "{n} lançamento(s) foram categorizados pela coluna de categoria do próprio banco (nenhuma regra casou). Confira no CSV."),
    # alerts
    "a_neg": ("Negative operating cash result: money out exceeded money in by {v}.",
              "Resultado de caixa operacional negativo: as saídas superaram as entradas em {v}."),
    "a_neg_draw": ("After owner draws of {d}, cash went down by {v} this month.",
                   "Depois das retiradas do dono ({d}), o caixa caiu {v} no mês."),
    "a_uncat": ("{p} of money out ({v}) is uncategorized or needs review (including Zelle/Venmo/Cash App payments to people). Review the categorized CSV and save rules.",
                "{p} das saídas ({v}) estão sem categoria ou a revisar (inclui Zelle/Venmo/Cash App para pessoas). Revise o CSV categorizado e salve regras."),
    "a_uncat_in": ("{p} of money in ({v}) is \"Other income (review)\". Tell me what these deposits are (sales, owner money, loan, refund).",
                   "{p} das entradas ({v}) estão em \"Outras entradas (revisar)\". Diga o que são (vendas, dinheiro do dono, empréstimo, estorno)."),
    "a_fees": ("Bank and merchant fees total {v} ({p} of sales deposits), above the 3% mark. Compare your card processing rate and bank plan; ask the bank to waive monthly fees or change plans.",
               "Tarifas bancárias e de maquininha somam {v} ({p} dos depósitos de vendas), acima de 3%. Compare a taxa de processamento de cartão e o plano da conta; peça isenção da tarifa mensal ou troque de plano."),
    "a_overdraft": ("Overdraft/NSF fees: {v} in {n} charge(s). Keep a cash cushion, set low-balance alerts, or link savings for overdraft protection.",
                    "Tarifas de overdraft/NSF (saldo insuficiente): {v} em {n} cobrança(s). Mantenha uma reserva, ative alertas de saldo baixo ou vincule a poupança como proteção."),
    "a_loans": ("Loan payments take {p} of money in ({v}). Note: on a P&L only the interest is an expense; the principal reduces the debt.",
                "Parcelas de empréstimo consomem {p} das entradas ({v}). Obs.: na contabilidade só os juros são despesa; o principal reduz a dívida."),
    "a_labor": ("Labor (payroll + payroll taxes) is {p} of money in. Many small businesses run about 20–40% (labor-heavy services such as cleaning run higher); compare with your industry and your prices.",
                "Mão de obra (folha + impostos da folha) é {p} das entradas. Muitos pequenos negócios ficam em ~20–40% (serviços intensivos em mão de obra, como limpeza, ficam acima); compare com seu setor e seus preços."),
    "a_card_with": ("Credit card payments of {v} were excluded as transfers; the purchases themselves come from the card statement(s) ({f}). This avoids counting the same spending twice.",
                    "Pagamentos de cartão de {v} ficaram fora como transferência; as compras vêm da(s) fatura(s) do cartão ({f}). Assim o mesmo gasto não é contado duas vezes."),
    "a_card_without": ("You paid {v} to credit card(s) from the bank account. It is excluded as a transfer, so purchases made on the card are NOT in this report. Add the card statement(s) for the same month; do not count the payment itself as an expense, or the spending would be counted twice.",
                       "Você pagou {v} de cartão(ões) de crédito pela conta. Isso ficou fora como transferência, então as compras feitas no cartão NÃO estão no relatório. Envie a fatura do mesmo mês; não conte o pagamento como despesa, senão o gasto seria contado duas vezes."),
    "a_est_tax": ("Quarterly estimated tax payment (Form 1040-ES, plus your state if it has income tax) is due around {d}. Set aside part of your profit; a common rule of thumb is 25–30% (estimate; confirm the amount with your CPA). IRS/state payments seen this month: {v}.",
                  "A estimativa trimestral de imposto (Form 1040-ES, e a do estado se houver imposto de renda estadual) vence por volta de {d}. Separe parte do lucro; uma regra prática comum é 25–30% (estimativa; confirme o valor com seu CPA). Pagamentos ao IRS/estado vistos neste mês: {v}."),
    "a_sales_tax": ("You paid {v} of sales tax to the state. Sales tax is your customers' money passing through: if your card deposits include it, part of \"sales\" is not yours. Set it aside every week until it is due.",
                    "Você pagou {v} de sales tax ao estado. Sales tax é dinheiro do cliente que só passa por você: se os depósitos de cartão incluem o imposto, parte das \"vendas\" não é sua. Separe toda semana até o vencimento."),
    "a_concentration": ("{p} of money in ({v}) came from one payer/client: {w}. Losing that payer would hurt; track it and diversify where you can.",
                        "{p} das entradas ({v}) vieram de um único pagador/cliente: {w}. Perder esse pagador doeria; acompanhe e diversifique quando puder."),
    "a_concentration_carrier": ("{p} of money in ({v}) came from one carrier/IMO: {w}. Losing that carrier would hurt; track it and diversify where you can.",
                                "{p} das entradas ({v}) vieram de uma única seguradora/IMO: {w}. Perder essa seguradora doeria; acompanhe e diversifique quando puder."),
    "a_concentration_anon": ("{p} of money in ({v}) came from a single payer/client. Losing that payer would hurt; track it and diversify where you can.",
                             "{p} das entradas ({v}) vieram de um único pagador/cliente. Perder esse pagador doeria; acompanhe e diversifique quando puder."),
    "a_concentration_carrier_anon": ("{p} of money in ({v}) came from a single carrier/IMO. Losing that carrier would hurt; track it and diversify where you can.",
                                     "{p} das entradas ({v}) vieram de uma única seguradora/IMO. Perder essa seguradora doeria; acompanhe e diversifique quando puder."),
    "a_chargebacks": ("Chargebacks/commission reversals took back {v} ({p} of commissions or sales; previous month {q}). Check which policies lapsed or which sales were disputed, and keep a reserve for advanced commissions.",
                      "Chargebacks/estornos de comissão tiraram {v} ({p} das comissões ou vendas; mês anterior {q}). Veja quais apólices caducaram ou quais vendas foram contestadas e mantenha reserva para comissões adiantadas."),
    "a_materials_high": ("Materials, supplies and equipment rental total {v} ({p} of money in). If customer deposits did not cover them, the business is financing jobs with its own cash; bill deposits/progress payments up front.",
                         "Materiais, insumos e aluguel de equipamentos somam {v} ({p} das entradas). Se os sinais dos clientes não cobriram isso, a empresa está financiando as obras com o próprio caixa; cobre sinal/medições antes."),
    "a_materials_up": ("Materials and equipment rose to {p} of money in (previous month {q}). Check whether prices went up, a job is over budget, or materials were bought ahead of the customer's payment.",
                       "Materiais e equipamentos subiram para {p} das entradas (mês anterior {q}). Veja se o preço subiu, se alguma obra estourou o orçamento ou se comprou antes do cliente pagar."),
    "a_big_deposits": ("{n} large customer receipt(s) or deposit(s) totaling {v} (largest {m} on {d}). If any is a deposit, down payment, progress payment or retainer for work not yet done, it is owed to the customer until earned: cash is not profit. Reserve what the job will still cost (materials, labor, subcontractors).",
                       "{n} recebimento(s) grande(s) ou sinal(is) de clientes somando {v} (maior: {m} em {d}). Se for sinal, entrada, medição ou adiantamento de serviço ainda não feito, é dívida com o cliente até ser executado: caixa não é lucro. Reserve o que a obra ainda vai custar (material, mão de obra, subempreiteiros)."),
    "a_big_deposits_gen": ("{n} large customer receipt(s) or deposit(s) totaling {v} (largest {m} on {d}). If any is a deposit, prepayment or retainer for an order or service not yet delivered, it is owed to the customer until earned: cash is not profit. Reserve what delivering it will still cost.",
                           "{n} recebimento(s) grande(s) ou sinal(is) de clientes somando {v} (maior: {m} em {d}). Se for sinal, pagamento antecipado ou adiantamento de pedido ou serviço ainda não entregue, é dívida com o cliente até ser entregue: caixa não é lucro. Reserve o que ainda vai custar entregar."),
    "a_dup": ("{n} possible duplicate payment(s) (same amount and description on the same day). Check the CSV.",
              "{n} possível(is) pagamento(s) em duplicidade (mesmo valor e descrição no mesmo dia). Confira no CSV."),
    "a_loan_in": ("{v} came in as loans or owner contributions. That is not revenue and was left out of the result.",
                  "Entraram {v} de empréstimos ou aportes do dono. Não é receita e ficou fora do resultado."),
    "a_people": ("{n} payment(s) to people via Zelle/Venmo/Cash App ({v}). Tell me who they are (employee, contractor, owner, supplier) so I can save rules. Contractors need a W-9; a 1099-NEC is required above the yearly threshold ($600 through 2025; $2,000 for payments made from 2026 under the 2025 law — confirm with your CPA).",
                 "{n} pagamento(s) a pessoas por Zelle/Venmo/Cash App ({v}). Diga quem são (funcionário, prestador, dono, fornecedor) para eu salvar regras. Prestador precisa de W-9; o 1099-NEC é obrigatório acima do limite anual ($600 até 2025; $2.000 para pagamentos a partir de 2026 pela lei de 2025 — confirme com seu CPA)."),
    "a_in_drop": ("Money in fell {p} compared with the previous month.", "As entradas caíram {p} em relação ao mês anterior."),
    "a_cat_up": ("'{c}' went up from {a} to {b} (+{p}).", "'{c}' subiu de {a} para {b} (+{p})."),
    "a_none": ("No automatic alerts. Still review the categories.", "Nenhum alerta automático. Revise as categorias mesmo assim."),
    # report
    "title": ("Monthly management report — {m}", "Relatório mensal de gestão — {m}"),
    "period": ("Period in the files: {a} to {b} · {n} transactions · {f} file(s)",
               "Período nos arquivos: {a} a {b} · {n} lançamentos · {f} arquivo(s)"),
    "h_warn": ("Data warnings", "Avisos sobre os dados"),
    "ind": ("Indicator", "Indicador"), "val": ("Amount", "Valor"),
    "r_in": ("Money in (operating)", "Entradas (operacionais)"),
    "r_out": ("Money out (operating)", "Saídas (operacionais)"),
    "r_res": ("Operating cash result", "Resultado de caixa operacional"),
    "r_margin": ("Cash margin", "Margem de caixa"),
    "r_draws": ("Owner draws/distributions", "Retiradas/distribuições do dono"),
    "r_after": ("Cash result after owner draws", "Resultado depois das retiradas"),
    "r_fixvar": ("Fixed / variable costs", "Custos fixos / variáveis"),
    "r_be": ("Estimated break-even (money in)", "Ponto de equilíbrio estimado (entradas)"),
    "r_be_none": ("— (contribution margin ≤ 0)", "— (margem de contribuição ≤ 0)"),
    "r_labor": ("Labor share of money in", "Peso da mão de obra nas entradas"),
    "r_prev": ("Operating result, previous month ({m})", "Resultado operacional do mês anterior ({m})"),
    "r_transf": ("Transfers between own accounts, net (excluded)", "Transferências entre contas próprias, líquido (fora)"),
    "r_card": ("Credit card payments made (excluded)", "Pagamentos de cartão feitos (fora)"),
    "r_loan_in": ("Loans/owner contributions received (excluded)", "Empréstimos/aportes recebidos (fora)"),
    "h_in": ("Money in by source", "Entradas por origem"), "src": ("Source", "Origem"),
    "h_out": ("Money out by category", "Saídas por categoria"), "cat": ("Category", "Categoria"),
    "type": ("Type", "Tipo"), "pct_in": ("% of money in", "% das entradas"), "prev": ("Previous month", "Mês anterior"),
    "fixed": ("fixed", "fixa"), "variable": ("variable", "variável"), "draw": ("draw", "retirada"),
    "contra": ("negative revenue", "receita negativa"), "in": ("in", "entrada"),
    "h_top": ("10 largest payments", "10 maiores saídas"), "dt": ("Date", "Data"), "desc": ("Description", "Descrição"),
    "h_week": ("Cash flow by week of the month", "Fluxo por semana do mês"), "week": ("Week", "Semana"),
    "wk_net": ("Net for the week", "Saldo da semana"), "cum": ("Cumulative", "Acumulado"),
    "wk_lbl": ("Week {s} (days {a}–{b})", "{s}ª semana (dias {a}–{b})"),
    "h_alerts": ("Alerts", "Alertas"), "h_trend": ("Trend", "Evolução"), "month": ("Month", "Mês"),
    "res": ("Result", "Resultado"),
    "note": ("_Cash basis: money that actually moved in and out of the accounts in these files. This is not a P&L or "
             "accrual statement: it ignores unpaid invoices (receivables and payables), depreciation, inventory changes "
             "and the principal/interest split of loan payments. Transfers between your accounts, credit card payments "
             "and loans/owner contributions received are excluded from the result; owner draws are shown separately. "
             "Your bookkeeper/CPA closes the books and files the taxes. Check the categories before deciding._",
             "_Regime de caixa: o dinheiro que de fato entrou e saiu das contas destes arquivos. Não é P&L (DRE) nem "
             "regime de competência: ignora faturas a receber e a pagar, depreciação, variação de estoque e a divisão "
             "entre principal e juros das parcelas. Transferências entre suas contas, pagamentos de cartão e "
             "empréstimos/aportes recebidos ficam fora do resultado; retiradas do dono aparecem à parte. Quem fecha a "
             "contabilidade e entrega os impostos é seu bookkeeper/CPA. Confira as categorias antes de decidir._"),
}
MONTHS = {"en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                 "November", "December"],
          "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
                 "novembro", "dezembro"]}


def t(key, **kw):
    s = MSG[key][0 if LANG == "en" else 1]
    return s.format(**kw) if kw else s


def label(cat):
    if cat.startswith("custom:"):
        return cat[7:]
    return CATS[cat][0 if LANG == "en" else 1]


def cost_type(cat):
    return "variable" if cat.startswith("custom:") else CATS[cat][2]


# ---------------------------------------------------------------- text helpers
def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def normalize(s):
    """No accents, lowercase, punctuation becomes a space."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", strip_accents(str(s))).split())


def hnorm(c):
    """Header normalization: keeps / # ( ) $ so 'Memo/Description' and 'Check or Slip #' stay recognizable."""
    return " ".join(re.sub(r"[^a-z0-9/#$()]+", " ", strip_accents(str(c))).split())


def compile_term(term):
    s = str(term).strip()
    number = s.endswith("#")
    s = s.rstrip("#").strip()
    prefix = s.endswith("*")
    n = normalize(s.rstrip("*"))
    if not n:
        return None
    if number:
        return re.compile(r"\b" + re.escape(n) + r" ?\d")
    return re.compile(r"\b" + re.escape(n) + ("" if prefix else r"\b"))


def resolve_category(name):
    n = normalize(name)
    for k, (en, pt, _) in CATS.items():
        if n in (normalize(k), normalize(en), normalize(pt)):
            return k
    if n in ALIASES:
        return ALIASES[n]
    return "custom:" + str(name).strip()


def build_rules(extra=None):
    """Order: user rules -> card payments -> transfers (-> loans/contributions on money in) -> defaults."""
    extra = extra or {}
    out = list(extra.get("expenses", [])) + [["card_payment", CARD_PAY_OUT], ["transfer", TRANSFER]] + RULES_OUT
    inn = list(extra.get("income", [])) + [["card_payment", CARD_PAY_IN], ["transfer", TRANSFER],
                                           ["loan_in", LOAN_IN]] + RULES_IN
    return out, inn


# ---------------------------------------------------------------- numbers and dates
def parse_amount(txt):
    """US and Brazilian styles: $1,234.56 · (1,234.56) · -$1,234.56 · 1.234,56 · 1.234,56- · 10,00 D · 125.00 CR.
    Both separators: the last one is the decimal. A lone separator followed by exactly 3 digits is thousands."""
    if txt is None:
        return None
    s = str(txt).strip()
    if not s:
        return None
    for dash in ("−", "‒", "–", "—"):
        s = s.replace(dash, "-")
    s = re.sub(r"(?i)us\$|r\$|usd|brl|\$", "", s)
    s = re.sub(r"[\s  ]", "", s)
    if not s:
        return None
    neg = False
    m = re.fullmatch(r"(?i)(.*\d)(cr|dr)", s)
    if m:
        s, neg = m.group(1), m.group(2).lower() == "dr"
    if s[:1] in "-+":
        neg, s = neg or s[0] == "-", s[1:]
    if s.startswith("(") and s.endswith(")"):
        neg, s = True, s[1:-1]
    if s[:1] in "-+":
        neg, s = neg or s[0] == "-", s[1:]
    if s[-1:].upper() in ("D", "C"):
        neg, s = neg or s[-1].upper() == "D", s[:-1]
    if s[-1:] in ("-", "+"):
        neg, s = neg or s[-1] == "-", s[:-1]
    if not re.fullmatch(r"\.?\d[\d.,]*", s) or s.endswith((",", ".")) and len(s) > 1 and not s[-2].isdigit():
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        if re.fullmatch(r"[1-9]\d{0,2}(,\d{3})+", s):
            s = s.replace(",", "")
        elif s.count(",") == 1:
            s = s.replace(",", ".")
        else:
            return None
    elif s.count(".") > 1 or re.fullmatch(r"[1-9]\d{0,2}\.\d{3}", s):
        if not re.fullmatch(r"[1-9]\d{0,2}(\.\d{3})+", s):
            return None
        s = s.replace(".", "")
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


DMY_RE = re.compile(r"^\s*(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})(?!\d)")
ISO_RE = re.compile(r"^\s*(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})(?!\d)")
TXT1_RE = re.compile(r"^\s*([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})")
TXT2_RE = re.compile(r"^\s*(\d{1,2})[\s-]([A-Za-z]{3,9})\.?[\s-](\d{2,4})")
MON_ABBR = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
                                              "nov", "dec"])}
MON_ABBR.update({"fev": 2, "abr": 4, "mai": 5, "ago": 8, "set": 9, "out": 10, "dez": 12})


def _mk(y, mo, d):
    y = int(y)
    if y < 100:
        y += 2000
    try:
        r = date(y, int(mo), int(d))
    except ValueError:
        return None
    return r if 1990 <= r.year <= 2100 else None


def parse_date(txt, order=None):
    """order: 'mdy', 'dmy' or None (try MM/DD first, then DD/MM)."""
    s = str(txt).strip()
    if not s:
        return None
    m = ISO_RE.match(s)
    if m:
        return _mk(m.group(1), m.group(2), m.group(3))
    m = DMY_RE.match(s)
    if m:
        a, b, y = m.groups()
        if order == "dmy":
            return _mk(y, b, a)
        if order == "mdy":
            return _mk(y, a, b)
        return _mk(y, a, b) or _mk(y, b, a)
    m = TXT1_RE.match(s)
    if m and m.group(1)[:3].lower() in MON_ABBR:
        return _mk(m.group(3), MON_ABBR[m.group(1)[:3].lower()], m.group(2))
    m = TXT2_RE.match(s)
    if m and m.group(2)[:3].lower() in MON_ABBR:
        return _mk(m.group(3), MON_ABBR[m.group(2)[:3].lower()], m.group(1))
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})(\d{6})?(\.\d+)?(\[.*\])?.*", s)  # OFX 20261031120000[-5:EST], Caixa 20261031
    if m:
        return _mk(m.group(1), m.group(2), m.group(3))
    if re.fullmatch(r"\d{5}(\.\d+)?", s) and 30000 < float(s) < 70000:  # Excel serial date (xlsx)
        return date(1899, 12, 30) + timedelta(days=int(float(s)))
    return None


def detect_order(values, br_hint):
    """Per file: a first field > 12 means DD/MM; a second field > 12 means MM/DD. Otherwise pick the reading with
    the shorter date span (a statement covers weeks, not a year); if still tied, MM/DD (DD/MM for Brazilian files)."""
    pairs = [m.groups() for m in (DMY_RE.match(str(v)) for v in values) if m]
    if not pairs:
        return None, False
    if any(int(a) > 12 for a, _, _ in pairs):
        return "dmy", False
    if any(int(b) > 12 for _, b, _ in pairs):
        return "mdy", False

    def span(order):
        ds = [d for d in (_mk(y, a, b) if order == "mdy" else _mk(y, b, a) for a, b, y in pairs) if d]
        return (max(ds) - min(ds)).days if ds else 10 ** 6
    sm, sd = span("mdy"), span("dmy")
    if sm != sd:
        return ("mdy" if sm < sd else "dmy"), False
    return ("dmy" if br_hint else "mdy"), len({p for p in pairs}) >= 1


# ---------------------------------------------------------------- reading files
COL_DATE = ["date", "transaction date", "trans date", "posting date", "posted date", "post date", "data",
            "dt", "data lancamento", "data do lancamento", "data movimento", "data mov", "fecha"]
COL_DESC = ["description", "transaction description", "original description", "payee", "name", "merchant",
            "merchant name", "memo", "memo/description", "descricao", "historico", "lancamento", "detalhe",
            "detalhes", "estabelecimento", "titulo", "identificacao", "complemento"]
COL_AMOUNT = ["amount", "transaction amount", "amount (usd)", "amount ($)", "valor", "valor (r$)", "valor r$",
              "quantia", "montante"]
COL_IN = ["credit", "credits", "credit amount", "deposit", "deposits", "deposit amount", "deposits/credits",
          "entrada", "entradas", "credito", "creditos", "credito (r$)", "receita"]
COL_OUT = ["debit", "debits", "debit amount", "withdrawal", "withdrawals", "withdrawal amount", "withdrawals/debits",
           "saida", "saidas", "debito", "debitos", "debito (r$)", "despesa"]
COL_TYPE = ["tipo lancamento", "tipo de lancamento", "tipo", "deb cred", "deb/cred", "debito/credito",
            "credito/debito", "d/c", "c/d", "dc", "cd", "natureza", "sinal", "tipo transacao", "tipo de transacao",
            "transaction type", "details", "type", "dr/cr", "cr/dr", "debit/credit", "credit/debit"]
COL_CAT = ["category", "categoria"]
TYPE_DEBIT = {"d", "db", "dr", "deb", "debit", "debito", "debitos", "saida", "saidas", "s", "sai", "withdrawal"}
TYPE_CREDIT = {"c", "cr", "cred", "credit", "credito", "creditos", "entrada", "entradas", "e", "ent", "deposit"}
TYPE_RE = re.compile(r"^(ach|pos|atm|wire|misc|quickpay|card|bill pay)? ?(debit|credit)$")
SKIP_DESC = ("saldo", "s a l d o", "beginning balance", "ending balance", "daily ending balance", "balance forward",
             "opening balance", "closing balance", "total credits", "total debits", "previous balance")
BR_HEADER_WORDS = {"data", "historico", "lancamento", "valor", "descricao", "saldo", "documento", "credito", "debito",
                   "docto", "situacao", "entrada", "saida"}


def type_sign(v):
    """-1 for a debit marker, +1 for a credit marker, None if the value is not a clean debit/credit marker."""
    raw = str(v).strip()
    if raw in ("-", "+"):
        return -1 if raw == "-" else 1
    n = normalize(raw)
    if n in TYPE_DEBIT:
        return -1
    if n in TYPE_CREDIT:
        return 1
    m = TYPE_RE.match(n)
    if m:
        return -1 if m.group(2) == "debit" else 1
    return None


def read_text(path):
    data = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace")


def find_col(header, options, exclude=(), prefix_min=2):
    norm = [hnorm(c) for c in header]
    for o in options:
        for i, c in enumerate(norm):
            if c == o and i not in exclude:
                return i
    for i, c in enumerate(norm):
        if i not in exclude and any(len(o) >= prefix_min and c.startswith(o) for o in options):
            return i
    return None


def _infer_without_header(rows):
    """Files with no header (Wells Fargo "date","amount","*","","description"; Itau date;desc;amount)."""
    sample = [r for r in rows[:40] if len(r) >= 3]
    if len(sample) < 2:
        return None
    ncol = max(len(r) for r in sample)

    def frac(test, j):
        return sum(1 for r in sample if j < len(r) and test(r[j])) / len(sample)
    i_date = next((j for j in range(ncol) if frac(lambda x: parse_date(x) is not None, j) >= 0.6), None)
    if i_date is None:
        return None
    numeric = [j for j in range(ncol) if j != i_date and frac(lambda x: parse_amount(x) is not None, j) >= 0.6]
    if not numeric:
        return None
    cents = [j for j in numeric if frac(lambda x: bool(re.search(r"[.,]\d{2}\s*[-DC]?\s*\)?$", x.strip(), re.I)), j) >= 0.6]
    i_val = (cents or numeric)[0]
    i_desc = [j for j in range(ncol) if j not in (i_date, i_val) and j not in numeric
              and frac(lambda x: bool(normalize(x)), j) >= 0.5]
    return i_date, i_val, i_desc


def card_heuristic(rows_amount):
    """Charges-positive card export: every 'PAYMENT - THANK YOU' row is negative and most other rows are positive."""
    pay = [x for x in rows_amount if PAY_THANK_RE.search(normalize(x["desc"]))]
    other = [x for x in rows_amount if x not in pay]
    if not pay or not other:
        return None
    if all(x["amount"] < 0 for x in pay) and sum(1 for x in other if x["amount"] > 0) / len(other) >= 0.7:
        return True
    if all(x["amount"] > 0 for x in pay):
        return False
    return None


def read_rows(rows, path, warns, ctx):
    """Interprets table rows (CSV or spreadsheet). Returns (transactions, is_card_file)."""
    base = os.path.basename(path)
    idx = None
    for i, r in enumerate(rows[:40]):
        if find_col(r, COL_DATE) is not None and any(find_col(r, c) is not None for c in (COL_AMOUNT, COL_IN, COL_OUT)):
            idx = i
            break
    i_in = i_out = i_type = i_cat = None
    hset = set()
    if idx is None:
        inf = _infer_without_header(rows)
        if inf is None:
            raise ValueError(t("no_cols", f=path, h=rows[0] if rows else "(empty)"))
        i_date, i_val, i_desc = inf
        body = rows
        warns.append(t("w_noheader", f=base, d=i_date + 1, v=i_val + 1))
        br_hint = any(";" in "".join(r) for r in rows[:1]) or False
    else:
        header = rows[idx]
        hset = {hnorm(c) for c in header}
        body = rows[idx + 1:]
        i_date = find_col(header, COL_DATE)
        i_type = find_col(header, COL_TYPE, exclude={i_date}, prefix_min=4)
        used = {i_date, i_type}
        i_val = find_col(header, COL_AMOUNT, exclude=used)
        i_in = find_col(header, COL_IN, exclude=used | {i_val})
        i_out = find_col(header, COL_OUT, exclude=used | {i_val, i_in})
        i_cat = find_col(header, COL_CAT, exclude=used | {i_val, i_in, i_out}, prefix_min=5)
        used |= {i_val, i_in, i_out, i_cat}
        norm = [hnorm(c) for c in header]
        i_desc = [i for i, c in enumerate(norm) if i not in used and (c in COL_DESC or any(c.startswith(o) for o in COL_DESC))]
        br_hint = bool(BR_HEADER_WORDS & {w for c in norm for w in c.split()})
    if i_type is not None:  # use the type column only if it really holds debit/credit markers
        vals = [r[i_type] for r in body if i_type < len(r) and r[i_type].strip()]
        if not vals or sum(1 for v in vals if type_sign(v) is not None) / len(vals) < 0.6:
            i_type = None
    raw_dates = [r[i_date] for r in body if i_date < len(r)]
    if any(re.search(r",\d{2}\s*[-DC]?$", r[i_val].strip()) for r in body[:40] if i_val is not None and i_val < len(r)):
        br_hint = True
    order, ambiguous = (ctx["date_order"], False) if ctx.get("date_order") else detect_order(raw_dates, br_hint)
    if ambiguous and order:
        warns.append(t("w_date_amb", f=base, o="MM/DD" if order == "mdy" else "DD/MM",
                       x="dmy" if order == "mdy" else "mdy"))
    out, dropped = [], 0
    for r in body:
        if len(r) <= i_date:
            continue
        d = parse_date(r[i_date], order)
        if not d:
            continue
        parts = []
        for i in i_desc:
            p = r[i].strip() if i < len(r) else ""
            if p and normalize(p) and normalize(p) not in (normalize(x) for x in parts):
                parts.append(p)
        desc = " - ".join(parts)
        nd = normalize(desc)
        if nd.startswith(SKIP_DESC) or nd == "total":
            continue
        cells = [r[i] for i in (i_val, i_in, i_out) if i is not None and i < len(r) and r[i].strip()]
        v, src = None, "amount"
        if i_val is not None and i_val < len(r):
            v = parse_amount(r[i_val])
        if v is None:
            src = "cols"
            ent = parse_amount(r[i_in]) if i_in is not None and i_in < len(r) else None
            sai = parse_amount(r[i_out]) if i_out is not None and i_out < len(r) else None
            if ent:
                v = abs(ent)
            elif sai:
                v = -abs(sai)
            elif ent is not None or sai is not None:
                v = 0.0
        if v is not None and i_type is not None and i_type < len(r):
            sg = type_sign(r[i_type])
            if sg is not None:
                v, src = sg * abs(v), "type"
        if v is None:
            if cells:
                dropped += 1
            continue
        if v == 0:
            continue
        hint = r[i_cat].strip() if i_cat is not None and i_cat < len(r) else ""
        out.append({"date": d, "desc": desc, "amount": round(v, 2), "file": path, "src": src, "hint": hint})
    if dropped:
        warns.append(t("w_dropped", f=base, n=dropped))
    # credit-card sign convention
    amount_rows = [x for x in out if x["src"] == "amount"]
    amex_like = bool({"card member", "appears on your statement as"} & hset) or ({"trans date", "category"} <= hset)
    card_cols = amex_like or bool({"card no", "card number", "card", "cardholder", "card member"} & hset) \
        or {"post date", "category"} <= hset or {"reference number", "payee"} <= hset
    heur = card_heuristic(amount_rows) if amount_rows else None
    name_hint = re.search(r"amex|american ?express|discover", base, re.I) and heur is not False
    flip = False
    if path in ctx["not_card"] or not amount_rows:
        flip = False
    elif path in ctx["card"]:
        flip = True
        warns.append(t("w_card_forced", f=base))
    elif amex_like or heur or name_hint:
        flip = True
        warns.append(t("w_card_auto", f=base, b=path))
    if flip:
        for x in amount_rows:
            x["amount"] = -x["amount"]
    is_card = flip or card_cols or heur is not None or path in ctx["card"] \
        or any(PAY_THANK_RE.search(normalize(x["desc"])) for x in out)
    if is_card and not flip and path not in ctx["not_card"] and out \
            and sum(1 for x in out if x["amount"] > 0) / len(out) > 0.6:
        warns.append(t("w_card_pos", f=base, b=path))
    return out, is_card


def read_csv(path, warns, ctx):
    text = read_text(path)
    if "\x00" in text:
        raise ValueError(t("binary", f=path))
    lines = [l for l in text.splitlines() if l.strip()]
    sample = "\n".join(lines[:30])
    delim = max([";", ",", "\t", "|"], key=lambda d: sample.count(d))
    rows = list(csv.reader(io.StringIO("\n".join(lines)), delimiter=delim))
    return read_rows(rows, path, warns, ctx)


def _xlsx_col(ref):
    n = 0
    for ch in re.match(r"[A-Z]*", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path, warns, ctx):
    """First sheet of a simple .xlsx, read with zipfile + xml."""
    m = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            shared = []
            if "xl/sharedStrings.xml" in names:
                for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(m + "si"):
                    shared.append("".join(x.text or "" for x in si.iter(m + "t")))
            sheets = sorted((n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)),
                            key=lambda n: int(re.search(r"(\d+)\.xml$", n).group(1)))
            if not sheets:
                raise ValueError("no sheets")
            root = ET.fromstring(z.read(sheets[0]))
    except (zipfile.BadZipFile, ET.ParseError, KeyError, ValueError) as e:
        raise ValueError(t("xlsx_bad", f=path, e=e))
    rows = []
    for row in root.iter(m + "row"):
        cells = {}
        for k, c in enumerate(row.iter(m + "c")):
            j = _xlsx_col(c.get("r", "")) if c.get("r") else k
            typ, v = c.get("t"), c.find(m + "v")
            if typ == "s" and v is not None:
                val = shared[int(v.text)]
            elif typ == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(m + "t"))
            else:
                val = (v.text or "") if v is not None else ""
                if typ in (None, "n") and val:
                    try:
                        f = float(val)
                        val = str(int(f)) if f.is_integer() else f"{f:.2f}"
                    except ValueError:
                        pass
            cells[j] = val
        if cells:
            rows.append([cells.get(j, "") for j in range(max(cells) + 1)])
    return read_rows(rows, path, warns, ctx)


def read_ofx(path, warns, ctx):
    text = read_text(path)
    out = []
    for block in re.findall(r"<STMTTRN>(.*?)(?:</STMTTRN>|(?=<STMTTRN>)|(?=</BANKTRANLIST>))", text, re.S | re.I):
        def tag(n):
            mm = re.search(rf"<{n}>([^<\r\n]*)", block, re.I)
            return mm.group(1).strip() if mm else ""
        raw = tag("TRNAMT")
        v = float(raw) if re.fullmatch(r"[+-]?\d*\.?\d+", raw) else parse_amount(raw)
        d = parse_date(tag("DTPOSTED"))
        if d and v:
            desc = " ".join(x for x in (tag("NAME"), tag("MEMO")) if x)
            out.append({"date": d, "desc": desc, "amount": round(v, 2), "file": path, "fitid": tag("FITID"),
                        "src": "ofx", "hint": ""})
    if not out:
        raise ValueError(t("ofx_none", f=path))
    is_card = bool(re.search(r"<CCSTMTRS>|<CREDITCARDMSGSRSV1>", text, re.I))
    if path in ctx["card"]:  # OFX already uses negative = charge; --card on an OFX would be a mistake, so ignore it
        is_card = True
    return out, is_card


def read_file(path, warns, ctx):
    with open(path, "rb") as f:
        head = f.read(4096)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".ofx", ".qfx", ".qbo") or b"<OFX>" in head.upper():
        return read_ofx(path, warns, ctx)
    if head.startswith(b"%PDF") or ext == ".pdf":
        raise ValueError(t("pdf", f=path))
    if head.startswith(b"\xd0\xcf\x11\xe0") or ext == ".xls":
        raise ValueError(t("xls", f=path))
    if head.startswith(b"PK") or ext in (".xlsx", ".xlsm"):
        return read_xlsx(path, warns, ctx)
    return read_csv(path, warns, ctx)


def merge_files(per_file, warns):
    """Adds the files up. Removes repeats only when it is clearly the same statement exported twice:
    same FITID (OFX) or >= 80% of the overlapping period's transactions equal (date + amount)."""
    accepted = []
    for name, L in per_file:
        removed, sources = 0, []
        seen = {(l["fitid"], l["date"], l["amount"]) for _, A in accepted for l in A if l.get("fitid")}
        if seen:
            before = len(L)
            L = [l for l in L if not (l.get("fitid") and (l["fitid"], l["date"], l["amount"]) in seen)]
            if len(L) < before:
                removed += before - len(L)
                sources.append(t("w_dup_fitid"))
        for name_a, A in accepted:
            if not L or not A:
                continue
            ini = max(min(l["date"] for l in L), min(l["date"] for l in A))
            end = min(max(l["date"] for l in L), max(l["date"] for l in A))
            if ini > end:
                continue
            ca = Counter((l["date"], l["amount"]) for l in A if ini <= l["date"] <= end)
            cb = Counter((l["date"], l["amount"]) for l in L if ini <= l["date"] <= end)
            n_min = min(sum(ca.values()), sum(cb.values()))
            if n_min >= 3 and sum((ca & cb).values()) >= 0.8 * n_min:
                new = []
                for l in L:
                    k = (l["date"], l["amount"])
                    if ca[k] > 0:
                        ca[k] -= 1
                        removed += 1
                    else:
                        new.append(l)
                L = new
                sources.append(os.path.basename(name_a))
        if removed:
            warns.append(t("w_dup", f=os.path.basename(name), n=removed, o=", ".join(sources)))
        accepted.append((name, L))
    return [l for _, L in accepted for l in L]


# ---------------------------------------------------------------- categorization
def _compile(rules):
    comp = []
    for name, terms in rules:
        if isinstance(terms, str):
            terms = [terms]
        key = name if name in CATS or name.startswith("custom:") else resolve_category(name)
        comp.append((key, [(p, x) for p, x in ((compile_term(x), x) for x in terms) if p]))
    return comp


def hint_category(hint):
    h = normalize(hint)
    if not h or "payment" in h:
        return None
    for word, cat in HINTS:
        if re.search(r"\b" + word, h):
            return cat
    return None


def categorize(txns, rules_out, rules_in):
    out_c, in_c = _compile(rules_out), _compile(rules_in)
    hinted = 0
    for l in txns:
        d = " ".join(w for w in normalize(l["desc"]).split() if w != "des")  # BofA/ACH "NAME DES:TYPE ID:..."
        rules, cat = (in_c, "other_in") if l["amount"] > 0 else (out_c, "other_out")
        for name, pats in rules:
            hit = next((x for p, x in pats if p.search(d)), None)
            if hit is not None:
                cat, l["term"] = name, hit
                break
        else:
            if l["amount"] < 0 and hint_category(l.get("hint", "")):
                cat = hint_category(l["hint"])
                hinted += 1
        l["cat"] = cat
    return hinted


# ---------------------------------------------------------------- summary
def money(v):
    return ("-$" if v < 0 else "$") + f"{abs(v):,.2f}"


def pct(a, b):
    return f"{a / b * 100:.1f}%" if b else "—"


def fdate(d, short=False):
    if LANG == "en":
        return d.strftime("%m/%d" if short else "%m/%d/%Y")
    return d.strftime("%d/%m" if short else "%d/%m/%Y")


def month_name(m):
    y, mm = int(m[:4]), int(m[5:7])
    return f"{MONTHS['en'][mm - 1]} {y}" if LANG == "en" else f"{MONTHS['pt'][mm - 1]} de {y}"


def summarize(txns):
    inc, exp = defaultdict(float), defaultdict(float)
    transf = card_out = card_in = loans_in = draws = 0.0
    for l in txns:
        c, v = l["cat"], l["amount"]
        if c == "transfer":
            transf += v
        elif c == "card_payment":
            card_out += -v if v < 0 else 0
            card_in += v if v > 0 else 0
        elif c == "loan_in":
            loans_in += v
        elif c == "owner_draw":
            draws += -v
        elif v > 0 or cost_type(c) == "contra":
            inc[c] += v
        else:
            exp[c] += -v
    ti, to = sum(inc.values()), sum(exp.values())
    fixed = sum(v for c, v in exp.items() if cost_type(c) == "fixed")
    var = to - fixed
    cm = (ti - var) / ti if ti else 0
    sales = sum(v for c, v in inc.items() if c in SALES_KEYS or c.startswith("custom:"))
    labor = sum(exp.get(k, 0) for k in LABOR_KEYS)
    big = [l for l in txns if l["amount"] > 0 and l["cat"] not in OUT_OF_RESULT and l["cat"] not in ("refunds", "interest", "commissions")
           and (l["cat"] == "cust_deposits" or (ti and l["amount"] >= max(5000, 0.25 * ti)
                                                 and l["cat"] not in ("sales_card", "sales_apps")))]
    payers, payer_cats = defaultdict(float), defaultdict(set)
    for l in txns:
        if l["amount"] > 0 and l["cat"] not in OUT_OF_RESULT and l["cat"] not in CONCENTRATION_SKIP:
            payers[payer(l)] += l["amount"]
            payer_cats[payer(l)].add(l["cat"])
    top = max(payers.items(), key=lambda x: x[1]) if payers else ("", 0)
    return {"cash_in_by_key": {c: round(v, 2) for c, v in inc.items()},
            "cash_out_by_key": {c: round(v, 2) for c, v in exp.items()},
            "total_cash_in": round(ti, 2), "total_cash_out": round(to, 2), "operating_result": round(ti - to, 2),
            "owner_draws": round(draws, 2), "result_after_draws": round(ti - to - draws, 2),
            "sales_deposits": round(sales, 2), "transfers_net": round(transf, 2),
            "card_payments_made": round(card_out, 2), "card_payments_received_on_cards": round(card_in, 2),
            "loans_contributions_in": round(loans_in, 2), "fixed_costs": round(fixed, 2),
            "variable_costs": round(var, 2), "contribution_margin_pct": round(cm * 100, 1) if ti else None,
            "break_even": round(fixed / cm, 2) if cm > 0 else None,
            "labor_pct": round(labor / ti * 100, 1) if ti and labor else None,
            "chargebacks": round(-inc.get("chargebacks", 0), 2),
            "materials": round(exp.get("supplies", 0) + exp.get("equipment", 0), 2),
            "large_receipts": [{"date": l["date"].isoformat(), "amount": l["amount"], "category": l["cat"]} for l in big],
            "top_payer": top[0], "top_payer_amount": round(top[1], 2),
            "top_payer_is_carrier": bool(top[0]) and payer_cats[top[0]] == {"commissions"},
            "top_payer_pct": round(top[1] / ti * 100, 1) if ti else None, "transaction_count": len(txns)}


CONCENTRATION_SKIP = {"sales_card", "sales_apps", "sales_deposit", "refunds", "interest"}
PAYER_CUT = re.compile(r"\b(des|id|orig id|indn|co id|conf|confirmation|transaction|ref|ppd|ccd|web|ach|ppd id)\b.*$")
PAYER_LEAD = ("zelle payment from", "zelle from", "venmo from", "venmo cashout", "payment from", "deposit from",
              "orig co name", "ach credit", "ach deposit", "wire type wire in", "incoming wire from", "wire in")


def payer(l):
    """Who paid: the carrier term for commissions, otherwise the first words of the description."""
    if l["cat"] == "commissions" and l.get("term") and normalize(l["term"]) not in ("commission", "comm pymt", "comm pmt"):
        n = normalize(l["term"].rstrip("*"))
        if not n.startswith(("commission", "comm ", "advisory", "renewal", "override")):
            return n
    n = normalize(l["desc"])
    for lead in PAYER_LEAD:
        if n.startswith(lead):
            n = n[len(lead):].strip()
    n = PAYER_CUT.sub("", n)
    words = [w for w in n.split() if not any(ch.isdigit() for ch in w)]
    return " ".join(words[:3]) or normalize(l["desc"])[:20]


def prev_month(m):
    y, mm = int(m[:4]), int(m[5:7])
    return f"{y - 1}-12" if mm == 1 else f"{y}-{mm - 1:02d}"


def looks_incomplete(txns):
    days = [l["date"].day for l in txns]
    return not days or min(days) > 7 or max(days) < 24


EST_TAX_DUE = {3: "04/15", 5: "06/15", 8: "09/15", 12: "01/15"}

# Business kind, used only to word alerts (job-deposit alert is for construction/trades, never for insurance).
INDUSTRY_HINTS = {
    "insurance": ("insurance", "insurer", "annuit", "financial advis",
                  "broker dealer", "seguro", "seguradora", "corretor", "corretora", "agencia de seguros"),
    "construction": ("construction", "contractor", "remodel", "renovation", "roofing", "roofer", "plumb", "hvac",
                     "electric", "landscap", "painting", "painter", "handyman", "flooring", "carpent", "drywall",
                     "concrete", "masonry", "builder", "trades", "construcao", "empreiteir", "reforma", "obra",
                     "pintura", "encanad", "eletricist", "telhad", "paisagism", "marcenari"),
}
CONSTRUCTION_SUPPLY = {"home depot", "the home depot", "homedepot", "lowe s", "lowes", "menards", "harbor freight",
                       "grainger", "ferguson", "sherwin williams", "abc supply", "84 lumber", "builders firstsource",
                       "lumber*", "beacon roofing", "srs distribution", "fastenal", "white cap", "hd supply",
                       "floor decor", "benjamin moore", "kelly moore", "plumbing supply", "electrical supply",
                       "ready mix", "concrete", "drywall", "roofing supply"}
CONSTRUCTION_DEPOSIT = {"draw request", "construction draw", "progress payment", "progress billing", "retainage",
                        "retention release", "job deposit", "project deposit"}


def industry_from_hint(hint):
    n = normalize(hint or "")
    if not n:
        return None
    for kind in ("insurance", "construction"):
        if any(k in n for k in INDUSTRY_HINTS[kind]):
            return kind
    return "general"


def business_kind(r, txns, hint=None):
    """'insurance' | 'construction' | 'general' from the --industry hint or the categories seen."""
    kind = industry_from_hint(hint)
    if kind:
        return kind
    ti = r["total_cash_in"]
    if r["cash_in_by_key"].get("commissions", 0) > 0 and (not ti or r["cash_in_by_key"]["commissions"] >= 0.5 * ti):
        return "insurance"
    exp = r["cash_out_by_key"]
    supply = -sum(l["amount"] for l in txns if l["amount"] < 0 and l["cat"] == "supplies"
                  and l.get("term") in CONSTRUCTION_SUPPLY)
    if (exp.get("equipment", 0) > 0 or exp.get("contractors", 0) > 0 or supply >= 300
            or any(l["cat"] == "cust_deposits" and l.get("term") in CONSTRUCTION_DEPOSIT for l in txns)):
        return "construction"
    return "general"


def alerts(r, txns, prev, compare, card_files, month, no_desc=False, industry=None):
    """no_desc: no counterparty names in any alert. industry: optional --industry hint."""
    a = []
    kind = business_kind(r, txns, industry)
    ti, to = r["total_cash_in"], r["total_cash_out"]
    exp = r["cash_out_by_key"]
    if r["operating_result"] < 0:
        a.append(t("a_neg", v=money(-r["operating_result"])))
    elif r["owner_draws"] and r["result_after_draws"] < 0:
        a.append(t("a_neg_draw", d=money(r["owner_draws"]), v=money(-r["result_after_draws"])))
    rev = sum(exp.get(k, 0) for k in REVIEW_KEYS)
    if to and rev / to > 0.15:
        a.append(t("a_uncat", p=pct(rev, to), v=money(rev)))
    oin = r["cash_in_by_key"].get("other_in", 0)
    if ti and oin / ti > 0.15:
        a.append(t("a_uncat_in", p=pct(oin, ti), v=money(oin)))
    fees = exp.get("fees", 0)
    base = r["sales_deposits"] or ti
    if base and fees / base > 0.03:
        a.append(t("a_fees", v=money(fees), p=pct(fees, base)))
    od = [l for l in txns if l["amount"] < 0 and l["cat"] not in OUT_OF_RESULT and OVERDRAFT_RE.search(normalize(l["desc"]))]
    if od:
        a.append(t("a_overdraft", v=money(-sum(l["amount"] for l in od)), n=len(od)))
    loans = exp.get("loan_pay", 0)
    if ti and loans / ti > 0.15:
        a.append(t("a_loans", p=pct(loans, ti), v=money(loans)))
    if r["labor_pct"] and r["labor_pct"] > 45:
        a.append(t("a_labor", p=f"{r['labor_pct']:.1f}%"))
    if r["card_payments_made"]:
        if card_files:
            a.append(t("a_card_with", v=money(r["card_payments_made"]), f=", ".join(card_files)))
        else:
            a.append(t("a_card_without", v=money(r["card_payments_made"])))
    mm, yy = int(month[5:7]), int(month[:4])
    if mm in EST_TAX_DUE:
        due_y = yy + 1 if mm == 12 else yy
        md = EST_TAX_DUE[mm]
        due = date(due_y, int(md[:2]), int(md[3:]))
        a.append(t("a_est_tax", d=fdate(due), v=money(exp.get("taxes", 0))))
    if exp.get("sales_tax"):
        a.append(t("a_sales_tax", v=money(exp["sales_tax"])))
    people = [l for l in txns if l["cat"] == "people_review"]
    if people:
        a.append(t("a_people", n=len(people), v=money(-sum(l["amount"] for l in people))))
    if r["loans_contributions_in"]:
        a.append(t("a_loan_in", v=money(r["loans_contributions_in"])))
    if prev and compare:
        if prev["total_cash_in"] and ti < prev["total_cash_in"] * 0.85:
            a.append(t("a_in_drop", p=pct(prev["total_cash_in"] - ti, prev["total_cash_in"])))
        for c, v in exp.items():
            va = prev["cash_out_by_key"].get(c, 0)
            if va >= 200 and v > va * 1.3:
                a.append(t("a_cat_up", c=label(c), a=money(va), b=money(v), p=pct(v - va, va)))
    if r["top_payer_pct"] and r["top_payer_pct"] >= 40 and r["top_payer_amount"] >= 1000:
        key = "a_concentration_carrier" if r.get("top_payer_is_carrier") else "a_concentration"
        if no_desc:
            a.append(t(key + "_anon", p=f"{r['top_payer_pct']:.1f}%", v=money(r["top_payer_amount"])))
        else:
            a.append(t(key, w=r["top_payer"].upper(), p=f"{r['top_payer_pct']:.1f}%", v=money(r["top_payer_amount"])))
    cb = r["chargebacks"]
    if cb:
        base_c = r["cash_in_by_key"].get("commissions", 0) or (r["sales_deposits"] or ti)
        prev_cb = prev["chargebacks"] if prev else 0
        if (base_c and cb / base_c > 0.10) or (prev and compare and cb >= 200 and cb > 1.5 * prev_cb):
            a.append(t("a_chargebacks", v=money(cb), p=pct(cb, base_c), q=money(prev_cb) if prev else "—"))
    mat = r["materials"]
    if mat >= 500 and ti:
        if mat / ti > 0.6:
            a.append(t("a_materials_high", v=money(mat), p=pct(mat, ti)))
        elif prev and compare and prev["total_cash_in"] and mat / ti - prev["materials"] / prev["total_cash_in"] >= 0.10:
            a.append(t("a_materials_up", p=pct(mat, ti), q=pct(prev["materials"], prev["total_cash_in"])))
    if r["large_receipts"] and kind != "insurance":
        tot = sum(x["amount"] for x in r["large_receipts"])
        mx = max(r["large_receipts"], key=lambda x: x["amount"])
        a.append(t("a_big_deposits" if kind == "construction" else "a_big_deposits_gen", n=len(r["large_receipts"]), v=money(tot), m=money(mx["amount"]),
                   d=fdate(date.fromisoformat(mx["date"]))))
    grp = defaultdict(list)
    for l in txns:
        if l["amount"] < 0:
            grp[(normalize(l["desc"])[:40], l["amount"])].append(l)
    dup = [k for k, v in grp.items() if len(v) > 1 and abs(k[1]) >= 100 and len({x["date"] for x in v}) < len(v)]
    if dup:
        a.append(t("a_dup", n=len(dup)))
    return a


def load_rules(path):
    """User rules JSON: {"expenses": [[category, [terms]]], "income": [...]} (or a {category: [terms]} object).
    Portuguese keys "despesas"/"receitas" also work."""
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except OSError as e:
        raise ValueError(t("rules_open", p=path, e=e.strerror))
    except json.JSONDecodeError as e:
        raise ValueError(t("rules_json", p=path, l=e.lineno, c=e.colno, m=e.msg))
    if not isinstance(raw, dict):
        raise ValueError(t("rules_obj", p=path))
    result = {}
    for key, alts in (("expenses", ("expenses", "despesas", "outflows", "saidas")),
                      ("income", ("income", "receitas", "inflows", "entradas"))):
        rules = []
        for alt in alts:
            if alt in raw:
                rules = raw[alt]
                break
        if isinstance(rules, dict):
            rules = list(rules.items())
        ok = []
        for item in rules if isinstance(rules, list) else [None]:
            if not (isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], str)):
                raise ValueError(t("rules_item", p=path, k=key, i=repr(item)))
            terms = [item[1]] if isinstance(item[1], str) else item[1]
            if not isinstance(terms, list) or not all(isinstance(x, str) for x in terms):
                raise ValueError(t("rules_terms", p=path, c=item[0]))
            ok.append([resolve_category(item[0]), terms])
        result[key] = ok
    return result


def labeled(r):
    """Summary with category labels (in the chosen language) for the JSON output."""
    out = dict(r)
    out["cash_in"] = {label(c): v for c, v in r["cash_in_by_key"].items()}
    out["cash_out"] = {label(c): v for c, v in r["cash_out_by_key"].items()}
    return out


def main():
    global LANG
    ap = argparse.ArgumentParser(description="Monthly management report from bank/card exports")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--lang", choices=["en", "pt"], default="en")
    ap.add_argument("--rules", "--regras", dest="rules")
    ap.add_argument("--out-csv", "--saida-csv", dest="out_csv")
    ap.add_argument("--out-json", "--saida-json", dest="out_json")
    ap.add_argument("--month", "--mes", dest="month", help="YYYY-MM")
    ap.add_argument("--no-descriptions", "--sem-descricoes", dest="no_desc", action="store_true")
    ap.add_argument("--card", action="append", default=[], help="credit-card file whose charges are positive")
    ap.add_argument("--not-card", action="append", default=[], help="turn off card sign detection for this file")
    ap.add_argument("--date-order", choices=["mdy", "dmy"])
    ap.add_argument("--industry", "--setor", dest="industry",
                    help="business type hint, e.g. construction, insurance agency, bakery / tipo de negócio")
    a = ap.parse_args()
    LANG = a.lang

    def fail(msg):
        print(f"{t('err')}: {msg}", file=sys.stderr)
        sys.exit(1)

    for target in (a.out_csv, a.out_json):
        if target and not os.path.isdir(os.path.dirname(os.path.abspath(target))):
            fail(t("no_dir", p=target, d=os.path.dirname(target) or "."))
    if a.month and not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", a.month):
        fail(t("bad_month"))
    try:
        extra = load_rules(a.rules) if a.rules else None
    except ValueError as e:
        fail(e)
    rules_out, rules_in = build_rules(extra)
    ctx = {"card": set(a.card), "not_card": set(a.not_card), "date_order": a.date_order}

    warns, per_file, card_files = [], [], []
    for f in dict.fromkeys(a.files):
        try:
            txns, is_card = read_file(f, warns, ctx)
        except OSError as e:
            fail(f"{f}: {e.strerror}")
        except (ValueError, csv.Error) as e:
            fail(e)
        per_file.append((f, txns))
        if is_card:
            card_files.append(os.path.basename(f))
    txns = merge_files(per_file, warns)
    if not txns:
        fail(t("no_txn"))
    txns.sort(key=lambda x: x["date"])
    hinted = categorize(txns, rules_out, rules_in)
    if hinted:
        warns.append(t("w_hint", n=hinted))

    by_month = defaultdict(list)
    for l in txns:
        by_month[l["date"].strftime("%Y-%m")].append(l)
    months = sorted(by_month)
    target = a.month or months[-1]
    if target not in by_month:
        fail(t("month_missing", m=target, ms=", ".join(months)))
    sums = {m: summarize(by_month[m]) for m in months}
    pm = prev_month(target)
    prev = sums.get(pm)
    compare = True
    for m in (target, pm):
        if m in by_month and looks_incomplete(by_month[m]):
            ds = sorted(l["date"] for l in by_month[m])
            warns.append(t("w_incomplete", m=m, a=fdate(ds[0], True), b=fdate(ds[-1], True)))
            compare = False
    if prev is None and len(months) > 1:
        warns.append(t("w_noprev", p=pm, m=target))
    r = sums[target]
    al = alerts(r, by_month[target], prev, compare, card_files, target, a.no_desc, a.industry)
    if a.no_desc:   # no counterparty names anywhere in the report or the JSON
        for s_ in sums.values():
            s_["top_payer"] = None

    days = sorted({l["date"] for l in by_month[target]})
    ti = r["total_cash_in"]
    out = [f"# {t('title', m=month_name(target))}", "",
           t("period", a=fdate(days[0]), b=fdate(days[-1]), n=r["transaction_count"], f=len(per_file)), ""]
    if warns:
        out += [f"## {t('h_warn')}", ""] + [f"- {x}" for x in warns] + [""]
    out += [f"| {t('ind')} | {t('val')} |", "|---|---|",
            f"| {t('r_in')} | {money(ti)} |",
            f"| {t('r_out')} | {money(r['total_cash_out'])} |",
            f"| **{t('r_res')}** | **{money(r['operating_result'])}** |",
            f"| {t('r_margin')} | {pct(r['operating_result'], ti)} |"]
    if r["owner_draws"]:
        out += [f"| {t('r_draws')} | {money(r['owner_draws'])} |",
                f"| {t('r_after')} | {money(r['result_after_draws'])} |"]
    out += [f"| {t('r_fixvar')} | {money(r['fixed_costs'])} / {money(r['variable_costs'])} |",
            f"| {t('r_be')} | {money(r['break_even']) if r['break_even'] is not None else t('r_be_none')} |"]
    if r["labor_pct"]:
        out.append(f"| {t('r_labor')} | {r['labor_pct']:.1f}% |")
    if prev:
        out.append(f"| {t('r_prev', m=pm)} | {money(prev['operating_result'])} |")
    if r["transfers_net"]:
        out.append(f"| {t('r_transf')} | {money(r['transfers_net'])} |")
    if r["card_payments_made"]:
        out.append(f"| {t('r_card')} | {money(r['card_payments_made'])} |")
    if r["loans_contributions_in"]:
        out.append(f"| {t('r_loan_in')} | {money(r['loans_contributions_in'])} |")
    out += ["", f"## {t('h_in')}", "", f"| {t('src')} | {t('val')} | % |", "|---|---|---|"]
    for c, v in sorted(r["cash_in_by_key"].items(), key=lambda x: -x[1]):
        out.append(f"| {label(c)} | {money(v)} | {pct(v, ti)} |")
    pcol = f" {t('prev')} |" if prev else ""
    out += ["", f"## {t('h_out')}", "", f"| {t('cat')} | {t('type')} | {t('val')} | {t('pct_in')} |" + pcol,
            "|---|---|---|---|" + ("---|" if prev else "")]
    rows_out = sorted(r["cash_out_by_key"].items(), key=lambda x: -x[1])
    if r["owner_draws"]:
        rows_out.append(("owner_draw", r["owner_draws"]))
    for c, v in rows_out:
        line = f"| {label(c)} | {t(cost_type(c))} | {money(v)} | {pct(v, ti)} |"
        if prev:
            pv = prev["owner_draws"] if c == "owner_draw" else prev["cash_out_by_key"].get(c, 0)
            line += f" {money(pv)} |"
        out.append(line)
    if not a.no_desc:
        top = sorted([l for l in by_month[target] if l["amount"] < 0 and l["cat"] not in OUT_OF_RESULT
                      and cost_type(l["cat"]) != "contra"],
                     key=lambda x: x["amount"])[:10]
        out += ["", f"## {t('h_top')}", "", f"| {t('dt')} | {t('desc')} | {t('cat')} | {t('val')} |", "|---|---|---|---|"]
        for l in top:
            out.append(f"| {fdate(l['date'], True)} | {l['desc'][:50].replace('|', '/')} | {label(l['cat'])} | {money(l['amount'])} |")
    wk = defaultdict(float)
    for l in by_month[target]:
        if l["cat"] not in OUT_OF_RESULT and l["cat"] != "owner_draw":
            wk[(l["date"].day - 1) // 7 + 1] += l["amount"]
    out += ["", f"## {t('h_week')}", "", f"| {t('week')} | {t('wk_net')} | {t('cum')} |", "|---|---|---|"]
    acc = 0.0
    for s in sorted(wk):
        acc += wk[s]
        out.append(f"| {t('wk_lbl', s=s, a=(s - 1) * 7 + 1, b=min(s * 7, 31))} | {money(wk[s])} | {money(acc)} |")
    out += ["", f"## {t('h_alerts')}", ""]
    out += [f"- {x}" for x in al] or [f"- {t('a_none')}"]
    if len(months) > 1:
        out += ["", f"## {t('h_trend')}", "", f"| {t('month')} | {t('r_in')} | {t('r_out')} | {t('res')} |", "|---|---|---|---|"]
        for m in months:
            rm = sums[m]
            out.append(f"| {m} | {money(rm['total_cash_in'])} | {money(rm['total_cash_out'])} | {money(rm['operating_result'])} |")
    out += ["", t("note")]
    print("\n".join(out))

    if a.out_csv:
        with open(a.out_csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["date", "description", "amount", "category", "file"] if LANG == "en"
                       else ["data", "descricao", "valor", "categoria", "arquivo"])
            for l in txns:
                w.writerow([l["date"].isoformat(), l["desc"], f"{l['amount']:.2f}", label(l["cat"]),
                            os.path.basename(l["file"])])
    if a.out_json:
        with open(a.out_json, "w", encoding="utf-8") as f:
            json.dump({"month": target, "previous_month": pm if prev else None, "lang": LANG,
                       "summary": labeled(r), "alerts": al, "warnings": warns, "card_files": card_files,
                       "months": {m: labeled(s) for m, s in sums.items()}},
                      f, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    main()
