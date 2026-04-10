# Nightreign Relic Assistant

黑夜君临遗物助手的重写版本。当前仓库重点在于重新整理桌面应用架构，把界面、持久化、OCR、规则判定和自动化边界拆开，方便后续继续迭代和替换实现。

## 当前状态

当前版本已经完成以下内容：

- 基于 PySide6 和 PySide6-Fluent-Widgets 的桌面界面。
- 商店筛选、仓库清理、预设管理、存档管理、设置、关于页等页面框架。
- 设置、预设、历史记录的 JSON 持久化。
- OCR 识别服务接入与 Nightreign 遗物 OCR 引擎迁移。
- Windows 自动化网关、日志系统、后台初始化线程。

当前仍处于“可运行骨架 + 部分能力已接通”阶段，以下能力还是占位实现：

- 规则引擎：当前为安全占位实现，尚未接入真实判定逻辑。
- 仓库状态检测器：当前为安全占位实现，尚未接入真实检测逻辑。

这意味着商店筛选和仓库清理流程目前会先完成运行环境检查；若规则引擎或检测器未就绪，流程会安全停止，不会执行真实自动化动作。

## 功能概览

- 商店筛选：提供流程入口、统计面板、日志输出与历史记录展示。
- 仓库清理：提供收藏 / 售出模式入口、统计面板、日志输出与历史记录展示。
- 预设管理：支持预设新增、编辑、删除、启停、拖拽排序、导入导出。
- 存档管理：支持 Steam 用户识别、存档备份、恢复、重命名、删除。
- 设置管理：支持 Steam 路径、主题和开发者选项等配置。

## 项目结构

```text
NightreignRelicAssistant/
├── main.py              # 仓库根目录启动入口
├── pyproject.toml       # 项目元数据与依赖
├── src/
│   ├── app/             # 启动装配与容器
│   ├── core/            # 核心接口与数据模型
│   ├── infra/           # OCR、自动化、持久化、日志等基础设施
│   ├── services/        # 业务流程编排
│   └── ui/              # 页面、组件、对话框、后台线程
├── OCR/                 # 本地 OCR 模型目录
└── data/                # 运行期数据目录（设置、预设、历史记录、日志）
```

## 环境要求

- Windows
- Python 3.10+

当前自动化能力主要面向 Windows 环境；如果只运行界面和数据层，不依赖真实自动化动作，也可以先完成基础安装与启动。

## 安装

建议先创建虚拟环境，然后安装项目依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

如果你后续要启用真实自动化动作，通常还需要额外准备这些常见依赖：

```powershell
pip install pyautogui pydirectinput pygetwindow pywin32
```

## 启动

方式一：直接从仓库根目录启动

```powershell
python main.py
```

方式二：安装可编辑包后使用入口命令启动

```powershell
nra
```

## OCR 模型与资源

OCR 模型查找顺序如下：

1. 优先使用 `OCR/PP-OCRv4/models/`
2. 如果不存在，则回退到 `resources/models/`
3. 如果仍不存在，则回退到 `参考/NRrelics/resources/models/`

当前默认就是直接使用 `OCR/PP-OCRv4/models/` 下的三个 ONNX 模型文件。

词条库默认直接从 `data/` 目录读取。

如果你后续要补充词条文本文件，请将它们放在 `data/` 下，由 `VocabularyLoader` 直接加载。

## 运行期数据

程序运行时会在仓库根目录下自动创建或更新这些内容：

- `data/settings.json`
- `data/presets.json`
- `data/history/`
- `data/logs/`

这些文件属于运行期数据，不建议手工维护其内部结构，除非你明确知道兼容性影响。

## 开发说明

- 当前 `tmp/` 和 `.vscode/` 已整体排除版本控制，仅作为本地工作区使用。
- 当前规则引擎与仓库状态检测器仍是占位实现。
- 如果你要接入自己的 OCR 或规则逻辑，主要入口在：
  - `src/app/container.py`
  - `src/infra/ocr/`
  - `src/infra/rules/`
  - `src/infra/detection/`

## 许可证

本项目采用 MIT License，详见 LICENSE。