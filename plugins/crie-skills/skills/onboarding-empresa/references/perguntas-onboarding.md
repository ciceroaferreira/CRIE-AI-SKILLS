# Onboarding questions

Seven blocks. Questions marked ★ are essential; the rest you can **infer and confirm** instead of asking.
Golden rule: each message has at most 3–4 questions and at least one comment showing you understand the
business. Ask in the user's language (Portuguese or English); the wording below is a guide, not a script.

## Block 0 — Language (first message)
- ★ "Do you prefer to work in English or Portuguese? / Prefere conversar em português ou inglês?"
  → `idioma` (`en` | `pt`). Folder and file names follow it.
- ★ "Should customer-facing material (posts, proposals, messages) be in English, Portuguese, or both?"
  → `idioma_entregas` (`en` | `pt` | `both`). Default for US customers: English. Many Brazilian-owned
  businesses serve both communities: suggest `both` when the customers are mixed.

## Block 1 — The company
- ★ Company name and, in one or two sentences, what it does.
- ★ Size: just me · 2–10 · 11–50 · 51–200 · 200+ people.
- ★ City and state(s) where you operate (and where customers are); online, in person or both; years in business.
- Entity type: sole proprietorship · single-member LLC · multi-member LLC · LLC with S-corp election · S-corp ·
  C-corp · not sure. (Don't lecture; note "confirm with your CPA" if they are unsure.)

**Right after:** identify the industry, read the pack in `references/setores/` (or build one with
`_modelo.md`) and say "what I already know about your industry" in 3–4 sentences (revenue model, metrics,
risks, regulation). Ask for corrections. Detect these on purpose — they are common in the audience and
regulated: law firms (especially **immigration**), tax preparers/bookkeepers, **life & health insurance
agents**, **financial services** (loan/mortgage brokers, advisors, credit repair, remittances),
**builders/contractors/remodelers**, health/wellness, real estate.

| They say… | Pack |
|---|---|
| law firm, attorney, immigration, paralegal | `legal` |
| tax prep, bookkeeping, CPA, EA, payroll service | `accounting` |
| life/health insurance, annuities, Medicare, agency | `insurance` |
| loans, mortgage, financial advisor/planner, credit repair, money transfer/remittance | `financial-services` |
| contractor, builder, remodeling, painting, flooring, plumbing, electrical, HVAC | `construction` |
| clinic, dental, therapy, med spa, chiropractic, PT | `health` |
| realtor, broker, property management | `real-estate` |
| restaurant, bakery, food truck, catering, cottage food | `food` |
| cleaning, salon, nails, lashes, landscaping, home services, translation | `services` |
| store, e-commerce, Etsy/Amazon/Shopify seller | `retail-ecommerce` |
| tutoring, language school, daycare, lessons | `education` |
| software, IT services, web/marketing agency | `technology` |

## Block 2 — Customers and market
- ★ Ideal customer (consumers or businesses; which community/language; where they are)?
- How do customers find you today, and which channel brings the most (referrals, Google Business Profile,
  Instagram, WhatsApp groups, Nextdoor, Yelp, church/community)?
- Main competitors and your differentiator.
- Average ticket and how you charge (per job, hourly, flat fee, retainer, subscription) — **propose** the
  industry's typical range in USD and ask for confirmation.
- ★ Payment methods: card (Square, Stripe, Clover, Toast), ACH, Zelle, Venmo Business, PayPal, Cash App,
  checks, cash. Card fees (~2.6–3.5% + fixed fee) matter for pricing.
- Sales tax: do you collect it? In which states? Through a marketplace (Amazon, Etsy, DoorDash) that collects
  it for you? (Not sure → note it for Ana and "confirm with your CPA".)
- Extra questions from the industry pack.

## Block 3 — Your routine (so Claude can do your work)
- ★ Your role (owner, partner, manager, attorney, agent, bookkeeper…)?
- ★ What does a typical week look like? What do you do every day, every week, every month-end?
- ★ Which 3 tasks take the most time or would you most like to hand off?
- Show the industry's "Routines Claude can run" list and ask which apply.
- Templates you already use (contracts, proposals, estimates, reports)? Ask them to drop copies in the
  templates folder later, without real customer data.
- Tools: QuickBooks, Gusto/ADP, Square, Jobber/Housecall Pro, Google Workspace/Microsoft 365, a CRM, an
  industry system (Clio, Docketwise, Drake, an agency management system), WhatsApp Business.

Result: 3–6 playbooks (see `references/playbooks.md`).

## Block 4 — Team
- ★ Who works with you: W-2 employees, 1099 contractors, family members, nobody yet? (Classification risk —
  IRS common-law test and state ABC tests in MA, NJ, CA, among others — is a topic for Rafael and the CPA.)
- Do you use a payroll service?

## Block 5 — Goals and challenges
- ★ The 3 biggest challenges today.
- ★ The main goal for the next 6–12 months.
- ★ Which areas do you want specialists for? Marketing · Finance · IT · Admin · HR · Sales · Legal ·
  Operations · Strategy — suggest them from the challenges and add the industry specialists.
- Preferred tone: more formal or more casual?

## Block 6 — Data and confidentiality
Explain in one sentence why you ask ("so I treat your documents with the right care").
- ★ Do you handle any of these? (multiple choice) customer contact lists · **SSNs/ITINs** · tax returns
  (IRC §7216) · bank/financial account data, loan applications or credit reports (GLBA) · **health
  information** (HIPAA) or insurance applications · immigration files · **children's data** (COPPA for under
  13 online; FERPA for education records) · client files under **attorney-client privilege** · card data
  (PCI-DSS) · employee files (I-9, payroll) · trade secrets/NDAs · none.
- Any internal policy, client contract or licensing-board rule about AI use?
- Propose the level (`standard`, `elevated`, `regulated`) from the industry and answers; the user decides.
  Regulated industries (legal, accounting/tax, insurance, financial services, health) → suggest `regulated`.

## Block 7 — Where to create the folder
See Step 3 in SKILL.md.

## Never ask
SSNs, ITINs, passwords, bank or card numbers, policy numbers, or any third-party personal data. The
onboarding doesn't need them. If the user volunteers them, don't repeat them and suggest deleting the message.
