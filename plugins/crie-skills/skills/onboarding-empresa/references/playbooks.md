# Playbooks: Claude doing the user's work

The question that changes everything in onboarding is not "what does your company do?", it is **"what do YOU
do every week?"**. Each recurring task the user describes becomes a **playbook**: a recipe Claude follows to
do the task end to end, the company's way, and deliver the finished result (document, spreadsheet, message,
analysis) instead of advice.

## 1. Map the routine (during onboarding)

Ask in plain words (in the user's language):
- "Walk me through a typical week: what do you do every Monday, every day, every month-end?"
- "Which 3 tasks take the most time or do you hate the most?"
- "Is there a task you always do the same way, following a template?"

Then **propose** the industry's typical tasks yourself (section "Routines Claude can run" of the pack) and ask
which apply. People forget half their routine; a list helps them remember.

Pick 3 to 6 tasks, prioritizing: high frequency × time spent × Claude can do it well.
Be honest about what Claude does **not** do: sign, file, submit to agencies, pay, send messages without
approval, access systems that aren't connected, decide about people.

## 2. Playbook format

Each playbook goes in `routines/<routine-name>.md` (`rotinas/` in a Portuguese folder), written in the
folder's language:

```markdown
# <Routine name>  (e.g., Weekly case status update)

- **Owner persona:** <name — area>
- **Frequency:** <daily | weekly | monthly | on demand>
- **Trigger (how the user asks):** "<typical phrase>", "<another phrase>"
- **Sensitivity:** <standard | elevated | regulated> — if it involves customer data, follow SECURITY.md
- **Deliverable language:** <en | pt | both> (from idioma_entregas unless this audience differs)

## Inputs
- What the user must provide (files, data, context). If missing, Claude asks once.

## Steps
1. ...
2. ...
(Include the checks an experienced professional would make.)

## Deliverable
- Format (docx, xlsx, md, WhatsApp/text message, email…), structure and where to save.
- If pseudonymized: revert with `tools/detectar_dados_sensiveis.py --reverter` (produces text) and only then
  build the final DOCX/XLSX from the reverted text.
- Company tone and standard. USD as `$1,234.56`; dates `MM/DD/YYYY` (English) or `DD/MM/AAAA` (Portuguese).

## Quality checklist
- [ ] ...

## Lessons learned
_Corrections the user made to past deliverables. Read before running._
```

## 3. Run a playbook (daily use)

When the request matches a playbook's trigger:
1. Read the playbook and the owner persona's card.
2. Check the inputs; ask only for what is missing, all at once.
3. If documents contain customer data, apply `SECURITY.md` **before** analyzing.
4. Run the steps and **deliver the finished file**, not a plan for how to do it.
5. Go through the quality checklist and say what needs human review.
6. If the user corrects something, ask whether to record it under "Lessons learned" for next time. That is
   how Claude gets to work the company's way.

## 4. Create new playbooks later

Whenever the user asks for something that looks recurring ("that report again…") and there is no playbook,
offer to turn what you just did into a new one.

## Example (Brazilian-owned immigration law firm in Newark, NJ — regulated)

**Case status update for the client**: persona Lúcia (docketing); weekly; trigger "write the status update for
client X". Inputs: case notes exported from Docketwise and the latest USCIS notice (text extracted from the
PDF). Steps: scan and pseudonymize (names, A-Numbers, receipt numbers become markers) → identify stage, last
action, next deadline and what the client must send → write a plain-language update in Portuguese (English
copy if requested) → list missing documents → revert markers only in the final version (the detector returns
text; any DOCX is built from the reverted text). Deliverable: WhatsApp/email text in `confidential/`, for the
attorney's review. Checklist: deadlines checked against the docket; no promise of outcome or processing time;
no unnecessary third-party data.
