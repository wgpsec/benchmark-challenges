[English](README.md) | 中文文档

# Benchmark Challenges

[benchmark-platform](https://github.com/wgpsec/benchmark-platform) 的靶场题目数据仓库。

## 目录结构

```
xbow/          # 来自 xbow-validation-benchmarks 的题目
custom/        # 自定义题目（XSS、Auth 等）
```

## 使用方式

本仓库由 benchmark-platform 的「靶场管理」功能消费。每次推送后，GitHub Action 会自动将题目打包发布为 Release 资产。

可以在平台 Web UI 侧边栏点击 **「靶场管理」** 浏览并下载题目，也可以手动拉取：

```bash
git clone https://github.com/wgpsec/benchmark-challenges /tmp/benchmarks
cp -r /tmp/benchmarks/xbow challenges/xbow
cp -r /tmp/benchmarks/custom challenges/custom
```

## 添加题目

1. 在对应分类下创建目录：`xbow/XBEN-XXX-24/` 或 `custom/MY-CHALLENGE/`
2. 至少包含：`docker-compose.yml`、`benchmark.json`、`.env`
3. 推送到 main — GitHub Action 会自动打包并发布

## 题目格式

```
XBEN-001-24/
├── docker-compose.yml    # 必须
├── benchmark.json        # 题目元数据（name, description, level, points）
├── benchmark.yaml        # 可选，多 flag 定义
├── .env                  # FLAG 环境变量
└── app/ mysql/ ...       # 应用代码
```

## CI/CD

每次推送到 `main` 分支时，GitHub Action 会：

1. 检测哪些题目目录发生了变更
2. 将变更的题目打包为 zip
3. 生成 `manifest.json` 列出所有题目
4. 上传资产到 `latest` Release

仅变更的题目会被重新打包（增量更新）。

## 许可证

[MIT](LICENSE)
