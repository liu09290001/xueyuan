#!/usr/bin/env python3
import json, time, csv
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://127.0.0.1:5001"
results = []

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

with open('ui/ui_tests.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    cases = list(reader)

# 先执行登录测试，增加重试机制
for row in cases:
    case_id = row.get('用例ID', '')
    if case_id == 'TC-UI-004':
        print(f"执行 {case_id}...")
        try:
            time.sleep(3)  # 等待避免限流
            driver.get(f"{BASE_URL}/login")
            time.sleep(1)
            driver.find_element(By.ID, "username").send_keys("admin")
            driver.find_element(By.ID, "password").send_keys("admin123")
            driver.find_element(By.CLASS_NAME, "btn-login").click()
            time.sleep(3)
            status = 'PASS' if driver.current_url == f"{BASE_URL}/" else 'FAIL'
            results.append({'case_id': case_id, 'status': status})
        except Exception as e:
            results.append({'case_id': case_id, 'status': 'ERROR'})
        break

# 执行其他测试
for row in cases:
    case_id = row.get('用例ID', '')
    if not case_id or case_id == 'TC-UI-004':
        continue

    print(f"执行 {case_id}...")
    try:
        if case_id == 'TC-UI-003':
            driver.get(f"{BASE_URL}/")
            time.sleep(1)
            cards = driver.find_elements(By.CLASS_NAME, "card")
            status = 'PASS' if len(cards) > 0 else 'FAIL'
        elif case_id in ['TC-UI-001', 'TC-UI-002']:
            driver.get(f"{BASE_URL}/statistics")
            time.sleep(2)
            charts = driver.find_elements(By.TAG_NAME, "canvas")
            status = 'PASS' if len(charts) > 0 else 'FAIL'
        else:
            status = 'SKIP'
        results.append({'case_id': case_id, 'status': status})
    except Exception as e:
        results.append({'case_id': case_id, 'status': 'ERROR'})

driver.quit()

total = len(results)
passed = sum(1 for r in results if r['status'] == 'PASS')
print(f"\n总计: {total}, 通过: {passed}")

report_dir = Path("../reports")
report_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

with open(report_dir / f"ui_test_{timestamp}.json", 'w', encoding='utf-8') as f:
    json.dump({'summary': {'total': total, 'passed': passed}, 'results': results}, f, ensure_ascii=False, indent=2)

html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>UI测试报告</title>
<style>body{{font-family:Arial;margin:20px;background:#f5f5f5}}.container{{max-width:1200px;margin:0 auto;background:#fff;padding:30px}}h1{{color:#333;border-bottom:3px solid #4CAF50}}table{{width:100%;border-collapse:collapse}}th,td{{padding:12px;border-bottom:1px solid #ddd}}th{{background:#4CAF50;color:#fff}}.pass{{color:#4CAF50}}.fail{{color:#f44336}}</style>
</head><body><div class="container"><h1>UI测试报告</h1><p>总计: {total}, 通过: {passed}, 通过率: {passed/total*100 if total>0 else 0:.1f}%</p>
<table><tr><th>用例ID</th><th>状态</th></tr>"""
for r in results:
    html += f"<tr><td>{r['case_id']}</td><td class='{'pass' if r['status']=='PASS' else 'fail'}'>{r['status']}</td></tr>"
html += "</table></div></body></html>"

with open(report_dir / f"ui_test_{timestamp}.html", 'w', encoding='utf-8') as f:
    f.write(html)

print(f"报告已保存: ui_test_{timestamp}.json/html")
