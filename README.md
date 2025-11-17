<div align="center">

<h1>Warrior Rimer</h1>

<p>一款基于 Python 的俯视角像素射击 / 生存闯关小游戏。专注轻量、可扩展、易于二次开发。</p>

<p>
	<img src="https://img.shields.io/badge/status-alpha-orange" alt="status" />
	<img src="https://img.shields.io/badge/python-3.7%2B-blue" alt="python" />
		<img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
	<img src="https://img.shields.io/badge/platform-Windows-green" alt="platform" />
	<a href="https://github.com/m0n3rt/Warrior-RimerV1.0/releases/latest">
		<img src="https://img.shields.io/github/v/release/m0n3rt/Warrior-RimerV1.0?display_name=release&sort=semver&color=blue" alt="latest release" />
	</a>
	<a href="https://github.com/m0n3rt/Warrior-RimerV1.0/releases/tag/nightly">
		<img src="https://img.shields.io/badge/nightly-latest-purple" alt="nightly build" />
	</a>
</p>

</div>

## 📌 项目简介
Warrior Rimer 是一个使用 Python（可能基于 pygame 等库，实际依赖请参考 `requirements.txt`）构建的本地单机射击游戏。玩家操控角色在地图中移动、射击、切换武器并通过成就系统记录进度。项目结构清晰，适合：

- 初学者学习简单游戏循环与数据持久化
- 想要扩展关卡、武器、敌人逻辑的开发者
- 练习打包分发（PyInstaller + Inno Setup）的实战示例

## ✨ 核心特性
- 多武器切换（数字 1/2/3）
- 基础移动与射击机制（WASD + 空格）
- 加速/强化触发（F 键）
- 游戏暂停（M 键）
- 成就与统计记录：`achievement_data.json`, `game_data.json`
- 可一键进行便携版与安装版打包
- 数据文件与逻辑分离，方便修改与扩展

## 🧱 技术栈 / 依赖
主要运行环境与工具：

- Python 3.7+ （建议使用 3.8~3.11 中的稳定版本）
- 第三方库：详见 `requirements.txt`
- 打包：PyInstaller (`Warrior_Rimer.spec`)
- 安装包：Inno Setup (`Warrior_Rimer.iss`，可选)

## 📂 目录结构（节选）
```
Warrior_RimerV1.0/
├─ start_game.py              # 游戏入口（源码运行推荐）
├─ main_game.py               # 主游戏循环/逻辑
├─ game_utils.py              # 工具函数与通用方法
├─ achievement_system.py      # 成就系统实现
├─ achievement_data.json      # 成就数据定义/记录
├─ game_data.json             # 当前游戏数据（可重置）
├─ game_data.clean.json       # 干净初始存档模板
├─ pack.bat                   # 一键打包脚本
├─ Warrior_Rimer.spec         # PyInstaller 配置
├─ Warrior_Rimer.iss          # Inno Setup 脚本
├─ music/                     # 音频资源（需确保包含 wav）
├─ Output/                    # 安装包输出目录
└─ build/                     # 构建临时文件
```

## 🚀 快速开始
克隆仓库（GitHub）：
```bash
git clone https://github.com/m0n3rt/Warrior-RimerV1.0.git
cd Warrior-RimerV1.0
```
安装依赖：
```bash
pip install -r requirements.txt
```
运行游戏：
```bash
python start_game.py
```

## 🛠 打包与发布
准备条件：
- Windows 平台
- 已安装依赖：`pip install -r requirements.txt`
- 安装 PyInstaller：`pip install pyinstaller`
- 可选：安装 Inno Setup (将 `iscc` 加入 PATH)

一键打包（PowerShell）：
```powershell
cd "$PSScriptRoot"
./pack.bat
```
脚本会执行：
1. 使用 `game_data.clean.json` 重置 `game_data.json`
2. 清理 `build/` 与 `dist/` 旧产物
3. 通过 `Warrior_Rimer.spec` 生成便携版到 `dist/WarriorRimer/`
4. 若检测到 `iscc`，用 `Warrior_Rimer.iss` 生成安装包到 `Output/Warrior_Rimer_Setup.exe`

产物定位：
- 便携版执行：`dist/WarriorRimer/WarriorRimer.exe`
- 安装包：`Output/Warrior_Rimer_Setup.exe`

## ⬇️ 下载与更新
- 稳定版（推荐）：从 GitHub Releases 获取以 `v*` 标签发布的版本
	- https://github.com/m0n3rt/Warrior-RimerV1.0/releases
- 每次提交自动构建的 Nightly（预发布）：推送至 `main` 会自动生成/更新 `nightly` 预发布，包含 `WarriorRimer-nightly` 压缩包与可执行文件，适合尝鲜测试。

## 🎮 操作指南
| 功能 | 按键 |
|------|------|
| 移动 | W / A / S / D |
| 射击 | 空格 |
| 切换武器 | 1 / 2 / 3 |
| 激活攻击加速 | F |
| 暂停 | M |

## 🏆 成就与数据系统
文件说明：
- `achievement_data.json`：定义或记录已解锁成就及相关状态。
- `game_data.json`：当前进度、分数、角色属性等运行时数据。
- `game_data.clean.json`：初始干净模板，打包或重置时使用。

建议：
- 若扩展新成就，保持字段一致性并在 `achievement_system.py` 中增加处理逻辑。
- 可添加版本字段以便未来迁移数据结构。

## ❓ 常见问题 (FAQ)
1. 启动后缺少声音？确保 `music/` 内存在对应 `.wav` 文件且打包时被包含。
2. 运行报缺少 DLL？安装 Visual C++ 运行库或换与目标机器一致的 Python 版本重新打包。
3. 安装步骤跳过 Inno Setup？将其安装路径加入环境变量 PATH，或手动运行 `iscc Warrior_Rimer.iss`。
4. 想要修改初始存档？编辑 `game_data.clean.json` 后再运行打包脚本。

## 🤝 贡献指南
欢迎 Issue / PR：
1. Fork 仓库并创建新分支：`feat/<feature-name>`
2. 编写与功能相关的注释与必要文档
3. 提交前运行游戏自测基本操作（启动、切武器、暂停）
4. 发起 Pull Request 并说明变更动机

未来可补充：
- 单元测试基础框架（如 `pytest`）
- 代码风格工具（`ruff` 或 `flake8`）

## 🗺 路线图 (Roadmap)
- [ ] 新敌人 AI 行为模式
- [ ] 关卡难度递增机制
- [ ] 更多武器与状态效果
- [ ] 存档加密或校验
- [ ] 简易配置文件支持（分辨率、音量）
- [ ] 多语言（zh/en）

## 📄 许可证 (License)
本项目采用 MIT 开源协议，详见根目录 `LICENSE` 文件。你可以在遵守保留版权和许可文本的前提下自由使用、修改与分发本项目代码，包含商业用途。

## 🙏 致谢 (Acknowledgements)
- Python 与相关第三方库维护者
- 社区提供的教程与示例

## 🖼 截图 / 预览
（占位：可在此放置游戏主界面、战斗场景、成就界面截图）

```
![主界面截图](docs/images/screenshot_main.png)
![战斗截图](docs/images/screenshot_battle.png)
```

## 🔖 徽章建议
- 构建状态（例如使用 Gitee CI / Github Actions）
- 版本号（手动或自动更新）
- 下载量（若发布 Release）

## 🧪 测试（规划）
建议添加：
- 基础模块的函数测试（如 `game_utils.py`）
- 成就系统边界测试（未达成/已达成状态切换）

当前已提供基础单元测试骨架：`tests/` 目录，使用内置 `unittest`。
运行测试：
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

CI（示例 GitHub Actions）会在推送/PR 时自动：
1. 安装依赖
2. 运行上述单元测试
3. 尝试 PyInstaller 打包并上传构建产物（便携版）

你可以在迁移到 Gitee 后使用其 CI（或保留 GitHub 镜像）实现同样流程。

查看更新记录：参见 `CHANGELOG.md`。

## 📬 联系方式
可在 Gitee Issue 反馈 Bug 或需求，或通过个人主页邮箱联系。

---
如果你觉得本项目对你有帮助，欢迎 Star ⭐、Fork、分享给更多正在学习 Python 游戏开发的朋友！

> 提示：完成 License 选择与截图补充后，本 README 将更趋完善。
