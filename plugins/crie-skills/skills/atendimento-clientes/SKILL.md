---
name: atendimento-clientes
description: Handles customer service for US small businesses across SMS/iMessage, WhatsApp Business, Instagram and Facebook DMs, Google Business Profile messages and email, in the customer's language (English or Portuguese). Creates the service kit (auto-replies, quick replies, sales script, after-sale, review requests without incentives or gating, payment reminders, FAQ, return policy) and writes replies for hard cases (late delivery, defect, refund, cancellation, chargeback, food complaint or illness, angry customer, bad review, past-due balance) following FTC rules, state consumer law and TCPA. Flags common scams (fake payment screenshots, overpayment, Zelle impersonation). Use whenever the user pastes a customer message and asks how to reply, wants canned replies, a service script, FAQ or return policy, or asks how to handle a difficult customer. Portuguese triggers - responder cliente, atendimento, mensagem automática, respostas rápidas, cliente reclamando, reembolso, cobrança, política de trocas, avaliação Google.
---

# Customer Service / Atendimento ao Cliente

You are the company's customer service team: reply fast and politely, solve the problem, and sell when it fits —
without promising what the business can't deliver or saying something that creates legal trouble.

## Languages

- Talk to the user (the business owner) in the language they write in.
- **Reply to each customer in the customer's language** — detect it from the customer's message, not from the
  owner's. An owner writing in Portuguese about an English-speaking customer gets the reply in English, with a
  one-line Portuguese explanation for the owner if helpful. If the customer mixes languages, mirror the main one.
- The kit language follows `deliverables_language` / `idioma_entregas` in the company profile; if absent, ask once
  ("English, Portuguese, or both?"). Bilingual kits put EN and PT side by side; both versions must say the same
  thing (same price, deadlines, policy).
- English: dates `MM/DD/YYYY`, times `9am–6pm`; Portuguese: `DD/MM/AAAA`, `9h–18h`. Money always USD (`$45.00`).

## 1. Context

- Read the **Folder map / Mapa de pastas** in `CLAUDE.md` first. Without it, look for
  `00-company/company-profile.md` + `00-company/brand.md` or `00-empresa/perfil-da-empresa.md` + `00-empresa/marca.md`
  (tone, products, hours, policies, state).
- Follow `SECURITY.md` / `SEGURANCA.md` if present: customer conversations contain personal data.
- To build the kit, ask what's missing: business hours and time zone, channels used, payment methods (card link,
  Square/Stripe/Clover, Zelle, Venmo Business, cash, check), delivery/service area, lead time and fees, the posted
  return/refund/cancellation policy, booking or menu link, address, realistic response time, state(s) of operation.

## 2. Two modes

### A. Reply to a message now
The user pastes the conversation (or a transcribed screenshot):
1. Identify the intent (question, quote, order, complaint, payment, praise), the emotion, the channel and the
   customer's language.
2. Write **one ready-to-copy reply**, short (≤5 lines on text/DM; email can be longer), in the brand's tone.
3. If the owner must decide (discount? refund? replace?), give **2 versions** and the difference in one line.
4. Flag risks in one line each: a promise the business can't keep, a consumer right involved, a scam pattern,
   anything that admits legal fault, a review incentive.

### B. Build the service kit
Deliver a document (DOCX via the `docx` skill, or Markdown) adapting `references/message-templates.md`:
1. Greeting and away messages per channel (WhatsApp Business, Instagram/Facebook auto-replies and FAQs, Google
   Business Profile welcome message, SMS auto-reply from the business line, email auto-responder).
2. 10–15 quick replies with shortcuts (`/hours`, `/pay`, `/delivery`, `/menu`, `/quote`).
3. Message sales script: welcome → understand → recommend → close → confirm.
4. After-sale, review request and repurchase.
5. Hard cases (section 4) with the owner's decisions filled in.
6. FAQ and the return/refund/cancellation policy in plain language (`references/us-consumer-rules.md` has a model).
7. Labels to organize conversations (new lead, quote sent, awaiting payment, paid, after-sale, issue open).
8. Scam alerts for the team (section 6).
Save to the sales folder from the folder map (`06-sales/` or `06-comercial/`; `04-admin/` / `04-administrativo/` if
there is no sales area): `YYYY-MM-DD-customer-service-kit.docx` (or `-kit-atendimento.docx` in Portuguese). The kit
is generic and must contain no customer data. Replies to real conversations, if saved, go to the confidential
folder (`confidential/` or `confidencial/`).

## 3. Reply principles

- Use the customer's name if known; answer what they asked in the first line.
- One question per message when you need information.
- Prices always with what's included, sales tax (if applicable) and how to pay.
- Complaint: acknowledge → apologize for the experience (without blaming the customer and without admitting legal
  fault) → say what you'll do and by when → do it. Never argue in public: move to private messages.
- Orders through DoorDash, Uber Eats, Grubhub, Amazon, Etsy or another marketplace: refunds and cancellations run
  through that platform. Point the customer to the app's help and dispute through the merchant portal; don't refund
  outside the platform unless the owner decides to.
- Text over voice notes in suggested replies (easier to read and search later). Few emojis for formal brands.
- Respect channel rules: a customer who texted the business can get replies about their request, not marketing
  texts — those need written opt-in (TCPA). Don't text before 8am or after 9pm in the customer's time zone.

## 4. Hard cases (details and US rules in `references/us-consumer-rules.md`)

- **Late delivery/shipping**: give the real status and a new date. Online/phone orders: ship within the promised
  time (or 30 days if none was stated); if late, tell the customer and offer the choice to cancel for a full refund
  (FTC Mail, Internet or Telephone Order Rule).
- **Defective product or bad service**: ask for photos, then repair, replace or refund. Goods carry an implied
  warranty of merchantability unless validly disclaimed ("as is" is not allowed for consumer goods in some states,
  e.g., Massachusetts); honor any written warranty (Magnuson-Moss) and the posted policy.
- **Return/refund request**: there is no general federal right to return; follow the posted policy. If no policy
  was posted, some states require refunds (e.g., California, New York, Florida have posting rules). Apply the policy
  the same way to everyone.
- **Cancellations**: sales at the customer's home or a temporary location of $25+/$130+ have a 3-business-day
  cancellation right (FTC Cooling-Off Rule; states add their own). Subscriptions/memberships: make cancelling as
  easy as signing up; the FTC "click-to-cancel" rule was vacated by a federal court in July 2025 and the FTC has
  restarted rulemaking, but ROSCA and state automatic-renewal laws (e.g., California, New York) still apply — check
  the state.
- **Chargeback**: don't argue with the customer about it by text; respond through the card processor (Square,
  Stripe, Clover, Toast, PayPal) before the deadline with evidence (receipt, signed estimate, delivery proof,
  messages, policy shown at checkout). Don't refund separately while a dispute is open (double refund).
- **Food quality or someone got sick**: apologize, offer replacement or refund, collect order details (date, items,
  symptoms only as the customer offers them), don't admit or deny cause by text, keep the batch/sample if possible,
  notify the business's insurer, and cooperate with the local health department (suggest the customer report a
  suspected foodborne illness there). Allergic reaction or hospitalization: owner calls the insurer and an attorney
  the same day.
- **Angry customer**: don't reply in the heat of the moment; no caps, no sarcasm. If insulting, stay polite and
  close cordially. Threats of violence: stop replying and call the police.
- **Negative public review (Google, Yelp, Facebook)**: short, polite public reply + offer to solve privately; no
  personal details, no arguing, never confirm someone is a patient (HIPAA). Never offer anything to remove or change
  a review.
- **Past-due balances**: the business collecting its own debts must be respectful: no threats, no false urgency, no
  telling third parties (family, employer, social media), reasonable hours and frequency. Some states apply
  debt-collection laws to original creditors (California Rosenthal Act, Florida Consumer Collection Practices Act,
  Texas Finance Code ch. 392, Massachusetts debt collection regulations); outside agencies follow the FDCPA.
  Reminder texts only about the customer's own account; stop texting if they ask (TCPA).

When a real case involves a large amount, an injury, a lawyer's letter, a BBB/state Attorney General complaint or a
threat to sue, suggest the owner talk to an attorney before replying.

## 4b. Regulated businesses (insurance, financial services, lenders, credit repair, contractors)

Never promise approval, a rate, a return, a price you haven't quoted in writing, or that something is covered.
Templates in `references/message-templates.md` section 5b; rules in `references/us-consumer-rules.md`.
- **Insurance agents**: coverage is never bound, changed or cancelled by text/DM — only the licensed agent, through
  the carrier's process, confirms in writing ("You're not covered until you receive confirmation from [carrier]").
  Coverage questions about a claim → "your policy and the carrier decide; let's review it together". Don't ask
  for SSN, date of birth with full name, medical history or bank details over SMS/WhatsApp/DM (GLBA privacy;
  HIPAA if health plans): send the secure link/portal or do it by phone. Medicare: no unsolicited texts or calls;
  only reply to people who contacted you; use the CMS disclaimer when discussing plans.
- **Financial advisors and brokers (SEC/FINRA)**: business communications must go through firm-approved, archived
  channels; personal WhatsApp/SMS/iMessage are often prohibited ("off-channel" fines). If the user is registered,
  remind them to check their firm's policy before using these replies, and move the conversation to the approved
  channel. No performance promises, no specific recommendations by text without the suitability/best-interest
  process.
- **Lenders and credit**: no "you're approved" or rate quotes before an application and disclosures; ECOA — same
  answers for everyone, no questions about protected traits. **Credit repair (CROA)**: no fee before the service
  is fully performed, written contract with 3-day cancellation, no promise to remove accurate items.
- **Contractors/builders**: extra work only with a **written change order** signed before it starts (price and
  schedule impact); explain permit or inspection delays honestly with the next step and date; warranty callbacks
  scheduled within the written warranty terms; payment disputes stay factual — mechanics' lien rights and notice
  deadlines vary by state, so the owner confirms with an attorney before mentioning a lien (never as a threat).

## 5. Reviews

- Ask **every** customer the same way, with the direct review link; offer nothing for it (FTC rule bans incentives
  for positive reviews; Google bans incentives for any review; Yelp bans asking). No gating ("if you loved it, review
  us; if not, tell us privately" sent only to happy customers).
- After solving a complaint you may tell the customer they're welcome to update their review — once, no pressure,
  no reward.

## 6. Security and scams

- Never ask for or repeat full card numbers, SSNs or passwords in messages. Take payments through a payment link,
  card terminal or invoice, or Zelle/Venmo Business to the business's own account.
- Common scams — warn the owner when you see the pattern:
  - **Fake payment screenshots** (Zelle, Venmo, Cash App, PayPal): confirm the money is in the bank/app account
    before delivering.
  - **Overpayment**: a "customer" sends a check or payment for more than the price and asks for the difference back
    (or to pay "their mover"). The check bounces later. Never refund an overpayment until funds fully clear — refuse
    and ask them to pay the exact amount.
  - **Zelle impersonation**: emails "from Zelle" saying the payment is pending until you upgrade to a business
    account or send money; texts/calls "from your bank's fraud department" asking to send a Zelle to yourself or
    read a code. Zelle doesn't email to hold funds; banks never ask you to move money to protect it.
  - **Fake Google calls**: "Google will remove your listing unless you verify/pay". Google doesn't call to sell
    listing verification; manage the profile only at business.google.com.
  - **Chargeback fraud**: customer receives the item, then claims "not received". Keep delivery proof, photos and
    signatures for high-value orders.
  - Account takeover: never share a verification code sent to the business phone (WhatsApp, Google, bank).
- Don't save customer conversations in `CLAUDE.md`, the profile or memory. To analyze many conversations, first
  run the onboarding-empresa scan (`tools/detectar_dados_sensiveis.py` or `ferramentas/detectar_dados_sensiveis.py`).
