#!/usr/bin/env python3
"""Check review coverage records from JSON on stdin; never inspect or modify source.

Input:
  catalog: [{id, source}] -- every source-linked review criterion (P1-P8 keep IDs)
  performance_paths: [scope] -- independent paths identified by applicability screen
  plan: [{id, item, scope, requirement, pass, applicable, intended_extent}]
  records: [{id, status, examined_scope, unexamined_scope, evidence, result,
             reason, stop_reason, execution: {status, detail},
             cost_evidence: {base, target, workload, workload_source, safety_reuse}}]
  review_status: complete | partial

All scalar fields are strings except applicable (boolean); `examined_scope` and `unexamined_scope` are lists
of nonempty strings; plan.scope is one independent path identifier. cost_evidence is required for inspected P1-P8 records; its
fields are nonempty strings containing evidence or specific evidence references.
execution.status is run | not_run | not_applicable.
A not-run check needs execution.detail explaining why. Each plan ID has exactly
one record. Every catalog item has at least one plan entry, even if inapplicable.
Each performance path has separate P1-P8 plan entries. Additional paths may be
added to the plan, but this tool cannot prove plan timing or source completeness.

Exit: 0 = structurally complete; 2 = valid partial review; 1 = invalid record.
This validates accounting, not factual evidence, review quality, or code safety.
"""
import json
import sys


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and all(nonempty(x) for x in value)


def keyed(rows, label):
    require(isinstance(rows, list), f'{label} must be a list')
    result = {}
    for row in rows:
        require(isinstance(row, dict) and nonempty(row.get('id')), f'{label}: missing id')
        require(row['id'] not in result, f'{label}: duplicate id {row["id"]}')
        result[row['id']] = row
    return result


def validate(data):
    require(isinstance(data, dict), 'input must be an object')
    catalog = keyed(data.get('catalog'), 'catalog')
    plan = keyed(data.get('plan'), 'plan')
    records = keyed(data.get('records'), 'records')
    require(bool(catalog) and bool(plan), 'catalog and plan must not be empty')
    require(set(plan) == set(records), 'plan/records mismatch: missing or extra records')
    for item in catalog.values():
        require(nonempty(item.get('source')), 'catalog: missing source')
    paths = data.get('performance_paths')
    require(strings(paths) and len(paths) == len(set(paths)), 'invalid performance_paths')
    used, dimensions, performance = set(), set(), set()
    partial = False
    for check_id, check in plan.items():
        for field in ('item', 'scope', 'requirement', 'pass', 'intended_extent'):
            require(nonempty(check.get(field)), f'{check_id}: missing plan {field}')
        require(check['item'] in catalog, f'{check_id}: unknown catalog item')
        require(isinstance(check.get('applicable'), bool), f'{check_id}: missing applicability')
        dimension = tuple(check[k] for k in ('item', 'scope', 'requirement', 'pass'))
        require(dimension not in dimensions, f'{check_id}: duplicate plan dimensions')
        dimensions.add(dimension)
        used.add(check['item'])
        if check['item'] in {f'P{i}' for i in range(1, 9)}:
            require(not check['applicable'] or check['scope'] in paths,
                    f'{check_id}: applicable performance scope missing from performance_paths')
            performance.add((check['scope'], check['item']))
        record = records[check_id]
        status = record.get('status')
        require(status in ('inspected', 'partial', 'not inspected', 'not applicable'),
                f'{check_id}: invalid status')
        for field in ('examined_scope', 'unexamined_scope'):
            require(strings(record.get(field)), f'{check_id}: invalid {field}')
        for field in ('evidence', 'result', 'reason', 'stop_reason'):
            require(isinstance(record.get(field), str), f'{check_id}: missing {field}')
        require(nonempty(record['result']) and nonempty(record['stop_reason']),
                f'{check_id}: missing result or stopping boundary')
        execution = record.get('execution')
        require(isinstance(execution, dict) and
                execution.get('status') in ('run', 'not_run', 'not_applicable') and
                nonempty(execution.get('detail')), f'{check_id}: missing execution status/detail')
        require(check['applicable'] == (status != 'not applicable'),
                f'{check_id}: applicability/status conflict')
        if status in ('inspected', 'partial'):
            require(bool(record['examined_scope']) and nonempty(record['evidence']),
                    f'{check_id}: inspection needs extent and evidence')
        if status == 'inspected':
            if check['item'] in {f'P{i}' for i in range(1, 9)}:
                cost = record.get('cost_evidence')
                require(isinstance(cost, dict) and all(nonempty(cost.get(field)) for field in
                        ('base', 'target', 'workload', 'workload_source', 'safety_reuse')),
                        f'{check_id}: missing per-path cost/workload evidence')
            require(not record['unexamined_scope'], f'{check_id}: inspected with remaining scope')
        else:
            require(nonempty(record['reason']), f'{check_id}: missing reason')
        if status in ('partial', 'not inspected'):
            require(bool(record['unexamined_scope']), f'{check_id}: missing remaining scope')
            partial = True
        if status == 'not inspected':
            require(not record['examined_scope'], f'{check_id}: use partial for mixed inspection')
        if status == 'not applicable':
            require(nonempty(record['evidence']), f'{check_id}: missing exclusion evidence')
    require(used == set(catalog), 'catalog items missing from plan')
    for path in paths:
        for number in range(1, 9):
            require((path, f'P{number}') in performance, f'{path}: missing P{number}')
    expected = 'partial' if partial else 'complete'
    require(data.get('review_status') == expected, f'review_status must be {expected}')
    return expected


def main():
    try:
        status = validate(json.load(sys.stdin))
    except (ValueError, TypeError) as exc:
        print(f'INVALID: {exc}', file=sys.stderr)
        return 1
    print(f'Coverage accounting valid: {status}. Evidence quality and catalog completeness require coordinator verification.')
    return 2 if status == 'partial' else 0


if __name__ == '__main__':
    sys.exit(main())
