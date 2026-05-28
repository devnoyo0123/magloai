# Research Notes

## uv 가상환경에서 pip 실행하기

### uv vs 표준 venv 차이

`pyvenv.cfg` 파일로 구분 가능:

```bash
# uv로 만든 가상환경 (magloai 프로젝트)
cat .venv/pyvenv.cfg
# home = /Users/.../uv/python/cpython-3.10.18-...
# uv = 0.8.0              ← 이 줄이 있으면 uv로 만든 것
# prompt = magloai

# 표준 python -m venv로 만든 가상환경
# home = /usr/bin/python
# uv = 0.8.0 줄이 없음
```

### 핵심 차이: pip 바이너리 없음

uv로 만든 가상환경에는 `pip` 바이너리가 존재하지 않는다:

```bash
# activate 후 pip 실행 → command not found
source .venv/bin/activate
pip install something
# zsh: command not found: pip
```

### 해결 방법

**`uv pip` 사용**:

```bash
# activate 없이도 가능
uv pip install <package>
uv pip install --upgrade <package>

# activate 후에도 동일
source .venv/bin/activate
uv pip install <package>
```

**또는 `python -m pip`** (uv venv에도 pip 모듈은 설치되어 있을 수 있음):

```bash
source .venv/bin/activate
python -m pip install <package>
```

### 요약

| 방법 | 명령어 | 비고 |
|------|--------|------|
| uv pip | `uv pip install <pkg>` | 권장. 빠름 |
| python -m pip | `python -m pip install <pkg>` | pip 모듈이 있을 때만 |
| pip 직접 | `pip install <pkg>` | ❌ uv venv에서는 불가 |
