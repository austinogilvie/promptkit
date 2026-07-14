# Outputs, Checks, and Documentation

Contents:
- [Outputs](#outputs)
- [Checks](#checks)
- [Documentation](#documentation)

---

## Outputs

Outputs should be clean, readable, and presentation-ready. They should summarize the model without exposing unnecessary calculation detail.

Every output should link back to the model. Do not manually type output values unless clearly marked as an input or assumption.

Group outputs by purpose:

- Operating performance
- Cash flow
- Valuation
- Returns
- Credit metrics
- Scenario analysis
- Sensitivity analysis

Sensitivity tables should clearly show:

- The input being changed
- The output being measured
- The active case or scenario
- Whether the output is pre-tax, after-tax, levered, unlevered, gross, or net

---

## Checks

Every model should include basic checks:

- Balance sheet balances
- Cash flow statement ties to cash movement
- Debt schedule rolls forward correctly
- Sources equal uses
- Shares outstanding tie correctly
- Historical data ties to source
- No missing required inputs
- No negative debt balances unless intentional
- No external links unless approved

Checks should be centralized in a `Checks` section or tab. The workbook should have a clear top-level status:

```text
Model Status: OK
```

Or:

```text
Model Status: ERROR - Review Checks
```

Failed checks should be obvious and formatted in red. Check outputs should be simple:

```text
OK
ERROR
TRUE
FALSE
0.0
```

---

## Documentation

Important models should include basic documentation. At minimum:

- Model purpose
- Owner
- Last updated date
- Version or file date
- Major open issues
- Important source notes

For models used across multiple review cycles, maintain a simple version log.

| Date       | Version | Owner | Description   |
| ---------- | ------- | ----- | ------------- |
| 2026-07-06 | v1      | AO    | Initial draft |

Use comments or notes for non-obvious assumptions, unusual formulas, manual overrides, and known limitations. Do not use comments as a substitute for clear structure.
