[中文文档](README.zh-CN.md) | English

# Benchmark Challenges

Challenge data repository for [benchmark-platform](https://github.com/wgpsec/benchmark-platform).

## Structure

```
xbow/          # 74 challenges from xbow-validation-benchmarks
custom/        # 4 custom challenges (XSS, Auth, etc.)
argus/         # 60 challenges from argus-validation-benchmarks
```

## Challenge Sources

| Source | Count | Link | Description |
|--------|-------|------|-------------|
| xbow | 74 | [xbow-validation-benchmarks](https://github.com/xbow-dev/xbow-validation-benchmarks) | Web app vulnerabilities across diverse frameworks |
| argus | 60 | [argus-validation-benchmarks](https://github.com/pensarai/argus-validation-benchmarks) | SSRF, XSS, SQLi, RCE, IDOR, deserialization (Next.js, Flask, Express, Go, Django, Rails, Spring Boot) |
| custom | 4 | — | Hand-crafted challenges for specific scenarios |

## Usage

This repo is consumed by benchmark-platform's Challenge Store feature. Challenges are automatically packaged and published as GitHub Release assets on each push.

You can browse and download challenges directly from the platform's Web UI sidebar (**Challenge Store**), or clone manually:

```bash
git clone https://github.com/wgpsec/benchmark-challenges /tmp/benchmarks
cp -r /tmp/benchmarks/xbow challenges/xbow
cp -r /tmp/benchmarks/custom challenges/custom
cp -r /tmp/benchmarks/argus challenges/argus
```

## Adding a Challenge

1. Create a directory under the appropriate category: `xbow/XBEN-XXX-24/`, `argus/APEX-XXX-25/`, or `custom/MY-CHALLENGE/`
2. Include at minimum: `docker-compose.yml`, `benchmark.json`, `.env`
3. Push to main — the GitHub Action will package and publish it automatically

## Challenge Format

```
XBEN-001-24/
├── docker-compose.yml    # Required
├── benchmark.json        # Metadata (name, description, level, points)
├── benchmark.yaml        # Optional, multi-flag definitions
├── .env                  # FLAG environment variable
└── app/ mysql/ ...       # Application code
```

## CI/CD

On every push to `main`, the GitHub Action:

1. Detects which challenge directories changed
2. Packs each changed challenge into a zip archive
3. Generates `manifest.json` listing all challenges
4. Uploads assets to the `latest` GitHub Release

Only changed challenges are re-packaged (incremental).

## WgpSec Agentic Ecosystem

benchmark-challenges is the data layer of the **WgpSec Agentic Ecosystem** — providing real-world vulnerable environments for evaluating AI agent offensive capabilities.

```
┌───────────────────── WgpSec Agentic Ecosystem ─────────────────────┐
│                                                                     │
│  Knowledge ➜ Service ➜ Execution ➜ Evaluation                      │
│                                                                     │
│  AboutSecurity ──▶ context1337 ──▶ tchkiller ──▶ benchmark-platform │
│  (Knowledge Base)  (MCP Server)    (Pentest Agent)  (Platform)     │
│                                         ▲                           │
│                                    PoJun (General Solver)           │
│                                         │                           │
│                              benchmark-challenges (this repo)       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

| Project | Role |
|---------|------|
| [AboutSecurity](https://github.com/wgpsec/AboutSecurity) | Structured pentest knowledge base (Skills, Dic, Payload, Vuln) |
| [context1337](https://github.com/wgpsec/context1337) | MCP Server — turns AboutSecurity into a searchable API for AI agents |
| [tchkiller](https://github.com/wgpsec/tchkiller) | Autonomous pentest agent with multi-round decision-making and team collaboration |
| [benchmark-platform](https://github.com/wgpsec/benchmark-platform) | CTF challenge platform for evaluating agent offensive capabilities |
| [benchmark-challenges](https://github.com/wgpsec/benchmark-challenges) | Challenge data repository — packed & distributed via GitHub Releases |
| PoJun | General-purpose AI problem-solving engine (private) |

## License

[MIT](LICENSE)
