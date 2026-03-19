#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime

report_dir = Path("../reports")
all_tests = sorted(report_dir.glob('all_tests_*.json'))
if not all_tests:
    print("未找到测试报告")
    exit(1)

with open(all_tests[-1], 'r', encoding='utf-8') as f:
    all_data = json.load(f)

e2e_tests = sorted(report_dir.glob('e2e_tests_*.json'))
e2e_data = {'summary': {'total': 0, 'passed': 0}, 'results': []}
if e2e_tests:
    with open(e2e_tests[-1], 'r', encoding='utf-8') as f:
        e2e_data = json.load(f)

ui_tests = sorted(report_dir.glob('ui_tests_*.json'))
ui_data = {'summary': {'total': 0, 'passed': 0}, 'results': []}
if ui_tests:
    with open(ui_tests[-1], 'r', encoding='utf-8') as f:
        ui_data = json.load(f)

api_p = all_data.get('api', {}).get('passed', 0)
api_t = all_data.get('api', {}).get('total', 0)
bound_p = all_data.get('boundary', {}).get('passed', 0)
bound_t = all_data.get('boundary', {}).get('total', 0)
exc_p = all_data.get('exception', {}).get('passed', 0)
exc_t = all_data.get('exception', {}).get('total', 0)
perf_p = all_data.get('performance', {}).get('passed', 0)
perf_t = all_data.get('performance', {}).get('total', 0)
sec_p = all_data.get('security', {}).get('passed', 0)
sec_t = all_data.get('security', {}).get('total', 0)

total_passed = api_p + bound_p + exc_p + perf_p + sec_p + e2e_data['summary']['passed'] + ui_data['summary']['passed']
total_count = api_t + bound_t + exc_t + perf_t + sec_t + e2e_data['summary']['total'] + ui_data['summary']['total']

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>测试报告</title>
<style>
body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}}
.container{{max-width:1200px;margin:0 auto;background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}}
h1{{color:#333;border-bottom:3px solid #4CAF50;padding-bottom:10px}}
.summary{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:20px 0}}
.card{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:20px;border-radius:8px;text-align:center}}
.card h3{{margin:0;font-size:14px;opacity:0.9}}
.card .number{{font-size:36px;font-weight:bold;margin:10px 0}}
table{{width:100%;border-collapse:collapse;margin:10px 0}}
th,td{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}
th{{background:#4CAF50;color:#fff}}
tr:hover{{background:#f5f5f5}}
.pass{{color:#4CAF50;font-weight:bold}}
.fail{{color:#f44336;font-weight:bold}}
</style>
</head>
<body>
<div class="container">
<h1>学员管理系统 - 测试报告</h1>
<p>生成时间: {timestamp}</p>
<div class="summary">
<div class="card"><h3>总用例数</h3><div class="number">{total_count}</div></div>
<div class="card"><h3>通过数</h3><div class="number">{total_passed}</div></div>
<div class="card"><h3>通过率</h3><div class="number">{total_passed/total_count*100 if total_count>0 else 0:.1f}%</div></div>
</div>
<h2>测试概览</h2>
<table>
<tr><th>测试类型</th><th>通过/总数</th><th>通过率</th></tr>
<tr><td>API测试</td><td>{api_p}/{api_t}</td><td>{api_p/api_t*100 if api_t>0 else 0:.1f}%</td></tr>
<tr><td>边界测试</td><td>{bound_p}/{bound_t}</td><td>{bound_p/bound_t*100 if bound_t>0 else 0:.1f}%</td></tr>
<tr><td>异常测试</td><td>{exc_p}/{exc_t}</td><td>{exc_p/exc_t*100 if exc_t>0 else 0:.1f}%</td></tr>
<tr><td>性能测试</td><td>{perf_p}/{perf_t}</td><td>{perf_p/perf_t*100 if perf_t>0 else 0:.1f}%</td></tr>
<tr><td>安全测试</td><td>{sec_p}/{sec_t}</td><td>{sec_p/sec_t*100 if sec_t>0 else 0:.1f}%</td></tr>
<tr><td>E2E测试</td><td>{e2e_data['summary']['passed']}/{e2e_data['summary']['total']}</td><td>{e2e_data['summary']['passed']/e2e_data['summary']['total']*100 if e2e_data['summary']['total']>0 else 0:.1f}%</td></tr>
<tr><td>UI测试</td><td>{ui_data['summary']['passed']}/{ui_data['summary']['total']}</td><td>{ui_data['summary']['passed']/ui_data['summary']['total']*100 if ui_data['summary']['total']>0 else 0:.1f}%</td></tr>
</table>
</div>
</body>
</html>
"""

output_file = report_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML报告已生成: {output_file}")
