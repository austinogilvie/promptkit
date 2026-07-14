# Formulas, Assumptions, and Sign Conventions

Contents:
- [Inputs and Assumptions](#inputs-and-assumptions)
- [Formula Standards](#formula-standards)
- [Sign Conventions](#sign-conventions)

---

## Inputs and Assumptions

All important assumptions should live in clearly labeled input sections, for example:

- Revenue Assumptions
- Margin Assumptions
- Working Capital Assumptions
- Capex Assumptions
- Debt Assumptions
- Valuation Assumptions
- Scenario Assumptions

Do not bury assumptions inside formulas.

Bad:

```excel
=B10*1.08
```

Good (where `$C$5` is a clearly labeled growth assumption):

```excel
=B10*(1+$C$5)
```

Avoid "magic numbers" — hard-coded values inside formulas.

Bad:

```excel
=Revenue*0.35
```

Good:

```excel
=Revenue*Tax_Rate
```

Material assumptions should include a source note when practical:

```text
Source: Management guidance
Source: FY2025 financials
Source: Investor case assumption
Source: Internal estimate
```

Scenario controls should be easy to find and centralized.

---

## Formula Standards

Each row should generally have one formula logic that copies across time. Avoid rows where each forecast period has a different manually adjusted formula. If a formula break is necessary, make it obvious and explain why.

Break complex formulas into helper rows.

Bad:

```excel
=IF(C10>0,(C10*(1+C15)-C20)*(1-C25)+MAX(C30-C31,0),0)
```

Better — decompose into auditable steps:

```text
Revenue
Revenue Growth
Projected Revenue
Operating Costs
Tax Rate
Tax-Affected Operating Profit
Working Capital Adjustment
Free Cash Flow
```

Avoid hiding rows, columns, or sheets that contain important logic.

Avoid volatile functions unless necessary, especially in large models:

- `OFFSET`
- `INDIRECT`
- `TODAY`
- `NOW`
- `RAND`
- `RANDBETWEEN`

Avoid circular references unless truly required. If a circular reference is necessary, document it and include a check.

---

## Sign Conventions

Choose one sign convention and use it consistently.

| Convention        | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| Positive expenses | Revenue and costs are positive; formulas subtract costs      |
| Natural signs     | Revenue is positive; expenses and cash outflows are negative |

Either is acceptable. Mixing them is not. Cash flow signs should be especially clear.

Example using natural signs:

| Item           | Sign     |
| -------------- | -------- |
| Revenue        | Positive |
| Expenses       | Negative |
| Capex          | Negative |
| Debt issuance  | Positive |
| Debt repayment | Negative |

If a line item intentionally flips the sign for presentation, label it clearly:

```text
Less: Capital Expenditures
```

```text
Capital Expenditures Presented as Positive
```
