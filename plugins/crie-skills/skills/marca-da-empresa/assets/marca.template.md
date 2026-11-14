<!--
Two templates in this file. Use ONLY the one in the user's language:
- English: from "TEMPLATE: EN" to "END EN" → save as 00-company/brand.md
- Português: from "TEMPLATE: PT" to "END PT" → save as 00-empresa/marca.md
Dates: EN MM/DD/YYYY, PT DD/MM/AAAA. Drop the voice/vocabulary rows of a language the business doesn't use.
Do not copy these comments or the TEMPLATE/END markers into the saved file.
-->

<!-- TEMPLATE: EN -->
# Brand manual — {{name}}

Updated {{date}}. Everything Claude produces for {{name}} follows this manual.

## Essence
**Three words:** {{three_words}}
**Who we talk to:** {{audience}}
**Customer languages:** {{customer_languages}}
**Reference brands (inspiration only, never copy):** {{reference_brands}}

## Colors
| Role | Color | HEX | Use |
|---|---|---|---|
| Primary | {{primary_name}} | {{hex_primary}} | Covers, bands, headers, details |
| Primary for text/headings | {{primary_text_name}} | {{hex_primary_text}} | Headings and brand-colored text (variant that passes contrast) |
| Secondary | {{secondary_name}} | {{hex_secondary}} | Support, charts, icons |
| Accent | {{accent_name}} | {{hex_accent}} | Buttons, calls to action, prices |
| Text | — | {{hex_text}} | Body text |
| Background | — | {{hex_background}} | Light backgrounds |

Contrast rule (WCAG 2.x): contrast = (L1 + 0.05) / (L2 + 0.05), L = relative luminance (L1 the lighter). Minimum 4.5:1 for normal text and 3:1 for large text (≥ 18 pt or ≥ 14 pt bold). A brand color that fails goes only on backgrounds and details; for text, use "primary for text/headings".

| Pair used | Contrast | Result |
|---|---|---|
| Text {{hex_text}} on background {{hex_background}} | {{c_text_bg}} | {{ok_text_bg}} |
| Headings {{hex_primary_text}} on background | {{c_heading_bg}} | {{ok_heading_bg}} |
| Accent {{hex_accent}} (prices/CTAs) on background | {{c_accent_bg}} | {{ok_accent_bg}} |
| {{header_text}} on primary (headers) | {{c_header_primary}} | {{ok_header_primary}} |
| {{button_text}} on accent (buttons) | {{c_button_accent}} | {{ok_button_accent}} |

Website accessibility: aim for WCAG 2.1/2.2 AA — contrast above, alt text on images, meaning not by color alone, visible focus on links and buttons.

## Typography
- **Headings:** {{heading_font}} (in Office: {{office_headings}})
- **Body:** {{body_font}} (in Office: {{office_body}})
- **License:** {{font_license}} (Google Fonts: open license, commercial use OK — check the font page)
- **Fonts used until now:** {{current_fonts}}

## Logo
- Main file: `{{logo_file}}`
- Versions: {{logo_versions}} (e.g., horizontal, stacked, icon, one-color, for dark backgrounds)
- Clear space: {{clear_space}} (e.g., free space around it equal to the height of the first letter)
- Use on: {{logo_backgrounds}}
- Don't: stretch, recolor, add shadows, place on busy photos.

## Voice — English
| Principle | Do | Don't |
|---|---|---|
| {{principle_1}} | {{do_en_1}} | {{dont_en_1}} |
| {{principle_2}} | {{do_en_2}} | {{dont_en_2}} |
| {{principle_3}} | {{do_en_3}} | {{dont_en_3}} |

- Address: {{address_en}} · Emojis: {{emojis_en}}

## Voice — Portuguese
| Principle | Faça assim | Evite assim |
|---|---|---|
| {{principle_1}} | {{do_pt_1}} | {{dont_pt_1}} |
| {{principle_2}} | {{do_pt_2}} | {{dont_pt_2}} |
| {{principle_3}} | {{do_pt_3}} | {{dont_pt_3}} |

- Address: {{address_pt}} (você / o senhor, a senhora) · Emojis: {{emojis_pt}}
- Mixing languages: {{language_mixing}}

## Vocabulary
| | English | Portuguese |
|---|---|---|
| We use | {{use_en}} | {{use_pt}} |
| We never use | {{avoid_en}} | {{avoid_pt}} |

- **Business name is written:** {{name_spelling}}

## Quick applications
- **Documents:** logo in the header, headings in primary for text, accent only on prices and calls to action.
- **Presentations:** cover in the primary color, light inner slides, up to 3 colors per slide.
- **Spreadsheets:** header in the primary color with {{header_text}} text, bold totals.
- **Posts:** manual palette and fonts, small logo in the same corner.
- **Email / text / WhatsApp:** {{messaging_rule}}
<!-- END EN -->

<!-- TEMPLATE: PT -->
# Manual da marca — {{name}}

Atualizado em {{date}}. Todas as entregas do Claude para {{name}} seguem este manual.

## Essência
**Três palavras:** {{three_words}}
**Para quem falamos:** {{audience}}
**Idiomas dos clientes:** {{customer_languages}}
**Marcas de referência (só inspiração, não copiar):** {{reference_brands}}

## Cores
| Papel | Cor | HEX | Uso |
|---|---|---|---|
| Primária | {{primary_name}} | {{hex_primary}} | Capas, faixas, cabeçalhos, detalhes |
| Cor para texto/títulos | {{primary_text_name}} | {{hex_primary_text}} | Títulos e textos na cor da marca (variante que passa no contraste) |
| Secundária | {{secondary_name}} | {{hex_secondary}} | Apoio, gráficos, ícones |
| Destaque | {{accent_name}} | {{hex_accent}} | Botões, chamadas, preços |
| Texto | — | {{hex_text}} | Texto corrido |
| Fundo | — | {{hex_background}} | Fundos claros |

Regra de contraste (WCAG 2.x): contraste = (L1 + 0,05) / (L2 + 0,05), com L = luminância relativa (L1 a mais clara). Mínimo 4,5:1 para texto normal e 3:1 para títulos grandes (≥ 18 pt ou ≥ 14 pt negrito). Cor da marca que não passa vai só em fundos e detalhes; em texto, use a "cor para texto/títulos".

| Par usado | Contraste | Resultado |
|---|---|---|
| Texto {{hex_text}} sobre fundo {{hex_background}} | {{c_text_bg}} | {{ok_text_bg}} |
| Títulos {{hex_primary_text}} sobre fundo | {{c_heading_bg}} | {{ok_heading_bg}} |
| Destaque {{hex_accent}} (preços/chamadas) sobre fundo | {{c_accent_bg}} | {{ok_accent_bg}} |
| {{header_text}} sobre primária (cabeçalhos) | {{c_header_primary}} | {{ok_header_primary}} |
| {{button_text}} sobre destaque (botões) | {{c_button_accent}} | {{ok_button_accent}} |

Acessibilidade do site: mire em WCAG 2.1/2.2 AA — contraste acima, texto alternativo nas imagens, não depender só da cor, foco visível em links e botões.

## Tipografia
- **Títulos:** {{heading_font}} (no Office: {{office_headings}})
- **Texto:** {{body_font}} (no Office: {{office_body}})
- **Licença:** {{font_license}} (Google Fonts: licença aberta, uso comercial permitido — confira na página da fonte)
- **Fontes usadas até hoje:** {{current_fonts}}

## Logo
- Arquivo principal: `{{logo_file}}`
- Versões: {{logo_versions}} (ex.: horizontal, vertical, ícone, monocromática, para fundo escuro)
- Área de respiro: {{clear_space}} (ex.: espaço livre ao redor igual à altura da letra inicial)
- Usar sobre: {{logo_backgrounds}}
- Não fazer: esticar, mudar as cores, aplicar sombra, colocar sobre fotos poluídas.

## Tom de voz — português
| Princípio | Faça assim | Evite assim |
|---|---|---|
| {{principle_1}} | {{do_pt_1}} | {{dont_pt_1}} |
| {{principle_2}} | {{do_pt_2}} | {{dont_pt_2}} |
| {{principle_3}} | {{do_pt_3}} | {{dont_pt_3}} |

- Tratamento: {{address_pt}} (você / o senhor, a senhora) · Emojis: {{emojis_pt}}

## Tom de voz — inglês
| Princípio | Do | Don't |
|---|---|---|
| {{principle_1}} | {{do_en_1}} | {{dont_en_1}} |
| {{principle_2}} | {{do_en_2}} | {{dont_en_2}} |
| {{principle_3}} | {{do_en_3}} | {{dont_en_3}} |

- Tratamento: {{address_en}} · Emojis: {{emojis_en}}
- Mistura de idiomas: {{language_mixing}}

## Vocabulário
| | Português | Inglês |
|---|---|---|
| Usamos | {{use_pt}} | {{use_en}} |
| Nunca usamos | {{avoid_pt}} | {{avoid_en}} |

- **Nome da empresa se escreve:** {{name_spelling}}

## Aplicações rápidas
- **Documentos:** logo no cabeçalho, títulos na cor para texto/títulos, destaque só em preços e chamadas.
- **Apresentações:** capa na cor primária, slides internos claros, até 3 cores por slide.
- **Planilhas:** cabeçalho na cor primária com texto {{header_text}}, totais em negrito.
- **Posts:** paleta e fontes do manual, logo pequeno no mesmo canto.
- **E-mail / SMS / WhatsApp:** {{messaging_rule}}
<!-- END PT -->
