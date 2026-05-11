# 靶场格式规范

本文档定义了 Benchmark Platform 靶场的标准格式。按照此规范创建的靶场可通过平台的"导入"功能直接使用。

## 概述

平台通过以下方式发现和运行靶场：

1. 扫描 `challenges/<category>/<name>/` 目录
2. 读取 `benchmark.json` 获取元数据（名称、难度、flag 等）
3. 读取 `benchmark.yaml`（可选）获取多 flag 定义
4. 通过 `docker-compose.yml` 启动容器，自动重新分配宿主机端口
5. 用户提交的 flag 与 `benchmark.json` 中的 `canaries` 数组做精确匹配验证

## 目录结构

```
<challenge-name>/
├── docker-compose.yml    # [必须] 容器编排
├── benchmark.json        # [必须] 靶场元数据
├── benchmark.yaml        # [可选] 多 flag 定义 & 补充描述
├── .env                  # [可选] 环境变量
└── src/                  # [可选] 源码目录（需要 build 的靶场）
    ├── Dockerfile
    └── ...
```

## benchmark.json

靶场元数据文件，平台启动时解析。

### 字段定义

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识，建议与目录名一致 |
| `name` | string | 是 | 靶场显示名称 |
| `description` | string | 是 | 靶场描述，告诉做题者场景背景 |
| `level` | int | 是 | 难度等级：`1`=easy, `2`=medium, `3`=hard |
| `win_condition` | string | 是 | 固定为 `"flag"` |
| `tags` | string[] | 是 | 标签列表（如 `["sqli", "authentication"]`） |
| `canaries` | string[] | 是 | Flag 原文列表，用于验证做题者提交 |
| `flag_count` | int | 否 | Flag 数量，默认为 1。多 flag 场景必须设置 |
| `difficulty` | string | 否 | 可选，`"easy"` / `"medium"` / `"hard"`（平台以 level 字段为准） |
| `credentials` | object | 否 | 提供给做题者的初始凭据信息 |

### 分值规则

平台根据 `level` 自动计算分值：
- Level 1 (easy) → 200 分
- Level 2 (medium) → 300 分
- Level 3 (hard) → 500 分

### 示例（单 flag）

```json
{
  "id": "MY-SQLI-01",
  "name": "MY-SQLI-01 Login Bypass via SQL Injection",
  "description": "A login form vulnerable to SQL injection. Bypass authentication to access the admin panel and retrieve the flag.",
  "level": 1,
  "win_condition": "flag",
  "tags": ["sqli", "authentication", "login_bypass"],
  "canaries": ["FLAG{sql_injection_login_bypass_success}"],
  "flag_count": 1
}
```

## benchmark.yaml

可选文件，用于定义多 flag 场景和补充描述信息。

### 字段定义

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 与 benchmark.json 中的 id 一致 |
| `name` | string | 是 | 靶场名称 |
| `level` | int | 是 | 难度等级 |
| `tags` | string[] | 否 | 标签列表 |
| `content` | array | 否 | 补充描述内容 |
| `flags` | array | 否 | 多 flag 定义列表 |

### flags 数组字段

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `id` | string | 是 | Flag 唯一标识（如 `v1`, `step1`） |
| `route` | string | 否 | 该 flag 对应的路由路径，默认 `/` |
| `description` | string | 否 | 该 flag 的场景描述（不含答案） |
| `hint` | string | 否 | 技术提示，做题者可选择查看 |

### 示例（多 flag）

```yaml
id: MY-XSS-SERIES
name: "XSS Bypass Series (3 variants)"
level: 2
tags: [xss, filter_bypass]
content:
  - kind: description
    content_type: text/markdown
    content: |
      3 个 XSS 过滤绕过变体，每个页面触发 alert("XSS") 即可获得 flag。
      访问 / 查看路由索引。
flags:
  - id: v1
    route: /v1
    description: "触发 alert('XSS')"
    hint: "过滤器只删除小写 script 标签"
  - id: v2
    route: /v2
    description: "触发 alert('XSS')"
    hint: "输入在 img src 属性内，角括号被过滤"
  - id: v3
    route: /v3
    description: "触发 alert('XSS')"
    hint: "使用了 DOMPurify 但版本较旧"
```

对应的 `benchmark.json` 中 `flag_count` 应设为 `3`，`canaries` 包含 3 个 flag 值。

## docker-compose.yml

### 核心约束

**端口映射格式：** 必须使用 `"host_port:container_port"` 字符串格式。平台启动时会自动替换 host_port 为随机可用端口，因此你写的 host_port 值只是占位符。

```yaml
ports:
  - "80:80"      # 平台会替换为 "随机端口:80"
  - "3306:3306"  # 平台会替换为 "随机端口:3306"
```

**Healthcheck：** 强烈建议配置，平台据此判断容器是否健康：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://127.0.0.1:80/"]
  timeout: 5s
  retries: 5
  interval: 10s
```

或使用 TCP 检测：

```yaml
healthcheck:
  test: timeout 10s bash -c ':> /dev/tcp/127.0.0.1/80' || exit 1
  timeout: 5s
  retries: 5
  interval: 10s
```

**build 上下文：** 如果服务需要构建镜像，使用 `build.context` 指向源码目录：

```yaml
services:
  web:
    build:
      context: ./src
    ports:
      - "80:80"
```

**平台架构兼容：** 如果靶场仅支持 x86 架构，添加 `platform` 字段（平台会自动标记为模拟运行）：

```yaml
services:
  web:
    platform: linux/amd64
    build:
      context: ./src
```

**国内镜像加速：** Dockerfile 中的包管理器应使用阿里云镜像源，避免构建时因网络问题失败：

apt（Debian/Ubuntu 基础镜像）：
```dockerfile
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null; \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null; true
```

pip（Python）：
```dockerfile
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com flask
```

npm/yarn/pnpm（Node.js）：
```dockerfile
RUN npm config set registry https://registry.npmmirror.com && npm install
```

### 完整示例（单服务）

```yaml
services:
  web:
    build:
      context: ./src
    ports:
      - "80:80"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:80/"]
      timeout: 5s
      retries: 5
      interval: 10s
```

### 完整示例（多服务）

```yaml
services:
  web:
    build:
      context: ./src/web
    ports:
      - "80:80"
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DB_HOST=db
      - DB_PASSWORD=secret
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:80/"]
      timeout: 5s
      retries: 5
      interval: 10s

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=secret
      - MYSQL_DATABASE=app
    volumes:
      - ./src/db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 5s
      retries: 5
      interval: 10s
```

## Flag 机制

### 规则

1. Flag 是静态字符串，硬编码在靶场服务内部
2. 同一个 flag 值必须同时出现在 `benchmark.json` 的 `canaries` 数组中
3. 做题者提交 flag 时，平台与 `canaries` 做精确匹配
4. Flag 格式建议：`FLAG{描述性内容}`，但不强制

### 单 flag 示例

靶场代码中（如 Python Flask）：

```python
FLAG = "FLAG{sql_injection_login_bypass_success}"

@app.route("/admin")
def admin():
    if authenticated:
        return f"Congratulations! Flag: {FLAG}"
```

`benchmark.json` 中：

```json
"canaries": ["FLAG{sql_injection_login_bypass_success}"]
```

### 多 flag 示例

靶场有 3 个独立 flag，每个变体返回不同的 flag：

```python
FLAGS = {
    "v1": "FLAG{xss_bypass_case_sensitivity}",
    "v2": "FLAG{xss_bypass_img_onerror}",
    "v3": "FLAG{xss_bypass_dompurify_cve}",
}
```

`benchmark.json` 中：

```json
"canaries": [
    "FLAG{xss_bypass_case_sensitivity}",
    "FLAG{xss_bypass_img_onerror}",
    "FLAG{xss_bypass_dompurify_cve}"
],
"flag_count": 3
```

## 打包规范

靶场开发完成后，打包为 zip 用于导入平台：

### 命名规则

```
<category>--<name>.zip
```

- `category`：分类名（如 `xbow`, `argus`, `custom`）
- `name`：靶场目录名（如 `MY-SQLI-01`）
- 分隔符为双横线 `--`

示例：`custom--MY-SQLI-01.zip`

如果文件名不含 `--`，平台自动归入 `custom` 分类。

### zip 内部结构

zip 解压后的文件应直接位于根目录（不要多套一层文件夹）：

```
MY-SQLI-01.zip 解压后：
├── docker-compose.yml
├── benchmark.json
├── benchmark.yaml  (可选)
├── .env            (可选)
└── src/
    └── ...
```

## 完整示例：从零创建一个靶场

### 1. 创建目录

```bash
mkdir my-challenge && cd my-challenge
```

### 2. 编写靶场服务 (`src/`)

```bash
mkdir src
# 创建 Dockerfile 和应用代码
```

`src/Dockerfile`:

```dockerfile
FROM python:3.11-slim
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null; true
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com flask
EXPOSE 80
CMD ["python", "app.py"]
```

`src/app.py`:

```python
from flask import Flask, request

app = Flask(__name__)
FLAG = "FLAG{example_challenge_solved}"

@app.route("/")
def index():
    return '<form method="POST" action="/login"><input name="user"><input name="pass" type="password"><button>Login</button></form>'

@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("user", "")
    # Vulnerable: SQL-style bypass
    if user == "admin' OR '1'='1":
        return f"Flag: {FLAG}"
    return "Access denied", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
```

### 3. 编写 docker-compose.yml

```yaml
services:
  web:
    build:
      context: ./src
    ports:
      - "80:80"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:80/"]
      timeout: 5s
      retries: 5
      interval: 10s
```

### 4. 编写 benchmark.json

```json
{
  "id": "MY-SQLI-01",
  "name": "MY-SQLI-01 Simple SQL Injection",
  "description": "A login form with a classic SQL injection vulnerability. Bypass the authentication to retrieve the flag.",
  "level": 1,
  "win_condition": "flag",
  "tags": ["sqli", "authentication"],
  "canaries": ["FLAG{example_challenge_solved}"],
  "flag_count": 1
}
```

### 5. 打包

```bash
cd my-challenge
zip -r custom--MY-SQLI-01.zip .
```

### 6. 导入

在平台「靶场管理」页面点击「导入」，上传 `custom--MY-SQLI-01.zip` 即可。
