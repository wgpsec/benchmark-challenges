# Dockur Boot Timeout Fix

## Problem

AD 系列靶机的 DC/DB 容器（dockurr/windows）在首次启动时被容器内部的 boot 检查杀死。

根因链：
1. `docker compose down -v` 删除 `dc-data` 命名卷（Windows 虚拟磁盘），确保每次干净环境 + 动态 flag
2. 每次启动都是全新 Windows 安装（从 ISO）
3. dockur 的 `/run/entry.sh` 中硬编码 `( sleep 30; boot ) &`
4. `boot()` 函数检查 QEMU PTY 文件大小 >7 字节，首次安装时 UEFI 图形模式无 serial 输出
5. 30 秒后 boot() 误判为启动失败，kill QEMU（signal 15）

## Design

在 docker-compose.yml 中覆盖 DC/DB 服务的 entrypoint + command，在执行原始 entry.sh 之前用 sed 将 `sleep 30` 改为 `sleep 1800`。

```yaml
entrypoint: ["/usr/bin/tini", "-s", "--"]
command: ["/bin/sh", "-c", "sed -i 's/sleep 30/sleep 1800/' /run/entry.sh && exec /run/entry.sh"]
```

### 为什么是 sed 而非挂载文件

- 挂载 `/run/entry.sh` 需要维护完整文件副本，dockur 升级后可能不兼容
- sed 只改一个数字，对版本变化容忍度高
- 如果 dockur 改了格式导致 sed 不匹配，不会报错，只是回退到 30 秒默认行为（安全降级）

### 保留 tini

原始 entrypoint 是 `/usr/bin/tini -s /run/entry.sh`。tini 负责信号转发和僵尸进程回收。新设计中 tini 仍是 PID 1，`exec /run/entry.sh` 确保 entry.sh 替换 shell 进程。

### 不影响正常流程

`( sleep N; boot ) &` 是纯后台检查进程，不参与启动逻辑。改为 1800 秒只是推迟"你还活着吗"检查。QEMU 启动、Windows 安装、网络配置等一切正常流程不受影响。

## 影响范围

| 文件 | 服务 |
|------|------|
| `AD/AD-001/docker-compose.yml` | dc |
| `AD/AD-002/docker-compose.yml` | dc |
| `AD/AD-003/docker-compose.yml` | dc, db |

## 平台代码

不变。`docker compose down -v --remove-orphans` 保留，确保干净环境。

## 风险

- dockur 未来版本如果删除或重命名 `sleep 30` 行：sed 不匹配，静默跳过，回退默认行为。最坏情况是回到当前问题，不会引入新问题。
- 首次安装 Windows 需 10-20 分钟：已有 `_COMPOSE_TIMEOUT_WINDOWS = 1800` 覆盖，平台不会提前超时。
