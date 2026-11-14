---
name: relatorio-mensal-gestao
description: Builds a small business's monthly management report from US bank and credit-card exports (Chase, Bank of America, Wells Fargo, Capital One, Amex, Citi, TD, Discover, QFX/OFX, QuickBooks exports; Brazilian bank files also read). Categorizes money in and out (Square, Stripe, Toast, DoorDash, Zelle, payroll, IRS, sales tax, rent, utilities, insurance commissions, chargebacks, materials, permits), excludes transfers and card payments to avoid double counting, and reports cash result, owner draws, fixed vs variable costs, break-even, month-over-month changes, weekly cash flow, alerts and an action plan, in English or Portuguese. Use whenever the user shares or mentions a bank statement, card statement, CSV, QFX, month-end close, "how did the month go", "where did the money go", cash flow, a report for partners, or sells a lot but has no cash left. Portuguese triggers - extrato bancario, fechamento do mes, como foi o mes, para onde foi o dinheiro, fluxo de caixa, relatorio para socios, vendo e nao sobra dinheiro.
---

# Monthly Management Report

You close the month with the owner: turn bank and card exports into clear numbers and decisions. It is a cash view
for management, not bookkeeping: the bookkeeper/CPA still closes the books and files taxes.

**Language.** Reply in the language the user writes in. For the report, use `deliverables_language` /
`idioma_entregas` from the company profile if present; otherwise ask once ("Should the report be in English,
Portuguese, or both?"). Pass `--lang en` or `--lang pt` to the script (default `en`).

## 1. Security first

Statements are confidential: account numbers, balances, and names of customers, employees and suppliers.
- Read the **Folder map** in the company `CLAUDE.md` (onboarding-empresa). Without it, look for `00-company/` or
  `00-empresa/`; with no company folder, work in the current folder and ask the minimum.
- Follow `SECURITY.md` / `SEGURANCA.md` at any level. The default one says to scan documents first:
  `python3 -I tools/detectar_dados_sensiveis.py <file>` (or `ferramentas/...`). Report counts, never full values.
- Keep statements in the **confidential** folder (`confidential/` or `confidencial/`). Let the script read the files;
  do not paste whole statements into the chat.
- Never write amounts, names or account numbers in `CLAUDE.md`, the profile or memory.
- Never ask for the bank password or online-banking access, and never log in for the user. The user downloads the
  files and shares them.
- At `regulated` / `regulado` level, or when the report goes to third parties, run with `--no-descriptions`.

## 2. What to ask for

1. The **whole month** (ideally the previous whole month too) from **every** business checking account **and every
   business credit card**, as CSV or QFX/OFX. Generic steps by bank (menus change; confirm on screen):
   - **Chase**: Account → Activity → download icon → choose the dates → "CSV" (or "Quicken (QFX)").
   - **Bank of America**: Account → "Download" (above the transactions) → period → "Microsoft Excel (CSV)" or "Quicken".
   - **Wells Fargo**: Account activity → "Download account activity" → dates → "Comma delimited" (the file has no
     header; that is fine).
   - **Capital One**: Card or 360 account → "View statements/Download transactions" → CSV.
   - **American Express**: Statements & Activity → "Download" → CSV (check "include all additional fields" if offered).
   - **Citi, TD, Discover, others**: look for "Download", "Export" or "Statements" → CSV or QFX.
   - **QuickBooks**: a Transaction Detail/Register export to CSV or .xlsx also works.
   PDF statements are not read by the script: ask for CSV/QFX, or extract the PDF text with the `pdf` skill and build a
   CSV. Old `.xls`: save as CSV or `.xlsx`.
2. Optional: Square/Stripe/Toast/DoorDash payout reports (deposits arrive in batches, net of fees), sales by channel,
   unpaid invoices and bills.
3. Context: expected sales, anything unusual (big purchase, vacation, loan, owner put money in, a large job deposit).

Save the files in `confidential/statements/` (or `confidencial/extratos/`) named `YYYY-MM-DD-bank-account.csv`.

## 3. Run the analysis

```
python3 -I <skill>/scripts/analisar_extrato.py confidential/statements/*.csv confidential/statements/*.qfx \
  --lang en --out-csv confidential/YYYY-MM-DD-categorized-YYYY-MM.csv --out-json confidential/YYYY-MM-DD-summary-YYYY-MM.json
```
- Many files and months at once. It reports the latest month (or `--month YYYY-MM`) against the calendar month right
  before it; if that month is missing or incomplete, there is no comparison and it says so.
- Formats: CSV/TXT with `,` `;` tab or `|`; title/summary rows above the header (Bank of America); files with no header
  (Wells Fargo); debit/credit columns (Capital One, Citi, TD); unsigned amount + type column (Capital One 360); signed amount + type column (Chase checking "Details"); QuickBooks exports; QFX/OFX; simple `.xlsx`. Brazilian exports (Itau, BB, Bradesco, Santander, Caixa,
  Inter, Nubank, C6) still work.
- Amounts: `$1,234.56`, `(1,234.56)`, `-$1,234.56`, `$-45.00`, `125.00 CR`, and Brazilian `1.234,56`.
- Dates are detected per file: a first field above 12 means DD/MM, a second field above 12 means MM/DD, otherwise the
  shorter date range wins; if still tied it reads MM/DD and warns. Force with `--date-order mdy|dmy`.
- **Credit cards.** Chase, Bank of America, Capital One and Citi exports show charges as negative or in a Debit column,
  which is already right. **Amex and Discover list charges as positive numbers**: the script flips them automatically
  when it recognizes the layout (Amex extended columns, Discover "Trans. Date", or "PAYMENT - THANK YOU" rows that are
  negative). If a card file is not recognized (most rows come out positive and the warning says so), rerun with
  `--card that-file.csv`; to turn detection off for a file use `--not-card that-file.csv`.
Pass `--industry construction|insurance|financial|food|services|retail` (`--setor`) when the profile says the
business type, so industry alerts (job deposits, carrier concentration, chargebacks) only fire where they apply.
- **No double counting.** Paying the card from checking is a transfer, not an expense: it is excluded, and the
  purchases come from the card statement. If the card statement is missing, the alert says the card purchases are not
  in the report: ask for it.
- Rows with a date but an unreadable amount are counted under "Data warnings"; repeated exports of the same period
  (same FITID, or ≥80% equal date+amount) are removed with a warning.
- Excluded from the result: transfers between own accounts, credit card payments, loans and owner contributions
  received. Owner draws are shown apart (operating result, then result after draws).

## 4. Review with the user before concluding

1. Show the category table and what landed in "Other expenses (review)", "Other income (review)" and
   "Zelle/Venmo/Cash App to people (review)".
2. Ask about the largest uncategorized items and doubtful ones ("Zelle to Maria Souza: employee, contractor (1099),
   owner, or supplier?"; "this $4,800 ACH from Blue Hill: a client contract?"; "is this $12,000 a job deposit?").
3. Owner draws/distributions: separate them so the owner sees what the business pays them. S-corp owners on payroll
   appear under payroll.
4. Loans received and money the owner put in are not revenue: confirm they are in "Loans and owner contributions".
5. Save the answers as rules in `confidential/rules.json` (`confidencial/regras.json`) — it holds people's names, so it
   never goes to the finance folder. Format: `references/regras-exemplo.json`. User rules run first; terms match whole
   words without accents or punctuation; `word*` matches a prefix; `word #` means the word followed by a number. Use
   the built-in category names (English or Portuguese label, or keys like `contractors`, `owner_draw`, `transfer`,
   `loan_in`, `commissions`, `cust_deposits`) or any new name (a new expense name counts as variable cost).
6. Rerun with `--rules confidential/rules.json`. The report gets better every month.

## 5. Final report

Build a DOCX (`docx` skill) or spreadsheet (`xlsx` skill), in the deliverables language:
1. **Five-line summary**: money in, money out, what was left, versus last month, the main reason.
2. **Indicators**: operating cash result and margin, owner draws and result after draws, fixed vs variable costs,
   labor share (payroll + payroll taxes), rent and taxes as % of money in, estimated break-even.
   - **Fixed**: payroll, payroll taxes, rent, utilities, insurance, software, professional services, loan payments.
     **Variable**: supplies/materials, equipment rental, vehicle, marketing, leads, fees, contractors, taxes, sales
     tax, travel, review items and new custom categories, unless the user says otherwise.
   - **Contribution margin %** = (money in − variable costs) ÷ money in. **Break-even** = fixed costs ÷ contribution
     margin % (no positive margin, no break-even: say so).
3. **Money in by source** and **money out by category**, with a simple bar chart.
4. **Weekly cash flow**: which week gets tight (useful to move due dates).
5. **Alerts**, explained in plain language: negative result, uncategorized share, bank/merchant fees above 3% of sales,
   overdraft/NSF fees, loan payments share, labor share, card payments (double counting), quarterly estimated tax
   (March, May, August, December: due around Apr 15, Jun 15, Sep 15, Jan 15), sales tax paid (customers' money),
   revenue concentration in one carrier/client, chargebacks/commission reversals, materials spike vs money in, large
   customer deposits not yet earned (cash is not profit), duplicates, categories that jumped.
6. **Action plan**: 3 concrete actions with estimated impact (e.g. "card processing at 3.2%; at 2.7% you'd save about
   $95/month on $19,000 of card sales").
7. Note: cash basis, not a P&L or accrual statement; your bookkeeper/CPA closes the books. Tax figures are estimates:
   confirm with your CPA.

Where to save: full version (with descriptions or names) in
`confidential/YYYY-MM-DD-management-report-YYYY-MM.docx` (or `confidencial/AAAA-MM-DD-relatorio-gestao-AAAA-MM.docx`),
where the first date is today and `YYYY-MM` the month analyzed. The version without transaction descriptions (rerun with
`--no-descriptions`) can go to `02-finance/` / `02-financas/` with the same name. For partners or investors, offer a
one-page version without descriptions.

## 6. Industry notes

- **Restaurants/bakeries**: POS deposits are net of processing fees and may include sales tax and tips; delivery-app
  payouts are net of commissions (often 15–30%; confirm your contract). Check sales tax set-aside.
- **Cleaning, construction and other services**: Zelle/ACH to individuals is usually labor; confirm employee vs 1099
  contractor (W-9 on file). Job deposits, progress payments and retainage are cash in but may be owed work: reserve the
  remaining job cost. Materials bought before the customer pays are financed by the business.
- **Insurance agents**: commissions arrive from carriers and IMOs/FMOs; chargebacks on lapsed policies are negative
  revenue; keep a reserve for advanced commissions; leads and E&O are normal costs.
- **Financial services**: advisory fees and commissions are money in; custodial and platform fees are fees; FINRA,
  NMLS and state registrations are licensing costs.

## 7. Cautions

- Do not invent numbers. Without the previous whole month, say the comparison comes next month.
- Transfers, card payments, loans received and owner money in are not revenue or expenses (the script separates them;
  confirm). Loan payments count as cash out; on a P&L only the interest is an expense.
- If a Finance persona exists in the company folder, present the report in its voice.
