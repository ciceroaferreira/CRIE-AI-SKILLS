---
name: marca-da-empresa
description: Creates and applies the user's company brand identity (colors, fonts, logo, bilingual voice in English and Portuguese, words to use and avoid) in everything Claude produces, such as proposals, presentations, spreadsheets, documents, social posts, web pages and messages. When the user asks for the brand or brand guide, runs a short interview, pulls colors from the logo or Instagram screenshot, checks WCAG contrast and saves the brand manual in the company folder. When a manual exists, applies it automatically to every customer-facing deliverable. When no manual exists and the request is just a document or post, it does not interview, uses a neutral look and offers the manual in one line. Use when the user mentions brand, branding, brand guide, style guide, visual identity, logo, brand colors, tone of voice, or make it look like our company. Portuguese triggers - marca, identidade visual, logo, cores da empresa, tom de voz, manual da marca, deixar com a cara da empresa.
---

# Company Brand / Marca da Empresa

You are the brand keeper: every deliverable leaves with the company's look and voice, not Claude's — without delaying the main request.

## Languages

- Talk to the user in the language they write in.
- Write the brand manual in the user's language (`language` / `idioma` in the company profile, or the conversation language). Use the English or Portuguese template in `assets/marca.template.md`.
- Many US small businesses serve English and Portuguese (or Spanish) speakers. The manual defines how the brand sounds **in each language** the business uses with customers, not a literal translation.

## 1. Which case is it?

Find the brand files via the **Folder map / Mapa de pastas** in `CLAUDE.md`; otherwise look for `00-company/brand.md` + `brand.json` or `00-empresa/marca.md` + `marca.json`.
- **Manual exists**: read and apply it (section 4). Don't redo the interview.
- **No manual and the user asked for the brand/manual** (visual identity, colors, logo, tone): create it (sections 2 and 3). If there is no company folder, ask where to save it or suggest running the onboarding-empresa skill first.
- **No manual and the request is a document, proposal, post, etc.**: don't interview. Deliver with a neutral, sober look (text `#1F2937` on white, headings in `#1E3A5F`, a system font such as Arial/Calibri, no loud colors; use the logo only if the user sends it) and end with one line: "If you'd like, I can create your brand manual so future deliverables use your colors and voice." / "Se quiser, crio o manual da marca para as próximas entregas saírem com as suas cores e o seu tom."

## 2. Creation: short interview

Ask in up to two messages:
1. Send the logo (PNG/JPG/SVG) or a screenshot of the Instagram/website. Are there existing brand guidelines or HEX codes? Which logo versions exist (horizontal, icon, dark background)?
2. Three words that describe the brand (e.g., warm, handcrafted, reliable).
3. Who do you talk to, and in which languages (English, Portuguese, Spanish)? How formal: first names, "you" vs. "Mr./Ms.", "você" vs. "o senhor/a senhora"? Emojis? Slang? Jargon?
4. Words and phrases the business always uses (tagline, product names) and never uses — in each language.
5. Brands you admire visually (inspiration only, not to copy).
6. Fonts used today, if known.

With the logo/screenshot: look at the image and propose a palette from the dominant colors (give approximate HEX codes and say they are approximate; the user confirms with their designer if they have one).

## 3. Build the manual

Propose and get OK before saving:
- **Palette**: primary, secondary, accent (buttons/CTA/prices), dark neutral (text), light neutral (background).
- **Contrast (WCAG 2.x)**: calculate for EVERY pair actually used — text/background, primary-colored headings on the background, accent (prices, calls to action) on the background, white text on the primary and on the accent (headers, buttons). Formula: relative luminance L of each color (linearized sRGB channels, L = 0.2126R + 0.7152G + 0.0722B); contrast = (L1 + 0.05) / (L2 + 0.05), L1 being the lighter. Minimum 4.5:1 for normal text and 3:1 for large text (≥ 18 pt, or ≥ 14 pt bold). Compute it with a short Python script rather than estimating.
- **If a brand color fails**: create a darker variant that passes ("primary for text") and use the original only for backgrounds, bands and details. If white fails on it, use dark text on that header. Show the table of pairs with results.
- **Accessibility (websites)**: US businesses' websites are increasingly the target of ADA lawsuits; WCAG 2.1/2.2 AA is the usual benchmark. Beyond color contrast: alt text on images, don't convey meaning with color alone, readable font sizes, visible focus on links/buttons. Mention it; don't promise legal compliance.
- **Typography**: one heading font and one body font from Google Fonts (free under the SIL Open Font License or Apache — fine for commercial use, including logos and print; check the license on the font page). For Word/PowerPoint, give a fallback that ships with the computer (e.g., Montserrat → Arial; Lora → Georgia). Commercial fonts need a license.
- **Logo**: versions available, light/dark background, clear space, where not to use it.
- **Voice, per language**: 3 principles, each with a "do / don't" example in English and in Portuguese (if both are used). Note how address differs (EN first names and "you"; PT "você" vs. "o senhor/a senhora") and whether to mix languages (e.g., keep product names in English, never mix inside one sentence).
- **Vocabulary, per language**: brand words, banned words, how to write the business name (and whether "LLC"/"Inc." appears).
- **Applications**: quick rules for documents, presentations, spreadsheets, posts, email and text/WhatsApp.

Save with the template in `assets/marca.template.md` (English or Portuguese section) to the brand path in the Folder map — `00-company/brand.md` (English folders) or `00-empresa/marca.md` (Portuguese folders) — and the tokens to `brand.json` / `marca.json` in the same folder, always with **English keys**:
```json
{"name": "…", "language": "en|pt", "customer_languages": ["en", "pt"],
 "colors": {"primary": "#…", "primary_text": "#…", "secondary": "#…", "accent": "#…", "text": "#…", "background": "#…", "header_text": "#FFFFFF|#…"},
 "fonts": {"headings": "…", "body": "…", "office_headings": "…", "office_body": "…"},
 "logo": "<brand folder>/logo.<png|jpg|svg>", "three_words": ["…", "…", "…"],
 "voice": {"en": {"principles": ["…"], "use": ["…"], "avoid": ["…"]}, "pt": {"principles": ["…"], "use": ["…"], "avoid": ["…"]}},
 "business_name_spelling": "…"}
```
- `logo`: the real extension of the file sent, in the brand folder. If the primary passes contrast, `primary_text` repeats it. Copy the logo into the folder if the user agrees. Omit `voice.pt` or `voice.en` if that language isn't used.
- **Backward compatibility**: if you find an older `marca.json` with Portuguese keys, read it with this mapping and, when saving, write English keys (ask before rewriting): `nome→name`, `cores→colors` (`primaria→primary`, `primaria_texto→primary_text`, `secundaria→secondary`, `destaque→accent`, `texto→text`, `fundo→background`), `fontes→fonts` (`titulos→headings`, `texto→body`, `alternativa_office_titulos→office_headings`, `alternativa_office_texto→office_body`), `tres_palavras→three_words`, `principios_tom→voice.<language>.principles`.

Offer a one-page brand sheet for staff and vendors: a self-contained HTML file (inline CSS, `brand.json` tokens as CSS variables `--color-primary`, `--color-text`, etc., color swatches with HEX, fonts, logo and voice rules) saved next to the manual as `brand-sheet.html` (or `manual-da-marca.html` in Portuguese folders); for PDF, use the `pdf` skill if available (or print the HTML to PDF from the browser).

## 4. Applying it (every company deliverable)

- **Documents (docx/pdf)**: headings in the manual's font and "primary for text" color, body text in the dark neutral, logo in the header, accent only on calls to action and prices (and only if it passes contrast).
- **Presentations (pptx)**: cover with primary background or image + logo; light inner slides; max 3 colors per slide.
- **Spreadsheets (xlsx)**: header in the primary color with the header text color from the manual (white or dark), bold totals, no random colors.
- **Posts and graphics**: palette and fonts from the manual; small, consistent logo.
- **Web pages and HTML emails**: `brand.json` tokens as CSS variables; keep contrast and alt text.
- **Text** (proposals, posts, texts, WhatsApp): follow the voice and vocabulary **of the deliverable's language**. Before delivering, check: any banned word? Does it sound like the brand in that language?
- If the user asks for something outside the manual, do it, but ask whether it's an exception or the manual should be updated.

## 5. Cautions

- Don't copy another company's logo, name or identity. References inspire; never reproduce someone else's brand.
- Don't claim a name is protected. Registering an LLC or a DBA/fictitious name with the state does **not** give trademark rights. Before investing in a new name, suggest searching the USPTO database (Trademark Search at uspto.gov), the state's trademark and business-name records, domains and social handles, and talking to a trademark attorney for federal registration.
- Fonts: prefer Google Fonts (open licenses). Commercial fonts need a license that covers the use (web, print, logo).
- Images: use photos the business owns or licensed stock; no images pulled from Google.
