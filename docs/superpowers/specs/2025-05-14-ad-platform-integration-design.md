# AD 靶场平台集成设计

## 目标

将 AD（Active Directory）靶场集成进现有的 CI/CD 打包流程和平台侧靶场管理系统，同时在平台端根据运行环境的硬件能力决定是否允许部署。

## 背景

AD 靶场使用 dockur/windows（QEMU/KVM in Docker）运行 Windows Server 虚拟机，硬性依赖 x86_64 架构和 KVM 硬件虚拟化。现有平台支持 xbow/custom/argus 三类靶场，均为纯 Docker 容器，无硬件架构限制。

## 设计方案

### 1. benchmark.json schema 扩展

在 `benchmark.json` 中增加可选的 `requires` 字段，声明硬件依赖：

```json
{
  "id": "AD-001",
  "name": "AD-001 域初探",
  "requires": {
    "arch": "x86_64",
    "kvm": true
  },
  "level": 2,
  "win_condition": "flag",
  ...
}
```

字段定义：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `requires` | object \| null | null | 硬件需求声明，null 表示无特殊要求 |
| `requires.arch` | string \| null | null | 要求的 CPU 架构：`"x86_64"` 或 `"aarch64"` |
| `requires.kvm` | bool | false | 是否依赖 KVM 硬件虚拟化 |

向后兼容：Pydantic v2 默认忽略未声明字段，旧版平台遇到 `requires` 会跳过，靶场正常加载。

### 2. CI/CD 打包流程改动

仓库：`benchmark-challenges`
文件：`.github/workflows/pack-challenges.yml`

#### 2.1 变更检测

第 23 行 grep 正则加入 `AD`：

```bash
CHANGED=$(git diff --name-only "$BEFORE" "${{ github.sha }}" | grep -E '^(xbow|custom|argus|AD)/' | cut -d'/' -f1,2 | sort -u || true)
```

同理 fallback 分支（第 25 行）：

```bash
CHANGED=$(git ls-tree -r --name-only HEAD | grep -E '^(xbow|custom|argus|AD)/' | cut -d'/' -f1,2 | sort -u || true)
```

#### 2.2 manifest 生成

manifest 生成脚本扫描目录列表加入 `AD`：

```python
if category_dir.name in ("xbow", "custom", "argus", "AD") and category_dir.is_dir():
```

manifest 条目中透传 `requires` 字段：

```python
challenges.append({
    "name": ch_dir.name,
    "category": category_dir.name,
    "asset": asset_name,
    "description": meta.get("description", ""),
    "difficulty": meta.get("difficulty", ""),
    "tags": meta.get("tags", []),
    "flag_count": meta.get("flag_count", 1),
    "requires": meta.get("requires"),  # 新增
    "size": size,
})
```

### 3. 平台侧改动

仓库：`benchmark-platform`

#### 3.1 Benchmark model 扩展

文件：`benchmark_platform/models/benchmark.py`

```python
class Requirements(BaseModel):
    arch: str | None = Field(default=None, description='Required CPU architecture: x86_64 or aarch64')
    kvm: bool = Field(default=False, description='Requires /dev/kvm hardware virtualization')

class Benchmark(BaseModel):
    ...existing fields...
    requires: Requirements | None = Field(default=None, description='Hardware/environment requirements')
```

#### 3.2 Challenge model 扩展

文件：`benchmark_platform/base.py`

Challenge 增加两个字段（与现有 `emulated` 平级）：

```python
class Challenge(BaseModel):
    ...existing fields...
    emulated: bool = False
    unsupported: bool = False
    unsupported_reason: str = ""
```

#### 3.3 环境检测逻辑

文件：`benchmark_platform/utils/challenge.py`，`_create_challenge()` 方法内

在构造 Challenge 对象前，根据 `bm.requires` 和当前环境判定：

```python
import platform as _platform
from pathlib import Path

host_arch = _platform.machine()  # 'x86_64', 'arm64', 'aarch64'
has_kvm = Path('/dev/kvm').exists()

is_unsupported = False
unsupported_reason = ""

if bm.requires:
    if bm.requires.arch == "x86_64" and host_arch in ('arm64', 'aarch64'):
        is_unsupported = True
        unsupported_reason = "需要 x86_64 架构"
    elif bm.requires.arch == "aarch64" and host_arch not in ('arm64', 'aarch64'):
        is_unsupported = True
        unsupported_reason = "需要 ARM64 架构"
    if bm.requires.kvm and not has_kvm:
        is_unsupported = True
        unsupported_reason = "需要 KVM 虚拟化支持 (/dev/kvm)"
    if bm.requires.arch == "x86_64" and host_arch in ('arm64', 'aarch64') and bm.requires.kvm:
        unsupported_reason = "需要 x86_64 架构 + KVM 虚拟化"
```

构造 Challenge 时传入：

```python
challenge = Challenge(
    ...existing args...
    unsupported=is_unsupported,
    unsupported_reason=unsupported_reason,
)
```

#### 3.4 启动拦截

文件：`benchmark_platform/utils/challenge.py`，`start_challenge_instance()` 方法开头

```python
def start_challenge_instance(self, challenge_code: str) -> list[str]:
    challenge = self._find_by_code(challenge_code)
    if challenge.unsupported:
        raise RuntimeError(f"无法启动: {challenge.unsupported_reason}")
    ...existing logic...
```

#### 3.5 前端展示

文件：`benchmark_platform/web/context.py`，`_challenge_to_card()` 返回值增加：

```python
return {
    ...existing fields...
    "unsupported": challenge.unsupported,
    "unsupported_reason": challenge.unsupported_reason,
}
```

前端模板中对 `unsupported=True` 的卡片：
- 卡片整体添加 `opacity-50` 样式
- 隐藏「启动实例」按钮
- 在卡片底部显示黄色警告条：`⚠️ 当前环境不支持（{unsupported_reason}）`

### 4. AD 靶场 benchmark.json 修改

为三个 AD 靶场添加 `requires` 字段：

- `AD/AD-001/benchmark.json`
- `AD/AD-002/benchmark.json`
- `AD/AD-003/benchmark.json`

统一添加：

```json
"requires": {"arch": "x86_64", "kvm": true}
```

### 5. 向后兼容性

| 场景 | 行为 |
|------|------|
| 旧平台 + 新 benchmark.json（带 requires） | Pydantic 忽略未知字段，靶场正常加载，无环境检测 |
| 旧平台 + AD 靶场在 arm 上启动 | docker compose up 时因缺少 /dev/kvm 自然失败 |
| 新平台 + 旧 benchmark.json（无 requires） | requires=None，unsupported=False，行为不变 |
| 新平台 + AD 靶场在 arm 上 | 显示灰色卡片 + 警告，阻止启动 |

### 6. 改动文件清单

| 仓库 | 文件 | 改动类型 |
|------|------|----------|
| benchmark-challenges | `.github/workflows/pack-challenges.yml` | 修改 |
| benchmark-challenges | `AD/AD-001/benchmark.json` | 修改 |
| benchmark-challenges | `AD/AD-002/benchmark.json` | 修改 |
| benchmark-challenges | `AD/AD-003/benchmark.json` | 修改 |
| benchmark-platform | `benchmark_platform/models/benchmark.py` | 修改 |
| benchmark-platform | `benchmark_platform/base.py` | 修改 |
| benchmark-platform | `benchmark_platform/utils/challenge.py` | 修改 |
| benchmark-platform | `benchmark_platform/web/context.py` | 修改 |
| benchmark-platform | `benchmark_platform/web/templates/` (卡片模板) | 修改 |
