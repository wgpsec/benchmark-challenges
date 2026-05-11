---
name: create-challenge
description: 交互式生成符合 Benchmark Platform 规范的 CTF/渗透测试靶场。当用户提到"创建靶场"、"生成靶场"、"做一道题"、"新建 challenge"、"写个漏洞环境"、"搭个靶机"，或描述任何攻击场景并暗示需要可运行的练习环境时，使用此 skill。即使用户只说了漏洞类型（如"帮我搞个 SSRF"），也应触发。
---

# 创建靶场

根据用户描述的攻击场景，生成一个可以直接 `docker compose up` 运行、并通过平台"导入"功能上传的完整靶场。

## 为什么需要这个 skill

平台对靶场的目录结构、元数据格式、端口声明方式有严格要求——不符合规范的 zip 导入后无法被平台识别和启动。这个 skill 确保生成的每个文件都能被平台正确解析。

## 快速参考

完整字段定义和示例见 `docs/challenge-spec.md`。生成文件前先读取它以获取最新的 schema。以下是核心约束的速查：

| 文件 | 必须 | 作用 |
|------|------|------|
| `docker-compose.yml` | 是 | 容器编排，端口用 `"host:container"` 字符串 |
| `benchmark.json` | 是 | 元数据（id, name, description, level, win_condition, tags, canaries） |
| `benchmark.yaml` | 多 flag 时 | flag 路由和提示定义 |
| `src/` | 需要 build 时 | 源码 + Dockerfile |

关键点：
- `level`: 1/2/3 → easy/medium/hard → 200/300/500 分
- `win_condition`: 固定 `"flag"`
- `canaries`: flag 原文数组，靶场内部返回相同字符串，平台做精确匹配验证
- 端口映射的 host 部分是占位符——平台启动时会替换为随机端口
- healthcheck 影响平台的健康状态显示，务必配置

## 工作流程

### 1. 理解场景

和用户对齐以下几点（不用一次问完，根据用户已给的信息灵活跳过）：

- **攻击场景** — 什么漏洞？什么利用路径？（这是最核心的，决定靶场质量）
- **难度** — Level 1/2/3。如果用户没说，根据攻击链复杂度建议一个
- **Flag 数量** — 单 flag 还是多步骤/多变体？多 flag 则需要 benchmark.yaml
- **技术栈** — 语言/框架偏好。没偏好就选最适合该漏洞类型的
- **辅助服务** — 是否需要数据库、缓存、内网模拟等
- **ID** — 建议格式 `<PREFIX>-<NNN>`，用户可自定

### 2. 生成文件

确认后在当前目录生成完整结构：

```
<challenge-id>/
├── docker-compose.yml
├── benchmark.json
├── benchmark.yaml       # 多 flag 时
└── src/
    ├── Dockerfile
    └── (应用代码)
```

生成原则：

- **漏洞必须真实可利用。** 这是靶场的核心价值。不要写一个看起来像漏洞但实际无法 exploit 的代码，也不要把 flag 放在不需要利用漏洞就能访问的地方。
- **代码精简聚焦。** 一个靶场解决一类问题。不需要完整的生产级应用——够展示漏洞的最小代码即可。
- **Flag 格式统一。** 使用 `FLAG{descriptive_content}`，内容用英文蛇形命名描述利用方式。
- **Dockerfile 用精简基础镜像。** `python:3.11-slim`, `node:20-slim`, `golang:1.22-alpine` 等。
- **healthcheck 必须配。** 平台依赖它判断服务是否就绪。用 curl 检测 HTTP 或 TCP 端口检测。
- **不要在 description/hint 里泄露解法。** description 描述场景，hint 给技术方向提示，都不应该直接告诉答案。

### 3. 验证和打包

生成后告知用户：

```bash
# 本地测试
cd <challenge-id>
docker compose up --build

# 验证：服务启动后尝试利用漏洞获取 flag

# 打包（用于平台导入）
zip -r <category>--<challenge-id>.zip .
```

zip 命名中 `--` 是分类和名称的分隔符。不含 `--` 的文件名自动归入 `custom` 分类。

## 示例

**用户**："帮我做一个 SSRF 的靶场，中等难度，Python 写"

**你的响应思路**：
1. 确认 SSRF 具体场景——"是想做内网探测、云元数据读取、还是利用 SSRF 打内网其他服务？"
2. 用户说"云元数据"→ 确认单 flag 即可
3. 生成：Flask 应用有个"URL 预览"功能，可以 SSRF 到模拟的 metadata endpoint，读出 flag

**用户**："搞个 XSS 系列题，5 个变体，过滤器越来越强"

**你的响应思路**：
1. 这是多 flag 场景，需要 benchmark.yaml 定义 5 个 flag
2. 确认难度（过滤器递进 → Level 2 合理）
3. 生成：单个 Express 应用，5 个路由各有不同 XSS 过滤策略，每个需要不同绕过技巧

## 常见陷阱

- **端口写成数字格式** `ports: [80]` → 平台无法重映射。必须是字符串 `"80:80"`
- **canaries 和代码中的 flag 不一致** → 做题者拿到 flag 但提交验证失败
- **flag_count 和 canaries 数量不匹配** → 平台显示的进度会出错
- **没有 healthcheck** → 平台无法判断服务健康状态，始终显示 "running"
- **Dockerfile 用了重量级基础镜像** → 下载慢、磁盘占用大，用 slim/alpine 变体
