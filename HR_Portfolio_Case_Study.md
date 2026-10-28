# US Government HR Data Intake & Reconciliation
**Case study | Public City and County of San Francisco HR data**

## The assignment
Demonstrate a defensible data-intake workflow for salary schedules and classification records. The primary goal is accurate matching of job classifications, source verification, exception handling, and reproducible quality checks—not dashboard design.

## Public source datasets
- **Compensation Plan**: [SF Open Data / h3jp-c25d](https://data.sf.gov/d/h3jp-c25d) — 20,637 records, 32 original columns, effective dates from July 2020 through July 2026.
- **Hourly Rates of Pay by Classification and Step**: [SF Open Data / t59u-ig8c](https://data.sf.gov/d/t59u-ig8c) — 34,729 records, 30 original columns, effective dates from July 2014 through January 2026.
- Original provided CSV files: `export.csv` and `export(1).csv`. Their SHA-256 values and individual source-line identifiers are documented in the workbook. **All included raw data values are unchanged.**

## Excel deliverable
Open `US_Government_HR_Data_Reconciliation_Portfolio.xlsx` and visit **Guide** first.

| Worksheet | What it demonstrates |
|---|---|
| Guide | KPI summary, reviewer workflow, controls, scope limitations |
| Reconciliation | 546 source-A records, composite-key joins, XLOOKUP, pay validation, annualization, editable review decisions |
| Plan_Raw | 546 unchanged sampled original records + calculated join key |
| Rates_Raw | 460 unchanged sampled original records + calculated join key |
| Rates_QC | COUNTIF/COUNTIFS duplicate checks on the selected rate extract |
| Title_History | 47 real job codes with different titles over time |
| Exceptions | Actual pay disagreements, duplicate key, historic naming, capitalization variant, source gaps |
| Dictionary | Field definitions, matching assumptions, escalation guidance |
| Sources | Dataset links, original counts, file hashes, source coverage and lineage |
| Formula_Lab | Live LET, FILTER, SORT, UNIQUE, XMATCH, INDEX, TEXTJOIN, SUMIFS, SUMPRODUCT examples |

### Matching rules
1. Generate the key **job code | UPPER(pay-set identifier) | effective date (YYYY-MM-DD)**. This avoids treating same-title jobs at different pay sets or dates as identical.
2. Return classification, union code, hourly first step and biweekly minimum **only for a unique key match**.
3. Compare hourly first-step rates numerically; differences beyond **0.0001** are flagged for review.
4. Use exact official title comparison within a unique key; treat historical title changes separately rather than blindly rewriting old records.
5. Flag duplicate rate keys—even if the underlying rate records happen to agree—and keep review decisions separate from formula output.
6. Estimate annual pay as **biweekly minimum × 26 pay periods**, with the period count visible and editable on Guide. This is an illustration, not an official payroll annualization or union-contract determination.

## Main findings

**Full original-file Python audit:** 18,259 source-A records uniquely match source B; 2,378 source-A records have no matching key in the uploaded rates data; two matched entries for job code **9916** (2024-01-06, COMMN and SFMTA) have an hourly first-step difference of **$0.0025**. One duplicated source-B composite-key group exists for **8578 / COMMN / 2018-07-01** (two identical-key source lines). One capitalization-only title difference is visible for **1576 / COMMN / 2025-01-04**. No substantive same-key title differences were found.

**Curated workbook extract:** 454 unique matched classifications; 452 pass the source-to-source checks; two hourly first-step disagreements require review; 92 plan rows have no counterpart *within the uploaded rate extract*. The rate-QC sheet also exposes the repeated 2018 key, which does not have a 2018 compensation-plan counterpart in the available plan dataset.

**Important:** A missing counterpart is not proof that the government record is wrong: the source files cover different time periods, notably July 2026 appears in the compensation plan but not in the rate export. Historical changes in the title linked to a code are evidence of changing wording, not automatically duplicates or errors. Union codes were preserved, but **labor-agreement/bargaining-unit relationships were not independently verified** and must not be presented as completed.

## Independent Python check
`hr_data_audit.py` uses the Python standard library only. Run from the directory containing the original source CSVs:

```bash
python hr_data_audit.py --plan export.csv --rates "export(1).csv" --out hr_audit_findings.csv
```

The script leaves source data unchanged and produces `hr_audit_findings.csv` and `audit_summary.json` with line-level evidence. This is a secondary verification layer; the main work remains formula-based in Excel.

## NOTE:
“I used real publicly available San Francisco HR records rather than synthetic examples. In Excel, I preserved the source rows, standardized a three-part matching key, and used XLOOKUP and other validation formulas to reconcile job classifications, union codes and pay rates. The workbook detects real pay discrepancies, duplicate keys and coverage gaps, with an exception log and editable reviewer decisions. I also wrote a small Python script to independently audit the full exports. The key principle is not forcing a match or assuming an unmatched record is an error.”

*Portfolio demonstration based only on the publicly available, uploaded extracts; not endorsed by the City and County of San Francisco.*
