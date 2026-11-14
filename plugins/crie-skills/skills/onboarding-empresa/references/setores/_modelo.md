# Industry pack template (for any business)

Use this template when the user's business does not fit any ready-made pack (`references/setores/*.md`) or fits
two at once. Build the pack from your own knowledge of the industry, write it to the company folder's industry
file (`00-company/industry.md` or `00-empresa/setor.md`), and show the user a short summary to correct. This is
how the skill works for **any** business: the ready-made packs are shortcuts, not limits. Write it in the
company's language (`idioma`); keep the headings below exactly as they are (or their Portuguese equivalents),
because the setup script looks for them.

Think like a consultant who just visited the business: what brings in money, what costs money, what can go
wrong, what the owner does all day, and what an expert would do differently. Use USD, US federal + state rules,
and say "confirm with your attorney/CPA" where a decision depends on the law.

```markdown
---
code: <industry-slug>
name: <readable name>
name_pt: <nome em português>
suggested_level: standard | elevated | regulated
---

## How the business works
Revenue model (how money comes in), main costs, seasonality, value chain, what separates winners from losers.

## Key metrics
5 to 8 KPIs specific to this industry, one line each explaining why it matters.

## Regulation, confidentiality and risks
Laws, licensing boards, permits, inspections, insurance and sensitive data typical of the industry (federal and state).
Say whether it calls for the `regulated` level and why.

## Persona adjustments
How each base persona changes in this industry, one bullet per persona, e.g. `- **Marina (Marketing)** follows ...`.

## Specialist personas
0 to 2 specialists that only exist in this industry. For each: name, area, call me when, frameworks, first deliverables, limits.

## Routines Claude can run
6 to 10 recurring tasks Claude can do end to end (input → steps → deliverable). They become playbook candidates.

## Extra onboarding questions
2 to 4 questions that only make sense in this industry. Never ask for SSNs, passwords or bank numbers.
```
