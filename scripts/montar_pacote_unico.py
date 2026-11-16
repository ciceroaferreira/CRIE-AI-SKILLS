#!/usr/bin/env python3
"""Monta docs/downloads/crie-skills.zip: as 7 skills numa skill só (um upload no app do Claude).

Fonte: plugins/crie-skills/skills/<skill>/ (a mesma do plugin do Claude Code) + bundle/SKILL.md (roteador).
Cada skill vira crie-skills/modulos/<skill>/, com o SKILL.md renomeado para GUIA.md.

Uso (na raiz do repositório):  python3 scripts/montar_pacote_unico.py
Rode de novo sempre que mudar alguma skill.
"""

import re
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "plugins" / "crie-skills" / "skills"
ROTEADOR = RAIZ / "bundle" / "SKILL.md"
SAIDA = RAIZ / "docs" / "downloads" / "crie-skills.zip"
IGNORAR = {"__pycache__", ".DS_Store"}
DATA_FIXA = (2026, 1, 1, 0, 0, 0)  # zip igual a cada execução, sem diff falso no git


def checar_roteador(texto):
    m = re.match(r"---\n(.*?)\n---\n", texto, re.S)
    if not m:
        raise SystemExit("bundle/SKILL.md sem frontmatter")
    desc = re.search(r"^description:\s*(.+)$", m.group(1), re.M).group(1).strip()
    if len(desc.encode("utf-8")) > 1024 or "<" in desc or ">" in desc:
        raise SystemExit(f"descrição do roteador inválida ({len(desc.encode())} bytes; máx. 1024, sem < >)")


def adicionar(z, nome, dados, executavel=False):
    info = zipfile.ZipInfo(nome, DATA_FIXA)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o755 if executavel else 0o644) << 16
    z.writestr(info, dados)


def main():
    roteador = ROTEADOR.read_text(encoding="utf-8")
    checar_roteador(roteador)
    modulos = sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SAIDA, "w") as z:
        adicionar(z, "crie-skills/SKILL.md", roteador.encode("utf-8"))
        for mod in modulos:
            for arq in sorted(mod.rglob("*")):
                if arq.is_dir() or IGNORAR & set(arq.parts):
                    continue
                rel = arq.relative_to(mod).as_posix()
                dados = arq.read_bytes()
                if rel == "SKILL.md":
                    rel = "GUIA.md"
                if arq.suffix == ".md":
                    dados = dados.decode("utf-8").replace("SKILL.md", "GUIA.md").encode("utf-8")
                adicionar(z, f"crie-skills/modulos/{mod.name}/{rel}", dados, arq.suffix == ".py")
    print(f"{SAIDA.relative_to(RAIZ)}: {len(modulos)} módulos, {SAIDA.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
