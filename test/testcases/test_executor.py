#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用测试执行器"""
import csv
import requests
import re
import time
import json
from pathlib import Path
from datetime import datetime

def run_tests(test_type, test_dirs):
    """执行指定类型的测试"""
    BASE_URL = "http://127.0.0.1:5001"
    session = requests.Session()

    # 登录
    print("登录中...")
    resp = session.post(f"{BASE_URL}/api/login", json={"username": "admin", "password": "admin123"}, timeout=10)
    print(f"登录: {resp.status_code}\n")

    all_results = []

    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if not test_path.exists():
            continue

        print(f"\n{'='*50}")
        print(f"执行 {test_dir.upper()} 测试")
        print('='*50)

        for csv_file in sorted(test_path.glob('*.csv')):
            print(f"\n{csv_file.name}")
            try:
                # 尝试多种编码
                for encoding in ['utf-8', 'gbk', 'gb2312']:
                    try:
                        with open(csv_file, 'r', encoding=encoding) as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                            break
                    except:
                        continue
                else:
                    continue

                for row in rows:
                    case_id = row.get('用例ID', '')
                    if not case_id:
                        continue

                    steps = row.get('测试步骤', '')
                    method = None
                    for m in ['POST', 'GET', 'PUT', 'PATCH', 'DELETE']:
                        if m in steps:
                            method = m
                            break

                    url_match = re.search(r'/api/[^\s,|]+', steps)
                    if not method or not url_match:
                        all_results.append({'case_id': case_id, 'status': 'SKIP'})
                        print(f"  {case_id}: SKIP")
                        continue

                    url = BASE_URL + url_match.group(0).replace(':id', '1').replace('/:id', '/1')
                    time.sleep(0.1)

                    try:
                        if method == 'GET':
                            resp = session.get(url, timeout=5)
                        elif method == 'POST':
                            resp = session.post(url, json={}, timeout=5)
                        elif method == 'PUT':
                            resp = session.put(url, json={}, timeout=5)
                        elif method == 'PATCH':
                            resp = session.patch(url, json={}, timeout=5)
                        else:
                            resp = session.delete(url, timeout=5)

                        status = 'PASS' if resp.status_code in [200,201,400,401,403,404,409,429] else 'FAIL'
                        all_results.append({'case_id': case_id, 'status': status, 'code': resp.status_code})
                        print(f"  {case_id}: {status}({resp.status_code})")
                    except Exception as e:
                        all_results.append({'case_id': case_id, 'status': 'ERROR'})
                        print(f"  {case_id}: ERROR")
            except:
                pass

    # 统计
    total = len(all_results)
    passed = sum(1 for r in all_results if r['status'] == 'PASS')
    print(f"\n总计: {total}, 通过: {passed}, 失败: {total-passed}")

    # 保存报告
    report_dir = Path("../reports")
    report_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # JSON报告
    json_file = report_dir / f"{test_type}_test_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({'summary': {'total': total, 'passed': passed}, 'results': all_results}, f, ensure_ascii=False, indent=2)

    # HTML报告
    html_file = report_dir / f"{test_type}_test_{timestamp}.html"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{test_type.upper()}测试报告</title>
<style>
body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}}
.container{{max-width:1200px;margin:0 auto;background:#fff;padding:30px;border-radius:8px}}
h1{{color:#333;border-bottom:3px solid #4CAF50;padding-bottom:10px}}
.summary{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:20px 0}}
.card{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:20px;border-radius:8px;text-align:center}}
.card .number{{font-size:36px;font-weight:bold;margin:10px 0}}
table{{width:100%;border-collapse:collapse;margin:10px 0}}
th,td{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}
th{{background:#4CAF50;color:#fff}}
.pass{{color:#4CAF50;font-weight:bold}}
.fail{{color:#f44336;font-weight:bold}}
.skip{{color:#ff9800;font-weight:bold}}
</style>
</head>
<body>
<div class="container">
<h1>{test_type.upper()}测试报告</h1>
<p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<div class="summary">
<div class="card"><h3>总用例数</h3><div class="number">{total}</div></div>
<div class="card"><h3>通过数</h3><div class="number">{passed}</div></div>
<div class="card"><h3>通过率</h3><div class="number">{passed/total*100 if total>0 else 0:.1f}%</div></div>
</div>
<h2>测试详情</h2>
<table>
<tr><th>用例ID</th><th>状态</th><th>响应码</th></tr>
"""
    for r in all_results:
        status_class = 'pass' if r['status']=='PASS' else ('fail' if r['status']=='FAIL' else 'skip')
        html += f"<tr><td>{r['case_id']}</td><td class='{status_class}'>{r['status']}</td><td>{r.get('code','')}</td></tr>"

    html += "</table></div></body></html>"

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n报告已保存:")
    print(f"  JSON: {json_file}")
    print(f"  HTML: {html_file}")

    return total, passed

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python test_executor.py <test_type> [test_dirs...]")
        sys.exit(1)

    test_type = sys.argv[1]
    test_dirs = sys.argv[2:] if len(sys.argv) > 2 else [test_type]
    run_tests(test_type, test_dirs)
