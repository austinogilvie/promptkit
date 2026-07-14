# Formatting and Presentation

Contents:
- [Cell Color Conventions](#cell-color-conventions)
- [Number Formatting](#number-formatting)
- [Line Item Presentation](#line-item-presentation)

---

## Cell Color Conventions

Color should communicate what a cell *is*.

| Font Color | Meaning                                                |
| ---------- | ------------------------------------------------------ |
| Blue       | Hard-coded input or historical data                    |
| Black      | Formula using cells on the same sheet                  |
| Green      | Formula linking to another sheet in the same workbook  |
| Purple     | Formula linking to another workbook                    |
| Red        | Error, warning, placeholder, or item needing attention |

Use these colors consistently.

Do not use red for ordinary emphasis. Red should mean something is wrong, incomplete, or needs review.

External workbook links should be avoided unless necessary. If they are used, flag and document them.

---

## Number Formatting

Use consistent number formats throughout the model. Every financial table should clearly state its units:

- `$ in millions`
- `$ in thousands`
- `shares in millions`
- `except per-share amounts`

Recommended formats:

| Item              | Format                                             |
| ----------------- | -------------------------------------------------- |
| Dollars           | One decimal place unless whole numbers are cleaner |
| Percentages       | One decimal place                                  |
| Multiples         | One decimal place plus `x`                          |
| Share counts      | One decimal place                                  |
| Per-share amounts | Two decimal places                                 |
| Dates             | One consistent date format                         |

Negative numbers should use parentheses:

```text
($45.2)
```

Avoid mixing dashes, blanks, and zeroes unless each has a clear meaning. Pick a convention and use it consistently.

---

## Line Item Presentation

Use formatting to show structure, not decoration.

- Bold major line items and key outputs.
- Indent sub-items under parent categories.
- Use a single top border for subtotals.
- Use a double top border for grand totals or final outputs.
- Use shading sparingly for section headers, input areas, and summary outputs.

Example:

```text
Revenue
  Product Revenue
  Services Revenue
Total Revenue
```

Avoid heavy fills, excessive borders, and decorative formatting that does not communicate meaning.
