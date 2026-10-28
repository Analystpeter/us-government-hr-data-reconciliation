#!/usr/bin/env python3
"""Independent QA check of two publicly sourced San Francisco HR exports.

Python's standard library only; no synthetic records or destructive data edits.
Run: python hr_data_audit.py --plan export.csv --rates 'export(1).csv'
"""
import argparse
import collections
import csv
import json
from pathlib import Path


def load(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return [(line, record) for line, record in enumerate(reader, start=2)]


def plan_key(row):
    return (row['jobCode'].strip(), row['setId'].strip().upper(), row['effectiveDate'][:10])


def rate_key(row):
    return (row['Job Code'].strip(), row['SetID'].strip().upper(),
            row['Eff. Date'].strip().replace('/', '-'))


def number(txt):
    return float(txt.replace('$', '').replace(',', '').strip()) if txt.strip() else None


def run(plan_path, rate_path, out_path):
    plan, rates = load(plan_path), load(rate_path)
    rate_index = collections.defaultdict(list)
    for line, row in rates:
        rate_index[rate_key(row)].append((line, row))

    rows = []
    full_matched = 0
    pay_disagree = 0
    matched_title_disagree = 0
    case_only_title_variants = 0
    source_only = 0
    for p_line, p in plan:
        code, payset, date = key = plan_key(p)
        candidates = rate_index.get(key, [])
        if not candidates:
            source_only += 1
            rows.append(['SOURCE_ONLY', 'Investigate coverage', code, payset, date,
                         p_line, '', p['title'], '', 'No composite-key match in uploaded rates CSV; not necessarily an error.'])
            continue
        if len(candidates) > 1:
            rows.append(['AMBIGUOUS_KEY', 'Review', code, payset, date,
                         p_line, '; '.join(str(i) for i, _ in candidates), '', '',
                         'Multiple source-B records; do not accept first match automatically.'])
            continue
        full_matched += 1
        r_line, r = candidates[0]
        if p['title'] != r['Title']:
            if p['title'].casefold() == r['Title'].casefold():
                case_only_title_variants += 1
                rows.append(['TITLE_CASE_VARIANT', 'Informational', code, payset, date,
                             p_line, r_line, p['title'], r['Title'], 'Same composite key; capitalization-only variant.'])
            else:
                matched_title_disagree += 1
                rows.append(['TITLE_CONTENT_DIFFERENCE', 'Review', code, payset, date,
                             p_line, r_line, p['title'], r['Title'], 'Same composite key but substantive title wording differs.'])
        a, b = number(p['step1']), number(r['Step 1'])
        if a is not None and b is not None and abs(a - b) > 0.0001:
            pay_disagree += 1
            rows.append(['HOURLY_STEP1_DIFFERENCE', 'Review', code, payset, date,
                         p_line, r_line, f'{a:.4f}', f'{b:.4f}',
                         'Pay difference exceeds tolerance of 0.0001 per hour; verify against official authority.'])
    dup_groups = 0
    for (code, payset, date), candidate_rows in sorted(rate_index.items()):
        if len(candidate_rows) > 1:
            dup_groups += 1
            rows.append(['DUPLICATE_RATE_KEY', 'Review', code, payset, date, '',
                         '; '.join(str(line) for line, _ in candidate_rows), '', '',
                         'Repeated composite key in rates CSV. Check whether row values agree before deduplicating.'])
    headers = ['Finding', 'Severity', 'Job code', 'Pay set', 'Effective date',
               'Plan CSV row', 'Rates CSV row(s)', 'Plan value', 'Rates value', 'Analyst note']
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    summary = {
        'plan_source_records': len(plan),
        'rates_source_records': len(rates),
        'unique_matches': full_matched,
        'source_only_plan_records': source_only,
        'same_key_substantive_title_disagreements': matched_title_disagree,
        'same_key_capitalization_only_title_variants': case_only_title_variants,
        'same_key_hourly_step1_disagreements': pay_disagree,
        'duplicate_rate_key_groups': dup_groups,
        'findings_exported': len(rows),
        'findings_file': str(out_path),
        'match_key': 'job code | uppercase pay set | effective date (YYYY-MM-DD)',
        'note': 'No source records were modified. A source-only result is not proof of an error.'
    }
    print(json.dumps(summary, indent=2))
    summary_path = out_path.with_name('audit_summary.json')
    summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', default='export.csv', type=Path)
    parser.add_argument('--rates', default='export(1).csv', type=Path)
    parser.add_argument('--out', default='hr_audit_findings.csv', type=Path)
    args = parser.parse_args()
    run(args.plan, args.rates, args.out)
