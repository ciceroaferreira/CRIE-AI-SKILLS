# US taxes, fees and costs for pricing — quick reference

> Planning ranges, not advice. Rates and fees change and vary by state, city and contract: ask for the user's real
> numbers (processor statement, app contract, payroll report) and tell them to confirm taxes with a CPA. Figures marked
> "verify" were current as of 2025 and should be checked before quoting them as fact.

## 1. Business structure and how taxes hit profit
| Structure | How profit is taxed | Owner's pay |
|---|---|---|
| Sole proprietorship | Schedule C on the owner's 1040: income tax + self-employment (SE) tax on net profit | Draws are not an expense |
| Single-member LLC | Same as sole prop by default (disregarded entity) | Draws are not an expense |
| Multi-member LLC | Partnership return (1065); each member pays income + SE tax on their share | Guaranteed payments / draws |
| S-corp election | Profit passes to owners (no SE tax on distributions); owner must take a **reasonable W-2 salary** with payroll tax | W-2 salary is an expense |
| C-corp | 21% federal corporate tax on profit; dividends taxed again for the owner | W-2 salary is an expense |

- **Income tax is on profit, not revenue.** Price for a pre-tax profit margin and set aside a share of profit.
  For a sole prop/single-member LLC the base is owner's pay + business profit (the draw isn't deductible).
- **SE tax**: 15.3% (12.4% Social Security up to the wage base + 2.9% Medicare) on 92.35% of net SE earnings; half is
  deductible. Wage base $176,100 for 2025, $184,500 for 2026 (SSA). Extra 0.9% Medicare above $200k (single).
- Federal income tax brackets 10–37%; the 20% QBI deduction may lower it for many small businesses (CPA).
  State income tax varies; no wage income tax in AK, FL, NV, SD, TN, TX, WY, NH (and WA taxes only capital gains).
- **Set-aside rule of thumb**: 25–35% of profit (federal + state + SE) for sole props/single-member LLCs. Estimate only.
- **Quarterly estimated taxes** (Form 1040-ES): due about Apr 15, Jun 15, Sep 15 and Jan 15. Missing them causes penalties.
- **Gross-receipts taxes** (on revenue, not profit) exist in some places (e.g. Washington B&O, Ohio CAT above an
  exclusion, Delaware, Nevada Commerce Tax, Oregon CAT, some cities). Only these go in `--revenue-taxes`.

## 2. Sales tax basics
- State and local tax **added on top of the price** at checkout for taxable goods (and some services); the business
  collects it and remits it. It is **not revenue** and never enters the price divisor.
- No statewide sales tax: Alaska (local taxes exist), Delaware, Montana, New Hampshire, Oregon.
- Examples (verify): Florida 6% + county surtax of 0–1.5% (2026: Orange County/Orlando 6.5%, Seminole 7%, Osceola
  7.5%; groceries exempt, prepared food taxable);
  Massachusetts 6.25% (meals 6.25% + up to 0.75% local option; most services not taxed); New York 4% + local
  (NYC 8.875%); Texas 6.25% + local up to 8.25%; California 7.25% base + district taxes.
- **Nexus**: physical presence (store, employees, inventory) or **economic nexus** — commonly $100,000 of sales into a
  state in a year (some states also a transaction count). Sellers must register before collecting.
- **Marketplace facilitators** (Amazon, Etsy, eBay, Walmart, DoorDash, Uber Eats, Grubhub) collect and remit sales tax on
  their orders in nearly every sales-tax state. Don't add it again; sales on your own site/POS are still yours to collect.
- Tax-included prices (food trucks, events): the business keeps price ÷ (1 + rate). Use `--price-includes-sales-tax`.
- Contractors: in many states (e.g. Massachusetts) the contractor pays sales tax on materials when buying them; include
  it in the materials cost, don't charge it on top. Rules differ by state and by contract type.

## 3. Payment and platform fees (typical, confirm the contract)
| Channel | Typical cost |
|---|---|
| Card in person (Square, Clover, Toast, Stripe Terminal) | ~2.6–2.9% + $0.05–0.15 per transaction |
| Card online / invoice (Stripe, Square, PayPal) | ~2.9–3.5% + $0.30 |
| Keyed-in card | ~3.5% + $0.15 |
| ACH bank transfer | ~0.8% (often capped at $5) or flat fee |
| Zelle | Usually free (no buyer protection) |
| Venmo/PayPal business, Cash App for Business | ~1.9–3.5% + fixed fee |
| Buy now, pay later (Affirm, Klarna, Afterpay) | ~3–6% + $0.30 merchant fee |
| DoorDash / Uber Eats marketplace plans | ~15% (basic), ~25% (plus), ~30% (premier) delivery commission (DoorDash says processing is included on Marketplace orders; its own-site Storefront charges 2.9% + $0.30); pickup ~6% |
| Grubhub | ~5–20% marketing + ~10% delivery + ~3.05% + $0.30 processing |
| Amazon | Referral fee ~8–17% (15% most categories) + FBA fees; $39.99/month Professional plan (fixed cost) |
| Etsy | $0.20 listing + 6.5% transaction (item + shipping) + ~3% + $0.25 payment processing; offsite ads 12–15% when they apply |
| eBay | ~13–15% final value fee + $0.30–0.40 per order |
| Shopify | Monthly plan (fixed) + ~2.5–2.9% + $0.30 |

- % fees go in `--variable-pct`; per-transaction fees in `--fee-per-sale`; monthly subscriptions in `--fixed-costs`.
- Card surcharges: card brands cap them (Visa 3%, Mastercard 4%, never above your actual cost) and require disclosure;
  never on debit or prepaid cards. Connecticut, Maine and Massachusetts ban them; Colorado caps them at 2%; other
  states add disclosure rules (verify yours). Cash/ACH discounts are generally allowed. Advertise the price actually charged.

## 4. Payroll and labor cost (add to wages)
- Employer FICA 7.65% (6.2% Social Security up to the wage base + 1.45% Medicare).
- FUTA 6% on the first $7,000 per employee, normally 0.6% after the state credit (~$42/year); more in credit-reduction states.
- SUTA (state unemployment): new-employer rates roughly 1–4% on a state wage base (Massachusetts base $15,000, verify).
  Some states add paid family/medical leave contributions (e.g. Massachusetts PFML).
- Workers' compensation: roughly 1–3% of payroll for office/cleaning-light work, 3–8% for cleaning and food, 5–20%+ for
  construction trades (by class code and state; ask for the quote).
- Rough total burden on wages: ~10–20% (low-risk services) to ~20–35% (construction). Paid time off and benefits extra.
- **1099 contractors**: no payroll tax or workers' comp from you, but misclassification risk (Massachusetts and California
  use a strict ABC test). File 1099-NEC (threshold $600 through 2025; raised to $2,000 for payments from 2026 by the 2025
  federal law, indexed for inflation from 2027) and collect a W-9 first.

## 5. Contractors and builders
- Estimate = materials + labor (crew hours × wage × (1 + burden)) + subcontractors + equipment rental + permits +
  dumpster/disposal + other direct costs + contingency (5–10% remodels, more on old houses) + overhead + profit.
- **"10 and 10"**: 10% overhead on cost, then 10% profit on cost + overhead = 1.21 × cost = 21% markup, but only 17.4%
  gross margin and 9.1% net margin. Many remodelers need 25–40% gross margin to cover real overhead; derive overhead %
  from last year: overhead ÷ revenue.
- Change orders: same or higher markup, written and signed (scope, price, schedule impact) before the work.
- Deposits and payments: Massachusetts Home Improvement Contractor law (M.G.L. c.142A) requires HIC registration and a
  written contract, and caps the deposit at the greater of 1/3 of the price or the cost of special-order materials;
  California caps it at 10% or $1,000, whichever is less; Florida (s. 489.126) requires a contractor who takes more
  than 10% up front on a residential job to apply for permits within 30 days and start work within 90 days of the
  permit. Typical schedule: deposit, progress payments at milestones,
  final on completion. Verify your state.

## 6. Commission-based businesses (insurance, loans, financial services)
- The price (premium, rate) is set by the carrier/lender. Plan income: sales needed = (target income + expenses −
  renewals) ÷ (net commission per sale − lead cost per sale); leads = sales ÷ close rate; budget = leads × cost per lead.
- Typical ranges (estimates, vary by carrier/contract): life insurance first-year 40–100%+ of first-year premium,
  renewals 2–10%; P&C new business 10–15%, renewals similar or lower; health 3–8% or per-member fees. Captive vs.
  independent and IMO/agency splits change the agent's share.
- **Anti-rebating**: most states forbid giving clients part of the commission or gifts as an inducement (California and
  Florida allow limited rebating under conditions — verify). **Fees on top of commissions** are prohibited or require a
  written, signed disclosure or a consultant license in many states.
- Loan originators: the CFPB LO compensation rule (Reg Z) bars pay based on loan terms and dual compensation.
- Financial advisors: fee models (AUM %, often ~1%; flat fee; hourly) must follow SEC or state adviser rules and be
  disclosed in Form ADV; broker-dealers follow Reg BI/FINRA. Defer to their compliance department.

## 7. Pricing psychology and presentation
- Retail and food: charm prices ($9.99, $4.49, $2.29) feel cheaper; keep menu ending styles consistent.
- Professional services and contractors: round prices ($150/hour, $1,200 package, $28,500 bid) signal quality and
  confidence. Quote packages (good/better/best) to anchor the middle option.
- Cleaning: per visit, per square foot (~$0.10–0.25 per sq ft for standard cleans, more for deep/move-out; estimate) or
  flat by bedrooms/bathrooms; recurring weekly/biweekly at a small discount because visits are faster.
- Translation: per word (~$0.10–0.25) or per page for certified translations (~$25–60 per page; estimate).
- All-in pricing: the FTC rule on unfair or deceptive fees (2025, live-event tickets and short-term lodging), the FTC Act
  in general and state laws (e.g. California SB 478, which covers restaurants) require mandatory fees to be in the
  advertised price. Never surprise customers with fees at checkout.
