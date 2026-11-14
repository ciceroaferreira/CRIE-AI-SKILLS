---
name: precificacao
description: Calculates the right selling price in USD for US small businesses (products, menus, services, contractor jobs) from direct cost, fixed costs, card, app and marketplace fees, commissions and the desired pre-tax profit. Shows markup vs margin, contribution margin, break-even (per product, per hour or for the whole business), hourly, project, per-visit, recurring and per-square-foot prices, deposits and payment schedules, change orders, margin scenarios, sales tax on top and how much profit to set aside for income and self-employment tax. Also plans sales, leads and marketing budget for commission sellers (insurance agents, loan brokers). Use when the user asks how much to charge, pricing, menu prices, hourly rate, job estimate or bid, markup, margin, break-even, raising prices, DoorDash, Etsy or Amazon pricing, or in Portuguese quanto cobrar, precificar, preço de venda, cardápio, valor da hora, orçamento de obra, margem, ponto de equilíbrio, reajuste de preço, quantas apólices vender, reserva de imposto.
---

# Pricing (Precificação)

Help the owner find a price that covers every cost and leaves profit, and explain the math in plain words.
Reply in the language the user writes in (English or Portuguese) and pass `--lang en|pt` to the script accordingly.

## 1. Context

- Read `CLAUDE.md` first and use its **Folder map / Mapa de pastas**. Without it, look for `00-company/company-profile.md`
  or `00-empresa/perfil-da-empresa.md` (business structure, state, industry, average ticket). If no company folder exists,
  work in the current folder and ask only what is missing.
- Follow `SECURITY.md` / `SEGURANCA.md` if present. Cost sheets and revenue are company data: save results in the
  finance folder (`02-finance/` or `02-financas/`), never in memory.
- Customer-facing material (price lists, quotes, proposals): use `deliverables_language` / `idioma_entregas` from the
  profile; if absent, ask once ("Should customer-facing material be in English, Portuguese, or both?"). Default English.

## 2. How US taxes enter the price (explain this when relevant)

- **Sales tax is not part of your price.** It is added on top at checkout for taxable items, collected for the state and
  passed on. Never put it in the price divisor. `--sales-tax 7` only shows what the customer pays. On Amazon, Etsy, eBay,
  DoorDash, Uber Eats and Grubhub the platform collects it in most states (marketplace facilitator laws).
- **Income tax and self-employment tax are on profit, not on revenue.** `--margin` is a **pre-tax** profit margin;
  `--tax-setaside 30` shows how much of the profit to set aside. Suggest 25–35% as a rough planning range for federal +
  state + SE tax for sole props and single-member LLCs, always marked as an estimate to confirm with a CPA.
- `--revenue-taxes` only for gross-receipts taxes charged on revenue (a few states/cities). Usually 0.
- Details and fee ranges: `references/us-taxes-and-fees.md`.

## 3. Identify the case and collect the numbers

Ask everything missing in one message. Accept estimates and label them as estimates.

**Product** (food, retail, handmade):
1. Direct cost per unit: ingredients, packaging, goods. For recipes, build the recipe cost (ingredient × quantity × price).
2. Monthly fixed costs: rent, salaries + payroll costs, owner's pay, insurance, software, bookkeeping, utilities.
3. Monthly revenue (for fixed costs as % of revenue) or, if the business sells **one main product**, units per month.
4. Variable costs as % of price: card processing (~2.6–3.5%) plus the fixed fee per transaction (`--fee-per-sale 0.30`),
   delivery-app commission, marketplace fees, sales commission.
5. Desired pre-tax margin (suggest 10–20% if they don't know), current price, sales tax rate, tax set-aside %.

**Several products** (menu, catalog): never spread fixed costs per unit across items (one item's volume would carry all
fixed costs, or a $1 coffee would "pay" as much as a cake). Use **fixed costs as %** of revenue and `menu` mode.
Ask per item: name, direct cost, current price and, if known, units per month.

**Service** (cleaning, beauty, consulting, translation, repairs):
1. Monthly fixed costs (insurance, software, vehicle, phone, marketing) and the owner's pay target.
2. Billable hours per month: usually 60–70% of hours worked (travel, quotes and admin are not billable).
3. Crew: wage per hour (`--labor-rate`) and employer payroll costs (`--payroll-burden`, see reference). For 1099
   contractors use what you pay them as `--labor-rate` and burden 0 (watch misclassification rules).
4. Per job: labor hours (crew size × hours), supplies/travel, deposit, upfront discount, installments, square feet,
   visits per month and recurring discount.

**Contractor job** (remodel, construction, roofing): materials (with the sales tax you pay), crew hours × wage +
payroll burden, subcontractors, equipment rental, permits, dumpster, contingency (5–10% on remodels; if the proposal will show contingency as a separate line billed only by change order, run with `--contingency 0` and let proposta-comercial add that line), overhead and profit
either as **markup on cost** (the classic "10 and 10") or as **% of price**, payment schedule, change orders.

**Commission seller** (insurance agent, loan officer/broker): they don't set the price. Plan income instead: target
annual income, monthly expenses, average annual premium × first-year commission % (or average commission per sale),
renewal %, agency split, chargebacks, cost per lead and close rate.

## 4. Run the script

`<skill>` is the folder containing this SKILL.md. Use its absolute path; if unknown, find it with
`find ~ -name calcular_preco.py -path "*precificacao*" 2>/dev/null`. Run with `python3 -I`.

```
# Florida bakery, whole menu (CSV name,direct_cost,current_price,volume; `;` or tab also work; EN or PT headers)
python3 -I <skill>/scripts/calcular_preco.py menu --file items.csv --variable-pct 2.9 --margin 15 \
  --fixed-costs 28000 --sales-tax 7 --tax-setaside 30 --output <finance>/YYYY-MM-DD-menu-pricing.csv

# One menu item (fixed costs as % of revenue)
python3 -I <skill>/scripts/calcular_preco.py product --direct-cost 4.10 --variable-pct 2.9 --fee-per-sale 0.15 \
  --fixed-cost-pct 30 --margin 15 --current-price 11.99 --sales-tax 7

# Single-product business (fixed costs spread over total units)
python3 -I <skill>/scripts/calcular_preco.py product --direct-cost 8.50 --variable-pct 3 --fee-per-sale 0.30 \
  --fixed-costs 12000 --volume 3000 --margin 15 --current-price 14.99 --tax-setaside 30

# Massachusetts cleaning company: 2 cleaners x 1.5 h = 3 labor hours, 2,000 sq ft, biweekly = 2 visits/month
python3 -I <skill>/scripts/calcular_preco.py service --fixed-costs 3500 --owner-pay 6000 --billable-hours 320 \
  --labor-rate 22 --payroll-burden 15 --variable-pct 3 --margin 15 --project-hours 3 --direct-cost 12 \
  --sqft 2000 --visits-per-month 2 --recurring-discount 10 --tax-setaside 30

# Immigration paralegal / translation, hourly + a 6-hour case package with 50% deposit
python3 -I <skill>/scripts/calcular_preco.py service --fixed-costs 1800 --owner-pay 5500 --billable-hours 90 \
  --variable-pct 3 --margin 20 --current-price 60 --project-hours 6 --deposit-pct 50 --lang pt

# Food truck on DoorDash (Plus plan ~25% + processing; DoorDash collects the sales tax)
python3 -I <skill>/scripts/calcular_preco.py product --direct-cost 3.80 --variable-pct 28 --fixed-cost-pct 25 \
  --margin 12 --current-price 12

# Etsy seller (6.5% transaction + ~3% processing; $0.20 listing + $0.25 processing per sale)
python3 -I <skill>/scripts/calcular_preco.py product --direct-cost 9 --variable-pct 9.5 --fee-per-sale 0.45 \
  --fixed-cost-pct 15 --margin 20 --current-price 24.99

# Massachusetts bathroom remodel, "10 and 10", 1/3 deposit schedule, a change order
python3 -I <skill>/scripts/calcular_preco.py job --materials 9800 --crew-hours 120 --labor-rate 32 \
  --payroll-burden 25 --subcontractors 6500 --equipment 350 --permits 600 --dumpster 650 --contingency 8 \
  --overhead-markup 10 --profit-markup 10 --schedule 33/33/34 --change-order-cost 1200 --tax-setaside 30

# Insurance agent income plan
python3 -I <skill>/scripts/calcular_preco.py commission --target-income 90000 --fixed-costs 1200 \
  --avg-premium 1500 --first-year-pct 50 --renewal-pct 5 --payout-pct 80 --chargeback-pct 10 \
  --cost-per-lead 35 --close-rate 10 --tax-setaside 30

# Business break-even
python3 -I <skill>/scripts/calcular_preco.py business --fixed-costs 35000 --avg-cm-pct 45 --monthly-revenue 95000
```

- Percentages as % (6 = 6%). Numbers accept US or Brazilian style: `8.50`, `8,50`, `1,234.56`, `1.234,56`, `$8.50`, `6%`.
  A lone separator followed by 3 digits is thousands (`12,000` = `12.000`), except in % flags (`8.875` = 8.875%).
- Portuguese aliases work for modes (`produto`, `servico`, `cardapio`, `empresa`, `obra`, `comissao`) and main flags
  (`--custo-direto`, `--margem`, `--custo-fixo-mensal`, `--pro-labore`, `--horas-produtivas`, `--preco-atual` ...).
- `--price-includes-sales-tax` when current prices are tax-included (food trucks, events): the script uses the net price.
- `--json` for spreadsheets. Relay every `Note:`/`Nota:` and `Warning:`/`Aviso:` line to the user.

Without Python, do the same math by hand and show it:
- Single product: `Price = (direct cost + fixed costs ÷ volume + fee per sale) ÷ (1 − (variable% + margin%))`
- Fixed costs as %: `Price = (direct cost + fee per sale) ÷ (1 − (variable% + fixed% + margin%))`
- Contribution margin = price − direct cost − fees; CM% = CM ÷ price. Business break-even = `fixed costs ÷ weighted CM%`.
- Service: `cost per hour = (fixed costs + owner's pay) ÷ billable hours + wage × (1 + burden%)`.
- Job, markup method: `Price = costs × (1 + contingency%) × (1 + overhead%) × (1 + profit%)`; margin method:
  `Price = costs × (1 + contingency%) ÷ (1 − (overhead% + margin%))`.
- Commission: `sales needed = (target income + 12 × monthly expenses − renewals) ÷ (net commission − cost per lead ÷ close rate)`;
  `leads = sales ÷ close rate`; `marketing budget = leads × cost per lead`.

## 5. Explain the result

In this order:
1. **Suggested price** and the breakdown of each dollar: cost, fees, overhead, pre-tax profit (the script makes the parts
   add up to the cent). Then the tax set-aside and, if sales tax applies, what the customer pays.
2. **Current-price diagnosis**: profit or loss per unit (or hour) and per month (needs `--volume`; services assume every
   billable hour is sold).
3. **Break-even**: units/month for a single product; for menus the **business** break-even in revenue/month; for services
   hours/month at the current rate versus available billable hours.
4. **Scenarios** (10–30% margin) and the price to show: charm prices for products ($7.62 → $7.69, $15.61 → $15.99);
   round prices for professional services and jobs ($140.26/h → $145; quotes in round dollars).
5. **Market**: if the price lands well above competitors, don't cut the margin by default. Show levers: lower direct cost,
   renegotiate suppliers, packages and tiers (good/better/best), minimum order or trip charge, delivery fee, a cheaper
   channel (pickup instead of app delivery, direct site instead of marketplace), a recurring plan.
6. One concrete **next step** ("raise these 3 menu items that lose money", "send the remodel quote with a 1/3 deposit").

For several products, deliver `<finance>/YYYY-MM-DD-pricing.xlsx` (one row per item, assumptions in their own cells,
visible formulas, red fill for items with negative profit): use the `xlsx` skill if available; else `openpyxl` if
installed (`FormulaRule`, e.g. `$F10<0` → red); else `menu --output YYYY-MM-DD-pricing.csv` (comma-separated, US
decimals, `status` column profit/loss or lucro/prejuízo).

## 6. Cautions

- **Markup ≠ margin.** Markup is on cost, margin is on price. "I sell at double the cost" = 100% markup = 50% margin.
  The contractor "10 and 10" (10% overhead on cost, then 10% profit) is a 21% markup but only a 17.4% gross margin and a
  ~9% net margin; a 10% net margin needs about 11.1% markup on cost after overhead. Always say which one you mean.
- Tax rates, fees and payroll costs are estimates: ask the user for their real contract/statement numbers and to confirm
  taxes with a CPA. Don't invent costs; if something is missing, ask or use a labeled range.
- Upfront and recurring discounts can't exceed the margin; the script warns when they turn the job into a loss.
- Advertised price must match the charged price; disclose mandatory fees up front (FTC rules and state junk-fee laws).
  Card surcharges are banned or capped in some states (Connecticut, Maine and Massachusetts ban them; Colorado caps at 2%; cash/ACH discounts are allowed) and card
  brands cap them; check before adding one.
- Contractors: several states cap home-improvement deposits (Massachusetts HIC law: generally up to 1/3; California 10% or
  $1,000) and require written contracts; get change orders signed before the work. Florida has no deposit cap, but
  taking more than 10% up front on residential work triggers permit (30 days) and start (90 days) deadlines
  (s. 489.126), and contracts over $2,500 need the lien-law and Recovery Fund notices (s. 713.015) — see
  proposta-comercial.
- Commission sellers: anti-rebating laws in most states forbid sharing commission with the client, and fees on top of
  commissions are prohibited or regulated in many states; financial advisors' fees (AUM %, flat, hourly) follow their
  SEC/state compliance rules; loan originator pay follows the CFPB LO compensation rule. Point them to compliance.
- Immigration services: only attorneys and DOJ-accredited representatives may give legal advice or represent clients;
  many states (e.g. California, New York) regulate immigration consultants. Price form preparation and translation as
  such, never as legal advice.
