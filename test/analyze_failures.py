import json
from collections import defaultdict

with open('reports/all_tests_20260318_125450.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

failed = [r for r in data['results'] if r['status'] != 'PASS']
print(f'失败用例: {len(failed)}个\n')

by_type = defaultdict(list)
for r in failed:
    case_type = r['case_id'].split('-')[1]
    by_type[case_type].append(r)

for t, cases in sorted(by_type.items()):
    print(f'\n{t}测试 - 失败{len(cases)}个:')
    for c in cases:
        print(f"  {c['case_id']}: {c['status']} (响应码: {c.get('code', 'N/A')})")
