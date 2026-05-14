# AD 域渗透靶场

本目录包含基于 Windows Active Directory 的渗透测试靶场，使用 [dockur/windows](https://github.com/dockur/windows) 在 Docker 中运行 Windows Server 虚拟机。

## 环境要求

| 要求 | 说明 |
|------|------|
| 架构 | **x86_64** (不支持 ARM) |
| 虚拟化 | 需要 KVM 支持 (`/dev/kvm`) |
| 内存 | 至少 8GB 可用内存（单 DC 场景），16GB+（多机场景） |
| 磁盘 | 至少 80GB 可用空间 |
| 系统 | Linux (推荐 Debian/Ubuntu/Kali) |

> **注意：** 这些靶场无法在 ARM Mac、ARM Linux 或没有 KVM 的环境上运行。如果在虚拟机中运行，需要开启嵌套虚拟化。

## Windows ISO 准备

dockur/windows 首次启动时需要 Windows Server 2022 安装 ISO（约 4.7 GB）。默认行为是从 Microsoft 服务器自动下载，但国内网络通常很慢或不可用。

**推荐做法：预先下载 ISO 并放入容器存储。**

### 步骤

```bash
# 1. 下载 Windows Server 2022 ISO（可用代理或其他方式获取）
#    官方地址：https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022
mkdir -p /root/iso
curl -L -o /root/iso/win2022.iso "你的下载地址"

# 2. 启动容器（创建 volume）
cd AD-001
docker compose up -d dc

# 3. 将 ISO 复制到容器存储（必须命名为 custom.iso）
docker cp /root/iso/win2022.iso ad-001-dc-1:/storage/custom.iso

# 4. 重启容器开始安装
docker restart ad-001-dc-1
```

### 注意事项

- ISO 文件必须命名为 `custom.iso` 放在 `/storage` 目录下，dockur 才会识别并使用本地文件
- Windows 安装 + AD 配置全过程约 **15-20 分钟**，全程自动无需干预
- 安装完成后磁盘镜像保存在 Docker volume 中，后续重启不需要重新安装
- 如果执行 `docker compose down -v`（删除 volume），则需要重新安装

## 靶场列表

| 编号 | 难度 | 域名 | 攻击链 |
|------|------|------|--------|
| AD-001 | Medium | corp.local | 凭据泄露 → Kerberoasting → 域控 |
| AD-002 | Hard | north.local | SQLi → AS-REP Roasting → ACL 滥用 → DCSync |
| AD-003 | Hard | castle.local | SSRF → MSSQL xp_cmdshell → ADCS ESC1 → 域管 |

## 端口暴露策略

正式运行时，**仅暴露 web 容器的入口端口（80）给攻击者**。Windows VM 的管理端口不对外暴露，防止非预期解：

| 端口 | 用途 | 正式运行 | 说明 |
|------|------|----------|------|
| 80 | Web 入口 | 暴露 | 唯一合法攻击入口 |
| 8006 | noVNC (无认证) | **不暴露** | 可直接看桌面读 flag |
| 3389 | RDP | **不暴露** | dockur 默认密码 `P@ssw0rd!` 是公开的 |

攻击者需通过 web 漏洞进入内网后，才能在 Docker 内网中访问 DC 的 Kerberos/LDAP/SMB 等服务。

### 调试模式

开发调试时，可临时开启 VNC/RDP 端口观察 Windows 状态。在 `docker-compose.yml` 中取消注释：

```yaml
# 调试端口（正式运行时不暴露，防止非预期解）
# ports:
#   - "3389:3389"
#   - "8006:8006"
```

开启后：
- **VNC**: 浏览器访问 `http://<host-ip>:8006`（无需认证，直接看桌面）
- **RDP**: 使用 `Administrator` / `P@ssw0rd!` 连接（DC promotion 后变为域管密码 `DsrmP@ss2024!`）

## 启动与健康检查

```bash
cd AD-001  # 或 AD-002、AD-003
docker compose up -d
```

DC 容器的健康检查依赖 `/run/ready` 文件（由 dockur 在 Windows 就绪后创建）。首次安装时 `start_period` 设为 600 秒。如果超时，可手动检查：

```bash
# 查看容器日志
docker logs ad-001-dc-1

# 通过 VNC 查看 Windows 桌面（排障用）
# 浏览器访问 http://<host-ip>:8006

# 如果 Windows 已完成配置但健康检查未通过，可手动标记
docker exec ad-001-dc-1 touch /run/ready
```

## 验证靶场是否就绪

Windows OEM 自动化脚本会在配置完成后写入 `C:\OEM\setup.state`（内容为 `done`）和 `C:\OEM\ready.txt`。可通过 VNC 或 WinRM 检查。

## 攻击工具建议

- [impacket](https://github.com/fortra/impacket) — Kerberoasting、psexec、wmiexec、DCSync
- [john](https://github.com/openwall/john) / [hashcat](https://hashcat.net/) — 离线密码破解
- [Certipy](https://github.com/ly4k/Certipy) — ADCS 攻击 (AD-003)
- [BloodHound](https://github.com/BloodHoundAD/BloodHound) — AD 路径分析

