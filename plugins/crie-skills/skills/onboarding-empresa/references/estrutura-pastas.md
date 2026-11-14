# Folder structure (manual creation, if Python is not available)

`<skill folder>/scripts/criar_estrutura.py` does all of this automatically. Use this guide only if you cannot
run it. Never overwrite existing files. Names follow the profile's `idioma`.

| Key | Portuguese (`idioma: pt`) | English (`idioma: en`) |
|---|---|---|
| profile | `00-empresa/perfil-da-empresa.md` | `00-company/company-profile.md` |
| sector | `00-empresa/setor.md` | `00-company/industry.md` |
| brand | `00-empresa/marca.md` + `marca.json` | `00-company/brand.md` + `brand.json` |
| marketing | `01-marketing/` | `01-marketing/` |
| finance | `02-financas/` | `02-finance/` |
| it | `03-ti/` | `03-it/` |
| admin | `04-administrativo/` | `04-admin/` |
| hr | `05-rh/` | `05-hr/` |
| sales | `06-comercial/` | `06-sales/` |
| legal | `07-juridico/` | `07-legal/` |
| operations | `08-operacoes/` | `08-operations/` |
| strategy | `09-estrategia/` | `09-strategy/` |
| personas | `personas/` | `personas/` |
| routines | `rotinas/` | `routines/` |
| templates | `modelos/` | `templates/` |
| confidential | `confidencial/` (+ `mapas/`) | `confidential/` (+ `maps/`) |
| tools | `ferramentas/detectar_dados_sensiveis.py` | `tools/detectar_dados_sensiveis.py` |
| security rules | `SEGURANCA.md` | `SECURITY.md` |
| deliverables | `99-entregas/` | `99-deliverables/` |

English example (Portuguese uses the left column):
```
<destination>/
├── CLAUDE.md                  ← assets/en/CLAUDE.template.md filled in (includes "Folder map / Mapa de pastas")
├── SECURITY.md                ← assets/en/SECURITY.template.md filled in for the level
├── .gitignore                 ← contains "confidential/"
├── .claude/settings.json      ← only at "regulated": reduces web access (denies WebSearch, WebFetch, curl, wget, scp, rsync, ftp; applies only in Claude Code / Code tab; does not block connectors or scripts)
├── 00-company/
│   ├── company-profile.md     ← onboarding answers (never customer data)
│   └── industry.md            ← copy of the industry pack, custom pack, or minimal "to fill in" file
├── 01-marketing/ … 09-strategy/   README.md per chosen area (unchosen areas are created on first use)
├── 11-<industry-specialist>/  README.md per extra persona
├── personas/                  ← base persona cards (references/personas/ or personas/pt/) + extras
├── routines/                  ← playbooks (one .md per routine) + README.md
├── templates/                 ← company templates (contracts, proposals…)
├── confidential/
│   ├── README.md
│   └── maps/                  ← pseudonymization maps
├── tools/detectar_dados_sensiveis.py   ← copy of the scan script
└── 99-deliverables/           ← deliverables without customer data
```

`CLAUDE.md` starts with a small block other skills read:
```
idioma: en
idioma_entregas: both
security_level: regulated
```

`.claude/settings.json` (regulated level only):
```json
{ "permissions": { "deny": ["WebSearch", "WebFetch", "Bash(curl:*)", "Bash(wget:*)", "Bash(scp:*)", "Bash(rsync:*)", "Bash(ftp:*)"] } }
```
