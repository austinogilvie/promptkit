---
name: financial-model-styleguide
description: Conventions for building readable, auditable, and maintainable financial model workbooks. Apply whenever reading, writing, reviewing, or auditing spreadsheet financial models (.xlsx), including operating models, three-statement models, LBO/DCF/returns models, debt schedules, and valuation or sensitivity tables. Use when structuring workbooks, applying cell color and number-format conventions, writing or refactoring model formulas, setting sign conventions, building outputs and checks, or running a model review.
---

# Financial Model Styleguide

Conventions for building readable, auditable, and maintainable financial model workbooks. A good model is easy to read, easy to audit, easy to update, and hard to misuse. The goal: someone who did not build the model should be able to open it, understand it, and trust it — without the original builder explaining how it works.

Apply these conventions whenever reading, writing, or auditing `.xlsx` models.

## Core Principles

- **Clarity over cleverness** — a slightly longer model with clear intermediate steps beats a compact model that is hard to audit.
- **Assumptions should be visible** — important assumptions live in clearly labeled input cells, never buried inside formulas.
- **Consistency matters** — same formatting, number formats, units, signs, formulas, and structure throughout. Inconsistency hides errors.
- **Build for review** — a reviewer should be able to trace where inputs come from, how calculations work, and whether checks pass.

## Always-On Quick Rules

Keep these in mind for every model. Deeper detail lives in the reference files below.

**Cell colors** (communicate what a cell *is*):

| Font Color | Meaning |
| ---------- | ------- |
| Blue   | Hard-coded input or historical actual |
| Black  | Formula using cells on the same sheet |
| Green  | Formula linked to another sheet in this workbook |
| Purple | Formula linked to another workbook |
| Red    | Error, warning, placeholder, or item needing attention |

Never use red for ordinary emphasis. State the color convention explicitly somewhere in the workbook.

**Structure** — separate inputs, calculations, outputs, and checks (sections on one sheet for small models, separate tabs for large ones). Historical periods on the left, forecast periods on the right, actuals vs. forecasts clearly labeled (`2025A`, `2026E`).

**Numbers** — always show units (`$ in millions`). Percentages and multiples to one decimal (multiples add `x`), per-share to two decimals. Negatives in parentheses: `($45.2)`.

**Formulas** — no magic numbers, no hidden assumptions. One row = one formula logic that copies across time. Break complex logic into helper rows. Avoid volatile functions (`OFFSET`, `INDIRECT`, `TODAY`, `NOW`, `RAND`) and undocumented circular references.

**Signs** — pick one sign convention and use it consistently; never mix. Label any line item that intentionally flips sign for presentation (`Less: Capital Expenditures`).

**Checks** — every model has a `Checks` section/tab with an obvious top-level status (`Model Status: OK`). Failed checks are red and easy to find.

## Reference Files

Read the relevant reference file when working on that area. Each is self-contained.

- **[references/workbook-structure.md](references/workbook-structure.md)** — workbook/sheet layout, the model map (sheet inventory, data flow, key inputs/outputs, named ranges, merged cells, data validation), and sheet naming. Read when setting up a new workbook, documenting an existing one, or reviewing overall structure.
- **[references/formatting.md](references/formatting.md)** — full cell color conventions, number formatting rules, and line-item presentation (bold, indent, borders, shading). Read when formatting a model or auditing its presentation.
- **[references/formulas-and-assumptions.md](references/formulas-and-assumptions.md)** — inputs and assumptions (no magic numbers, source notes), formula standards (helper rows, volatile functions, circular references), and sign conventions. Read when writing, refactoring, or auditing formulas.
- **[references/outputs-checks-docs.md](references/outputs-checks-docs.md)** — output design and sensitivity tables, model checks and status, and documentation/version logs. Read when building the presentation layer, check tab, or model documentation.
- **[references/review-checklist.md](references/review-checklist.md)** — the full pre-send review checklist, forbidden patterns, and the model quality standard. Read before signing off on or reviewing a model.

## Review Workflow

When asked to review or audit a model, work through **[references/review-checklist.md](references/review-checklist.md)** systematically, consulting the domain reference files for any area that needs a deeper standard. Report failures against the checklist categories: Structure, Formatting, Formulas, Inputs and Outputs, and Checks.
