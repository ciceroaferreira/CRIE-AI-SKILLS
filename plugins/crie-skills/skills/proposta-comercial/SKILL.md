---
name: proposta-comercial
description: Creates proposals, estimates, bids and quotes for US small businesses (scope, deliverables, timeline, good/better/best options, payment terms, sales tax, exclusions, terms), as DOCX or PDF, in English, Portuguese or both. Understands the customer's problem first, builds one-time, milestone or recurring pricing, and drafts the email or text to send it. Covers freelancers, home services, catering, translation, contractors and builders (line-item bids, allowances, change orders, lien waivers), insurance agents (needs analysis without unapproved premiums) and financial services (engagement letters, advisers, loan brokers, tax preparers, credit repair). Use whenever the user asks for a proposal, estimate, quote, bid, scope of work, SOW, change order, needs analysis, engagement letter or follow-up on a sent proposal. Portuguese triggers - proposta, orçamento, cotação, orçamento de obra, aditivo, escopo, carta de contratação, análise de necessidades. If the user only wants to know what to charge, use precificacao.
---

# Business Proposal / Proposta Comercial

You turn a quote request into a proposal that sells: clear, specific to that customer, legally sensible for the US, and ready to send — without slowing the user down.

If the user only wants to know what to charge (no document for the customer), use the `precificacao` skill if installed and offer the proposal afterwards.

## Languages

- Talk to the user in the language they write in (Portuguese or English).
- The **proposal language** is separate: it follows the customer. Read `deliverables_language` / `idioma_entregas` from the company profile; if absent, ask once ("Should the proposal be in English, Portuguese, or both?"). Default for US customers: English. A Portuguese conversation can produce an English proposal — that is common and expected.
- English documents: dates `MM/DD/YYYY`, money `$1,234.56`. Portuguese documents: dates `DD/MM/AAAA`, money still in USD (`US$ 1,234.56` or `$1,234.56`). File names always `YYYY-MM-DD-proposal-<customer>.docx` (or `-proposta-` for Portuguese).
- Numbers the user types may be US (`1,234.56`) or Brazilian (`1.234,56`): if both separators appear, the last one is the decimal; a lone separator followed by exactly 3 digits is thousands (`12.000` = twelve thousand). Confirm when in doubt.

## 1. Load the company context

- Read the **Folder map / Mapa de pastas** in `CLAUDE.md` first (created by the onboarding-empresa skill). It gives the real paths for profile, brand, sales, confidential and templates. Without CLAUDE.md, look for either language: `00-company/company-profile.md` or `00-empresa/perfil-da-empresa.md`.
- From the profile: business name, entity type (sole prop, LLC, S-corp, corporation, freelancer), state(s) where it operates, what it sells, tone, typical ticket, differentiators, licenses and insurance.
- Read `SECURITY.md` / `SEGURANCA.md` if present: security level (`standard | elevated | regulated`, also `padrao | elevado | regulado`) and where customer data goes.
- If the templates folder (`templates/` or `modelos/`) has an old proposal or company template, use it as the base.
- If a brand manual exists (`00-company/brand.md` or `00-empresa/marca.md`, from the marca-da-empresa skill), apply colors, fonts and tone.
- With none of this, ask only the minimum: business or professional name, what you sell, state, tone (formal or friendly).

## 2. Understand the customer before writing

Ask in one message, only what is missing (accept "I don't know" and continue with flagged assumptions):
1. Who is the customer: a business (legal name, size, industry, who signs) or a consumer (individual/homeowner)? Where is the job (state matters for tax and consumer rules)?
2. What problem or goal triggered the request? What happens if they don't solve it?
3. What exactly did they ask for (scope), and what is out?
4. Timeline and constraints (budget, date, location). One-time job or recurring (weekly, biweekly, monthly)?
5. The price you plan to charge, or help calculating it. Use the `precificacao` skill if installed; otherwise calculate and show the math: **price = cost ÷ (1 − fees% − margin%)**, then **add sales tax on top** if the item/service is taxable in that state. Example: cost $1,000, card fees 3%, target pre-tax margin 25% → 1,000 ÷ 0.72 = $1,388.89; if taxable at 6.5%, the customer pays $1,388.89 + $90.28 = $1,479.17. Income tax is on profit, not revenue: suggest setting aside a share of profit for taxes (confirm with a CPA) instead of loading it into the price.
6. Payment methods accepted (ACH, card, Zelle, check, Venmo Business, PayPal) and deposit/terms.

If the user pastes the customer's email or message, extract the answers from it and ask only the rest.

## 3. Proposal structure

Follow `references/estrutura.md`. In short:
1. Cover: outcome-oriented title ("A stress-free office lunch program for Acme Corp"), customer, date, number (`YYYY-NNN`), valid until.
2. Understanding of the need: the problem in the customer's words.
3. Scope of work: what will be done, in steps.
4. Deliverables: objective list of what the customer receives.
5. Timeline: steps with business days.
6. Investment: good/better/best options when it makes sense, subtotal, sales tax line (when applicable), total, payment terms.
   - **One-time job**: deposit % + balance on completion, or milestone billing; Net 15/30 for B2B.
   - **Recurring service**: price per visit/period, billing frequency and due date, annual price review (state it as a fixed % or "with 30 days' written notice"), minimum term if any, cancellation notice (e.g., 14 or 30 days), skipped-visit/lockout policy, optional prepay discount. Show the monthly equivalent (biweekly = 26 visits/year ÷ 12 = 2.17 visits/month) — don't promise "2 visits a month".
7. Exclusions (avoid disputes later).
8. Change orders, terms and conditions: validity (typically 30 days), cancellation, warranty/workmanship (trades), insurance and license info (contractors), e-signature under ESIGN/UETA, consumer notices when they apply.
9. Next steps: how to approve (sign, pay deposit, schedule kickoff).

## 3b. Regulated or specialized industries

If the business is one of these, read the matching section of `references/industries.md` before writing — it changes what the document may say:
- **Contractors/builders**: line-item bid (materials, labor, subs, permits, equipment, disposal), allowances, alternates, contingency, signed change orders before work, milestone payments within state deposit limits, lien waivers, permits, EPA lead-safe (RRP) for pre-1978 homes, license/insurance, cancellation notice. Worked kitchen-remodel example.
- **Insurance agents**: a needs analysis/recommendation summary — never premiums or policy values not taken from the carrier's quote or illustration; not-a-contract disclaimer, license number, no rebating, replacement and annuity best-interest documentation.
- **Financial services**: advisers (fees, Form ADV 2/Form CRS, no return guarantees, compliance review), loan brokers (no rate/approval promises, lender disclosures, NMLS ID), tax/bookkeeping (engagement letter, §7216 consent), credit repair (CROA — no fees before services are performed, 3-day cancellation).
For these, also say that the firm's compliance department, carrier or attorney must approve the final wording, and save in the confidential folder when the document holds client financial, health or household data.

## 4. Quality and US rules

- Write for the decision-maker: benefits and outcome before technical detail.
- Good/better/best when the scope allows; highlight the recommended one. Don't force tiers on simple jobs.
- Check every number: add line items, deposit and balance, sales tax, recurring annual value. Show the math to the user before generating the file.
- No promises the business doesn't control ("guaranteed #1 on Google", "guaranteed visa approval").
- Never invent an EIN, SSN, license number, insurance policy, address or bank details: use `[fill in]` / `[preencher]`. Never ask for or include passwords or full bank account numbers in the proposal.
- **Sales tax**: state and local; taxable status depends on the state and the item (prepared food and catering are usually taxable; many services are not, some are). Add a separate line and tell the user to confirm the rate and taxability with the state revenue department or their CPA. B2B buyers may give a resale or exemption certificate.
- **Card surcharges**: banned in some states (Connecticut, Maine, Massachusetts; Colorado caps them at 2% — confirm the current list), capped by card networks (Visa 3%, Mastercard 4%), not allowed on debit/prepaid cards, and require disclosure. If unsure, suggest a cash/ACH discount instead and tell the user to confirm with their processor.
- **Late fees**: only if written into the agreement and within state law limits; don't invent a rate.
- **Consumer customers** (individuals buying for personal/household use) — see `references/estrutura.md` for details:
  - FTC Cooling-Off Rule: if the sale is made at the buyer's home or a temporary location ($25+ at home, $130+ elsewhere), the buyer has 3 business days to cancel and must get the written notice and cancellation form.
  - Home improvement/contractor work: many states require a written contract with license/registration number, start and end dates, a cancellation notice and deposit limits (e.g., Massachusetts, New Jersey, California). Say "check your state's rules" — don't assert specifics as final.
  - Some states require the quoted price to include mandatory fees (e.g., California): don't hide fees outside the total.
- **Freelancers and contractors**: B2B clients will ask for a **W-9**; mention it in next steps. Clients who pay a freelancer $2,000+ in a year (threshold raised from $600 for payments from 2026) issue a 1099-NEC. Never put the SSN in the proposal; suggest an EIN (free from the IRS) for sole proprietors.
- **Immigration-related services** (translation, form preparation, document help): never guarantee a USCIS outcome or timeline. Only attorneys or DOJ-accredited representatives may give immigration legal advice — add the non-attorney disclaimer and do not use the word "notario" (notario fraud is a major problem in immigrant communities; some states regulate immigration consultants). Certified translations for USCIS carry the translator's certification of competence and accuracy.
- If the proposal turns into a contract or involves legal, health or financial matters, say the terms should be reviewed by an attorney.

## 5. Where to save (consistent with SECURITY.md)

Use the paths from the Folder map:
- **B2B customer with only commercial data** (legal name, business address, work contact): sales folder (`06-sales/` or `06-comercial/`).
- **Consumer customer with personal data** (name + home address, personal phone/email, anything about their family, finances or health — e.g., a homeowner's remodel bid, a life insurance needs analysis), or a business whose security level is `elevated`/`regulated` (health, legal, tax, insurance, financial, immigration): confidential folder (`confidential/` or `confidencial/`).
- The rule "customer personal data only in confidential" applies to personal data; a company's commercial info can stay in sales. When in doubt, confidential. Tell the user where you saved it and why.
- No company folder (e.g., a freelancer just starting): save in the current folder, say so, and suggest a private subfolder that is not shared or synced publicly for proposals containing client personal data.
- Customer data stays only in the proposal file, never in `CLAUDE.md`, the profile, personas or memory.

## 6. Delivery

1. Show a summary (customer, scope, price math, total, proposal language, where it will be saved) and ask for OK.
2. Generate the file:
   - DOCX: use the `docx` skill if available; otherwise `python-docx` if installed; otherwise well-formatted Markdown.
   - PDF (when asked): use the `pdf` skill if available; otherwise convert the DOCX with LibreOffice (`soffice --headless --convert-to pdf file.docx`) if installed; otherwise deliver the DOCX and explain: in Word, File → Save As → PDF (or Google Docs → File → Download → PDF).
3. Write the cover message (email or text) — short, with the main benefit and the next step, in the proposal language. Never send anything without the user's authorization.
4. Offer a follow-up in 3 business days if the customer doesn't reply (templates in `references/estrutura.md`).
