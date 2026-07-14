# Review Checklist, Forbidden Patterns, and Quality Standard

Contents:
- [Review Checklist](#review-checklist)
- [Forbidden Patterns](#forbidden-patterns)
- [Quick Reference](#quick-reference)
- [Model Quality Standard](#model-quality-standard)

---

## Review Checklist

Before sending or relying on a model, check the following.

### Structure

- [ ] Inputs, calculations, outputs, and checks are clearly separated.
- [ ] Historical periods are on the left and forecast periods are on the right.
- [ ] Time periods are labeled consistently.
- [ ] Units are clearly stated.
- [ ] Sheet names are clear.

### Formatting

- [ ] Blue font is used for hard-coded inputs.
- [ ] Black font is used for same-sheet formulas.
- [ ] Green font is used for cross-sheet formulas.
- [ ] Purple font is used only for external workbook links.
- [ ] Red is used only for errors, warnings, placeholders, or required attention.
- [ ] Number formats are consistent.
- [ ] Negative numbers use parentheses.
- [ ] Major line items are bolded.
- [ ] Sub-items are indented.

### Formulas

- [ ] No assumptions are buried inside formulas.
- [ ] No unexplained magic numbers are present.
- [ ] Formulas copy across time where possible.
- [ ] Complex logic is broken into auditable steps.
- [ ] Formula breaks are documented.
- [ ] Circular references are avoided or documented.
- [ ] Volatile functions are avoided unless necessary.

### Inputs and Outputs

- [ ] Assumptions are easy to find.
- [ ] Key assumptions include source notes where useful.
- [ ] Scenario controls are centralized.
- [ ] Outputs link to calculations and are not manually typed.
- [ ] Sensitivity tables identify inputs and outputs clearly.

### Checks

- [ ] All model checks pass.
- [ ] Failed checks are obvious.
- [ ] External links are identified.
- [ ] Open issues are documented.

---

## Forbidden Patterns

Avoid the following:

- Hard-coded assumptions buried inside formulas
- Inconsistent color conventions
- Inconsistent number formats
- Mixed sign conventions
- Manual overrides without explanation
- Hidden core logic
- Unlabeled units
- Broken external links
- Decorative formatting that does not communicate meaning

---

## Quick Reference

```text
GOAL:
Build readable, auditable, updateable financial models.

STRUCTURE:
Separate assumptions, calculations, outputs, checks, and sources.

COLORS:
Blue   = hard-coded input or historical actual
Black  = same-sheet formula
Green  = formula linked to another sheet
Purple = external workbook link
Red    = error, warning, placeholder, or required attention

FORMULAS:
No magic numbers.
No hidden assumptions.
One row, one formula logic.
Formulas should copy across time.
Break complex logic into helper rows.
Avoid unnecessary volatile functions.
Document circular references.

TIME:
Historical periods on the left.
Forecast periods on the right.
Actuals and forecasts clearly labeled.

NUMBERS:
Units always shown.
Percentages to one decimal.
Multiples to one decimal plus "x".
Negatives in parentheses.

PRESENTATION:
Bold key line items.
Indent sub-items.
Use borders for subtotals and totals.
Use shading sparingly.

CHECKS:
Include a Checks section or tab.
Top-level model status should be obvious.
Failed checks should be red and easy to find.

DO NOT:
Bury assumptions in formulas.
Hide core logic.
Use inconsistent signs or formatting.
Leave unexplained manual overrides.
Present unlabeled units.
Leave broken external links.
```

---

## Model Quality Standard

A model is not finished when the math works.

A model is finished when another competent reviewer can open it, understand it, audit it, update it, and trust it without needing the original builder to explain how it works.
