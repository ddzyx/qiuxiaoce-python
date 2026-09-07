# `qiuxiaoce` Python SDK 发布操作指南

本指南手把手指导如何将本项目发布至 **PyPI 官方索引** 与 **GitHub 独立开源仓库**，并在发布时完整植入指向官网 `https://www.qiuxiaoce.com` 的反向链接。

---

## 平台一：发布到 PyPI 官方包索引 (pypi.org)

发布到 PyPI 后，全球十几个依赖收录平台（`libraries.io`、`pepy.tech`、`snyk.io` 等）会在 24~48 小时内自动镜像并保留你的官网链接。

### 1. 注册与准备
1. 访问 PyPI 官网：`https://pypi.org/account/register/` 完成注册（已有账号跳过）。
2. 在 PyPI 后台 **Account settings** -> **API tokens** -> 点击 **Add API token**：
   - Token name 填：`qiuxiaoce-publish`
   - Scope 选：`Entire account (all projects)`
   - 生成后保存形如 `pypi-AgEIcHlwaS5vcm...` 的 Token。

### 2. 本地构建与打包（在当前目录执行）

```bash
# 进入项目目录
cd /www/git/qiuxiaozhiwp/analysis-bot-v2/open_source_matrix/qiuxiaoce-python

# 安装构建与上传工具
pip install --upgrade build twine

# 执行打包（生成 dist/ 目录下的 .whl 和 .tar.gz）
python -m build
```

### 3. 一键上传至 PyPI

```bash
# 执行上传
python -m twine upload dist/*
```
- **Username** 处输入：`__token__`
- **Password** 处粘贴你刚才在 PyPI 生成的 API Token（以 `pypi-` 开头）。

### 4. 验证与检查
上传成功后，访问：
👉 `https://pypi.org/project/qiuxiaoce/`
你将看到：
- 项目主页完美展示 `README.md`；
- 左侧 **Project links** 栏显示：
  - `Homepage: https://www.qiuxiaoce.com`
  - `Documentation: https://www.qiuxiaoce.com/mei-ri-bao-gao-su-lan/`
  - `Daily Report: https://www.qiuxiaoce.com/mei-ri-bao-gao-su-lan/`

---

## 平台二：发布到 GitHub 开源仓库 (github.com)

### 1. 在 GitHub 创建新仓库
1. 登录 GitHub，点击右上角 `+` -> **New repository**；
2. 填写表单字段：
   - **Repository name**: `qiuxiaoce-python-sdk`
   - **Description**: `球小策 (QiuXiaoCe) 官方 Python SDK - 欧洲五大联赛足球大数据、赛程积分榜、攻防模型与赛前研报 API 客户端`
   - **Public / Private**: 必须选 **Public**（公开）
   - **Initialize this repository with**: 全部不勾选（不要勾选 README、.gitignore 或 License，因为本地已经有了）。
3. 点击 **Create repository**。

### 2. 推送本地代码到 GitHub

在当前目录执行：
```bash
cd /www/git/qiuxiaozhiwp/analysis-bot-v2/open_source_matrix/qiuxiaoce-python

git init
git add .
git commit -m "feat: initial release of qiuxiaoce python sdk v0.1.0"
git branch -M main
# 将下面的用户名换成你的 GitHub 账号名
git remote add origin https://github.com/<你的GitHub用户名>/qiuxiaoce-python-sdk.git
git push -u origin main
```

### 3. 设置 GitHub 仓库核心外链字段（极为关键）
进入 GitHub 仓库页面，点击右上角的 **⚙️ (Settings) 齿轮图标**（位于 About 旁边）：
1. **Description**: 填入：
   `球小策 (QiuXiaoCe) 官方 Python SDK - 足球大数据、五大联赛赛程积分榜、攻防模型与赛前研报 API 客户端`
2. **Website**: 填入 👉 `https://www.qiuxiaoce.com/`（必须带完整的 https 网址）
3. **Topics (标签，回车添加)**:
   - `football`
   - `soccer`
   - `sports-analytics`
   - `sports-data`
   - `python-sdk`
   - `premier-league`
   - `xg`
   - `qiuxiaoce`
4. 点击 **Save changes** 保存。

---

## 平台三：提交到 Gitee 码云（国内百度收录加成）

1. 登录 `https://gitee.com/`；
2. 点击右上角 `+` -> **新建仓库**：
   - 仓库名称：`qiuxiaoce-python-sdk`
   - 仓库介绍：`球小策官方 Python SDK - 足球大数据、赛程积分榜与模型研报 API 客户端`
   - 勾选：开源
3. 或者直接在 Gitee 选 **“从 GitHub 导入仓库”**，一键完成同步。
4. 在 Gitee 仓库主页右上角编辑项目属性，把 **项目主页** 同样设置为 `https://www.qiuxiaoce.com`。
