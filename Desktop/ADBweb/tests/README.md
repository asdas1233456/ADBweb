# ADBweb 测试套件

## 📋 概述

全面的自动化测试套件，覆盖 ADBweb 平台的所有功能模块。

- **测试总数**: 107 个
- **测试框架**: Pytest 7.4.0
- **报告工具**: Allure 2.37.0
- **通过率**: 100%

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 运行所有测试
python -m pytest test_all_features.py -v

# 运行测试并生成 Allure 报告
run_tests_with_allure.bat
```

### 3. 查看报告

```bash
# 生成并打开 Allure 报告
allure generate allure-results -o allure-report --clean
allure open allure-report

# 或使用批处理脚本
generate_allure_report.bat
```

## 📊 测试覆盖

### 功能模块 (26个)

1. 健康检查和基础功能 (3)
2. 设备管理 (5)
3. 脚本管理 (5)
4. 模板市场 (2)
5. 定时任务 (2)
6. 设备健康度 (6)
7. 失败分析 (3)
8. 仪表盘 (1)
9. 数据一致性 (4)
10. 性能测试 (2)
11. 集成测试 (2)
12. 边界条件测试 (7)
13. 并发测试 (2)
14. 数据完整性 (2)
15. 复杂业务场景 (3)
16. 搜索和过滤 (5)
17. 数据导出和报告 (2)
18. 脚本步骤 (7)
19. 设备操作 (5)
20. 定时任务详细 (6)
21. 模板市场详细 (6)
22. 健康度监控详细 (5)
23. 脚本分类 (7)
24. 设备状态统计 (5)
25. 执行历史 (5)
26. 数据库完整性高级 (5)

## 📁 文件说明

```
tests/
├── test_all_features.py          # 主测试文件 (107个测试用例)
├── conftest.py                   # Pytest 配置和 Allure 钩子
├── pytest.ini                    # Pytest 配置文件
├── requirements.txt              # Python 依赖
├── run_tests_with_allure.bat     # 一键运行测试并生成报告
├── generate_allure_report.bat    # 生成 Allure 报告
├── allure-results/               # 测试结果目录
└── allure-report/                # HTML 报告目录
```

## 🎯 Allure 报告特性

- 📊 交互式图表和统计
- 📦 按功能模块分类
- 🎯 严重程度分布
- ⏱️ 执行时间线
- 📎 详细的测试步骤和附件
- 📈 历史趋势分析

## 🔧 配置说明

### pytest.ini

```ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --alluredir=allure-results
log_cli = true
log_cli_level = INFO
```

### conftest.py

包含 Allure 环境信息和测试钩子：
- 自动附加失败详情
- 记录执行时长
- 环境信息配置

## 📈 测试结果

最近一次测试运行：

```
测试总数: 107
✅ 通过: 107 (100%)
❌ 失败: 0 (0%)
⏱️ 执行时间: 12.68 秒
```

## 🛠️ 常用命令

```bash
# 运行特定测试类
pytest test_all_features.py::TestDeviceManagement -v

# 运行特定测试方法
pytest test_all_features.py::TestDeviceManagement::test_get_devices_list -v

# 运行并显示详细输出
pytest test_all_features.py -v -s

# 运行并生成 Allure 结果
pytest test_all_features.py --alluredir=allure-results

# 生成 Allure HTML 报告
allure generate allure-results -o allure-report --clean

# 打开 Allure 报告
allure open allure-report
```

## 📚 参考资源

- [Pytest 文档](https://docs.pytest.org/)
- [Allure 文档](https://docs.qameta.io/allure/)
- [Allure Pytest 插件](https://docs.qameta.io/allure/#_pytest)

## 🎉 总结

测试套件已完全配置并可以使用。运行 `run_tests_with_allure.bat` 即可一键运行测试并查看美观的报告！
