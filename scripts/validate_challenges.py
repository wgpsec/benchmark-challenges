#!/usr/bin/env python3
"""Validate all challenges comply with the dynamic flag specification.

Checks:
- benchmark.json exists with non-empty canaries and hint
- Each canary value appears in at least one source file
- .env exists with FLAG variable(s)
- .env FLAG values are consistent with canaries
- No Dockerfile ARG FLAG usage
- docker-compose.yml ports use string format
- Orphan FLAG{...} literals not declared in canaries (warning)

Exit code 0 = all pass, 1 = errors found.
"""

import json
import re
import sys
from pathlib import Path

TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.go', '.rb', '.php', '.java', '.sh', '.bash',
    '.sql', '.html', '.htm', '.xml', '.json', '.yaml', '.yml', '.toml',
    '.env', '.txt', '.md', '.cfg', '.ini', '.conf', '.tpl', '.tmpl',
    '.jsx', '.tsx', '.vue', '.css', '.csv',
}
TEXT_FILENAMES = {'Dockerfile', 'Makefile', 'Procfile'}
FLAG_LITERAL_RE = re.compile(r'[Ff][Ll][Aa][Gg]\{[\w-]+\}')
GENERIC_FLAGS = {
    'FLAG{default}', 'FLAG{placeholder}', 'FLAG{test_flag}',
    'FLAG{default_flag}', 'flag{default}',
}


def is_text_file(fpath: Path) -> bool:
    return fpath.suffix.lower() in TEXT_EXTENSIONS or fpath.name in TEXT_FILENAMES


def collect_text_content(challenge_dir: Path) -> str:
    parts = []
    for fpath in challenge_dir.rglob('*'):
        if not fpath.is_file() or not is_text_file(fpath):
            continue
        try:
            parts.append(fpath.read_text(encoding='utf-8'))
        except (UnicodeDecodeError, OSError):
            continue
    return '\n'.join(parts)


def validate_challenge(challenge_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    bm_path = challenge_dir / 'benchmark.json'
    if not bm_path.exists():
        errors.append("缺少 benchmark.json")
        return errors, warnings

    try:
        meta = json.loads(bm_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError) as e:
        errors.append(f"benchmark.json 解析失败: {e}")
        return errors, warnings

    canaries = [c for c in meta.get('canaries', []) if c]
    if not canaries:
        errors.append("canaries 为空或缺失")

    if not meta.get('hint'):
        errors.append("hint 字段为空或缺失")

    env_path = challenge_dir / '.env'
    if not env_path.exists():
        errors.append("缺少 .env 文件")
    else:
        env_content = env_path.read_text(encoding='utf-8')
        env_flag_re = re.compile(r'^(FLAG(?:_\w+|[0-9]*))\s*=\s*["\']?([^"\'\n]+)["\']?', re.MULTILINE)
        env_matches = env_flag_re.findall(env_content)
        if not env_matches:
            errors.append(".env 中未找到 FLAG 变量")
        elif canaries:
            env_values = [m[1].strip().strip('"').strip("'") for m in env_matches]
            for val in env_values:
                if val and val not in canaries and val not in GENERIC_FLAGS:
                    warnings.append(f".env FLAG 值 '{val[:40]}' 不在 canaries 中")
                    break

    if canaries:
        all_text = collect_text_content(challenge_dir)
        for canary in canaries:
            if canary not in all_text:
                errors.append(f"canary '{canary[:50]}' 未在源码中找到")

    for df in challenge_dir.rglob('Dockerfile'):
        try:
            content = df.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        if re.search(r'^\s*ARG\s+FLAG', content, re.MULTILINE):
            rel = df.relative_to(challenge_dir)
            errors.append(f"{rel}: 使用了 ARG FLAG（会烘焙进镜像层）")

    compose_path = challenge_dir / 'docker-compose.yml'
    if compose_path.exists():
        try:
            import yaml
            data = yaml.safe_load(compose_path.read_text(encoding='utf-8'))
            for svc_name, svc in (data or {}).get('services', {}).items():
                for p in svc.get('ports', []):
                    if isinstance(p, int):
                        errors.append(f"服务 {svc_name} 端口 {p} 必须是字符串格式 \"host:container\"")
        except ImportError:
            pass
        except Exception:
            pass

    if canaries:
        all_text = collect_text_content(challenge_dir)
        found_flags = set(FLAG_LITERAL_RE.findall(all_text))
        found_flags -= GENERIC_FLAGS
        orphans = found_flags - set(canaries)
        if orphans:
            orphan_list = sorted(orphans)[:5]
            warnings.append(f"发现未在 canaries 中声明的 flag: {orphan_list}")

    return errors, warnings


def discover_challenges(root: Path) -> list[Path]:
    challenges = []
    for bm in sorted(root.rglob('benchmark.json')):
        if '.git' in bm.parts:
            continue
        challenges.append(bm.parent)
    return challenges


def main():
    root = Path('.')
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])

    challenges = discover_challenges(root)
    if not challenges:
        print("未发现任何靶场")
        sys.exit(1)

    total_errors = 0
    total_warnings = 0

    print(f"校验 {len(challenges)} 个靶场...\n")

    for cdir in challenges:
        errors, warnings = validate_challenge(cdir)
        if errors or warnings:
            rel = cdir.relative_to(root) if cdir != root else cdir
            print(f"{'❌' if errors else '⚠️ '} {rel}")
            for e in errors:
                print(f"    ERROR: {e}")
            for w in warnings:
                print(f"    WARN:  {w}")
            total_errors += len(errors)
            total_warnings += len(warnings)

    print(f"\n{'='*60}")
    print(f"结果: {len(challenges)} 靶场, {total_errors} 错误, {total_warnings} 警告")

    if total_errors:
        print("\n校验失败 — 请修复上述 ERROR 后重新提交")
        sys.exit(1)
    else:
        print("\n校验通过 ✓")
        sys.exit(0)


if __name__ == '__main__':
    main()
