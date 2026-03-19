#!/usr/bin/env python3
import subprocess, json
from pathlib import Path
from datetime import datetime

scripts = [
    ('run_api_tests.py', 'API测试'),
    ('run_boundary_tests.py', '边界测试'),
    ('run_exception_tests.py', '异常测试'),
    ('run_performance_tests.py', '性能测试'),
    ('run_security_tests.py', '安全测试'),
    ('run_smoke_tests.py', '冒烟测试'),
    ('run_e2e_tests.py', 'E2E测试'),
    ('run_ui_tests.py', 'UI测试'),
]

all_results = []
print("开始执行完整测试套件\n")

for script, desc in scripts:
    print(f"\n{'='*60}")
    print(f"执行: {desc}")
    print('='*60)
    try:
        result = subprocess.run(['python', script], capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"执行失败: {e}")

# 汇总所有报告
report_dir = Path("../reports")
summary = {}
for test_type in ['api', 'boundary', 'exception', 'performance', 'security', 'smoke', 'e2e', 'ui']:
    files = sorted(report_dir.glob(f'{test_type}_test_*.json'))
    if files:
        with open(files[-1], 'r', encoding='utf-8') as f:
            data = json.load(f)
            summary[test_type] = data['summary']
            all_results.extend(data['results'])

total = sum(s['total'] for s in summary.values())
passed = sum(s['passed'] for s in summary.values())

print(f"\n{'='*60}")
print("测试汇总")
print('='*60)
for k, v in summary.items():
    print(f"{k.upper()}: {v['passed']}/{v['total']}")
print(f"总计: {passed}/{total}")

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# 保存汇总JSON
with open(report_dir / f"all_tests_{timestamp}.json", 'w', encoding='utf-8') as f:
    json.dump({'summary': summary, 'total': total, 'passed': passed, 'results': all_results}, f, ensure_ascii=False, indent=2)

# 生成汇总HTML
html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>完整测试报告</title>
<style>body{{font-family:Arial;margin:20px;background:#f5f5f5}}.container{{max-width:1200px;margin:0 auto;background:#fff;padding:30px}}h1{{color:#333;border-bottom:3px solid #4CAF50}}table{{width:100%;border-collapse:collapse}}th,td{{padding:12px;border-bottom:1px solid #ddd}}th{{background:#4CAF50;color:#fff}}.pass{{color:#4CAF50}}.fail{{color:#f44336}}</style>
</head><body><div class="container"><h1>完整测试报告</h1><p>总计: {total}, 通过: {passed}, 通过率: {passed/total*100 if total>0 else 0:.1f}%</p>
<h2>测试概览</h2><table><tr><th>测试类型</th><th>通过/总数</th><th>通过率</th></tr>"""
for k, v in summary.items():
    html += f"<tr><td>{k.upper()}</td><td>{v['passed']}/{v['total']}</td><td>{v['passed']/v['total']*100 if v['total']>0 else 0:.1f}%</td></tr>"
html += f"""</table><h2>详细结果</h2><table><tr><th>用例ID</th><th>状态</th></tr>"""
for r in all_results[:100]:
    html += f"<tr><td>{r['case_id']}</td><td class='{'pass' if r['status']=='PASS' else 'fail'}'>{r['status']}</td></tr>"
html += "</table></div></body></html>"

with open(report_dir / f"all_tests_{timestamp}.html", 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n报告已保存: all_tests_{timestamp}.json/html")
