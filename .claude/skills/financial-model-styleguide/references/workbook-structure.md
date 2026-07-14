# Workbook Structure, Model Map, and Sheet Naming

Contents:
- [Workbook Structure](#workbook-structure)
- [Model Map and Workbook Notes](#model-map-and-workbook-notes)
- [Sheet Naming](#sheet-naming)

---

## Workbook Structure

Keep inputs, calculations, outputs, and checks clearly separated. For small models, these can be sections on one or two sheets. For larger models, use separate tabs.

Recommended basic structure:

| Sheet         | Purpose                                                       |
| ------------- | ------------------------------------------------------------- |
| `Assumptions` | Key inputs, sources, and scenario controls                    |
| `Historical`  | Historical financials and source data                         |
| `Model`       | Core calculations and projections                             |
| `Outputs`     | Summary tables, charts, valuation, returns, and sensitivities |
| `Checks`      | Error checks and model status                                 |

Optional tabs for larger models:

| Sheet     | Purpose                                                    |
| --------- | ---------------------------------------------------------- |
| `Cover`   | Model purpose, owner, date, version notes, and open issues |
| `Sources` | Source notes, filings, exports, raw data references        |
| `TOC`     | Table of contents for large workbooks                      |

Historical periods should be on the left. Forecast periods should be on the right.

| 2023A | 2024A | 2025A | 2026E | 2027E | 2028E |
| ----: | ----: | ----: | ----: | ----: | ----: |

Use one period-labeling convention consistently.

---

## Model Map and Workbook Notes

For any model that will be reviewed, reused, or edited by someone other than the original builder, include a short model map. This can live on the `Cover`, `Assumptions`, or `Checks` tab. The model map should help a reviewer understand the workbook without relying on memory or visual inspection of the tabs.

### Sheet Inventory

List each sheet with a one-line description of its purpose. Label each sheet as one of: Input, Calculation, Output, Check, Source, or Documentation.

| Sheet         | Type        | Purpose                                                                |
| ------------- | ----------- | ---------------------------------------------------------------------- |
| `Assumptions` | Input       | Key model assumptions, scenario controls, and user-editable inputs     |
| `Historical`  | Source      | Historical financials and source data                                  |
| `Model`       | Calculation | Core operating model and forecast calculations                         |
| `Debt`        | Calculation | Debt schedule, interest expense, and repayment logic                   |
| `Outputs`     | Output      | Summary financial outputs, valuation, returns, and sensitivity tables  |
| `Checks`      | Check       | Error checks and top-level model status                                |

### Data Flow

Describe how the major sheets connect. A reviewer should be able to understand which sheets feed the model and which are downstream outputs.

```text
Historical feeds Model.
Assumptions feeds Model, Debt, Valuation, and Returns.
Model feeds Outputs, Valuation, Returns, and Checks.
Debt feeds Model and Checks.
Valuation feeds Outputs.
Returns feeds Outputs.
Checks pulls from Model, Debt, Valuation, and Returns.
```

### Color Convention

State the cell color convention explicitly in the workbook.

```text
Cell color conventions:
Blue font   = user input or hard-coded historical data
Black font  = formula using cells on the same sheet
Green font  = formula linked to another sheet in this workbook
Purple font = formula linked to another workbook
Red font    = error, warning, placeholder, or item requiring attention
```

### Key Inputs and Outputs

Document where the most important inputs and outputs live. This does not need to list every assumption — it should identify the main places a user goes to change the model and read the answer.

| Item                       | Location              | Notes                              |
| -------------------------- | --------------------- | ---------------------------------- |
| Revenue growth assumptions | `Assumptions!C10:H10` | User-editable forecast assumptions |
| EBITDA margin assumptions  | `Assumptions!C15:H15` | User-editable forecast assumptions |
| Debt interest rate         | `Debt!C8`             | User-editable debt assumption      |
| Exit multiple              | `Valuation!C20`       | Used in return cases               |
| Revenue forecast           | `Outputs!C8:H8`       | Summary output                     |
| EBITDA forecast            | `Outputs!C12:H12`     | Summary output                     |
| IRR / MOIC                 | `Returns!C25:D25`     | Key investor return outputs        |

Approximate ranges are acceptable if exact cell references are not practical.

### Named Ranges

If the workbook uses named ranges, list them and explain what they represent. Named ranges are optional, but if used, they should be documented.

| Named Range         | Meaning                               |
| ------------------- | ------------------------------------- |
| `Revenue_Growth`    | Forecast revenue growth assumption    |
| `Tax_Rate`          | Tax rate used in projected cash flow  |
| `Exit_Multiple`     | Exit multiple used in valuation cases |
| `Scenario_Selected` | Active scenario toggle                |

### Merged Cells

Avoid merged cells in calculation areas. They may be used sparingly for presentation headers, but must not interfere with formulas, data tables, or model logic. If merged cells are used, flag where they appear.

```text
Merged cells:
- Outputs sheet: title/header area in rows 1-3
- Valuation sheet: presentation headers in rows 4-5
- No merged cells used in calculation sections
```

### Data Validation and Dropdowns

If a cell uses data validation or a dropdown, document the valid options. This prevents reviewers from entering invalid assumptions or suggesting changes the model does not support.

| Cell             | Purpose          | Valid Values                           |
| ---------------- | ---------------- | -------------------------------------- |
| `Assumptions!C5` | Active scenario  | Base, Upside, Downside                 |
| `Debt!C10`       | Repayment type   | Interest Only, Amortizing, Bullet      |
| `Valuation!C8`   | Valuation method | EBITDA Multiple, Revenue Multiple, DCF |

---

## Sheet Naming

Use short, descriptive sheet names.

Good examples:

```text
Assumptions  Historical  Model  Revenue  OpEx  Capex
Debt  Valuation  Returns  Outputs  Checks  Sources
```

Avoid vague names:

```text
Sheet1  Calc  Stuff  Old  New  Final Final  Austin Edits
```

Do not rely on tab colors alone to explain the workbook.
