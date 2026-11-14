#!/usr/bin/env python3
"""Create the company work folder from the onboarding profile (bilingual: en / pt).
Cria a pasta de trabalho da empresa a partir do perfil do onboarding (bilíngue: en / pt).

Usage / Uso:
    python3 criar_estrutura.py --perfil profile.json --destino "~/Documents/My-Company" [--lang en|pt]

- Folder and file names follow the profile's `idioma` (pt | en; default en).
- `--lang` sets the language of this script's messages (default: the profile's `idioma`, else en).
- Standard library only (macOS, Linux, Windows). Never overwrites existing files: they are kept and listed.
- The whole input is validated and normalized before any file is created.
"""

import argparse
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REF = SKILL_DIR / "references"
ASSETS = SKILL_DIR / "assets"
MSG_LANG = "en"

# ------------------------------------------------------------------ folder contract (see the brief / SKILL.md)
PASTAS = {
    "en": {"company": "00-company", "profile": "00-company/company-profile.md", "sector": "00-company/industry.md",
           "brand": "00-company/brand.md", "brand_json": "00-company/brand.json",
           "marketing": "01-marketing", "finance": "02-finance", "it": "03-it", "admin": "04-admin",
           "hr": "05-hr", "sales": "06-sales", "legal": "07-legal", "operations": "08-operations",
           "strategy": "09-strategy", "personas": "personas", "routines": "routines", "templates": "templates",
           "confidential": "confidential", "maps": "confidential/maps",
           "tools": "tools/detectar_dados_sensiveis.py", "security": "SECURITY.md",
           "deliverables": "99-deliverables"},
    "pt": {"company": "00-empresa", "profile": "00-empresa/perfil-da-empresa.md", "sector": "00-empresa/setor.md",
           "brand": "00-empresa/marca.md", "brand_json": "00-empresa/marca.json",
           "marketing": "01-marketing", "finance": "02-financas", "it": "03-ti", "admin": "04-administrativo",
           "hr": "05-rh", "sales": "06-comercial", "legal": "07-juridico", "operations": "08-operacoes",
           "strategy": "09-estrategia", "personas": "personas", "routines": "rotinas", "templates": "modelos",
           "confidential": "confidencial", "maps": "confidencial/mapas",
           "tools": "ferramentas/detectar_dados_sensiveis.py", "security": "SEGURANCA.md",
           "deliverables": "99-entregas"},
}
AREAS = ["marketing", "finance", "it", "admin", "hr", "sales", "legal", "operations", "strategy"]
PERSONA_ARQ = {"en": {a: a for a in AREAS},
               "pt": {"marketing": "marketing", "finance": "financas", "it": "ti", "admin": "administrativo",
                      "hr": "rh", "sales": "comercial", "legal": "juridico", "operations": "operacoes",
                      "strategy": "estrategia"}}
# Keys already normalized by norm(): lowercase, no accents, no punctuation.
ALIASES = {
    "marketing": "marketing", "marketing e marca": "marketing", "marketing and brand": "marketing",
    "brand": "marketing", "marca": "marketing", "mkt": "marketing", "comunicacao": "marketing",
    "advertising": "marketing", "publicidade": "marketing", "social media": "marketing",
    "finance": "finance", "finances": "finance", "financas": "finance", "financeiro": "finance",
    "accounting": "finance", "contabilidade": "finance", "bookkeeping": "finance", "controladoria": "finance",
    "financas e controladoria": "finance", "financas e contabilidade": "finance", "finance and accounting": "finance",
    "taxes": "finance", "tax": "finance", "impostos": "finance", "fiscal": "finance",
    "it": "it", "ti": "it", "t i": "it", "i t": "it", "tech": "it", "technology": "it", "tecnologia": "it",
    "it and technology": "it", "ti e tecnologia": "it", "informatica": "it", "sistemas": "it",
    "admin": "admin", "administrative": "admin", "administration": "admin", "administrativo": "admin",
    "administracao": "admin", "adm": "admin", "processes": "admin", "processos": "admin", "office": "admin",
    "admin and processes": "admin", "administrativo e processos": "admin", "secretaria": "admin",
    "hr": "hr", "rh": "hr", "human resources": "hr", "recursos humanos": "hr", "people": "hr", "pessoas": "hr",
    "hr and people": "hr", "rh e pessoas": "hr", "payroll": "hr", "folha": "hr", "hiring": "hr",
    "sales": "sales", "vendas": "sales", "comercial": "sales", "comercial e vendas": "sales",
    "sales and customers": "sales", "comercial e clientes": "sales", "business development": "sales",
    "legal": "legal", "juridico": "legal", "compliance": "legal", "legal and compliance": "legal",
    "juridico e compliance": "legal", "direito": "legal", "contracts": "legal", "contratos": "legal",
    "operations": "operations", "operacoes": "operations", "ops": "operations", "logistics": "operations",
    "logistica": "operations", "operations and logistics": "operations", "operacoes e logistica": "operations",
    "producao": "operations", "production": "operations",
    "strategy": "strategy", "estrategia": "strategy", "management": "strategy", "gestao": "strategy",
    "planning": "strategy", "planejamento": "strategy", "diretoria": "strategy", "advisor": "strategy",
}
SETOR_ALIASES = {
    "legal": ["juridico", "advocacia", "law", "law firm", "lawyer", "attorney", "immigration", "imigracao",
              "escritorio de advocacia", "paralegal"],
    "accounting": ["contabilidade", "contabil", "tax prep", "tax preparation", "tax preparer", "bookkeeping",
                   "cpa", "imposto de renda", "taxes", "payroll services"],
    "health": ["saude", "clinic", "clinica", "dental", "dentist", "therapy", "terapia", "wellness", "med spa",
               "medspa", "chiropractic", "home health", "home care", "physical therapy", "fisioterapia", "estetica"],
    "retail-ecommerce": ["varejo", "ecommerce", "e commerce", "varejo ecommerce", "retail", "loja", "store",
                         "online store", "loja virtual"],
    "services": ["servicos", "cleaning", "limpeza", "house cleaning", "construction cleaning", "post construction cleaning", "beauty", "beleza", "salon", "salao",
                 "nails", "unhas", "lashes", "home services", "landscaping", "jardinagem", "translation",
                 "traducao", "consulting", "consultoria"],
    "construction": ["construcao", "construction", "contractor", "builder", "builders", "remodeling", "reforma",
                     "reformas", "trades", "painting", "pintura", "flooring", "plumbing", "electrical", "hvac",
                     "industria", "empreiteira"],
    "real-estate": ["imobiliaria", "imobiliario", "real estate", "realtor", "corretor de imoveis",
                    "property management", "administracao de imoveis"],
    "food": ["alimentacao", "food", "restaurant", "restaurante", "bakery", "padaria", "confeitaria",
             "food truck", "catering", "cafe", "cottage food", "lanchonete"],
    "education": ["educacao", "education", "tutoring", "aulas", "school", "escola", "daycare", "creche",
                  "language school", "escola de idiomas", "lessons"],
    "technology": ["tecnologia", "technology", "software", "saas", "it services", "msp", "agency", "agencia",
                   "web agency", "marketing agency", "agencia de marketing"],
    "insurance": ["seguros", "seguro", "insurance", "insurance agency", "insurance agent", "life insurance",
                  "seguro de vida", "corretora de seguros", "corretor de seguros", "health insurance"],
    "financial-services": ["financeira", "financeiro", "financial services", "servicos financeiros", "loans",
                           "emprestimos", "mortgage", "hipoteca", "mortgage broker", "loan broker", "lender",
                           "financial advisor", "financial planner", "planejador financeiro", "credit repair",
                           "money transmitter", "remittance", "remessas", "envio de dinheiro", "ria"],
}
NIVEIS = {"standard": "standard", "padrao": "standard", "basic": "standard", "normal": "standard",
          "elevated": "elevated", "elevado": "elevated", "high": "elevated", "alto": "elevated",
          "regulated": "regulated", "regulado": "regulated", "sigilo": "regulated", "confidential": "regulated"}
NIVEL_PT = {"standard": "padrao", "elevated": "elevado", "regulated": "regulado"}

# Profile JSON accepts Portuguese keys (canonical) or English aliases.
CHAVES_EN = {
    "name": "nome", "company_name": "nome", "what_it_does": "o_que_faz", "industry": "setor", "sector": "setor",
    "segment": "segmento", "years_in_business": "tempo_de_mercado", "location": "localizacao",
    "size": "porte", "ideal_customer": "cliente_ideal", "acquisition_channels": "canais_aquisicao",
    "competitors_differentiators": "concorrentes_diferenciais", "pricing_and_billing": "ticket_e_cobranca",
    "team": "equipe", "tools": "ferramentas", "entity_type": "tipo_entidade", "states": "estados",
    "sales_tax": "imposto_vendas", "payment_methods": "formas_pagamento", "user_role": "papel_usuario",
    "user_routine": "rotina_usuario", "challenges": "desafios", "goal_12_months": "objetivo_12_meses",
    "tone": "tom", "sensitivity_level": "nivel_sensibilidade", "security_level": "nivel_sensibilidade",
    "data_handled": "dados_tratados", "ai_policy": "politica_ia", "onboarding_date": "data_onboarding",
    "custom_industry_md": "setor_personalizado_md", "extra_personas": "personas_extras",
    "language": "idioma", "deliverables_language": "idioma_entregas",
}

# ------------------------------------------------------------------ texts
CAMPOS_PERFIL = [  # (key, en label, pt label)
    ("o_que_faz", "What it does", "O que faz"),
    ("segmento", "Industry / segment", "Setor / segmento"),
    ("tipo_entidade", "Entity type and tax status", "Tipo de empresa e tributação"),
    ("estados", "State(s) of operation", "Estado(s) onde atua"),
    ("tempo_de_mercado", "Years in business", "Tempo de mercado"),
    ("localizacao", "Location / service area", "Localização / atendimento"),
    ("porte", "Size", "Porte"),
    ("cliente_ideal", "Ideal customer", "Cliente ideal"),
    ("canais_aquisicao", "How customers find us", "Como os clientes chegam"),
    ("concorrentes_diferenciais", "Competitors and differentiators", "Concorrentes e diferenciais"),
    ("ticket_e_cobranca", "Average ticket and billing", "Ticket médio e forma de cobrança"),
    ("formas_pagamento", "Payment methods accepted", "Formas de pagamento aceitas"),
    ("imposto_vendas", "Sales tax", "Sales tax (imposto sobre vendas)"),
    ("equipe", "Team (W-2 employees / 1099 contractors)", "Equipe (funcionários W-2 / autônomos 1099)"),
    ("ferramentas", "Current tools", "Ferramentas atuais"),
    ("papel_usuario", "Role of the person using this folder", "Papel de quem usa esta pasta"),
    ("objetivo_12_meses", "6–12 month goal", "Objetivo para 6–12 meses"),
    ("tom", "Communication tone", "Tom de comunicação"),
    ("politica_ia", "Internal AI policy", "Política interna de IA"),
]
TX = {
    "en": {
        "na": "(not provided)", "profile_title": "Company profile — {n}", "onboarded": "_Onboarding on {d}._",
        "lang_line": "- **Working language:** `{i}` · **Deliverables language:** `{e}`",
        "level_line": "- **Security level:** `{v}`",
        "routine": "Routine of the person using this folder", "challenges": "Biggest challenges",
        "data": "Types of data handled (categories only, never the data itself)",
        "notes": "Notes", "notes_tx": "_Lasting facts about the company. Never record customer data here._",
        "specialist": "Specialist", "card": "full card in", "call_me": "Call me when",
        "tbd": "(to be defined with the user)", "adj": "Industry adjustments",
        "adj_more": "_More in `../{s}` (section \"Persona adjustments\")._",
        "first": "Suggested first deliverables", "first_none": "(define with the specialist)",
        "how": "How to ask", "how_tx": 'Open the company folder in Claude and say: _"{n}, {x}"_.',
        "help_area": "help me with this area",
        "extra_intro": "**Industry specialist created during onboarding.** Also follow `{s}`.",
        "extra_first": "First deliverables", "specialist_default": "Specialist", "sector_tag": " _(industry)_",
        "pb_stub": "# {t}\n\n(Complete it following the playbook format: inputs, steps, deliverable, checklist, "
                   "lessons learned.)\n",
        "routines_readme": "# Routines (playbooks)\n\nRecipes Claude follows to run the company's recurring tasks "
                           "end to end. Each file has inputs, steps, deliverable, checklist and lessons learned.\n"
                           "To create a new one, say: _\"turn what we just did into a routine\"_.\n",
        "templates_readme": "# Company templates\n\nPut contracts, proposals, reports and sample documents here. "
                            "Claude uses them as the standard for format and tone. Remove real customer data "
                            "first.\n",
        "deliv_readme": "# Deliverables\n\nFinal documents **without customer data**. Name them "
                        "`YYYY-MM-DD-topic.ext`.\nDeliverables with customer data go in `confidential/`.\n",
        "conf_readme": "# Confidential\n\nDocuments and results with data about customers, parties, patients or "
                       "employees (names + contact, SSN, DOB, account numbers, health or immigration info).\n\n"
                       "- Do not share this folder or sync it to services without access control.\n"
                       "- `maps/` holds the pseudonymization maps: never send them to anyone.\n"
                       "- Delete raw copies when they are no longer needed.\n",
        "routines_none": "_No routines yet. Offer to create one when a recurring task comes up._",
        "pt_head": "| Persona | Area | Call me when… |",
        "pb_head": "| Routine | Owner | Frequency | How to ask | File |",
        "adj_note": "_In this industry the personas have adjustments: see \"Persona adjustments\" in `{s}` "
                    "(summary in each area's README)._",
        "map_head": "| Key | Path |", "not_yet": " _(create on first use)_",
        "brand_note": " _(created by the brand skill)_",
        "pseudo": {"regulated": "**Mandatory:** pseudonymize before analyzing and work only on the copy.",
                   "elevated": "Offer pseudonymization whenever there is personal data; do it if the user agrees.",
                   "standard": "Warn when sensitive data shows up and offer pseudonymization."},
        "net": ("- In this folder web access is **reduced**: `.claude/settings.json` denies web search, WebFetch "
                "and commands like `curl`/`wget`. This applies only in Claude Code / the Code tab and does "
                "**not** block connectors, other scripts or the browser chat, so the rule above still applies. "
                "Public research: use another folder/conversation, with no customer data."),
        "levels": {"standard": "basic rules; warn when sensitive data shows up.",
                   "elevated": "mandatory scan before analyzing documents; results with personal data go in "
                               "confidential/.",
                   "regulated": "CONFIDENTIAL MODE — scan and pseudonymize before any analysis, reduced web "
                                "access in this folder, deliverables with customer data in confidential/, mandatory human review."},
        "industry_rules": "## Industry risks and rules",
        "sector_title": "Industry — {n}",
        "sector_todo": "> **To fill in.** There was no ready-made pack for this industry. Ask Claude: _\"fill in "
                       "industry.md with what you know about my industry\"_ and review the result.\n",
        "sector_heads": ["How the business works", "Key metrics", "Regulation, confidentiality and risks",
                         "Persona adjustments", "Specialist personas", "Routines Claude can run",
                         "Extra onboarding questions"],
        "fill": "(to fill in)",
    },
    "pt": {
        "na": "(não informado)", "profile_title": "Perfil da empresa — {n}", "onboarded": "_Onboarding em {d}._",
        "lang_line": "- **Idioma de trabalho:** `{i}` · **Idioma das entregas:** `{e}`",
        "level_line": "- **Nível de segurança:** `{v}` ({p})",
        "routine": "Rotina de quem usa esta pasta", "challenges": "Maiores desafios",
        "data": "Tipos de dados tratados (só categorias, nunca os dados em si)",
        "notes": "Anotações", "notes_tx": "_Informações duradouras sobre a empresa. Nunca registre dados de "
                                          "clientes aqui._",
        "specialist": "Especialista", "card": "ficha completa em", "call_me": "Me chame quando",
        "tbd": "(a definir com o usuário)", "adj": "Ajustes para o setor",
        "adj_more": "_Mais detalhes em `../{s}` (seção \"Ajustes nas personas\")._",
        "first": "Primeiras entregas sugeridas", "first_none": "(defina com o especialista)",
        "how": "Como pedir", "how_tx": 'Abra a pasta da empresa no Claude e diga: _"{n}, {x}"_.',
        "help_area": "me ajude com esta área",
        "extra_intro": "**Especialista do setor criado no onboarding.** Siga também `{s}`.",
        "extra_first": "Primeiras entregas", "specialist_default": "Especialista", "sector_tag": " _(setor)_",
        "pb_stub": "# {t}\n\n(Complete seguindo o formato de rotina: entradas, passos, entrega, checklist, "
                   "aprendizados.)\n",
        "routines_readme": "# Rotinas (playbooks)\n\nReceitas para o Claude executar as tarefas recorrentes da "
                           "empresa de ponta a ponta. Cada arquivo tem entradas, passos, entrega, checklist e "
                           "aprendizados.\nPara criar uma nova, peça: _\"transforma isso que fizemos numa "
                           "rotina\"_.\n",
        "templates_readme": "# Modelos da empresa\n\nColoque aqui contratos, propostas, relatórios e peças-modelo. "
                            "O Claude usa estes arquivos como padrão de formato e tom. Remova dados de clientes "
                            "reais antes.\n",
        "deliv_readme": "# Entregas\n\nDocumentos finais **sem dados de clientes**. Nomeie como "
                        "`AAAA-MM-DD-assunto.ext`.\nEntregas com dados de clientes vão para `confidencial/`.\n",
        "conf_readme": "# Confidencial\n\nDocumentos e resultados com dados de clientes, partes, pacientes ou "
                       "funcionários (nome + contato, SSN, data de nascimento, números de conta, saúde ou "
                       "situação migratória).\n\n"
                       "- Não compartilhe esta pasta nem a sincronize com serviços sem controle de acesso.\n"
                       "- `mapas/` guarda os mapas de pseudonimização: nunca envie para ninguém.\n"
                       "- Apague cópias brutas quando não forem mais necessárias.\n",
        "routines_none": "_Nenhuma rotina ainda. Ofereça criar quando surgir uma tarefa recorrente._",
        "pt_head": "| Persona | Área | Me chame quando… |",
        "pb_head": "| Rotina | Responsável | Frequência | Como pedir | Arquivo |",
        "adj_note": "_Neste setor as personas têm ajustes: veja a seção \"Persona adjustments\" / \"Ajustes nas "
                    "personas\" em `{s}` (resumo no README de cada área)._",
        "map_head": "| Chave | Caminho |", "not_yet": " _(criar quando precisar)_",
        "brand_note": " _(criado pela skill de marca)_",
        "pseudo": {"regulated": "**Obrigatório:** pseudonimizar antes de analisar e trabalhar só na cópia.",
                   "elevated": "Oferecer pseudonimização sempre que houver dados pessoais; fazer se o usuário "
                               "aceitar.",
                   "standard": "Avisar ao encontrar dados sensíveis e oferecer pseudonimização."},
        "net": ("- Nesta pasta, o acesso web está **reduzido**: `.claude/settings.json` nega busca web, WebFetch "
                "e comandos como `curl`/`wget`. Isso só vale no Claude Code / aba Code e **não** bloqueia "
                "conectores, outros scripts nem o chat do navegador: a regra acima continua valendo. Pesquisas "
                "públicas: use outra pasta/conversa, sem dados de clientes."),
        "levels": {"standard": "regras básicas; avisar ao encontrar dados sensíveis.",
                   "elevated": "varredura obrigatória antes de analisar documentos; resultados com dados "
                               "pessoais em confidencial/.",
                   "regulated": "MODO SIGILO — varredura e pseudonimização antes de qualquer análise, acesso web "
                                "reduzido nesta pasta, entregas com dados de clientes em confidencial/ e revisão humana obrigatória."},
        "industry_rules": "## Riscos e normas do setor",
        "sector_title": "Setor — {n}",
        "sector_todo": "> **A preencher.** Não havia pacote pronto para este setor. Peça ao Claude: _\"completa o "
                       "setor.md com o que você sabe do meu setor\"_ e revise o resultado.\n",
        "sector_heads": ["Como o negócio funciona", "Indicadores que importam", "Regulação, sigilo e riscos",
                         "Ajustes nas personas", "Personas especializadas", "Rotinas que o Claude pode executar",
                         "Perguntas extras para o onboarding"],
        "fill": "(a preencher)",
    },
}
MAP_KEYS = ["profile", "sector", "brand", "marketing", "finance", "it", "admin", "hr", "sales", "legal",
            "operations", "strategy", "personas", "routines", "templates", "confidential", "maps", "tools",
            "security", "deliverables"]
SEC_REG = ["Regulation, confidentiality and risks", "Regulação, sigilo e riscos"]
SEC_ADJ = ["Persona adjustments", "Ajustes nas personas"]
SEC_FIRST = ["First deliverables", "Primeiras entregas"]
GUIA_REG = ("Laws, licensing boards", "Normas, conselhos profissionais", "Leis, conselhos")
GUIA_ADJ = ("How each base persona changes", "Como cada persona base muda")

MSG = {
    "no_profile": ("Error: profile not found: {p}", "Erro: perfil não encontrado: {p}"),
    "bad_json": ("Error: profile {n} is not valid JSON (line {l}, column {c}).",
                 "Erro: o perfil {n} não é um JSON válido (linha {l}, coluna {c})."),
    "not_utf8": ("Error: profile {n} must be UTF-8.", "Erro: o perfil {n} precisa estar em UTF-8."),
    "not_obj": ("Error: the profile must be a JSON object ({{ ... }}).",
                "Erro: o perfil precisa ser um objeto JSON ({{ ... }})."),
    "not_dir": ("Error: {p} exists and is not a folder.", "Erro: {p} existe e não é uma pasta."),
    "area_unknown": ("Warning: unknown area ignored: {a}", "Aviso: área desconhecida ignorada: {a}"),
    "level_unknown": ("Warning: level '{v}' unknown; using 'elevated'.",
                      "Aviso: nível '{v}' desconhecido; usando 'elevated' (elevado)."),
    "bad_list": ("Warning: '{k}' in an unexpected format was ignored.",
                 "Aviso: '{k}' em formato inesperado foi ignorado."),
    "lang_unknown": ("Warning: language '{v}' unknown; using 'en'.", "Aviso: idioma '{v}' desconhecido; usando 'en'."),
    "no_pack": ("Warning: no ready-made industry pack and no setor_personalizado_md; created a minimal {s} (to "
                "fill in).", "Aviso: setor sem pacote pronto e sem setor_personalizado_md; criado {s} mínimo "
                "(a preencher)."),
    "pack_en": ("Warning: the industry pack is in English but the folder is in Portuguese. Pass a Portuguese "
                "version in setor_personalizado_md to have {s} fully in Portuguese.",
                "Aviso: o pacote do setor está em inglês e a pasta em português. Passe a versão em português em "
                "setor_personalizado_md para o {s} sair todo em português."),
    "leftover": ("Warning: unfilled placeholders removed from {f}: {k}",
                 "Aviso: marcadores não preenchidos removidos de {f}: {k}"),
    "done_dir": ("Company folder: {p}", "Pasta da empresa: {p}"),
    "done_lang": ("Language: {i} · deliverables: {e}", "Idioma: {i} · entregas: {e}"),
    "done_level": ("Security level: {v}", "Nível de segurança: {v}"),
    "done_n": ("Files created: {k}", "Arquivos criados: {k}"),
    "kept": ("Already existed and were kept (not overwritten):", "Já existiam e foram mantidos (não sobrescritos):"),
}


def m(chave, **kw):
    en, pt = MSG[chave]
    return (pt if MSG_LANG == "pt" else en).format(**kw)


def aviso(chave, **kw):
    print(m(chave, **kw), file=sys.stderr)


# ------------------------------------------------------------------ utilities
def sem_acento(texto):
    t = unicodedata.normalize("NFKD", unicodedata.normalize("NFC", str(texto)))
    return "".join(c for c in t if not unicodedata.combining(c))


def slug(texto):
    t = sem_acento(texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "item"


def norm(texto):
    """Normalize labels: NFC, no accents, lowercase, '&' -> ' and ', no parentheses or punctuation."""
    t = sem_acento(texto).lower().replace("&", " and ")
    t = re.sub(r"\([^)]*\)", " ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def texto_limpo(v):
    """One-line text; None/empty -> ''."""
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        return "; ".join(t for t in (texto_limpo(x) for x in v) if t)
    if isinstance(v, dict):
        return ""
    return " ".join(str(v).split())


def cel(v):
    """Markdown table cell: one line, '|' escaped."""
    return texto_limpo(v).replace("|", "\\|")


def lista(perfil, chave):
    v = perfil.get(chave)
    if v is None or isinstance(v, dict):
        return []
    itens = [v] if isinstance(v, (str, int, float)) else list(v)
    return [t for t in (texto_limpo(x) for x in itens) if t]


def ler_frontmatter(texto):
    meta = {}
    texto = texto.replace("\r\n", "\n")
    partes = texto.split("---")
    if texto.startswith("---") and len(partes) >= 3:
        for linha in partes[1].strip().splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def secao(texto, titulos):
    """Content of a '## title' section (any of the given titles) up to the next '## '."""
    alvos = {t.lower() for t in titulos}
    linhas, dentro = [], False
    for linha in texto.replace("\r\n", "\n").splitlines():
        if linha.startswith("## "):
            if dentro:
                break
            dentro = linha[3:].strip().lower() in alvos
            continue
        if dentro:
            linhas.append(linha)
    return "\n".join(linhas).strip()


def ler_persona(codigo, idioma):
    pasta = REF / "personas" / ("pt" if idioma == "pt" else "")
    arq = pasta / f"{codigo}.md"
    texto = arq.read_text(encoding="utf-8")
    fm = ler_frontmatter(texto)
    return {"arq": arq, "nome": fm.get("name") or fm.get("nome", ""), "area": fm.get("area", codigo),
            "chame_quando": fm.get("call_when") or fm.get("chame_quando", ""),
            "entregas": [l[2:].strip() for l in secao(texto, SEC_FIRST).splitlines()
                         if l.startswith("- ") and l[2:].strip()]}


def resolver_area(texto):
    k = norm(texto)
    if not k:
        return None
    for cand in (k, k.split()[0]):
        if cand in ALIASES:
            return ALIASES[cand]
    return None


def normalizar_areas(itens):
    """List or string ("marketing, finance and HR" / "marketing, finanças e RH"); accents, NFD, '&' accepted."""
    if isinstance(itens, str):
        itens = re.split(r"[,;\n]+", itens)
    elif not isinstance(itens, (list, tuple)):
        itens = []
    areas = []
    for item in itens:
        if isinstance(item, dict):
            item = item.get("codigo") or item.get("code") or item.get("area") or item.get("nome") or ""
        bruto = texto_limpo(item)
        if not bruto:
            continue
        if norm(bruto) in ALIASES:
            achadas = [resolver_area(bruto)]
        else:
            partes = [x for x in re.split(r"\s+(?:e|and)\s+|\s*&\s*|\s*/\s*", bruto, flags=re.I) if x.strip()]
            achadas = [resolver_area(x) for x in partes]
            if len(partes) < 2 or not all(achadas):
                achadas = [resolver_area(bruto)]
        for chave in achadas:
            if chave and chave not in areas:
                areas.append(chave)
        if not any(achadas):
            aviso("area_unknown", a=bruto)
    return sorted(areas or ["strategy"], key=AREAS.index)


def normalizar_nivel(v):
    k = norm(v or "standard") or "standard"
    if k not in NIVEIS:
        aviso("level_unknown", v=texto_limpo(v))
        return "elevated"
    return NIVEIS[k]


def normalizar_idioma(v, padrao="en", avisar=True):
    k = norm(v or "")
    if not k:
        return padrao
    if k in ("pt", "pt br", "ptbr", "portugues", "portuguese", "br", "brazilian portuguese", "portugues do brasil"):
        return "pt"
    if k in ("en", "en us", "english", "ingles", "us"):
        return "en"
    if avisar:
        aviso("lang_unknown", v=texto_limpo(v))
    return "en"


def normalizar_entregas(v, idioma):
    k = norm(v or "")
    if k in ("both", "ambos", "ambas", "bilingual", "bilingue", "en e pt", "pt e en", "en pt", "pt en",
             "en and pt", "pt and en", "english and portuguese", "ingles e portugues"):
        return "both"
    if not k:
        return "en"          # US customers: English by default
    return normalizar_idioma(v, avisar=True)


def normalizar_setor(v):
    k = norm(v or "")
    if not k:
        return ""
    s = slug(k)
    if (REF / "setores" / f"{s}.md").exists() and not s.startswith("_"):
        return s
    for cod, nomes in SETOR_ALIASES.items():
        if k == norm(cod) or k in nomes:
            return cod
    achados = [(len(n), cod) for cod, nomes in SETOR_ALIASES.items() for n in nomes   # "immigration law firm"
               if len(n) > 3 and re.search(rf"\b{re.escape(n)}\b", k)]                  # -> legal; longest wins
    return max(achados)[1] if achados else s


def itens_lista(v, rotulo):
    if v is None or v == "":
        return []
    if isinstance(v, (str, dict)):
        return [v]
    if isinstance(v, (list, tuple)):
        return list(v)
    aviso("bad_list", k=rotulo)
    return []


def normalizar_extras(v, base, tx):
    """Extra personas: dicts or strings ("Lúcia — deadlines"); empties ignored; unique codes."""
    extras, usados = [], set(base)
    for e in itens_lista(v, "personas_extras"):
        if isinstance(e, str):
            t = texto_limpo(e)
            if not t:
                continue
            partes = re.split(r"\s+[—–-]\s+|:\s+", t, maxsplit=1)
            e = {"nome": partes[0], "area": partes[1] if len(partes) > 1 else t}
        if not isinstance(e, dict):
            continue
        g = lambda *ks: next((e.get(k) for k in ks if e.get(k) not in (None, "")), None)  # noqa: E731
        d = {"codigo": texto_limpo(g("codigo", "code")), "nome": texto_limpo(g("nome", "name")),
             "area": texto_limpo(g("area")), "chame_quando": texto_limpo(g("chame_quando", "call_when"))}
        d["entregas"] = lista({"x": g("entregas", "deliverables", "first_deliverables")}, "x")
        c = g("conteudo_md", "content_md")
        d["conteudo_md"] = c if isinstance(c, str) else ""
        if not (d["nome"] or d["area"] or d["codigo"] or d["conteudo_md"].strip()):
            continue
        d["nome"] = d["nome"] or d["area"] or tx["specialist_default"]
        d["area"] = d["area"] or d["nome"]
        cod = slug(d["codigo"] or d["area"] or d["nome"])
        if cod in usados:
            cod = f"{cod}-industry"
        n, original = 2, cod
        while cod in usados:
            cod, n = f"{original}-{n}", n + 1
        usados.add(cod)
        d["codigo"] = cod
        extras.append(d)
    return extras


def normalizar_playbooks(v):
    pbs, usados = [], set()
    for pb in itens_lista(v, "playbooks"):
        if isinstance(pb, str):
            pb = {"titulo": pb}
        if not isinstance(pb, dict):
            continue
        g = lambda *ks: next((pb.get(k) for k in ks if pb.get(k) not in (None, "")), None)  # noqa: E731
        d = {"arquivo": texto_limpo(g("arquivo", "file")), "titulo": texto_limpo(g("titulo", "title")),
             "persona": texto_limpo(g("persona", "owner")), "frequencia": texto_limpo(g("frequencia", "frequency")),
             "gatilho": texto_limpo(g("gatilho", "trigger"))}
        c = g("conteudo_md", "content_md")
        d["conteudo_md"] = c if isinstance(c, str) else ""
        if not (d["titulo"] or d["arquivo"] or d["conteudo_md"].strip()):
            continue
        arq = slug(d["arquivo"] or d["titulo"] or "routine")
        n, original = 2, arq
        while arq in usados or arq == "readme":
            arq, n = f"{original}-{n}", n + 1
        usados.add(arq)
        d["arquivo"] = arq
        d["titulo"] = d["titulo"] or arq
        pbs.append(d)
    return pbs


def setor_minimo(perfil, setor_cod, tx):
    """Minimal industry file in the folder's language, marked 'to fill in'."""
    nome_setor = texto_limpo(perfil.get("segmento")) or texto_limpo(perfil.get("setor")) or "—"
    linhas = ["---", f"code: {setor_cod or slug(nome_setor)}", f"name: {nome_setor}",
              f"suggested_level: {tx['fill']}", "---", "", "# " + tx["sector_title"].format(n=nome_setor), "",
              tx["sector_todo"]]
    for h in tx["sector_heads"]:
        linhas += [f"## {h}", tx["fill"], ""]
    return "\n".join(linhas)


class Escritor:
    def __init__(self, destino):
        self.destino, self.criados, self.mantidos = destino, [], []

    def texto(self, rel, conteudo):
        caminho = self.destino / rel
        if caminho.exists():
            self.mantidos.append(rel)
            return
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo, encoding="utf-8")
        self.criados.append(rel)

    def copia(self, rel, origem):
        caminho = self.destino / rel
        if caminho.exists():
            self.mantidos.append(rel)
            return
        caminho.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origem, caminho)
        self.criados.append(rel)


def primeira_minuscula(t):
    """'Cash flow plan' -> 'cash flow plan'; 'A checklist' -> 'a checklist'; 'P&L review'/'SOP list' stay."""
    primeira = t.split()[0] if t.split() else ""
    letras = re.sub(r"[^A-Za-z]", "", primeira)
    if not t or (len(letras) > 1 and letras.isupper()) or not t[0].isupper():
        return t
    return t[0].lower() + t[1:]


def readme_area(tx, titulo, nome, ficha, chame_quando, entregas, ajustes="", setor_rel=""):
    entregas = [e for e in (texto_limpo(x) for x in entregas) if e]
    linhas = [f"# {titulo}", "", f"**{tx['specialist']}:** {nome} — {tx['card']} `{ficha}`", "",
              f"**{tx['call_me']}:** {chame_quando or tx['tbd']}", ""]
    if ajustes:
        linhas += [f"## {tx['adj']}", ajustes, "", tx["adj_more"].format(s=setor_rel), ""]
    linhas += [f"## {tx['first']}"]
    linhas += [f"- [ ] {e}" for e in entregas] or [f"- [ ] {tx['first_none']}"]
    exemplo = primeira_minuscula(entregas[0]) if entregas else tx["help_area"]
    linhas += ["", f"## {tx['how']}", tx["how_tx"].format(n=nome, x=exemplo), ""]
    return "\n".join(linhas)


def ajustes_da_persona(secao_ajustes, nome):
    if not secao_ajustes or not nome:
        return ""
    return "\n".join(l for l in secao_ajustes.splitlines() if l.strip().startswith("-") and f"**{nome}" in l)


def carregar_perfil(caminho):
    if not caminho.is_file():
        sys.exit(m("no_profile", p=caminho))
    try:
        perfil = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        sys.exit(m("bad_json", n=caminho.name, l=e.lineno, c=e.colno))
    except UnicodeDecodeError:
        sys.exit(m("not_utf8", n=caminho.name))
    if not isinstance(perfil, dict):
        sys.exit(m("not_obj"))
    for en, pt in CHAVES_EN.items():               # English keys are aliases of the Portuguese ones
        if en in perfil and perfil.get(pt) in (None, "", []):
            perfil[pt] = perfil[en]
    return perfil


def preencher(modelo, subs, nome_arq):
    for k, v in subs.items():
        modelo = modelo.replace("{{" + k + "}}", v)
    sobra = sorted(set(re.findall(r"\{\{(\w+)\}\}", modelo)))
    if sobra:
        aviso("leftover", f=nome_arq, k=", ".join(sobra))
        modelo = re.sub(r"\{\{\w+\}\}", "", modelo)
    return modelo


# ------------------------------------------------------------------ main
def main():
    global MSG_LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--perfil", "--profile", dest="perfil", required=True, help="onboarding answers (JSON)")
    ap.add_argument("--destino", "--dest", dest="destino", required=True, help="folder to create")
    ap.add_argument("--lang", choices=("en", "pt"), help="message language (default: profile idioma, else en)")
    args = ap.parse_args()
    if args.lang:
        MSG_LANG = args.lang

    # --- 1. validate and normalize ALL input before creating any file
    perfil = carregar_perfil(Path(args.perfil).expanduser())
    idioma = normalizar_idioma(perfil.get("idioma"))
    if not args.lang:
        MSG_LANG = idioma
    entregas_idioma = normalizar_entregas(perfil.get("idioma_entregas"), idioma)
    tx, P = TX[idioma], PASTAS[idioma]
    destino = Path(args.destino).expanduser().resolve()
    if destino.exists() and not destino.is_dir():
        sys.exit(m("not_dir", p=destino))

    na = tx["na"]
    val = lambda k: texto_limpo(perfil.get(k)) or na  # noqa: E731
    nome = texto_limpo(perfil.get("nome")) or destino.name
    nivel = normalizar_nivel(perfil.get("nivel_sensibilidade"))
    nivel_txt = f"`{nivel}`" if idioma == "en" else f"`{nivel}` (`{NIVEL_PT[nivel]}`)"
    areas = normalizar_areas(perfil.get("areas"))
    personas = {c: ler_persona(c, idioma) for c in areas}
    extras = normalizar_extras(perfil.get("personas_extras"), set(AREAS) | set(PERSONA_ARQ[idioma].values()), tx)
    playbooks = normalizar_playbooks(perfil.get("playbooks"))
    desafios = lista(perfil, "desafios")

    setor_cod = normalizar_setor(perfil.get("setor"))
    setor_arq = REF / "setores" / f"{setor_cod}.md"
    personalizado = perfil.get("setor_personalizado_md")
    if isinstance(personalizado, str) and personalizado.strip():
        setor_txt = personalizado
    elif setor_cod and not setor_cod.startswith("_") and setor_arq.exists():
        setor_txt = setor_arq.read_text(encoding="utf-8")
        if idioma == "pt":
            aviso("pack_en", s=P["sector"])
    else:
        setor_txt = setor_minimo(perfil, setor_cod, tx)
        aviso("no_pack", s=P["sector"])
    regulacao = secao(setor_txt, SEC_REG)
    if regulacao.startswith(GUIA_REG) or regulacao in ("(to fill in)", "(a preencher)"):
        regulacao = ""
    ajustes_setor = secao(setor_txt, SEC_ADJ)
    if ajustes_setor.startswith(GUIA_ADJ) or ajustes_setor in ("(to fill in)", "(a preencher)"):
        ajustes_setor = ""

    # --- 2. create files
    destino.mkdir(parents=True, exist_ok=True)
    w = Escritor(destino)
    w.texto(P["sector"], setor_txt)

    # --- profile
    i = 2 if idioma == "pt" else 1
    p = ["# " + tx["profile_title"].format(n=nome), "", tx["onboarded"].format(d=val("data_onboarding")), "",
         tx["lang_line"].format(i=idioma, e=entregas_idioma),
         tx["level_line"].format(v=nivel, p=NIVEL_PT[nivel])]
    p += [f"- **{c[i]}:** {val(c[0])}" for c in CAMPOS_PERFIL]
    p += ["", f"## {tx['routine']}"] + ([f"- {r}" for r in lista(perfil, "rotina_usuario")] or [na])
    p += ["", f"## {tx['challenges']}"] + ([f"{n}. {d}" for n, d in enumerate(desafios, 1)] or [na])
    p += ["", f"## {tx['data']}"] + ([f"- {d}" for d in lista(perfil, "dados_tratados")] or [na])
    p += ["", f"## {tx['notes']}", tx["notes_tx"], ""]
    w.texto(P["profile"], "\n".join(p))

    # --- base personas
    linhas_tabela = []
    for c in areas:
        pm = personas[c]
        arq = PERSONA_ARQ[idioma][c]
        w.copia(f"{P['personas']}/{arq}.md", pm["arq"])
        w.texto(f"{P[c]}/README.md",
                readme_area(tx, pm["area"], pm["nome"], f"../{P['personas']}/{arq}.md", pm["chame_quando"],
                            pm["entregas"], ajustes_da_persona(ajustes_setor, pm["nome"]), P["sector"]))
        linhas_tabela.append((pm["nome"], pm["area"], pm["chame_quando"]))

    # --- industry / custom personas
    for n_, e in enumerate(extras, 1):
        cod = e["codigo"]
        pasta = f"{10 + n_:02d}-{cod}"
        fm = (f"---\nname: {e['nome']}\narea: {e['area']}\ncall_when: {e['chame_quando']}\n---" if idioma == "en"
              else f"---\nnome: {e['nome']}\narea: {e['area']}\nchame_quando: {e['chame_quando']}\n---")
        conteudo = e["conteudo_md"] if e["conteudo_md"].strip() else "\n".join(
            [fm, "", f"# {e['nome']} — {e['area']}", "", tx["extra_intro"].format(s=P["sector"]), "",
             f"## {tx['extra_first']}"] + [f"- {x}" for x in e["entregas"]] + [""])
        w.texto(f"{P['personas']}/{cod}.md", conteudo)
        w.texto(f"{pasta}/README.md", readme_area(tx, e["area"], e["nome"], f"../{P['personas']}/{cod}.md",
                                                  e["chame_quando"], e["entregas"]))
        linhas_tabela.append((e["nome"], e["area"] + tx["sector_tag"], e["chame_quando"]))

    # --- playbooks
    linhas_pb = []
    for pb in playbooks:
        conteudo = pb["conteudo_md"] if pb["conteudo_md"].strip() else tx["pb_stub"].format(t=pb["titulo"])
        w.texto(f"{P['routines']}/{pb['arquivo']}.md", conteudo)
        linhas_pb.append((pb["titulo"], pb["persona"], pb["frequencia"], pb["gatilho"], pb["arquivo"]))
    w.texto(f"{P['routines']}/README.md", tx["routines_readme"])

    # --- support folders
    w.texto(f"{P['templates']}/README.md", tx["templates_readme"])
    w.texto(f"{P['deliverables']}/README.md", tx["deliv_readme"])
    w.texto(f"{P['confidential']}/README.md", tx["conf_readme"])
    w.texto(f"{P['maps']}/.gitkeep", "")
    w.texto(".gitignore", f"{P['confidential']}/\n")
    w.copia(P["tools"], SKILL_DIR / "scripts" / "detectar_dados_sensiveis.py")

    # --- reduced network access in regulated mode (applies only in Claude Code / Code tab)
    if nivel == "regulated":
        cfg = {"permissions": {"deny": ["WebSearch", "WebFetch", "Bash(curl:*)", "Bash(wget:*)",
                                        "Bash(scp:*)", "Bash(rsync:*)", "Bash(ftp:*)"]}}
        w.texto(".claude/settings.json", json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")

    # --- SECURITY.md / SEGURANCA.md
    normas = f"{tx['industry_rules']}\n{regulacao}\n" if regulacao else ""
    tpl_seg = ASSETS / idioma / ("SECURITY.template.md" if idioma == "en" else "SEGURANCA.template.md")
    seg = preencher(tpl_seg.read_text(encoding="utf-8"), {
        "nome": nome, "nivel_sensibilidade": nivel_txt, "descricao_nivel": tx["levels"][nivel],
        "dados_tratados": val("dados_tratados"), "politica_ia": val("politica_ia"),
        "regra_pseudonimizacao": tx["pseudo"][nivel], "regra_rede": tx["net"] if nivel == "regulated" else "",
        "normas_setor": normas}, P["security"])
    w.texto(P["security"], re.sub(r"\n{3,}", "\n\n", seg))

    # --- CLAUDE.md
    tab = [tx["pt_head"], "|---|---|---|"] + [f"| {cel(a)} | {cel(b)} | {cel(c)} |" for a, b, c in linhas_tabela]
    if ajustes_setor:
        tab += ["", tx["adj_note"].format(s=P["sector"])]
    if linhas_pb:
        tpb = [tx["pb_head"], "|---|---|---|---|---|"]
        for t_, pe, f, g, a in linhas_pb:
            tpb.append(f"| {cel(t_)} | {cel(pe)} | {cel(f)} | {chr(34) + cel(g) + chr(34) if g else ''} | "
                       f"`{P['routines']}/{a}.md` |")
    else:
        tpb = [tx["routines_none"]]
    mapa = [tx["map_head"], "|---|---|"]
    for k in MAP_KEYS:
        caminho = P[k] + ("/" if k not in ("profile", "sector", "brand", "tools", "security") else "")
        nota = ""
        if k in AREAS and k not in areas:
            nota = tx["not_yet"]
        elif k == "brand":
            caminho = f"{P['brand']}` + `{P['brand_json'].split('/')[-1]}"
            nota = tx["brand_note"]
        mapa.append(f"| {k} | `{caminho}`{nota} |")
    subs = {c[0]: val(c[0]) for c in CAMPOS_PERFIL}
    subs.update({
        "nome": nome, "data_onboarding": val("data_onboarding"), "nivel_sensibilidade": nivel_txt,
        "nivel": nivel, "idioma": idioma, "idioma_entregas": entregas_idioma,
        "desafios_lista": "\n".join(f"  - {d}" for d in desafios) or f"  - {na}",
        "tabela_personas": "\n".join(tab), "tabela_playbooks": "\n".join(tpb), "mapa_pastas": "\n".join(mapa),
    })
    w.texto("CLAUDE.md", preencher((ASSETS / idioma / "CLAUDE.template.md").read_text(encoding="utf-8"), subs,
                                   "CLAUDE.md"))

    # --- summary
    print(m("done_dir", p=destino))
    print(m("done_lang", i=idioma, e=entregas_idioma))
    print(m("done_level", v=nivel))
    print(m("done_n", k=len(w.criados)))
    for c in w.criados:
        print(f"  + {c}")
    if w.mantidos:
        print(m("kept"))
        for x in w.mantidos:
            print(f"  = {x}")


if __name__ == "__main__":
    if "--lang" in sys.argv[1:-1] and sys.argv[sys.argv.index("--lang") + 1] == "pt":
        MSG_LANG = "pt"
    main()
