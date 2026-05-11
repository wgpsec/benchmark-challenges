[中文文档](README.zh-CN.md) | English

# Benchmark Challenges

Challenge data repository for [benchmark-platform](https://github.com/wgpsec/benchmark-platform).

## Structure

```
xbow/          # Challenges from xbow-validation-benchmarks
custom/        # Custom challenges (XSS, Auth, etc.)
```

## Usage

This repo is consumed by benchmark-platform's Challenge Store feature. Challenges are automatically packaged and published as GitHub Release assets on each push.

You can browse and download challenges directly from the platform's Web UI sidebar (**Challenge Store**), or clone manually:

```bash
git clone https://github.com/wgpsec/benchmark-challenges /tmp/benchmarks
cp -r /tmp/benchmarks/xbow challenges/xbow
cp -r /tmp/benchmarks/custom challenges/custom
```

## Adding a Challenge

1. Create a directory under the appropriate category: `xbow/XBEN-XXX-24/` or `custom/MY-CHALLENGE/`
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

## License

[MIT](LICENSE)
