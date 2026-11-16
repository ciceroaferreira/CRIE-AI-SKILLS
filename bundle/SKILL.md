---
name: crie-skills
description: All-in-one Claude toolkit for US small businesses from the CRIE AI talk, in English or Portuguese. Seven modules - company onboarding (interview, company folder, specialist team, confidentiality rules), brand identity (colors, fonts, voice), pricing (what to charge, markup, margin, break-even, sales tax), proposals and estimates (quotes, bids, change orders), customer service replies (SMS, WhatsApp, Instagram, Google reviews, refunds, scams), content calendar (posts, captions, Reels, US holidays) and a monthly report from bank or card statements (cash flow, where the money went). Use whenever a business owner asks for any of these or sends a customer document. Portuguese triggers - onboarding da empresa, configurar o Claude para minha empresa, marca, quanto cobrar, preço, proposta, orçamento, responder cliente, atendimento, o que postar, calendário de conteúdo, extrato bancário, fechamento do mês, para onde foi o dinheiro.
---

# CRIE Skills — 7 modules in one / 7 módulos em um

This skill bundles the seven CRIE skills so participants install **one** file. Each module keeps its own full
guide in `modulos/<module>/GUIA.md`. Your job here is only to pick the right module, read its guide and follow
it exactly as if it were a standalone skill.

## How to route / Como encaminhar

1. Pick the module from the table. If the request spans several (e.g. "price this job and send a proposal"),
   start with the first step's module and move to the next when it is done.
2. Read **only** that module's `GUIA.md` before answering. Don't load the others unless needed.
3. If the request is vague, or the user is new ("what can you do?", "o que você faz?"), offer the onboarding
   first: it sets up the company folder that every other module uses. Then list the modules in one line each.

| Module | Use when the user… | Guide |
|---|---|---|
| `onboarding-empresa` | wants to set up Claude for the business, onboard, build a virtual team, or **sends a customer document** (contracts, case files, tax, health, customer spreadsheets) — its security protocol comes first | `modulos/onboarding-empresa/GUIA.md` |
| `marca-da-empresa` | asks for brand, logo, colors, fonts, tone of voice, style guide, "make it look like our company" | `modulos/marca-da-empresa/GUIA.md` |
| `precificacao` | asks what to charge, price, markup, margin, break-even, hourly rate, menu prices, job bid math, sales tax, tax set-aside, commission targets | `modulos/precificacao/GUIA.md` |
| `proposta-comercial` | wants a proposal, estimate, quote, bid, scope of work, change order, engagement letter or a follow-up on one | `modulos/proposta-comercial/GUIA.md` |
| `atendimento-clientes` | pastes a customer message, wants replies, canned answers, FAQ, return policy, review requests, help with an angry customer or a possible scam | `modulos/atendimento-clientes/GUIA.md` |
| `calendario-conteudo` | asks what to post, content calendar, captions, Reels/TikTok scripts, holiday campaign, giveaway | `modulos/calendario-conteudo/GUIA.md` |
| `relatorio-mensal-gestao` | shares a bank or card statement (CSV, QFX, OFX), asks how the month went, where the money went, cash flow, month-end report | `modulos/relatorio-mensal-gestao/GUIA.md` |

## Path rules / Regras de caminho

- Inside a module guide, `<skill>`, `<skill folder>` and every relative path (`references/…`, `scripts/…`,
  `assets/…`) mean **that module's folder**: `<this skill>/modulos/<module>/`. Example:
  `python3 -I <this skill>/modulos/precificacao/scripts/calcular_preco.py …`.
- When a guide mentions another skill by name ("use the `precificacao` skill if installed",
  "created by the onboarding-empresa skill"), that skill **is installed**: it is the module with the same name
  in `modulos/`. Read its `GUIA.md` and continue.

## Always / Sempre

- Reply in the user's language (English or Portuguese).
- If the current folder has a company `CLAUDE.md` or `00-company/` / `00-empresa/`, read it first: it holds the
  profile, brand and folder map that all modules use.
- The onboarding security protocol (`modulos/onboarding-empresa/references/seguranca.md`) applies to every
  module whenever customer documents or personal data are involved.
