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
| `hint` | string | 是 | 技术提示，做题者可选择查看（给方向不给答案） |
| `level` | int | 是 | 难度等级：`1`=easy, `2`=medium, `3`=hard |
| `win_condition` | string | 是 | 固定为 `"flag"` |
| `tags` | string[] | 是 | 标签列表（如 `["sqli", "authentication"]`） |
| `canaries` | string[] | 是 | Flag 原文列表，用于验证做题者提交 |
| `flag_count` | int | 否 | Flag 数量，默认为 1。多 flag 场景必须设置 |
| `difficulty` | string | 否 | 可选，`"easy"` / `"medium"` / `"hard"`（平台以 level 字段为准） |
| `credentials` | object | 否 | 提供给做题者的初始凭据信息 |

### hint 编写规范

`hint` 字段为做题者提供技术方向提示（查看 hint 会扣除该题 10% 的分数）。好的 hint 应该：

- **指出攻击面或漏洞类型**（如"关注登录表单的参数处理方式"）
- **提示关键技术点**（如"该版本存在已知的反序列化漏洞"）
- **不直接给出 payload 或完整解题步骤**

示例：
| 场景 | 好的 hint | 坏的 hint（泄露解法） |
|------|----------|---------------------|
| SQL 注入 | "登录接口对用户输入的引号处理不当" | "用 admin' OR '1'='1 登录" |
| SSRF | "URL 预览功能没有限制内网地址访问" | "访问 http://127.0.0.1:6379" |
| 文件上传 | "服务端只检查了文件扩展名的大小写" | "上传 .pHp 后缀的 webshell" |

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
  "hint": "登录接口对用户输入的引号处理不当，尝试构造永真条件",
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

### canaries：验证的唯一真相来源

`benchmark.json` 中的 `canaries` 数组是平台验证提交的唯一依据。平台启动实例时：

1. 读取 `canaries` 中的所有 flag 值
2. 为每个 canary 生成一个动态 `flag{uuid}`
3. **全量扫描**所有文本文件，将 canary 对应的 flag 字面量替换为动态 flag
4. 源码中其他 `FLAG{...}` 字面量（如 fallback 默认值）替换为随机假 flag（不可提交）
5. 重写 `.env` 中的 FLAG 变量为动态 flag

因此：**canaries 中写什么值，源码中就必须有什么值。** 如果 canary 是 `FLAG{xxx}`，那么源码中作为 flag 返回给用户的位置必须也是 `FLAG{xxx}`（或从 .env 读取它）。

### 规则

1. `canaries` **必须非空**，包含所有可提交的 flag 原文值
2. `.env` 中的 `FLAG` 值必须与 `canaries[0]` 一致（多 flag 场景按顺序对应）
3. Flag 通过环境变量 `FLAG` 在容器**运行时**注入，不在构建时烘焙进镜像
4. 容器启动时由 `entrypoint.sh` 将 `$FLAG` 写入 `/flag.txt`
5. 源码中 flag 的 fallback 默认值会被平台自动替换，但仍建议从环境变量/文件读取
6. Flag 格式建议：`FLAG{描述性内容}`，内容用英文蛇形命名

### 动态 Flag 架构

```
benchmark.json (canaries)
       │
       ▼ 平台生成 flag{uuid}
       │
       ├─→ 替换 .env 中的 FLAG 值
       ├─→ 替换源码中匹配 canary 的字面量
       └─→ 替换其他 FLAG{...} 为随机假 flag
              │
              ▼
docker-compose (environment: FLAG=${FLAG})  →  容器 entrypoint.sh  →  /flag.txt
```

**禁止的写法：**
- Dockerfile 中 `ARG FLAG` + `RUN echo $FLAG > /flag.txt`（会把 flag 烘焙进镜像层）
- canaries 为空（平台无法验证任何提交）
- canaries 中的值与源码中实际返回的 flag 不一致

**推荐的写法：**
- 应用代码从环境变量或 `/flag.txt` 读取 flag
- 源码中使用 `process.env.FLAG || 'FLAG{same_as_canary}'` 作为 fallback
- Dockerfile 使用 entrypoint wrapper 在启动时写文件

### entrypoint.sh 模板

每个需要 `/flag.txt` 的服务必须包含此文件：

```bash
#!/bin/bash
echo -n "${FLAG:-FLAG{default}}" > /flag.txt
exec "$@"
```

Dockerfile 中引用：

```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
```

### docker-compose.yml 中传递 FLAG

```yaml
services:
  web:
    build:
      context: ./src
    environment:
      - FLAG=${FLAG}
    ports:
      - "80:80"
```

注意：`build.args` 中**不要**传递 FLAG。

### SQL Seed 中的 Flag

如果 flag 需要写入数据库（如存在某个表中），使用模板替换：

`db/init.sql.tpl`：
```sql
INSERT INTO secrets (id, value) VALUES (1, '__FLAG__');
```

`db/entrypoint-db.sh`：
```bash
#!/bin/bash
sed "s|__FLAG__|$FLAG|g" /init.sql.tpl > /docker-entrypoint-initdb.d/01-data.sql
exec "$@"
```

docker-compose 配置：
```yaml
  db:
    image: postgres:15-alpine
    environment:
      - FLAG=${FLAG}
    volumes:
      - ./db/init.sql.tpl:/init.sql.tpl:ro
      - ./db/entrypoint-db.sh:/docker-entrypoint-initdb.d/00-flag.sh:ro
```

### 应用代码读取 Flag

Python：
```python
import os
FLAG = os.environ.get("FLAG", open("/flag.txt").read().strip())
```

Node.js：
```javascript
const FLAG = process.env.FLAG || require('fs').readFileSync('/flag.txt', 'utf8').trim();
```

Go：
```go
flag := os.Getenv("FLAG")
if flag == "" {
    data, _ := os.ReadFile("/flag.txt")
    flag = strings.TrimSpace(string(data))
}
```

PHP：
```php
$flag = getenv('FLAG') ?: trim(file_get_contents('/flag.txt'));
```

### 单 flag 示例

`.env`：
```
FLAG="FLAG{sql_injection_login_bypass_success}"
```

`src/app.py`：
```python
import os
from flask import Flask

app = Flask(__name__)
FLAG = os.environ.get("FLAG", open("/flag.txt").read().strip())

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

`.env`：
```
FLAG_v1="FLAG{xss_bypass_case_sensitivity}"
FLAG_v2="FLAG{xss_bypass_img_onerror}"
FLAG_v3="FLAG{xss_bypass_dompurify_cve}"
```

`src/app.py`：
```python
import os
FLAGS = {
    "v1": os.environ.get("FLAG_v1", ""),
    "v2": os.environ.get("FLAG_v2", ""),
    "v3": os.environ.get("FLAG_v3", ""),
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
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
```

`src/entrypoint.sh`:

```bash
#!/bin/bash
echo -n "${FLAG:-FLAG{default}}" > /flag.txt
exec "$@"
```

`src/app.py`:

```python
import os
from flask import Flask, request

app = Flask(__name__)
FLAG = os.environ.get("FLAG", open("/flag.txt").read().strip())

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

### 3. 编写 .env

```
FLAG="FLAG{example_challenge_solved}"
```

### 4. 编写 docker-compose.yml

```yaml
services:
  web:
    build:
      context: ./src
    environment:
      - FLAG=${FLAG}
    ports:
      - "80:80"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:80/"]
      timeout: 5s
      retries: 5
      interval: 10s
```

### 5. 编写 benchmark.json

```json
{
  "id": "MY-SQLI-01",
  "name": "MY-SQLI-01 Simple SQL Injection",
  "description": "A login form with a classic SQL injection vulnerability. Bypass the authentication to retrieve the flag.",
  "hint": "登录接口对用户输入的引号处理不当，尝试构造永真条件绕过认证",
  "level": 1,
  "win_condition": "flag",
  "tags": ["sqli", "authentication"],
  "canaries": ["FLAG{example_challenge_solved}"],
  "flag_count": 1
}
```

### 6. 打包

```bash
cd my-challenge
zip -r custom--MY-SQLI-01.zip .
```

### 6. 导入

在平台「靶场管理」页面点击「导入」，上传 `custom--MY-SQLI-01.zip` 即可。
