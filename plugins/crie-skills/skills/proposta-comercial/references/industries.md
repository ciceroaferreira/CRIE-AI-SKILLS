# Industry rules: contractors, insurance, financial services

Read the section that matches the business. These are general US rules; state rules vary — tell the user to check their state and their licensing board, carrier or compliance department. Never invent license numbers, NMLS IDs, rates, premiums or policy values: use `[fill in]`.

---

## A. Contractors and builders (bid / estimate / orçamento de obra)

### Structure
1. **Project and site**: address, scope summary, plans/drawings referenced (with date/version).
2. **Line items** (by phase or trade), each with quantity and price: materials, labor, subcontractors (electrical, plumbing, HVAC), permits and inspection fees, equipment rental, dumpster/disposal, cleanup.
3. **Allowances**: amounts for items the owner hasn't picked yet (tile, fixtures, appliances). State the allowance, what it covers, and that the difference above or below is billed or credited by change order.
4. **Alternates**: optional add/deduct items with their own price ("Alt 1: quartz instead of laminate countertops, +$2,400").
5. **Exclusions**: e.g., hidden conditions (rot, mold, asbestos, knob-and-tube wiring), structural engineering, appliance hookups by others, landscaping, painting outside the work area.
6. **Contingency**: a separate line (commonly 5–10%) for unforeseen conditions, used only through an approved change order; unused contingency is not billed. If the price came from `precificacao` with a contingency built in, either rerun it with `--contingency 0` or state in the proposal that contingency is included in the price — never charge it twice.
7. **Change-order process**: every change is written, priced (cost and schedule impact) and signed by both parties **before** the work is done. No verbal changes.
8. **Payment schedule tied to milestones** (deposit, rough-in inspection passed, cabinets installed, substantial completion, final walkthrough). Never front-load beyond the work done. **Deposit limits exist in some states** — check your state. Examples: Massachusetts home improvement contracts cap the deposit at 1/3 of the total price or the actual cost of special-order materials, whichever is greater; California caps the down payment on home improvement at $1,000 or 10%, whichever is less; Florida has no cap, but a residential contractor who takes more than 10% up front must apply for permits within 30 days and start work within 90 days of the permit (s. 489.126).
9. **Start and substantial completion dates**, and what can delay them (weather, permit approval, owner selections, supply delays).
10. **Permits**: who pulls them (normally the licensed contractor) and who pays; work subject to inspection.
11. **Lead-safe work (EPA RRP)**: for homes or child-occupied facilities built **before 1978**, renovation that disturbs painted surfaces above the minimums (about 6 sq ft interior / 20 sq ft exterior, or any window replacement) must be done by an EPA (or state) certified firm with lead-safe practices, and the owner must receive the "Renovate Right" pamphlet before work starts. State the firm certification number `[fill in]`.
12. **Lien waivers**: contractor provides conditional/unconditional lien waivers (own and subcontractors' / major suppliers') with each progress payment and a final unconditional waiver at final payment. Some states require preliminary notices or lien rights notices in the contract — check your state (Florida: residential contracts over $2,500 must include the s. 713.015 lien-law disclosure and the Homeowners' Construction Recovery Fund notice; subs and suppliers serve a Notice to Owner within 45 days of first furnishing).
13. **Warranty / workmanship**: e.g., 1 year on workmanship from substantial completion; manufacturer warranties pass through; what voids it.
14. **License and insurance**: state license/registration number, general liability carrier and limits, workers' comp (or exemption). `[fill in]` if not provided.
15. **Cancellation notice when required**: the FTC Cooling-Off Rule (sale at the home) and state home-improvement laws (e.g., MA, NJ, CA) require a written 3-business-day cancellation notice — attach the form the state requires.
16. **Sales tax**: in many states contractors improving real property pay sales tax on materials when they buy them and don't add it to the customer's invoice; in others it's different. Confirm with the state revenue department or CPA before adding a tax line.

### Worked example — kitchen remodel (Massachusetts homeowner, consumer)
| Line | Amount |
|---|---|
| Materials (cabinets $9,800 special order, countertops, drywall, trim) | $18,500.00 |
| Labor (demo, carpentry, install, finish) | $14,200.00 |
| Subcontractors (electrical $3,800, plumbing $3,200) | $7,000.00 |
| Permits and inspections | $650.00 |
| Equipment rental | $400.00 |
| Dumpster / disposal | $500.00 |
| Allowances (tile $1,500, fixtures $1,200) | $2,700.00 |
| **Total cost** | **$43,950.00** |

Price with a 22% pre-tax margin, paid by check/ACH (no card fees): $43,950 ÷ (1 − 0.22) = **$56,346.15**.
Contingency (5%, billed only by approved change order): $2,817.31 — shown separately, not in the contract price.
Alternate 1: quartz upgrade +$2,400.00 (if accepted, by change order).

MA deposit cap = greater of 1/3 × $56,346.15 = $18,782.05 or special-order materials $9,800 → max deposit **$18,782.05**.

| Milestone | % | Amount |
|---|---|---|
| Deposit at signing | 33.33% | $18,782.05 |
| Rough-in inspection passed | 30% | $16,903.85 |
| Cabinets and countertops installed | 25% | $14,086.54 |
| Final walkthrough and punch list complete | balance | $6,573.71 |
| **Total** | | **$56,346.15** |

House built 1962 → RRP applies (certified firm, Renovate Right pamphlet). Contract includes HIC registration number `[fill in]`, 3-day cancellation notice, start/completion dates and lien waiver with each payment. Save in the confidential folder (homeowner's name and home address).

---

## B. Insurance agents (needs analysis / análise de necessidades)

A "proposal" from an agent is a **needs analysis and recommendation summary**, not a price quote.
- **Never state premiums, coverage amounts as offered, cash values, dividends or illustrated values** unless they come from an insurer-approved quote or illustration the user provides. Use placeholders `[premium from carrier quote]`, `[carrier]`, `[product]`, filled only from that document. Life insurance illustrations must be the carrier's own (NAIC illustration rules) — don't make your own projections.
- **Needs math is fine** (it's the client's need, not a policy value). Common method — DIME: debts + income replacement (years × income) + mortgage + education, plus final expenses, minus existing coverage and liquid assets. Label it "estimate for discussion".
- **Required wording**: "This is not a contract of insurance and does not bind coverage. Coverage, rates and eligibility are subject to underwriting, approval by the insurer, and the terms of the policy issued." Add the agent's name, agency and **license number** (and any state-required disclosures, e.g., California license number on materials) — `[fill in]`.
- **No rebating or inducements**: don't offer gifts, premium discounts or cash back to buy a policy (prohibited in most states; a few allow limited exceptions — check your state).
- **Replacement**: if the recommendation replaces or changes an existing policy or annuity, flag it — the state replacement regulation requires a replacement notice/comparison forms and carrier notification. Don't advise canceling the old policy before the new one is issued.
- **Annuities**: recommendations must meet the state's best-interest/suitability standard (NAIC model adopted by most states): document the client's financial situation, objectives, liquidity needs, risk tolerance, and why the product fits; disclose surrender charges and agent compensation as required. The carrier's forms rule.
- **Health information** in the analysis → confidential folder; don't keep it beyond what's needed.
- Advertising and testimonials follow state insurance department rules and carrier compliance approval.

### Worked example — term life needs analysis (family of four)
Client 38, income $85,000, spouse, children 2 and 5.
| Need | Amount |
|---|---|
| Debts (car, cards) | $18,000 |
| Income replacement (10 years × $85,000) | $850,000 |
| Mortgage balance | $320,000 |
| Education (2 × $100,000, estimate) | $200,000 |
| Final expenses | $15,000 |
| **Total need** | **$1,403,000** |
| Less group life at work (2× salary) | −$170,000 |
| Less savings available | −$40,000 |
| **Coverage gap (estimate)** | **$1,193,000** → discuss ~$1.2 million |

Suggested term: 20 years (until the youngest is about 22). Premium: `[from carrier quote]`, carrier `[fill in]`, rating class `[subject to underwriting]`. Include the not-a-contract disclaimer and license number. Save in the confidential folder.

---

## C. Financial services

### Investment advisers and broker-dealers (engagement / advisory proposal)
- Follow the firm's compliance process: compliance reviews proposals and marketing before use.
- Disclose all fees (AUM % with breakpoints, flat or hourly fees, how billed) and conflicts of interest.
- RIAs: deliver **Form ADV Part 2A (brochure) and 2B** at or before signing the advisory agreement; deliver **Form CRS** to retail investors (RIAs and broker-dealers).
- **No guarantees of returns** and no cherry-picked performance; testimonials and performance follow the SEC Marketing Rule (or state rules for state-registered advisers).
- Fiduciary (Advisers Act) or Reg BI (broker-dealers) language comes from compliance — don't draft your own legal standard of care.

### Loan brokers and mortgage loan originators
- Never promise a rate, approval, or closing date: "Rates and approval depend on lender underwriting."
- Required disclosures come from the lender: for most mortgages, the **Loan Estimate** within 3 business days of application and the Closing Disclosure (TRID). Don't reproduce your own version.
- Show the NMLS ID of the company and originator (SAFE Act) — `[fill in]`.
- Disclose broker fees and who pays them; follow state broker licensing (many states also license commercial/business loan brokers). Advance fees for consumer loans are restricted in many cases — check your state.

### Tax preparation and bookkeeping (engagement letter / carta de contratação)
- Engagement letter: scope (which returns, which years, which services), what's excluded (audits, amended returns, tax planning, state returns not listed), fees (fixed or hourly, retainers), due dates, **client responsibilities** (accurate and complete records, deadlines for documents, final review and signature), timeline, termination, record retention.
- **IRC §7216**: using or disclosing tax return information for anything other than preparing the return (e.g., marketing other services, sharing with a third party, some offshore processing) needs the client's prior written consent in the IRS-required format (Rev. Proc. 2013-14).
- Tax preparers are covered by the FTC Safeguards Rule (written information security plan) and IRS Pub 4557; PTIN required for paid preparers; Circular 230 for practitioners.
- Save in the confidential folder (regulated).

### Credit repair (Credit Repair Organizations Act — CROA)
- **No fees before the services are fully performed.**
- Written contract with the total payment, a detailed description of services, the time to perform them (or estimated), the business name and address, and a conspicuous notice of the **right to cancel within 3 business days** of signing, with the cancellation form.
- Give the "Consumer Credit File Rights Under State and Federal Law" disclosure before the contract is signed.
- No promises to remove accurate negative information or to create a "new credit identity". Many states add bonding/registration rules. Telemarketing sales can't charge in advance either (Telemarketing Sales Rule).

### Worked example — bookkeeping + tax engagement (two-member LLC)
Monthly bookkeeping $450 × 12 = $5,400 + annual partnership return (Form 1065) and K-1s $1,800 = **$7,200 per year**. Billed monthly $450; the return fee is billed at filing. Excluded: state returns not listed, payroll, audit representation (separate engagement). Includes §7216 consent form only if the firm will use the data for other services. Save in the confidential folder.
