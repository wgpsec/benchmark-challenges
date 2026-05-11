[English](README.md) | 中文文档

# Benchmark Challenges

[benchmark-platform](https://github.com/wgpsec/benchmark-platform) 的靶场题目数据仓库。

## 目录结构

```
xbow/          # 74 道题目，来自 xbow-validation-benchmarks
custom/        # 4 道自定义题目（XSS、Auth 等）
argus/         # 60 道题目，来自 argus-validation-benchmarks
```

## 题目来源

| 来源 | 数量 | 链接 | 说明 |
|------|------|------|------|
| xbow | 74 | [xbow-validation-benchmarks](https://github.com/xbow-dev/xbow-validation-benchmarks) | 多框架 Web 应用漏洞 |
| argus | 60 | [argus-validation-benchmarks](https://github.com/pensarai/argus-validation-benchmarks) | SSRF、XSS、SQLi、RCE、IDOR、反序列化（Next.js、Flask、Express、Go、Django、Rails、Spring Boot） |
| custom | 4 | — | 针对特定场景手工编写的题目 |

## 使用方式

本仓库由 benchmark-platform 的「靶场管理」功能消费。每次推送后，GitHub Action 会自动将题目打包发布为 Release 资产。

可以在平台 Web UI 侧边栏点击 **「靶场管理」** 浏览并下载题目，也可以手动拉取：

```bash
git clone https://github.com/wgpsec/benchmark-challenges /tmp/benchmarks
cp -r /tmp/benchmarks/xbow challenges/xbow
cp -r /tmp/benchmarks/custom challenges/custom
cp -r /tmp/benchmarks/argus challenges/argus
```

## 添加题目

1. 在对应分类下创建目录：`xbow/XBEN-XXX-24/`、`argus/APEX-XXX-25/` 或 `custom/MY-CHALLENGE/`
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

## WgpSec Agentic Ecosystem

benchmark-challenges 是 **WgpSec Agentic Ecosystem** 的数据层 — 提供真实漏洞环境，用于评估 AI Agent 的攻防能力。

```
┌───────────────────── WgpSec Agentic Ecosystem ─────────────────────┐
│                                                                     │
│  Knowledge ➜ Service ➜ Execution ➜ Evaluation                      │
│                                                                     │
│  AboutSecurity ──▶ context1337 ──▶ tchkiller ──▶ benchmark-platform │
│  (知识库)          (MCP 服务)      (渗透Agent)     (平台)           │
│                                         ▲                           │
│                                    PoJun (通用求解引擎)              │
│                                         │                           │
│                              benchmark-challenges (本仓库)           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

| 项目 | 定位 |
|------|------|
| [AboutSecurity](https://github.com/wgpsec/AboutSecurity) | 结构化渗透知识库（Skills, Dic, Payload, Vuln） |
| [context1337](https://github.com/wgpsec/context1337) | MCP Server — 将 AboutSecurity 转化为 AI Agent 可调用的搜索 API |
| [tchkiller](https://github.com/wgpsec/tchkiller) | 自主渗透 Agent，支持多轮决策与团队协作 |
| [benchmark-platform](https://github.com/wgpsec/benchmark-platform) | CTF 靶场平台，评估 Agent 攻防能力 |
| [benchmark-challenges](https://github.com/wgpsec/benchmark-challenges) | 靶场数据仓库 — 通过 GitHub Releases 打包分发 |
| PoJun | 通用 AI 求解引擎（私有） |

## 许可证

[MIT](LICENSE)
