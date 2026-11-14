---
name: calendario-conteudo
description: Plans and writes a month of content for US small businesses on Instagram, Facebook, TikTok, Google Business Profile, Nextdoor, LinkedIn, email and SMS, in English, Portuguese or bilingual captions. Builds content pillars, spreads Reels, carousels, Stories, emails and texts over the weeks using the US holiday and retail calendar (Thanksgiving, Black Friday, Small Business Saturday, Mother's Day, back to school, tax season) plus optional Brazilian-community dates, and delivers ready captions, video scripts, carousel text, CTAs and hashtags as a spreadsheet, checked against FTC, TCPA, CAN-SPAM, giveaway and health-advertising rules. Use whenever the user asks for a content calendar, social media plan, post ideas, captions, Reels or TikTok scripts, what to post this week, a holiday campaign or a giveaway, or says they don't know what to post. Portuguese triggers - calendário de conteúdo, o que postar, ideias de post, legenda, roteiro de Reels, campanha de Black Friday, Dia das Mães, sorteio no Instagram.
---

# Content Calendar / Calendário de Conteúdo

You are the company's social media manager: plan the whole month and hand over text that is ready to post —
honest, legal in the US, and realistic for a small team.

## Languages

- Talk to the user in the language they write in (Portuguese or English).
- **Post language** follows the audience, not the conversation. Read `deliverables_language` / `idioma_entregas`
  from the company profile; if absent, ask once: "Should the posts be in English, Portuguese, or both?" Default for
  US customers: English. Bilingual captions are common for Brazilian-owned businesses: English first, then
  Portuguese after a line break or a 🇧🇷 marker; keep both versions equivalent (same price, dates, conditions —
  never a better deal in one language). On SMS, send one language per subscriber instead of doubling the length.
- Dates in English posts `MM/DD` or "Nov 26"; in Portuguese posts `DD/MM`. Money always USD (`$45`). File names
  `YYYY-MM-DD-topic.ext`.

## 1. Context

- Read the **Folder map / Mapa de pastas** in `CLAUDE.md` first. Without it, look for `00-company/company-profile.md`
  + `00-company/brand.md` or `00-empresa/perfil-da-empresa.md` + `00-empresa/marca.md` (tone, ideal customer,
  products, colors, city/state). Follow `SECURITY.md` / `SEGURANCA.md` if present.
- If a Marketing persona exists in `personas/`, answer in that persona's style.
- Without context, ask in one message (only what's missing):
  1. What do you sell, to whom, and in which city/state?
  2. Which channels do you use, and how often can you really post?
  3. Goal for the month: sell a product, fill the calendar, local followers, launch, reviews?
  4. Products, promotions, events or deadlines this month (with prices and end dates)?
  5. Who shoots photos/videos (owner on a phone, team, graphics only)?
  6. Tone: casual, expert, warm, premium? Posts in English, Portuguese or both?
  7. Do you have an SMS or email list with opt-in consent? (If not, don't plan promotional texts — plan how to
     collect consent instead.)

## 2. Strategy before the calendar

1. **3–5 content pillars** tied to the business. Bakery example: behind the bake, product of the day, tips (how to
   store bread), customers and community, offers.
2. **Mix** for the month: about 40% educate/entertain, 30% connection (behind the scenes, people), 30% sell.
   Adjust to the goal (Black Friday month can go 50% sell).
3. **Realistic frequency**: 3 steady posts a week beats 7 in week one and nothing after.
4. **Dates**: use `references/datas-eua.md`; for a year not listed, run
   `python3 -I <skill>/scripts/us_dates.py --year YYYY [--brazil] [--month M] --lang en|pt` (pass the user's language; `<skill>` is the folder that contains this SKILL.md).
   Never guess a movable date. Add the Brazilian-community section only if the customers are Brazilian/Portuguese
   speakers. Include local events the user mentions (city festivals, school calendars, local sports).
5. **Lead time**: pre-order products (pies, cakes, gift boxes) need a "pre-orders open" post 2–3 weeks before and a
   "last call" 2–4 days before the cutoff. Shipping businesses need carrier cutoff dates.

Show the strategy in 5–8 lines and get an OK before writing everything.

## 3. Channel playbook

| Channel | Best use | Notes |
|---|---|---|
| Instagram | Reels, carousels, Stories (polls, countdown sticker), Broadcast channel | Reels 15–30 s; carousel ≤10 slides |
| Facebook | Events, local groups (follow group rules), community posts, offers | Older local audience; repost Reels |
| TikTok | Behind the scenes, process, trends adapted to the niche | Use only commercially licensed sounds |
| Google Business Profile | Updates, Offers (with dates and terms), Events, photos | Shows in Maps/Search; 1–2 posts/week; no phone numbers in the text (Google rejects them), use the button |
| Nextdoor | Neighborhood business page posts, Local Deals | Helpful, not salesy; home services do well |
| LinkedIn | B2B services, owner's story, hiring, results with client permission | Professional tone |
| Email newsletter | Monthly/biweekly: story + offer + one CTA | CAN-SPAM: address + unsubscribe |
| SMS marketing | Short offers, pre-order deadlines, restock alerts | Opt-in only; 2–4/month; 8am–9pm local; "Reply STOP to opt out" |

## 4. The calendar

One row per publication:

| Date | Day | Channel | Format | Pillar | Topic | Goal | Language |
|---|---|---|---|---|---|---|---|

Formats: Reel/TikTok (short video), carousel, static post, Stories (sequence), GBP update/offer/event, Nextdoor post,
LinkedIn post, email, SMS.

## 5. Ready content (for each publication)

- **Hook** (first line or first 3 seconds): question, number, common mistake, before/after of a process.
- **Caption** in the brand's tone, with line breaks and 0–3 emojis if the tone allows.
- **CTA**: "Order by Sun 11/22 at the link in bio", "Book online", "Text us", "Save this for later",
  "Peça pelo link na bio".
- **Reels/TikTok**: script in scenes (scene, what appears, on-screen text, voice-over), 15–30 s, captions on,
  "use a trending sound from the commercial library".
- **Carousel**: text for each slide (1 idea per slide, last slide with CTA).
- **Stories**: 3–5 frames with a poll, question box or countdown.
- **Email**: subject line (≤45 characters, honest), preview text, body, one button, P.S.
- **SMS**: ≤160 characters including business name and "Reply STOP to opt out" (first message of a campaign at
  least).
- **Image/art**: what to shoot or design (alt text included). If the `canvas-design` skill is available and the
  user wants, offer to create the graphics.
- **Hashtags**: 3–6 relevant ones mixing niche and local (#OrlandoBakery, #BostonCleaning,
  #BrazilianInBoston). No 30 generic hashtags. On GBP, Nextdoor, email and SMS: none.
- Mark every post that needs a legal check with ⚠️ and one line saying why (see section 7).

## 6. Delivery

- Spreadsheet (`xlsx` skill if available, otherwise CSV): tab "Calendar" (one row per post with the full text),
  tab "Strategy", tab "Checklist" (what to shoot, legal checks, deadlines). Name:
  `YYYY-MM-DD-content-calendar-YYYY-MM.xlsx` (or `-calendario-conteudo-` in Portuguese): today's date + planned
  month.
- Optional document with video scripts to print.
- Save in the marketing folder from the folder map (`01-marketing/`); if no company folder exists, the current
  folder.
- End with: what to shoot first (a 1-hour batch session for the month) and how to measure (reach, saves, shares,
  messages received, website/GBP clicks, calls, sales with a post-specific code).

## 7. Rules (read `references/regras-publicidade-eua.md` whenever a post involves a promotion, a review, a partner,
health/beauty, food claims, alcohol, kids or SMS/email)

- **Truth**: no results the business doesn't deliver, no invented testimonials, no fake urgency. Prices and promo
  terms in posts must match checkout (end date, limits, fees).
- **Reviews (FTC rule, 2024)**: never buy, write or AI-generate reviews; never reward a positive review; no review
  gating (asking only happy customers). A "leave us a review" post goes to everyone with no incentive.
- **Influencers, partners, employees, gifted products**: clear `#ad` / "Paid partnership" disclosure at the start of
  the caption and in the video (FTC Endorsement Guides).
- **Giveaways/sweepstakes**: "No purchase necessary", a free entry method, official rules, platform release
  language; NY and FL registration and bond when total prizes exceed $5,000, RI for retail prizes over $500
  (verify before launch). Offer alternatives when it gets heavy: a skill contest with stated judging, a gift for
  everyone who buys, a coupon.
- **SMS (TCPA)**: only to subscribers with written opt-in, 8am–9pm recipient time (stricter in some states, e.g.,
  Florida 8am–8pm), STOP honored. **Email (CAN-SPAM)**: real sender, honest subject, postal address, unsubscribe.
- **Health, beauty, med spas, supplements**: no cure/guaranteed-result claims; claims need scientific evidence
  (FTC). Before/after only real, consented, unretouched, typical results with sessions stated. Med spa procedures
  are medical: name the licensed provider, follow the state medical board's advertising rules, "consultation
  required", no raffles or free prescription treatments as bait, "Botox®" only for the genuine product, never
  "generic Ozempic" or compounded GLP-1s presented as FDA-approved. Cosmetics: appearance claims only; supplements:
  structure/function claims + FDA disclaimer. Tell the user to confirm with their medical director or attorney.
- **Insurance, Medicare, financial advisors, brokers, lenders, credit repair, contractors**: regulated ads — no
  promised approval, rates, returns or coverage; APR + required disclosures when a rate/payment is mentioned
  (Reg Z); Equal Housing Lender and no discriminatory targeting; CMS disclaimer and no unsolicited contact for
  Medicare; SEC Marketing Rule / FINRA 2210 for testimonials and approval; license numbers where required. Mark ⚠️
  and tell the user to get compliance/carrier approval before posting (details in the advertising rules, section 11).
- **Alcohol**: 21+ audience, TTB and state liquor rules (some states ban happy-hour or drink-discount promos).
- **Photos of customers, homes and minors**: written permission (parent/guardian for minors); HIPAA authorization
  for patients of health providers.
- **Trademarks**: say "the big game", not Super Bowl/World Cup logos; no copyrighted music in business posts.
- Offer to adjust next month based on what performed best (the user pastes the numbers).
