# Win-RPA - Windows 桌面 RPA 自动化平台

<div align="center">

**基于 Robot Framework 和 PyQt5 的智能自动化办公平台**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Robot Framework](https://img.shields.io/badge/Robot%20Framework-6.1.1-green.svg)](https://robotframework.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15.10-orange.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

## 📖 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [流程配置](#流程配置)
- [自定义关键字](#自定义关键字)
- [常见问题](#常见问题)
- [Bug 修复记录](#bug-修复记录)
- [开发文档](#开发文档)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 🎯 项目简介

**Win-RPA** 是一款专为 Windows 平台设计的桌面 RPA（机器人流程自动化）应用程序。它使用 Robot Framework 作为自动化核心，结合 PyQt5 提供友好的图形界面，帮助用户轻松实现网站自动化操作、数据提取和业务流程自动化。

### 核心优势

- **🖱️ 可视化操作** - 无需编写代码，通过 GUI 界面配置自动化流程
- **🤖 强大的自动化能力** - 基于 Robot Framework 和 Selenium 实现浏览器自动化
- **🔧 灵活配置** - 支持 JSON/YAML 格式的流程配置文件
- **📊 实时监控** - 提供流程执行状态实时反馈和详细日志
- **⏰ 定时任务** - 支持 Cron、Interval、Date 多种调度方式
- **🌐 跨平台兼容** - 虽然专为 Windows 设计，但核心代码支持跨平台运行
- **🔌 可扩展** - 易于添加自定义关键字和功能模块

### 适用场景

- 智能体网站自动化操作
- 数据采集和提取
- 重复性业务流程自动化
- 网站功能测试
- 表单自动填写
- 报告自动生成

---

## ✨ 功能特性

### 1. 流程管理
- ✅ 创建、编辑、删除流程配置
- ✅ 导入/导出流程配置文件
- ✅ 流程克隆（快速复制现有流程）
- ✅ 流程列表管理

### 2. 流程执行
- ✅ 一键执行自动化流程
- ✅ 实时执行状态显示
- ✅ 详细的执行日志
- ✅ 执行统计信息（总数、通过、失败）
- ✅ 生成 HTML 格式执行报告

### 3. 流程调度
- ✅ **Cron 表达式调度** - 灵活的定时任务（如：每天 9:00 执行）
- ✅ **间隔调度** - 固定时间间隔执行（如：每 30 分钟执行一次）
- ✅ **单次调度** - 指定日期时间执行
- ✅ 任务启动/暂停/删除
- ✅ 任务执行历史记录

### 4. 浏览器操作
- ✅ 支持 Chrome、Firefox、Edge 等主流浏览器
- ✅ 打开网页
- ✅ 元素点击
- ✅ 文本输入
- ✅ 数据提取（文本、属性）
- ✅ 下拉框选择
- ✅ 元素等待和滚动
- ✅ JavaScript 执行
- ✅ 截图保存

### 5. 日志查看
- ✅ 实时日志显示
- ✅ 日志级别过滤（INFO、WARNING、ERROR）
- ✅ 日志文件查看器
- ✅ HTML 报告查看

---

## 🛠️ 技术栈

### 核心框架
- **[Python](https://www.python.org/)** `3.8+` - 编程语言
- **[Robot Framework](https://robotframework.org/)** `6.1.1` - 自动化测试框架
- **[PyQt5](https://www.riverbankcomputing.com/software/pyqt/)** `5.15.10` - GUI 框架

### 自动化库
- **[Selenium](https://www.selenium.dev/)** `4.16.0` - 浏览器自动化
- **[SeleniumLibrary](https://github.com/robotframework/SeleniumLibrary)** `6.2.0` - Robot Framework 的 Selenium 库
- **[webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)** `4.0.1` - WebDriver 自动管理

### 任务调度
- **[APScheduler](https://github.com/agronholm/apscheduler)** `3.10.4` - 高级任务调度器

### 数据处理
- **[PyYAML](https://pyyaml.org/)** `6.0.1` - YAML 解析
- **[SQLAlchemy](https://www.sqlalchemy.org/)** `2.0.23` - 数据库 ORM

### 工具库
- **[colorlog](https://github.com/borntyping/python-colorlog)** `6.8.0` - 彩色日志输出
- **[python-dateutil](https://github.com/dateutil/dateutil)** `2.8.2` - 日期时间处理

---

## 📁 项目结构

```
Win-Rpa/
│
├── main.py                          # 主程序入口
├── requirements.txt                 # 项目依赖
├── README.md                        # 项目文档
│
├── gui/                             # GUI 界面模块
│   ├── __init__.py
│   ├── main_window.py              # 主窗口
│   ├── flow_editor.py              # 流程编辑器
│   ├── executor.py                 # 流程执行器界面
│   └── log_viewer.py               # 日志查看器
│
├── service/                         # 业务逻辑服务层
│   ├── __init__.py
│   └── flow/                       # 流程相关服务
│       ├── __init__.py
│       ├── FlowParserService.py    # 流程解析服务
│       ├── FlowExecutorService.py  # 流程执行服务
│       ├── FlowManagementService.py # 流程管理服务
│       └── FlowSchedulerService.py # 流程调度服务
│
├── resources/                       # 资源文件
│   └── keywords.robot              # 自定义关键字库（中文）
│
├── flows/                          # 流程配置文件
│   ├── example_flow.json           # 示例流程
│   ├── 1.json
│   └── 2.json
│
├── logs/                           # 执行日志和报告
│   ├── flow_*.robot                # 生成的 Robot 测试文件
│   ├── output_*.xml                # 执行结果 XML
│   ├── output_*.html               # 执行报告 HTML
│   └── output_*_debug.txt          # 调试日志
│
└── docs/                           # 文档目录
    ├── BUG_FIX_KEYWORD_PATH.md     # Bug 修复：关键字路径问题
    ├── BUG_FIX_STATISTICS.md       # Bug 修复：统计信息获取
    ├── REFACTOR_SUMMARY.md         # 重构总结
    ├── COMPATIBILITY_FIX.md        # 兼容性修复
    ├── FILE_CLEANUP_SUMMARY.md     # 文件清理总结
    └── CLEANUP_COMPLETE.md         # 清理完成文档
```

---

## 🚀 快速开始

### 1. 环境要求

- **操作系统**: Windows 10/11（推荐）
- **Python**: 3.8 或更高版本
- **浏览器**: Chrome 浏览器（推荐）

### 2. 安装依赖

```bash
# 克隆或下载项目
cd Win-Rpa

# 安装 Python 依赖
pip install -r requirements.txt
```

### 3. 运行应用

```bash
# 启动 GUI 应用
python main.py
```

### 4. 第一个自动化流程

1. 启动应用后，点击 **"流程管理"** 标签
2. 点击 **"加载流程"** 按钮
3. 选择 `flows/example_flow.json` 示例流程
4. 切换到 **"执行器"** 标签
5. 点击 **"执行流程"** 按钮
6. 查看执行状态和日志

---

## 📘 使用指南

### 流程编辑器

1. **创建新流程**
   - 点击 "新建流程" 按钮
   - 填写流程名称和描述
   - 选择浏览器类型

2. **添加步骤**
   - 选择操作类型（点击、输入、等待等）
   - 填写元素定位器（支持 id、xpath、css selector）
   - 配置步骤参数

3. **保存流程**
   - 点击 "保存流程" 按钮
   - 选择保存位置（JSON 格式）

### 流程执行器

1. **加载流程**
   - 点击 "加载流程" 从文件加载
   - 或通过流程管理器选择

2. **执行流程**
   - 点击 "执行流程" 开始自动化
   - 实时查看执行状态
   - 查看统计信息（通过/失败用例数）

3. **查看报告**
   - 点击 "查看日志" 打开 HTML 报告
   - 查看详细的执行步骤和截图

### 流程调度

1. **创建定时任务**
   - 选择流程
   - 选择调度类型：
     - **Cron**: 输入 Cron 表达式（如 `0 9 * * *` 表示每天 9:00）
     - **Interval**: 设置间隔时间（如每 30 分钟）
     - **Date**: 选择具体执行日期时间

2. **管理任务**
   - 查看任务列表
   - 启动/暂停任务
   - 删除任务
   - 查看执行历史

---

## 📝 流程配置

### JSON 配置格式

```json
{
  "flow_name": "流程名称",
  "description": "流程描述",
  "browser": "chrome",
  "steps": [
    {
      "action": "open_browser",
      "url": "http://example.com"
    },
    {
      "action": "input_text",
      "locator": "id=username",
      "text": "admin"
    },
    {
      "action": "click",
      "locator": "xpath=//button[@type='submit']"
    },
    {
      "action": "get_text",
      "locator": "xpath=//div[@class='result']"
    },
    {
      "action": "screenshot",
      "filename": "result"
    },
    {
      "action": "close_browser"
    }
  ]
}
```

### 支持的操作类型

| 操作 | 说明 | 参数 |
|------|------|------|
| `open_browser` | 打开浏览器 | `url`, `browser` |
| `close_browser` | 关闭浏览器 | 无 |
| `click` | 点击元素 | `locator` |
| `input_text` | 输入文本 | `locator`, `text` |
| `get_text` | 获取文本 | `locator` |
| `get_attribute` | 获取属性 | `locator`, `attribute` |
| `wait` | 等待指定秒数 | `seconds` |
| `wait_until_element_visible` | 等待元素可见 | `locator`, `timeout` |
| `screenshot` | 截图 | `filename` |
| `scroll_to_element` | 滚动到元素 | `locator` |
| `select_from_list` | 下拉框选择 | `locator`, `value` |
| `execute_javascript` | 执行 JS | `script` |

### 元素定位器格式

- `id=element_id` - 通过 ID 定位
- `name=element_name` - 通过 name 属性
- `xpath=//div[@class='content']` - 通过 XPath
- `css=.class-name` - 通过 CSS 选择器
- `link=链接文本` - 通过链接文本

---

## 🔧 自定义关键字

项目提供了丰富的中文自定义关键字，定义在 `resources/keywords.robot` 文件中：

### 常用关键字

- **打开智能体网站** - 打开指定 URL 并初始化浏览器
- **安全点击元素** - 等待元素可见后点击
- **智能输入文本** - 清空输入框后输入文本
- **提取元素文本** - 获取元素的文本内容
- **提取元素属性值** - 获取元素的指定属性
- **截图保存** - 保存当前页面截图
- **滚动到元素位置** - 滚动页面使元素可见
- **从下拉框选择** - 从下拉列表选择选项
- **执行JavaScript并获取结果** - 执行 JS 代码并返回结果

### 添加自定义关键字

编辑 `resources/keywords.robot` 文件：

```robot
*** Keywords ***
我的自定义关键字
    [Arguments]    ${arg1}    ${arg2}
    [Documentation]    关键字说明
    Log    执行自定义操作: ${arg1}, ${arg2}
    # 添加你的逻辑
```

---

## ❓ 常见问题

### 1. 无法找到 ChromeDriver

**解决方案**: 项目使用 webdriver-manager 自动管理驱动。首次运行时会自动下载。如果网络问题导致下载失败，可以：
```bash
# 手动安装 ChromeDriver
pip install webdriver-manager --upgrade
```

### 2. 中文关键字无法识别

**原因**: 文件编码问题或路径问题

**解决方案**:
- 确保 `resources/keywords.robot` 文件为 UTF-8 编码
- 检查日志中的资源路径是否正确（应使用正斜杠 `/`）

### 3. 执行失败返回码 1

**排查步骤**:
1. 查看日志文件 `logs/output_*_debug.txt`
2. 检查网站 URL 是否可访问
3. 验证元素定位器是否正确
4. 确认浏览器驱动版本匹配

### 4. GUI 界面显示异常

**解决方案**:
```bash
# 重新安装 PyQt5
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip
pip install PyQt5==5.15.10
```

### 5. 任务调度不执行

**检查项**:
- 确认任务已启动（状态为 Running）
- 验证 Cron 表达式格式正确
- 查看调度器日志

---

## 🐛 Bug 修复记录

### ✅ 已修复的问题

#### 1. Windows 路径格式导致关键字加载失败
- **问题**: `No keyword with name '打开智能体网站' found`
- **原因**: Robot Framework 在 Windows 上无法正确解析反斜杠路径
- **修复**: 将资源文件路径从 `D:\path\file.robot` 转换为 `D:/path/file.robot`
- **位置**: `service/flow/FlowExecutorService.py:101`
- **详细文档**: [BUG_FIX_KEYWORD_PATH.md](BUG_FIX_KEYWORD_PATH.md)

#### 2. Robot Framework 统计信息 API 兼容性
- **问题**: `'int' object has no attribute 'total'`
- **原因**: Robot Framework 6.x 版本 API 结构变更
- **修复**: 添加版本检测和兼容性处理，支持 3.x ~ 6.x 所有版本
- **位置**: `service/flow/FlowExecutorService.py:213-231`
- **详细文档**: [BUG_FIX_STATISTICS.md](BUG_FIX_STATISTICS.md)

#### 3. 服务层重构后的向后兼容性
- **问题**: `'FlowParserService' object has no attribute 'load_from_dict'`
- **原因**: 方法重命名后缺少向后兼容
- **修复**: 添加 `load_from_dict` 和 `load_from_file` 别名方法
- **位置**: `service/flow/FlowParserService.py`
- **详细文档**: [COMPATIBILITY_FIX.md](COMPATIBILITY_FIX.md)

---

## 📚 开发文档

### 架构设计

项目采用分层架构：

```
Presentation Layer (GUI)
        ↓
Service Layer (Business Logic)
        ↓
Framework Layer (Robot Framework)
        ↓
Infrastructure Layer (Selenium/WebDriver)
```

### 核心服务说明

#### FlowParserService
- **职责**: 解析和验证流程配置
- **主要方法**:
  - `parse_from_file(file_path)` - 从文件解析
  - `parse_from_dict(flow_dict)` - 从字典解析
  - `validate_flow(flow_data)` - 验证流程配置
  - `save_to_file(flow_data, file_path)` - 保存流程

#### FlowExecutorService
- **职责**: 执行自动化流程
- **主要方法**:
  - `generate_robot_file(flow_data)` - 生成 Robot 测试文件
  - `execute(flow_data)` - 执行流程
  - `execute_from_file(config_file)` - 从文件加载并执行

#### FlowManagementService
- **职责**: 管理流程配置文件
- **主要方法**:
  - `create_flow(flow_data, filename)` - 创建流程
  - `load_flow(filename)` - 加载流程
  - `delete_flow(filename)` - 删除流程
  - `list_flows()` - 列出所有流程
  - `duplicate_flow(filename, new_name)` - 复制流程

#### FlowSchedulerService
- **职责**: 调度流程定时执行
- **主要方法**:
  - `add_cron_job(flow_data, cron_expr)` - 添加 Cron 任务
  - `add_interval_job(flow_data, minutes)` - 添加间隔任务
  - `add_date_job(flow_data, run_date)` - 添加单次任务
  - `start()` / `stop()` - 启动/停止调度器

### 测试

```bash
# 运行服务层测试
python test_refactor.py

# 运行清理后的测试
python test_after_cleanup.py
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码风格
- 添加必要的注释和文档字符串
- 编写单元测试
- 更新相关文档

### 报告 Bug

请在 Issues 中提供以下信息：
- 操作系统和版本
- Python 版本
- 详细的错误信息和堆栈跟踪
- 复现步骤
- 预期行为和实际行为

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [Robot Framework](https://robotframework.org/) - 优秀的自动化测试框架
- [Selenium](https://www.selenium.dev/) - 强大的浏览器自动化工具
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 成熟的 GUI 框架

---

## 📧 联系方式

- **项目主页**: [Win-RPA GitHub](https://github.com/yourusername/Win-Rpa)
- **问题反馈**: [GitHub Issues](https://github.com/yourusername/Win-Rpa/issues)

---

<div align="center">

**Made with ❤️ by RPA Solutions Team**

**[⬆ 回到顶部](#win-rpa---windows-桌面-rpa-自动化平台)**

</div>
