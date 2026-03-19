# -*- coding: utf-8 -*-
"""
综合测试运行器 - 执行所有测试并生成报告
"""
from datetime import datetime
from e2e_test import run_e2e_tests
from functional_test import run_functional_tests
from security_test import run_security_tests

def run_all_tests():
    print("=" * 50)
    print("  综合测试报告")
    print("  时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)

    print("\n>>> 功能测试")
    func_results = run_functional_tests()

    print("\n>>> 安全测试")
    sec_results = run_security_tests()

    print("\n>>> E2E测试")
    e2e_results = run_e2e_tests()

    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    run_all_tests()
