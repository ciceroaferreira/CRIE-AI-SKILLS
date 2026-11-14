#!/usr/bin/env python3
"""Detect and (optionally) pseudonymize sensitive data in documents.
Detecta e (opcionalmente) pseudonimiza dados sensíveis em documentos.

Usage (inside the company folder the script lives in tools/ or ferramentas/):
    # Report only (default) - never prints full values
    python3 tools/detectar_dados_sensiveis.py contract.docx --lang en

    # Pseudonymized copy + reversal map (keep the map on your computer only)
    python3 tools/detectar_dados_sensiveis.py contract.docx --anonimizar contract-anon.txt \\
        --mapa confidential/maps/contract.json --nomes "John Smith;ACME LLC"

    # Also replace health conditions/medications (diabetes, metformin...) with [HEALTH_n] / [SAUDE_n]
    python3 tools/detectar_dados_sensiveis.py intake.txt --anonimizar intake-anon.txt \\
        --mapa confidential/maps/intake.json --health-terms

    # Revert a text with markers using the map
    python3 tools/detectar_dados_sensiveis.py memo-anon.txt --reverter memo.txt \\
        --mapa confidential/maps/contract.json

Formats: .txt .md .csv .tsv .json .html .xml .docx.
- PDF: extract the text first. XLSX/XLS: export as "CSV UTF-8" in Excel.
- DOCX: output is always text (.txt/.md). Build the final DOCX from the reverted text.
- Text files in UTF-8 or Windows-1252 (Excel CSV) are written back in the same encoding and with the same
  line endings (LF/CRLF), so reversal returns a byte-identical file.
Standard library only. Nothing is sent to the internet.

Health data: diagnosis codes (ICD-10) are replaced like other identifiers. Named conditions and medications
(curated EN+PT list) are counted in the report but replaced only with --health-terms / --termos-saude.

Limits: detection uses patterns (regex + check digits + context words). It does NOT reliably find names
(use --nomes), street addresses, ZIP codes, or data written in unusual ways. A helper, not a guarantee.
"""

import argparse
import json
import re
import sys
import unicodedata
import zipfile
from html import unescape
from pathlib import Path

LANG = "en"


class ErroUsuario(Exception):
    """User-facing error (no traceback). Args: (message key, format kwargs)."""

    def __init__(self, chave, **kw):
        super().__init__(chave)
        self.chave, self.kw = chave, kw

    def texto(self):
        return t(self.chave, **self.kw)


# ---------------------------------------------------------------- messages (en / pt)
MSG = {
    "not_found": ("File not found: {p}", "Arquivo não encontrado: {p}"),
    "is_dir": ("{p} is a folder; give a file.", "{p} é uma pasta; informe um arquivo."),
    "binary_fmt": ("Format {ext} is not read directly: {hint}", "Formato {ext} não é lido diretamente: {hint}"),
    "docx_no_body": ("{n} does not look like a valid DOCX (Word content missing). Open it in Word and save "
                     "again, or export as .txt.",
                     "{n} não parece um DOCX válido (falta o conteúdo do Word). Abra no Word e salve de novo, "
                     "ou exporte como .txt."),
    "docx_bad": ("{n} is not a valid DOCX (corrupted or wrong extension). Open it in Word and save again as "
                 ".docx, or export as .txt.",
                 "{n} não é um DOCX válido (arquivo corrompido ou com extensão trocada). Abra no Word e salve de "
                 "novo como .docx, ou exporte como .txt."),
    "binary": ("{n} looks like a binary file. Convert it to text (.txt/.csv) and run again.",
               "{n} parece ser um arquivo binário. Converta para texto (.txt/.csv) e rode de novo."),
    "undecodable": ("Could not read {n} as text. Save it as UTF-8 and run again.",
                    "Não consegui ler {n} como texto. Salve como UTF-8 e rode de novo."),
    "enc_warn": ("Warning: {n} is not UTF-8; it was read as {enc}. Outputs are written in the same encoding as "
                 "the original.",
                 "Aviso: {n} não está em UTF-8; foi lido como {enc}. As saídas são gravadas na mesma codificação "
                 "do original."),
    "enc_fallback": ("Warning: the text has characters that do not fit in {enc}; {n} was written as UTF-8.",
                     "Aviso: o texto tem caracteres que não cabem em {enc}; {n} foi gravado em UTF-8."),
    "out_text": ("Warning: output is plain text; writing {new} instead of {old}. For Word, build the DOCX from "
                 "this text.",
                 "Aviso: a saída é texto puro; gravando como {new} em vez de {old}. Para entregar em Word, gere o "
                 "DOCX a partir deste texto."),
    "map_missing": ("Map not found: {p}. Use the same --mapa used for pseudonymization.",
                    "Mapa não encontrado: {p}. Use o mesmo --mapa da pseudonimização."),
    "map_json": ("The map {p} is not valid JSON. Do not edit the map by hand.",
                 "O mapa {p} não é um JSON válido. Não edite o mapa à mão."),
    "map_shape": ("The map {p} is not in the expected format (marker -> value, e.g. [SSN_1]).",
                  "O mapa {p} não está no formato esperado (marcador -> valor, ex.: [SSN_1])."),
    "both_modes": ("Use --anonimizar or --reverter, not both.", "Use --anonimizar ou --reverter, não os dois."),
    "need_map_rev": ("Use --mapa to revert.", "Use --mapa para reverter."),
    "need_map_anon": ("Use --mapa to store the reversal map (it stays on your computer).",
                      "Use --mapa para guardar o mapa de reversão (fica só no seu computador)."),
    "same_io": ("The output file cannot be the input file: pick another name so the original is not lost.",
                "O arquivo de saída não pode ser o mesmo da entrada: escolha outro nome para não perder o original."),
    "map_sep": ("The map must be a file separate from the input and the output.",
                "O mapa precisa ser um arquivo separado da entrada e da saída."),
    "reverted": ("Reverted text saved to {p}", "Texto revertido salvo em {p}"),
    "rev_missing": ("Warning: {k} marker(s) are not in the map and were left as is: {lst}",
                    "Aviso: {k} marcador(es) não estão no mapa e ficaram como estavam: {lst}"),
    "scan_title": ("Sensitive-data scan: {n}", "Varredura de dados sensíveis: {n}"),
    "nothing": ("No sensitive pattern found.", "Nenhum padrão sensível encontrado."),
    "ids": ("Identifiers found:", "Identificadores encontrados:"),
    "id_line": ("  - {d}: {k} (e.g. {ex})", "  - {d}: {k} (ex.: {ex})"),
    "terms": ("Possible sensitive data (special categories) - term mentions:",
              "Possíveis dados sensíveis (categorias especiais) — menções a termos:"),
    "term_line": ("  - {c}: {k} mention(s)", "  - {c}: {k} menção(ões)"),
    "health_hint": ("Health conditions/medications named in the text: {k} (counted, not replaced). Add "
                    "--health-terms to replace them with [HEALTH_n] markers too.",
                    "Condições de saúde/medicamentos citados no texto: {k} (contados, não substituídos). Use "
                    "--termos-saude para substituí-los também por marcadores [SAUDE_n]."),
    "grave": ("WARNING: the document has credentials or card numbers. Do not reproduce them; recommend "
              "changing/removing them.",
              "ATENÇÃO: há credenciais ou cartões no documento. Não reproduza; recomende trocar/retirar."),
    "limits": ("Not detected automatically: people's names (use --nomes), street addresses, ZIP codes, and IDs "
               "or dates written without a label (e.g. a driver's license or birth date with no \"DL\"/\"DOB\" "
               "nearby). Review before sharing.",
               "Não são detectados automaticamente: nomes de pessoas (use --nomes), endereços, ZIP/CEP, e "
               "documentos ou datas sem rótulo (ex.: carteira de motorista ou data de nascimento sem \"DL\"/"
               "\"DOB\"/\"nascimento\" por perto). Revise antes de compartilhar."),
    "anon_copy": ("Pseudonymized copy: {p}", "Cópia pseudonimizada: {p}"),
    "anon_map": ("Reversal map (do not share): {p}", "Mapa de reversão (não compartilhe): {p}"),
    "err": ("Error: {m}", "Erro: {m}"),
    "perm": ("Error: no permission to access {p}.", "Erro: sem permissão para acessar {p}."),
    "oserr": ("Error reading or writing a file: {m} ({p}).", "Erro ao ler ou gravar arquivo: {m} ({p})."),
    "hint_pdf": ("extract the PDF text (copy/paste or an extraction tool) into a .txt and run again.",
                 "extraia o texto do PDF (copiar/colar ou ferramenta de extração) para um .txt e rode de novo."),
    "hint_xls": ("in Excel use File > Save As > \"CSV UTF-8 (Comma delimited)\" and run on the .csv.",
                 "no Excel, use Arquivo → Salvar como → \"CSV UTF-8 (delimitado por vírgulas)\" e rode no .csv."),
    "hint_ods": ("export the spreadsheet as CSV UTF-8 and run on the .csv.",
                 "exporte a planilha como CSV UTF-8 e rode no .csv."),
    "hint_ppt": ("export the presentation text to .txt and run again.",
                 "exporte o texto da apresentação para .txt e rode de novo."),
    "hint_doc": ("open it in Word and save as .docx or .txt.", "abra no Word e salve como .docx ou .txt."),
    "hint_other": ("save it as .docx or .txt.", "salve como .docx ou .txt."),
}


def t(chave, **kw):
    en, pt = MSG[chave]
    return (pt if LANG == "pt" else en).format(**kw)


# ---------------------------------------------------------------- validators
def _so_digitos(s):
    return re.sub(r"\D", "", s)


def cpf_valido(s):
    d = _so_digitos(s)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(d[i]) * (n + 1 - i) for i in range(n))
        if (soma * 10) % 11 % 10 != int(d[n]):
            return False
    return True


def cnpj_valido(s):
    """Numeric or alphanumeric CNPJ: 12 chars [0-9A-Z] + 2 numeric check digits (value = ord(c) - 48)."""
    d = re.sub(r"[^0-9A-Z]", "", s.upper())
    if len(d) != 14 or not d[12:].isdigit() or d == d[0] * 14:
        return False
    valores = [ord(c) - 48 for c in d[:12]]
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for pesos in (pesos1, [6] + pesos1):
        r = sum(v * p for v, p in zip(valores, pesos)) % 11
        valores.append(0 if r < 2 else 11 - r)
    return valores[12] == int(d[12]) and valores[13] == int(d[13])


def luhn_valido(s):
    d = _so_digitos(s)
    if not 13 <= len(d) <= 19:
        return False
    total = 0
    for i, ch in enumerate(reversed(d)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def ssn_valido(s):
    """SSA rules: area not 000/666/900-999, group not 00, serial not 0000."""
    d = _so_digitos(s)
    if len(d) != 9:
        return False
    area, grupo, serie = d[:3], d[3:5], d[5:]
    return area not in ("000", "666") and area[0] != "9" and grupo != "00" and serie != "0000"


def itin_valido(s):
    """ITIN: 9XX-NN-XXXX with the middle group in 50-65, 70-88, 90-92 or 94-99."""
    d = _so_digitos(s)
    if len(d) != 9 or d[0] != "9":
        return False
    g = int(d[3:5])
    return 50 <= g <= 65 or 70 <= g <= 88 or 90 <= g <= 92 or 94 <= g <= 99


EIN_PREFIXOS = {int(x) for x in (
    "01 02 03 04 05 06 10 11 12 13 14 15 16 20 21 22 23 24 25 26 27 30 31 32 33 34 35 36 37 38 39 "
    "40 41 42 43 44 45 46 47 48 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 71 72 73 74 "
    "75 76 77 80 81 82 83 84 85 86 87 88 90 91 92 93 94 95 98 99").split()}


def ein_valido(s):
    d = _so_digitos(s)
    return len(d) == 9 and int(d[:2]) in EIN_PREFIXOS and d[2:] != "0000000"


def aba_valido(s):
    """ABA routing number: valid Federal Reserve prefix + 3-7-1 checksum."""
    d = _so_digitos(s)
    if len(d) != 9:
        return False
    p = int(d[:2])
    if not (0 <= p <= 12 or 21 <= p <= 32 or 61 <= p <= 72 or p == 80) or d == "000000000":
        return False
    n = [int(c) for c in d]
    return (3 * (n[0] + n[3] + n[6]) + 7 * (n[1] + n[4] + n[7]) + (n[2] + n[5] + n[8])) % 10 == 0


def nanp_valido(s):
    """US/Canada number: area and exchange start with 2-9, are not N11; area's middle digit is not 9."""
    d = _so_digitos(s)
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    if len(d) != 10:
        return False
    area, troca = d[:3], d[3:6]
    if area[0] in "01" or area[1] == "9" or area[1:] == "11":
        return False
    return troca[0] not in "01" and troca[1:] != "11"


def a_number_valido(s):
    return len(_so_digitos(s)) in (8, 9)


DDDS = {11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34, 35, 37, 38,
        41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55, 61, 62, 63, 64, 65, 66, 67, 68, 69,
        71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99}


def telefone_br_valido(s):
    t_ = s.strip()
    d = _so_digitos(t_)
    if t_.startswith("+"):
        if not d.startswith("55"):
            return False
        d = d[2:]
    if len(d) not in (10, 11) or int(d[:2]) not in DDDS:
        return False
    numero = d[2:]
    if len(numero) == 9:
        return numero[0] == "9"
    return numero[0] in "2345"


# ---------------------------------------------------------------- patterns
_SEG = r"[^\s:=,;]+"
_CRED_CHAVE = (r"(?i)(?<![\w])(?:senhas?|password|passwd|pwd|passcode|token|api[_ -]?key|secret|"
               r"chave\s+de\s+acesso|pin)(?![\w])")
_CRED_QUALIF = (r"(?:\s+(?:d[aoe]s?|n[ao]s?|para(?:\s+[ao]s?)?|for(?:\s+the)?|to|of)(?:\s+" + _SEG +
                r"){1,2}?)??")
_CRED_ASPAS = r"(?:'[^'\n]*'|\"[^\"\n]*\"|“[^”\n]*”|‘[^’\n]*’)"
_CRED_VALOR = r"(?:" + _CRED_ASPAS + r"|\S*[^\s.,;:])"
_CRED_FORTE = r"(?:" + _CRED_ASPAS + r"|(?=\S*[\d@#$%&*!?_])\S*[^\s.,;:])"   # without ":" it must look like a secret
_CRED = (_CRED_CHAVE + _CRED_QUALIF +
         r"(?:\s*[:=]\s*" + _CRED_VALOR +
         r"|\s+(?:é|eh|era|será|is|was)\s*:?\s*" + _CRED_VALOR +
         r"|\s+" + _CRED_FORTE + r")")

# Label after a context word: "SSN #: ", "Social Security No. ", "n.º "
_ROT = r"\s*(?:#|no\.?|nos\.?|num(?:ber)?\.?|n[ºo°]\.?|n[úu]mero)?\s*[:#=-]?\s*(?:is\s+|é\s+)?"
_NUM_TEL_BR = r"(?:9\d{4}|[2-5]\d{3})[\s.-]?\d{4}"
_LIVRE = r"(?<![\w-])"          # not glued to a word, digit or dash on the left
_FIM = r"(?![\w-]|[.,]\d)"      # ... nor on the right (also not "123.4")
_MESES = (r"(?:jan(?:uary|eiro)?|feb(?:ruary)?|fev(?:ereiro)?|mar(?:ch|ço|co)?|apr(?:il)?|abr(?:il)?|may|maio|"
          r"jun(?:e|ho)?|jul(?:y|ho)?|aug(?:ust)?|ago(?:sto)?|sep(?:t(?:ember)?)?|set(?:embro)?|oct(?:ober)?|"
          r"out(?:ubro)?|nov(?:ember|embro)?|dec(?:ember)?|dez(?:embro)?)\.?")
_DATA = (r"(?:\d{1,2}[/.-]\d{1,2}[/.-](?:\d{4}|\d{2})|\d{4}-\d{2}-\d{2}|" + _MESES + r"\s+\d{1,2},?\s+\d{4}|"
         r"\d{1,2}\s+(?:de\s+)?" + _MESES + r"\s+(?:de\s+)?\d{4})")
_MBI_L = "AC-HJKMNP-RT-Y"       # MBI letters: no S, L, O, I, B, Z
_MBI = (rf"[1-9][{_MBI_L}][{_MBI_L}0-9]\d-?[{_MBI_L}][{_MBI_L}0-9]\d-?[{_MBI_L}]{{2}}\d{{2}}")
_ICD = r"[A-TV-Z]\d[0-9A-Z](?:\.[0-9A-Z]{1,4})?"
_USCIS = r"(?:EAC|WAC|LIN|SRC|NBC|MSC|IOE|YSC|TSC|VSC|NSC|CSC|ESC|ZLA|ZNY|ZSF)"

# Words right before a number that mean "this is a product/order code", not a personal identifier.
_NEG = re.compile(
    r"(?i)\b(?:sku|part|item|model|order|invoice|inv|po|ref|reference|serial|s/n|tracking|lot|batch|"
    r"confirmation|conf|pedido|nota|fatura|c[óo]digo|code|product|produto|ticket|claim|style|upc|isbn|"
    r"receipt|recibo|transaction|transa[çc][ãa]o|id)\b\.?\s*(?:no\.?|number|num|n[ºo°]\.?)?\s*[:#=-]?\s*#?\s*$")

# (type, description en, description pt, regex, validator, check negative context)
# Order = priority: earlier patterns win on overlap. Patterns with a group (?P<v>...) replace only that group
# (the context word stays in the text).
PADROES = [
    ("CREDENTIAL", "Password, token or access key", "Senha, token ou chave de acesso",
     re.compile(_CRED), None, False),
    ("API_KEY", "Known API key format", "Chave de API conhecida",
     re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|xox[bp]-[A-Za-z0-9-]{10,})\b"),
     None, False),
    ("CASE_FED", "US federal case number", "Número de processo federal dos EUA",
     re.compile(r"(?i)\b\d{1,2}:\d{2}-(?:cv|cr|mc|mj|bk|ap|md|po|sw|ml)-\d{3,6}(?:-[A-Z]{1,4}){0,3}\b"),
     None, False),
    ("CASE_BR", "Brazilian court case number (CNJ)", "Número de processo judicial (CNJ)",
     re.compile(r"\b\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}\b"), None, False),
    ("USCIS_RECEIPT", "USCIS receipt number", "Número de recibo do USCIS",
     re.compile(r"\b" + _USCIS + r"[-\s]?\d{10}\b"), None, False),
    ("A_NUMBER", "Alien Registration Number (A-Number)", "A-Number (registro de estrangeiro)",
     re.compile(r"(?<![\w-])(?:A|a)(?:\s?#\s?|-|\s)?(?:\d{3}[-\s]?\d{3}[-\s]?\d{3}|\d{2}[-\s]?\d{3}[-\s]?\d{3})"
                r"(?![\w-])|(?i:\b(?:A-?number|alien\s+(?:registration\s+)?(?:number|no\.?|#)|USCIS\s*#)"
                + _ROT + r")(?P<v>A?-?\d{8,9})\b"), a_number_valido, False),
    ("MBI", "Medicare Beneficiary Identifier", "Identificador do Medicare (MBI)",
     re.compile(r"\b" + _MBI + r"\b"), None, False),
    ("CARD", "Payment card number", "Número de cartão de pagamento",
     re.compile(r"\b(?:\d[ .-]?){12,18}\d\b"), luhn_valido, False),
    ("ITIN", "ITIN (taxpayer ID)", "ITIN (identificação de contribuinte)",
     re.compile(r"(?i:\bITIN\b" + _ROT + r")(?P<v>9\d{2}[-\s]?\d{2}[-\s]?\d{4})\b"
                r"|" + _LIVRE + r"9\d{2}-\d{2}-\d{4}" + _FIM), itin_valido, True),
    ("SSN", "Social Security number", "SSN (Social Security)",
     re.compile(r"(?i:\b(?:SSN|SS#|SSA|soc\.?\s*sec\.?|social\s+security(?:\s+(?:number|card))?|"
                r"seguro\s+social)" + _ROT + r")(?P<v>\d{3}[-\s]?\d{2}[-\s]?\d{4})\b"
                r"|" + _LIVRE + r"\d{3}-\d{2}-\d{4}" + _FIM), ssn_valido, True),
    ("CNPJ", "CNPJ (Brazilian company ID)", "CNPJ",
     re.compile(r"\b[0-9A-Z]{2}\.?[0-9A-Z]{3}\.?[0-9A-Z]{3}/?[0-9A-Z]{4}-?\d{2}\b"), cnpj_valido, False),
    ("CPF", "CPF (Brazilian taxpayer ID)", "CPF",
     re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), cpf_valido, False),
    ("EIN", "EIN (employer ID)", "EIN (identificação de empresa)",
     re.compile(r"(?i:\b(?:F?EIN|employer\s+(?:identification|id)(?:\s+number)?|tax\s+id|TIN)" + _ROT +
                r")(?P<v>\d{2}-?\d{7})\b|" + _LIVRE + r"\d{2}-\d{7}" + _FIM), ein_valido, True),
    ("ROUTING", "Bank routing number (ABA)", "Routing number bancário (ABA)",
     re.compile(r"(?i:\b(?:routing|ABA|RTN|transit|roteamento)(?:\s+(?:number|no\.?|#|n[úu]mero))?"
                r"(?:\s+(?:and|&|e)\s+account(?:\s+numbers?)?)?" + _ROT + r")(?P<v>\d{9})\b"), aba_valido, False),
    ("ACCOUNT", "Bank account number", "Número de conta bancária",
     re.compile(r"(?i:\b(?:(?:bank\s+|checking\s+|savings\s+)?account|acct|a/c|conta(?:\s+corrente|\s+poupan[çc]a)?|"
                r"c/c|ag(?:ência|encia|\.)?)" + _ROT + r")(?P<v>\d[\d-]{2,16}[\dxX])\b"), None, False),
    ("POLICY", "Insurance policy / member number", "Número de apólice / carteirinha",
     re.compile(r"(?i:\b(?:(?:insurance\s+|life\s+|health\s+)?policy|ap[óo]lice|member\s+id|subscriber\s+id|"
                r"group\s+(?:number|no\.?|#)|certificate\s+(?:number|no\.?|#))" + _ROT +
                r")(?P<v>(?=[A-Z0-9-]*\d)[A-Z0-9][A-Z0-9-]{4,18}[A-Z0-9])\b"), None, False),
    ("LOAN", "Loan / credit file number", "Número de empréstimo / financiamento",
     re.compile(r"(?i:\b(?:loan|mortgage|empr[ée]stimo|financiamento|credit\s+file|application)" + _ROT +
                r")(?P<v>(?=[A-Z0-9-]*\d{3})[A-Z0-9][A-Z0-9-]{4,18}[A-Z0-9])\b"), None, False),
    ("PASSPORT", "Passport number", "Número de passaporte",
     re.compile(r"(?i:\b(?:passport|passaporte)" + _ROT + r")(?P<v>[A-Z]{2}\d{6}|[A-Z]\d{8}|\d{9})\b"),
     None, False),
    ("DRIVER_LICENSE", "Driver's license number", "Carteira de motorista",
     re.compile(r"(?i:\b(?:driver'?s?\s+licen[cs]e|driving\s+licen[cs]e|DL|CNH|carteira\s+de\s+motorista|"
                r"habilita[çc][ãa]o)" + _ROT + r")(?P<v>(?=[A-Z0-9-]*\d)[A-Z0-9][A-Z0-9-]{4,17}[A-Z0-9])\b"),
     None, False),
    ("DOB", "Date of birth", "Data de nascimento",
     re.compile(r"(?i)(?:\b(?:DOB|D\.O\.B\.?|date\s+of\s+birth|birth\s*date|birthday|born(?:\s+on)?|"
                r"data\s+de\s+nascimento|nascimento|nascid[oa]\s+em|d\.\s?n\.)" + _ROT + r")(?P<v>" + _DATA + r")"),
     None, False),
    ("OAB", "Brazilian bar registration (OAB)", "Inscrição na OAB",
     re.compile(r"\bOAB\s*/?\s*[A-Z]{2}\s*(?:n[ºo°.]?\s*)?\d{3,6}\b"), None, False),
    ("RG", "RG (Brazilian ID card)", "RG",
     re.compile(r"(?i)\bRG\s*(?:n[ºo°.]?\s*)?:?\s*\d{1,2}\.?\d{3}\.?\d{3}-?[\dxX]\b"), None, False),
    ("EMAIL", "Email address", "E-mail",
     re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), None, False),
    ("PHONE", "US phone number", "Telefone dos EUA",
     re.compile(r"(?<![\w+(-])(?:\+?1[\s.-]?)?(?:\(\d{3}\)\s?|\d{3}[\s.-])\d{3}[\s.-]\d{4}(?![\w-])"
                r"|(?i:\b(?:phone|tel|cell|mobile|fax|telefone|celular|fone|whats(?:app)?)" + _ROT +
                r")(?P<v>\+?1?\d{10})\b"), nanp_valido, True),
    ("PHONE_BR", "Brazilian phone number", "Telefone do Brasil",
     re.compile(r"(?<![\w+(])(?:\+55\s?\(?\d{2}\)?[\s.-]?" + _NUM_TEL_BR + r"|\(\d{2}\)\s?" + _NUM_TEL_BR +
                r"|\d{2}[\s.-]" + _NUM_TEL_BR + r")(?![\w])"), telefone_br_valido, True),
    ("ICD", "Diagnosis code (ICD-10)", "Código de doença (CID/ICD-10)",
     re.compile(r"(?i:\b(?:ICD(?:-?10)?(?:-?CM)?|CID(?:-?10)?|dx|diagnos[ie]s(?:\s+codes?)?|diagn[óo]stico)"
                r"\s*(?:codes?)?\s*[:#-]?\s*)(?P<v>" + _ICD + r"(?:\s*[,;/]\s*" + _ICD + r")*)\b"), None, False),
]
# ICD-10 code WITHOUT a label (e.g. "E11.9", "F32.A"). Only the strong form: chapter letter (A-T, V-Z; U is
# reserved for special codes) + 2 digits + "." + 1-4 alphanumerics, uppercase, standing alone (start of line,
# space, "(", "[", ",", ";", ":" before; space, punctuation or end after; not followed by ".digit" as in "E11.9.2").
# Tradeoff: an unlabeled part/room/version code with this exact shape (e.g. "Part B12.5") would also match. To limit
# that, a product/version word right before it (sku, part, model, room, version, step...) blocks the match unless the
# same line mentions a health term. A false positive only costs one reversible marker; a missed diagnosis leaks PHI.
_ICD_SOLTO = re.compile(r"(?:^|(?<=[\s(\[,;:]))(?P<v>[A-TV-Z]\d{2}\.[0-9A-Z]{1,4})(?![\w-]|[.,]\d)(?=[\s)\],;:.!?]|$)",
                        re.M)
_NEG_ICD = re.compile(
    r"(?i)\b(?:sku|part|item|model|order|invoice|inv|po|ref|serial|s/n|tracking|lot|batch|code|product|style|"
    r"room|suite|unit|apt|building|bldg|section|sec|chapter|ch|step|rule|version|ver|v|rev|release|table|fig|"
    r"figure|class|zone|row|seat|gate|flight|bay|aisle|pe[çc]a|modelo|vers[ãa]o|sala|se[çc][ãa]o)\b\.?\s*"
    r"(?:no\.?|number|num|n[ºo°]\.?)?\s*[:#=-]?\s*#?\s*$")

# Common health conditions/diagnoses and medications/procedures (en + pt), whole word, any case. Counted under
# "health"; replaced only with --health-terms. Kept curated and short: words with everyday meanings ("stroke" of a
# brush, "depression" in economics) are a known false-positive tradeoff, acceptable because they are only counted.
SAUDE_TERMOS = [
    # conditions / diagnoses (en)
    "diabetes", "diabetic", "prediabetes", "hypertension", "high blood pressure", "cancer", "tumor", "leukemia",
    "lymphoma", "melanoma", "chemotherapy", "chemo", "radiation therapy", "hiv", "hepatitis", "tuberculosis",
    "pregnant", "pregnancy", "prenatal", "miscarriage", "abortion", "ivf", "depression", "anxiety", "panic disorder",
    "bipolar", "schizophrenia", "ptsd", "adhd", "autism", "ocd", "eating disorder", "anorexia", "bulimia",
    "dementia", "alzheimer", "parkinson's", "parkinson’s", "epilepsy", "seizure disorder", "multiple sclerosis", "lupus",
    "asthma", "copd", "emphysema", "stroke", "heart attack", "heart disease", "heart failure", "arrhythmia",
    "stent", "pacemaker", "bypass surgery", "dialysis", "kidney disease", "cirrhosis", "hiv positive",
    "overdose", "opioid use disorder", "alcoholism", "substance abuse", "addiction", "suicidal", "suicide attempt",
    "mastectomy", "hysterectomy", "rheumatoid arthritis", "crohn's", "crohn’s", "celiac disease",
    # medications (en: generic + common brand names)
    "insulin", "metformin", "ozempic", "semaglutide", "mounjaro", "tirzepatide", "lisinopril", "amlodipine",
    "atorvastatin", "warfarin", "eliquis", "oxycodone", "hydrocodone", "fentanyl", "morphine", "methadone",
    "buprenorphine", "suboxone", "naloxone", "narcan", "tramadol", "codeine", "oxycontin", "percocet", "vicodin",
    "sertraline", "zoloft", "fluoxetine", "prozac", "escitalopram", "lexapro", "citalopram", "paroxetine", "paxil",
    "bupropion", "wellbutrin", "venlafaxine", "effexor", "duloxetine", "cymbalta", "trazodone", "lithium carbonate",
    "alprazolam", "xanax", "lorazepam", "ativan", "clonazepam", "klonopin", "diazepam", "valium", "adderall",
    "ritalin", "methylphenidate", "quetiapine", "seroquel", "aripiprazole", "abilify", "risperidone", "olanzapine",
    "truvada", "biktarvy", "antiretroviral", "antidepressant", "antidepressants", "antipsychotic",
    # conditions / diagnoses (pt)
    "diabético", "diabetico", "diabética", "diabetica", "hipertensão", "hipertensao", "pressão alta", "câncer",
    "tumor", "leucemia", "linfoma", "quimioterapia", "quimio", "radioterapia", "hepatite", "tuberculose", "gestante",
    "grávida", "gravida", "gravidez", "pré-natal", "pre-natal", "aborto", "depressão", "depressao", "ansiedade",
    "transtorno bipolar", "esquizofrenia", "autismo", "tdah", "demência", "demencia", "epilepsia",
    "convulsão", "esclerose múltipla", "asma", "dpoc", "enfisema", "avc", "derrame", "infarto", "cardiopatia",
    "insuficiência cardíaca", "marca-passo", "marcapasso", "diálise", "dialise", "doença renal", "cirrose",
    "dependência química", "alcoolismo", "overdose", "mastectomia", "histerectomia",
    # medications (pt)
    "insulina", "metformina", "morfina", "codeína", "codeina", "metadona", "fentanil", "oxicodona", "tramadol",
    "sertralina", "fluoxetina", "escitalopram", "citalopram", "paroxetina", "bupropiona", "venlafaxina",
    "duloxetina", "trazodona", "alprazolam", "clonazepam", "rivotril", "diazepam", "antidepressivo",
    "antidepressivos", "antipsicótico", "ritalina", "quetiapina", "risperidona",
]
_SAUDE_RE = None


def regex_saude():
    """Whole-word, any case, NFC or NFD, optional English plural "s"."""
    global _SAUDE_RE
    if _SAUDE_RE is None:
        termos = sorted({unicodedata.normalize("NFC", x) for x in SAUDE_TERMOS}, key=len, reverse=True)
        _SAUDE_RE = re.compile(rf"(?i)(?<![\w{_MARCAS}-])(?:" + "|".join(_padrao_nome(x) for x in termos) +
                               rf")s?(?![\w{_MARCAS}-])")
    return _SAUDE_RE


def _linha(texto, ini, fim):
    a = texto.rfind("\n", 0, ini) + 1
    b = texto.find("\n", fim)
    return texto[a:b if b >= 0 else len(texto)]


def icd_solto_valido(valor, texto, ini, fim):
    """Unlabeled ICD-10 code: accept unless a product/version word precedes it and the line has no health term."""
    if not _NEG_ICD.search(texto[max(0, ini - 40):ini]):
        return True
    linha = _linha(texto, ini, fim)
    return bool(regex_saude().search(linha) or _tem_termo_saude_generico(linha))


def _tem_termo_saude_generico(linha):
    baixo = unicodedata.normalize("NFC", linha).lower()
    return any(re.search(r"(?<![\w-])" + re.escape(x) + r"(?![\w-])", baixo) for x in TERMOS_SENSIVEIS[_SAUDE_CAT])


icd_solto_valido.contexto = True
PADROES.append(("ICD", "Diagnosis code (ICD-10)", "Código de doença (CID/ICD-10)", _ICD_SOLTO, icd_solto_valido,
                False))


def padrao_saude():
    tipo = "SAUDE" if LANG == "pt" else "HEALTH"
    return [(tipo, "Health condition / medication", "Condição de saúde / medicamento", regex_saude(), None, False)]


GRAVES = {"CREDENTIAL", "API_KEY", "CARD"}
NUMERICOS = {"CPF", "CNPJ", "CARD", "CASE_BR", "CASE_FED", "PHONE", "PHONE_BR", "RG", "ACCOUNT", "SSN", "ITIN",
             "EIN", "ROUTING", "A_NUMBER", "POLICY", "LOAN", "USCIS_RECEIPT", "MBI", "PASSPORT", "DRIVER_LICENSE"}

# Special-category terms (en + pt). Counted only, never replaced.
TERMOS_SENSIVEIS = {
    ("health", "saúde"): [
        "diagnosis", "medical record", "medical records", "prescription", "disorder", "medication",
        "mental health", "therapy session", "treatment plan", "patient", "phi", "icd", "icd-10", "disability",
        "substance use", "rehab", "diagnóstico", "diagnostico", "prontuário", "prontuario", "atestado",
        "laudo médico", "transtorno", "medicação", "paciente", "cid", "saúde mental", "deficiência"],
    ("religion / beliefs", "religião/convicção"): [
        "religion", "religious", "church", "mosque", "synagogue", "religião", "religiao", "igreja",
        "convicção religiosa"],
    ("sexual orientation / sex life", "orientação sexual / vida sexual"): [
        "sexual orientation", "gay", "lesbian", "homosexual", "bisexual", "transgender",
        "orientação sexual", "orientacao sexual", "homossexual", "bissexual", "transgênero"],
    ("race or ethnicity", "origem racial ou étnica"): [
        "race", "ethnicity", "ethnic origin", "raça", "etnia", "cor da pele"],
    ("union or political affiliation", "filiação sindical ou política"): [
        "union member", "labor union", "political party", "sindicato", "filiação sindical", "filiado ao partido"],
    ("biometrics / genetics", "biometria / genética"): [
        "biometric", "fingerprint", "facial recognition", "dna", "genetic", "biometria", "impressão digital",
        "reconhecimento facial", "genético"],
    ("children", "crianças ou adolescentes"): [
        "minor", "child", "children", "under 13", "student record", "custody",
        "menor de idade", "criança", "adolescente", "guarda do menor"],
    ("immigration status", "situação migratória"): [
        "immigration status", "undocumented", "asylum", "deportation", "removal proceedings", "green card",
        "visa overstay", "daca", "tps", "refugee", "asilo", "deportação", "indocumentado", "sem documentos",
        "status migratório"],
    ("criminal history", "antecedentes criminais"): [
        "criminal record", "arrest", "conviction", "felony", "misdemeanor", "antecedentes criminais", "condenação"],
    ("credit / loan data", "dados de crédito / empréstimo"): [
        "credit report", "credit history", "fico", "loan application", "form 1003", "adverse action",
        "bankruptcy", "foreclosure", "collections account", "relatório de crédito", "histórico de crédito",
        "falência", "pedido de empréstimo"],
    ("insurance underwriting", "subscrição de seguro"): [
        "underwriting", "medical exam", "paramedical exam", "tobacco use", "beneficiary", "beneficiaries",
        "exame médico", "beneficiário", "beneficiários"],
    ("financial data", "dados financeiros"): [
        "bank statement", "account balance", "credit score", "tax return", "w-2", "1099", "income", "debt",
        "extrato", "saldo", "renda mensal", "salário", "dívida", "score de crédito", "declaração de imposto"],
}

_SAUDE_CAT = ("health", "saúde")

FORMATOS_BINARIOS = {".pdf": "hint_pdf", ".xlsx": "hint_xls", ".xls": "hint_xls", ".xlsm": "hint_xls",
                     ".ods": "hint_ods", ".pptx": "hint_ppt", ".ppt": "hint_ppt", ".doc": "hint_doc",
                     ".odt": "hint_other", ".rtf": "hint_other"}
EXT_SAIDA_INVALIDA = {".docx", ".doc", ".pdf", ".xlsx", ".xls", ".pptx", ".odt", ".rtf"}
BOM_UTF16 = {"utf-16-le-bom": b"\xff\xfe", "utf-16-be-bom": b"\xfe\xff"}   # keep the original byte order
NOME_CODIFICACAO = {"utf-8": "UTF-8", "utf-8-sig": "UTF-8 BOM", "utf-16-le-bom": "UTF-16 LE",
                    "utf-16-be-bom": "UTF-16 BE",
                    "cp1252": "Windows-1252 (Excel default)", "latin-1": "Latin-1"}


# ---------------------------------------------------------------- reading and writing
def ler_texto(caminho):
    """Compatibility: return only the text."""
    return ler_documento(caminho)[0]


def ler_documento(caminho):
    """Return (text, encoding). For DOCX, encoding = 'docx'.
    Text is decoded straight from bytes: line endings (LF/CRLF) stay as in the original."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise ErroUsuario("not_found", p=caminho)
    if caminho.is_dir():
        raise ErroUsuario("is_dir", p=caminho)
    ext = caminho.suffix.lower()
    if ext in FORMATOS_BINARIOS:
        raise ErroUsuario("binary_fmt", ext=ext, hint=t(FORMATOS_BINARIOS[ext]))
    if ext == ".docx":
        try:
            with zipfile.ZipFile(caminho) as z:
                partes = [n for n in z.namelist()
                          if n.startswith("word/") and n.endswith(".xml")
                          and any(k in n for k in ("document", "header", "footer", "footnotes"))]
                if "word/document.xml" not in partes:
                    raise ErroUsuario("docx_no_body", n=caminho.name)
                textos = []
                for n in sorted(partes, key=lambda n: n != "word/document.xml"):
                    xml = z.read(n).decode("utf-8", errors="replace")
                    xml = re.sub(r"</w:p>", "\n", xml)
                    xml = re.sub(r"<w:tab/>", "\t", xml)
                    textos.append(unescape(re.sub(r"<[^>]+>", "", xml)))
                return "\n".join(textos), "docx"
        except (zipfile.BadZipFile, KeyError):
            raise ErroUsuario("docx_bad", n=caminho.name)
    dados = caminho.read_bytes()
    if b"\x00" in dados[:4096] and not dados.startswith((b"\xff\xfe", b"\xfe\xff")):
        raise ErroUsuario("binary", n=caminho.name)
    if dados.startswith(b"\xef\xbb\xbf"):
        tentativas = ["utf-8-sig"]
    elif dados.startswith(b"\xff\xfe"):
        tentativas = ["utf-16-le-bom"]
    elif dados.startswith(b"\xfe\xff"):
        tentativas = ["utf-16-be-bom"]
    else:
        tentativas = ["utf-8", "cp1252", "latin-1"]
    for enc in tentativas:
        try:
            if enc in BOM_UTF16:
                return dados[2:].decode(enc[:9]), enc
            return dados.decode(enc), enc
        except UnicodeDecodeError:
            continue
    raise ErroUsuario("undecodable", n=caminho.name)


def avisar_codificacao(enc, nome):
    if enc not in ("utf-8", "utf-8-sig", "docx"):
        print(t("enc_warn", n=nome, enc=NOME_CODIFICACAO.get(enc, enc)), file=sys.stderr)


def gravar_documento(caminho, texto, enc):
    """Write in the source encoding (text already holds the original line endings)."""
    if enc == "docx":
        enc = "utf-8"
    try:
        dados = BOM_UTF16[enc] + texto.encode(enc[:9]) if enc in BOM_UTF16 else texto.encode(enc)
    except UnicodeEncodeError:
        print(t("enc_fallback", enc=NOME_CODIFICACAO.get(enc, enc), n=caminho.name), file=sys.stderr)
        dados = texto.encode("utf-8")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(dados)


def saida_texto(caminho_saida, entrada_docx):
    """Output can never be .docx/.pdf etc. (it would be plain text with the wrong extension)."""
    ext = caminho_saida.suffix.lower()
    if ext in EXT_SAIDA_INVALIDA or (entrada_docx and ext not in (".txt", ".md")):
        novo = caminho_saida.with_suffix(".txt")
        print(t("out_text", new=novo.name, old=caminho_saida.name), file=sys.stderr)
        return novo
    return caminho_saida


def mesmo_arquivo(a, b):
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return False


def ler_mapa(caminho, obrigatorio):
    if not caminho.exists():
        if obrigatorio:
            raise ErroUsuario("map_missing", p=caminho)
        return {}
    try:
        mapa = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ErroUsuario("map_json", p=caminho)
    if not isinstance(mapa, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in mapa.items()):
        raise ErroUsuario("map_shape", p=caminho)
    return mapa


# ---------------------------------------------------------------- detection
_MARCAS = "̀-ͯ"   # combining accents (NFD text)


def _padrao_nome(nome):
    """Regex matching the name in NFC or NFD, any case, flexible spaces."""
    partes = []
    for ch in unicodedata.normalize("NFC", nome):
        if ch.isspace():
            if not partes or partes[-1] != r"\s+":
                partes.append(r"\s+")
            continue
        nfd = unicodedata.normalize("NFD", ch)
        partes.append(f"(?:{re.escape(ch)}|{re.escape(nfd)})" if nfd != ch else re.escape(ch))
    return "".join(partes)


def padroes_nomes(nomes):
    """User-given names become the highest-priority pattern."""
    lista = sorted({unicodedata.normalize("NFC", " ".join(n.split())) for n in nomes if n and n.strip()},
                   key=len, reverse=True)
    if not lista:
        return []
    regex = re.compile(rf"(?i)(?<![\w{_MARCAS}])(?:" + "|".join(_padrao_nome(n) for n in lista) +
                       rf")(?![\w{_MARCAS}])")
    return [("PERSON", "Name given by the user", "Nome informado pelo usuário", regex, None, False)]


def encontrar(texto, nomes=(), saude=False):
    """Return a list of (start, end, type, value) without overlaps. saude=True also returns named health
    conditions/medications (lowest priority)."""
    ocupado, achados = [], []
    for tipo, _en, _pt, regex, validador, negativo in padroes_nomes(nomes) + PADROES + (padrao_saude() if saude else []):
        for m in regex.finditer(texto):
            if "v" in regex.groupindex and m.group("v") is not None:
                ini, fim = m.span("v")
            else:
                ini, fim = m.span()
            valor = texto[ini:fim]
            if validador and not (validador(valor, texto, ini, fim) if getattr(validador, "contexto", False)
                                  else validador(valor)):
                continue
            if negativo and m.start() == ini and _NEG.search(texto[max(0, ini - 40):ini]):
                continue
            if any(ini < f and fim > i for i, f in ocupado):
                continue
            ocupado.append((ini, fim))
            achados.append((ini, fim, tipo, valor))
    achados.sort()
    return achados


def mascarar(valor, tipo=""):
    """Show at most 2-4 characters of the value."""
    v = " ".join(valor.split())
    n = len(v)
    if tipo in GRAVES:
        return v[:2] + "*" * max(4, n - 2) if n > 6 else "*" * n
    if n <= 6:
        return "*" * n
    if n < 12:
        return v[0] + "*" * (n - 2) + v[-1]
    return v[:2] + "*" * (n - 4) + v[-2:]


def contar_termos(texto):
    baixo = unicodedata.normalize("NFC", texto).lower()
    res = {}
    for categoria, termos in TERMOS_SENSIVEIS.items():
        n = sum(len(re.findall(r"(?<![\w-])" + re.escape(x) + r"(?![\w-])", baixo)) for x in termos)
        if categoria == _SAUDE_CAT:
            n += contar_saude(texto)
        if n:
            res[categoria] = n
    return res


def contar_saude(texto):
    """Mentions of named health conditions/medications."""
    return len(regex_saude().findall(texto))


# ---------------------------------------------------------------- commands
def relatorio(achados, termos, nome, saude_n=0, saude_on=False):
    i = 1 if LANG == "pt" else 0
    desc = {p[0]: p[1 + i] for p in PADROES}
    desc["PERSON"] = ("Name given by the user", "Nome informado pelo usuário")[i]
    desc["HEALTH"] = desc["SAUDE"] = ("Health condition / medication", "Condição de saúde / medicamento")[i]
    print(t("scan_title", n=nome))
    if not achados and not termos:
        print(t("nothing"))
    por_tipo = {}
    for _i, _f, tipo, valor in achados:
        por_tipo.setdefault(tipo, []).append(valor)
    if por_tipo:
        print("\n" + t("ids"))
        for tipo, vals in por_tipo.items():
            print(t("id_line", d=desc[tipo], k=len(vals), ex=mascarar(vals[0], tipo)))
    if termos:
        print("\n" + t("terms"))
        for cat, n in termos.items():
            print(t("term_line", c=cat[i], k=n))
        if saude_n and not saude_on:
            print(t("health_hint", k=saude_n))
    if GRAVES & set(por_tipo):
        print("\n" + t("grave"))
    print("\n" + t("limits"))


CHAVE_CODIFICACAO = "__codificacao__"   # encoding of the last pseudonymized original (to revert the same way)
_RE_MARCADOR = re.compile(r"\[([A-Z][A-Z_]*?)_(\d+)(?:_v(\d+))?\]")


def chave_normalizada(tipo, valor):
    """Same person/identifier written with different case, accents (NFC/NFD) or punctuation."""
    v = unicodedata.normalize("NFC", valor)
    if tipo in NUMERICOS:
        return re.sub(r"[^0-9A-Z]", "", v.upper())
    return " ".join(v.casefold().split())


def anonimizar(texto, achados, mapa_existente):
    """Replace each finding with a marker. Different forms of the same value (e.g. case) get the same number
    with a variant suffix ([PERSON_1], [PERSON_1_v2]) so reversal returns the exact text."""
    mapa = dict(mapa_existente)                  # marker -> exact original value
    exato = {v: k for k, v in mapa.items() if _RE_MARCADOR.fullmatch(k)}
    grupo, contadores, variantes = {}, {}, {}
    for marcador, val in mapa.items():
        m = _RE_MARCADOR.fullmatch(marcador)
        if not m:
            continue
        tipo, n, var = m.group(1), int(m.group(2)), int(m.group(3) or 1)
        contadores[tipo] = max(contadores.get(tipo, 0), n)
        variantes[(tipo, n)] = max(variantes.get((tipo, n), 1), var)
        grupo.setdefault((tipo, chave_normalizada(tipo, val)), n)
    partes, pos = [], 0
    for ini, fim, tipo, valor in achados:
        if valor not in exato:
            chave = (tipo, chave_normalizada(tipo, valor))
            if chave in grupo:
                n = grupo[chave]
                variantes[(tipo, n)] = variantes.get((tipo, n), 1) + 1
                marcador = f"[{tipo}_{n}_v{variantes[(tipo, n)]}]"
            else:
                contadores[tipo] = contadores.get(tipo, 0) + 1
                n = contadores[tipo]
                grupo[chave] = n
                variantes[(tipo, n)] = 1
                marcador = f"[{tipo}_{n}]"
            exato[valor] = marcador
            mapa[marcador] = valor
        partes.append(texto[pos:ini])
        partes.append(exato[valor])
        pos = fim
    partes.append(texto[pos:])
    return "".join(partes), mapa


def reverter(texto, mapa):
    faltando = set()

    def troca(m):
        if m.group(0) in mapa:
            return mapa[m.group(0)]
        faltando.add(m.group(0))
        return m.group(0)

    return _RE_MARCADOR.sub(troca, texto), sorted(faltando)


def main():
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo", help="file to scan / arquivo a analisar")
    ap.add_argument("--anonimizar", "--pseudonymize", dest="anonimizar", metavar="OUT",
                    help="write a copy with markers instead of the data / grava cópia com marcadores")
    ap.add_argument("--reverter", "--revert", dest="reverter", metavar="OUT",
                    help="replace markers with the original values using the map / reverte com o mapa")
    ap.add_argument("--mapa", "--map", dest="mapa", metavar="MAP.json",
                    help="map file (required with --anonimizar/--reverter) / arquivo do mapa")
    ap.add_argument("--nomes", "--names", dest="nomes", default="",
                    help='names to replace, separated by ";" (e.g. "John Smith;ACME LLC") / nomes a substituir')
    ap.add_argument("--health-terms", "--termos-saude", dest="saude", action="store_true",
                    help="also replace health conditions/medications with [HEALTH_n]/[SAUDE_n] markers / "
                         "substitui também condições de saúde e medicamentos")
    ap.add_argument("--lang", choices=("en", "pt"), default="en", help="message language (default en)")
    args = ap.parse_args()
    LANG = args.lang
    if args.anonimizar and args.reverter:
        raise ErroUsuario("both_modes")

    caminho = Path(args.arquivo).expanduser()
    alvo = args.anonimizar or args.reverter
    mapa_path = Path(args.mapa).expanduser() if args.mapa else None
    if alvo:
        if not mapa_path:
            raise ErroUsuario("need_map_rev" if args.reverter else "need_map_anon")
        saida = saida_texto(Path(alvo).expanduser(), caminho.suffix.lower() == ".docx")
        if mesmo_arquivo(saida, caminho):
            raise ErroUsuario("same_io")
        if mesmo_arquivo(saida, mapa_path) or mesmo_arquivo(caminho, mapa_path):
            raise ErroUsuario("map_sep")

    texto, enc = ler_documento(caminho)
    avisar_codificacao(enc, caminho.name)

    if args.reverter:
        mapa = ler_mapa(mapa_path, obrigatorio=True)
        if texto.isascii() and enc in ("utf-8", "cp1252", "latin-1") and mapa.get(CHAVE_CODIFICACAO):
            enc = mapa[CHAVE_CODIFICACAO]    # ASCII-only copy: write back in the original's encoding
        novo, faltando = reverter(texto, mapa)
        gravar_documento(saida, novo, enc)
        print(t("reverted", p=saida))
        if faltando:
            print(t("rev_missing", k=len(faltando), lst=", ".join(faltando[:10])), file=sys.stderr)
        return

    achados = encontrar(texto, args.nomes.split(";"), saude=args.saude)
    termos = contar_termos(texto)
    relatorio(achados, termos, caminho.name, contar_saude(texto), args.saude)

    if args.anonimizar:
        existente = ler_mapa(mapa_path, obrigatorio=False)
        novo, mapa = anonimizar(texto, achados, existente)
        mapa[CHAVE_CODIFICACAO] = "utf-8" if enc == "docx" else enc
        gravar_documento(saida, novo, enc)
        mapa_path.parent.mkdir(parents=True, exist_ok=True)
        mapa_path.write_text(json.dumps(mapa, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\n" + t("anon_copy", p=saida))
        print(t("anon_map", p=mapa_path))


if __name__ == "__main__":
    if "--lang" in sys.argv[1:-1]:
        LANG = "pt" if sys.argv[sys.argv.index("--lang") + 1] == "pt" else "en"
    elif any(a == "--lang=pt" for a in sys.argv):
        LANG = "pt"
    try:
        main()
    except ErroUsuario as e:
        sys.exit(t("err", m=e.texto()))
    except PermissionError as e:
        sys.exit(t("perm", p=e.filename))
    except OSError as e:
        sys.exit(t("oserr", m=e.strerror or e, p=e.filename or ""))
