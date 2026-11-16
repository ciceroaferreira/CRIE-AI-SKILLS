# CRIE AI Skills

**Português** · [English](#english)

Sete skills do Claude para pequenas empresas nos EUA, criadas para a palestra de IA do CRIE Orlando. Elas transformam o Claude em um time de especialistas que conhece o seu negócio, organiza uma pasta de trabalho e entrega o serviço pronto, em português ou inglês.

**Site:** https://ciceroaferreira.github.io/CRIE-AI-SKILLS/ · **Catálogo com 33 skills verificadas:** [docs/catalogo.html](docs/catalogo.html)

## As skills

| Skill | O que faz |
|---|---|
| `onboarding-empresa` | Entrevista sobre a empresa, identifica o setor (seguros, construção, financeiras, contabilidade, advocacia e imigração, imóveis, limpeza, alimentação e outros), cria a pasta de trabalho, o time de especialistas, as rotinas e as regras de sigilo. **Instale primeiro.** |
| `marca-da-empresa` | Cores com contraste legível, fontes e tom de voz em inglês e português, aplicados em todas as entregas. |
| `precificacao` | Preço em dólar para produto, serviço, cardápio, obra ou comissão, com taxas de cartão e apps, sales tax por fora, margem e reserva para impostos. |
| `proposta-comercial` | Propostas e orçamentos com opções, termos de pagamento, ordens de alteração para obras, análise de necessidades para seguros e regras de consumidor. |
| `atendimento-clientes` | Respostas para SMS, WhatsApp, Instagram, Google e e-mail no idioma do cliente, casos difíceis, avaliações e alertas de golpe. |
| `calendario-conteudo` | O mês de posts com legendas bilíngues, calendário do varejo americano e regras de publicidade por setor. |
| `relatorio-mensal-gestao` | Lê extratos do Chase, Bank of America, Wells Fargo, Capital One, Amex e outros e mostra para onde foi o dinheiro. |

## Como instalar

**App do Claude (site, desktop ou Cowork)**
1. Baixe [`docs/downloads/crie-skills.zip`](docs/downloads/crie-skills.zip). **Não descompacte.** As 7 skills estão dentro dele.
2. No Claude: **Configurações → Capacidades**, ative **Execução de código e criação de arquivos**.
3. Em **Skills**, clique em **Fazer upload** e envie o `crie-skills.zip`. É um upload só.
4. Numa conversa nova: *"Quero fazer o onboarding da minha empresa."*

**Claude Code**
```
/plugin marketplace add ciceroaferreira/CRIE-AI-SKILLS
/plugin install crie-skills@crie-ai-skills
```

## Segurança

- Uma varredura local procura SSN, ITIN, EIN, contas, cartões, apólices, processos e dados de saúde antes de qualquer análise e só mostra os valores mascarados.
- Nomes e números podem virar marcadores reversíveis; o mapa fica só no seu computador.
- Instruções escondidas em documentos são tratadas como dados, nunca como ordens.
- Entregas jurídicas, fiscais, de seguros e de crédito são rascunhos para o profissional licenciado revisar. Os planos pessoais do Claude não incluem BAA para HIPAA.

As skills orientam com base em regras gerais dos EUA e marcam o que varia por estado. Elas não substituem advogado, contador ou a área de conformidade.

---

## English

Seven Claude skills for small businesses in the US, built for the CRIE Orlando AI talk. They turn Claude into a team of specialists that knows your business, sets up a work folder and delivers finished work, in English or Portuguese.

**Website:** https://ciceroaferreira.github.io/CRIE-AI-SKILLS/ · **Catalog of 33 vetted skills:** [docs/catalogo.html](docs/catalogo.html)

| Skill | What it does |
|---|---|
| `onboarding-empresa` | Interviews you about the business, detects the industry (insurance, construction, financial services, accounting, law and immigration, real estate, cleaning, food and more), creates the work folder, specialist team, routines and confidentiality rules. **Install it first.** |
| `marca-da-empresa` | Readable brand colors, fonts and voice in English and Portuguese, applied to every deliverable. |
| `precificacao` | Pricing in USD for products, services, menus, construction jobs or commissions, with card and app fees, sales tax on top, margin and a tax set-aside. |
| `proposta-comercial` | Proposals and estimates with options, payment terms, change orders for construction, needs analysis for insurance and consumer rules. |
| `atendimento-clientes` | Replies for SMS, WhatsApp, Instagram, Google and email in the customer's language, hard cases, reviews and scam alerts. |
| `calendario-conteudo` | A month of posts with bilingual captions, the US retail calendar and industry ad rules. |
| `relatorio-mensal-gestao` | Reads Chase, Bank of America, Wells Fargo, Capital One, Amex and other statements and shows where the money went. |

**Install in the Claude app:** download [`docs/downloads/crie-skills.zip`](docs/downloads/crie-skills.zip) (don't unzip it; all 7 skills are inside), then in Claude go to **Settings → Capabilities**, turn on **Code execution and file creation**, and under **Skills** upload `crie-skills.zip`. That's one upload. Then open a new chat and say *"I want to onboard my business."*

**Install in Claude Code:**
```
/plugin marketplace add ciceroaferreira/CRIE-AI-SKILLS
/plugin install crie-skills@crie-ai-skills
```

The skills give general US guidance and flag what varies by state. They don't replace your attorney, CPA or compliance team.

## Repository layout

```
.claude-plugin/marketplace.json     Claude Code marketplace
plugins/crie-skills/skills/         source of the 7 skills
bundle/SKILL.md                     router that turns the 7 skills into one upload
scripts/montar_pacote_unico.py      builds docs/downloads/crie-skills.zip
docs/                               website (GitHub Pages) and downloads
```

After changing any skill, rebuild the single-upload zip: `python3 scripts/montar_pacote_unico.py`.
The per-skill zips and `Pacote-CRIE-Skills.zip` in `docs/downloads/` still work for anyone who wants only some skills.
