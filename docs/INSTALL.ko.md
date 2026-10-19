# ReviewLens 설치 가이드 (한국어)

[English installation guide — default](INSTALL.md) · [한국어 README](../README.ko.md)

ReviewLens는 Claude Code와 Codex에서 사용하는 하나의 [Agent Skill](https://agentskills.io/specification)입니다. 리뷰를 실행하기 위해 별도의 Python/Rust 패키지나 서버를 설치할 필요는 없습니다. 다음 방법 중 **하나**를 선택하세요.

> **GitHub 게시 전 주의:** `Tangeroooo/reviewlens`를 참조하는 원격 설치 명령은 해당 저장소가 실제로 생성되고 게시된 이후에 사용할 수 있습니다. 게시 이전에는 제공된 압축 파일을 풀고 아래 수동 설치 방법을 사용하세요.

## 방법 A — 공통 스킬 설치 (Claude Code + Codex)

`npx` 실행을 위해 Node.js/npm이 필요하지만, ReviewLens 자체를 실행할 때는 Node.js가 필요하지 않습니다.

**설치하려는 프로젝트 폴더에서** 실행합니다.

```bash
# 현재 프로젝트에서 Claude Code와 Codex가 모두 사용
npx skills add Tangeroooo/reviewlens --skill reviewlens -a claude-code -a codex

# 모든 로컬 프로젝트에서 사용하도록 개인 영역에 설치
npx skills add Tangeroooo/reviewlens --skill reviewlens -a claude-code -a codex -g
```

한쪽만 설치할 경우 불필요한 `-a` 옵션을 빼세요. 확인 없이 설치하려면 `-y`를 추가할 수 있습니다. 프로젝트 설치 경로는 `.claude/skills/`, `.agents/skills/`이고, 개인 설치 경로는 `~/.claude/skills/`, `~/.agents/skills/`입니다. 설치 프로그램이 공용 사본으로 심볼릭 링크를 만들 수도 있습니다.

호출:

- Claude Code: `/reviewlens Review my changes against origin/main.`
- Codex: `$reviewlens Review my storage changes with Rust and Systems lenses.`

## 방법 B — Claude Code 네이티브 플러그인 (전용 서브 에이전트 지원)

**Claude Code 세션 안에서** 다음 명령을 입력합니다.

```text
/plugin marketplace add Tangeroooo/reviewlens
/plugin install reviewlens@reviewlens-marketplace
```

터미널에서 Claude Code CLI를 직접 사용할 경우:

```bash
claude plugin marketplace add Tangeroooo/reviewlens
claude plugin install reviewlens@reviewlens-marketplace
```

이후 `/reviewlens:reviewlens Review this PR.`처럼 호출합니다. 이 설치 방식에는 Claude Code에서 인식하는 `reviewlens-reviewer`, `reviewlens-validator` 서브 에이전트 정의도 포함됩니다. 모든 리뷰에서 에이전트가 고정 개수로 실행되는 것은 아닙니다.

**Claude Code에 방법 A와 B를 중복 설치하지 않는 것을 권장합니다.** Codex는 방법 A, Claude Code는 방법 B로 설치할 경우 방법 A를 Codex 전용으로 실행하세요.

```bash
npx skills add Tangeroooo/reviewlens --skill reviewlens -a codex -g
```

## 방법 C — 수동 설치 / 로컬 ZIP

압축 파일을 해제하거나, GitHub 게시 후 `git clone https://github.com/Tangeroooo/reviewlens.git`으로 저장소를 가져옵니다. 저장소 루트에 있는 `skills/reviewlens/` 폴더가 실제 스킬입니다.

macOS/Linux:

```bash
# Claude Code: 개인 스킬
mkdir -p ~/.claude/skills
cp -R skills/reviewlens ~/.claude/skills/reviewlens

# Codex: 개인 스킬
mkdir -p ~/.agents/skills
cp -R skills/reviewlens ~/.agents/skills/reviewlens
```

현재 프로젝트에만 설치하고 싶다면 홈 경로 대신 대상 프로젝트의 `.claude/skills/reviewlens`, `.agents/skills/reviewlens`를 사용합니다.

Windows PowerShell (압축 해제한 저장소 루트에서):

```powershell
New-Item -ItemType Directory -Force "$HOME/.claude/skills" | Out-Null
Copy-Item -Recurse -Force "skills/reviewlens" "$HOME/.claude/skills/reviewlens"
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
Copy-Item -Recurse -Force "skills/reviewlens" "$HOME/.agents/skills/reviewlens"
```

동일한 목적지 폴더가 이미 있다면 폴더가 중첩되지 않도록 확인한 후 교체하세요. 스킬 목록에 바로 나타나지 않으면 Claude Code 또는 Codex를 재시작합니다.

## 설치 검증

**다운로드한 ReviewLens 저장소 루트에서** 다음 명령을 실행합니다.

```bash
python3 -m unittest discover -s tests -v
# Claude Code CLI가 설치된 경우 선택적으로 실행
claude plugin validate .
```

Claude Code의 단독 설치는 `/reviewlens`, 플러그인 설치는 `/reviewlens:reviewlens`, Codex는 `/skills` 또는 `$reviewlens`로 확인합니다. 실제 Git diff를 대상으로 리뷰를 요청하고 결과에 **리뷰 범위, 모드, 검토한 불변식, 코드 확인과 테스트 실행의 차이, 실제 서브 에이전트 사용 여부**가 기록되는지 확인하세요. 명세가 없다면 Spec 결과는 통과가 아닌 **미평가**로 보고해야 합니다.

## 리뷰 모드 사용 예시

```text
# Claude Code 네이티브 플러그인
/reviewlens:reviewlens origin/main 대비 이 PR을 Adversarial 모드로 리뷰해줘. 취소와 복구 경로를 집중 검증해줘.

# Claude Code 단독 스킬
/reviewlens 작업 트리를 적대적으로 검토하고 불변식과 미검증 경로를 보고해줘.

# Codex
$reviewlens Adversarial mode로 Storage 변경의 반례를 찾아 검증해줘.
```

위험도가 낮은 변경은 Standard가 기본이며, 고위험 변경은 Adversarial을 자동 선택합니다. 독립 Challenger는 **서브 에이전트가 실제 지원되는 경우에만** 실행됩니다. 지원하지 않는 경우 단계별 단일 에이전트 검토로 전환하고 독립 실행이 아니었음을 표시합니다. Fuzzing·Miri·장애 주입·고비용 테스트는 승인 없이 실행하지 않습니다. 성능 평가 방법은 [한국어 평가 가이드](EVALUATION.ko.md)를 참고하세요.

## 업데이트

- 공통 설치 도구: `npx skills update reviewlens` (설치 범위에 맞춰 선택)
- Claude Code 플러그인: 플러그인 업데이트 기능 사용
- 수동 설치: 복사한 `skills/reviewlens/` 폴더를 새 버전으로 교체

## 문제 해결 및 보안

- **스킬이 보이지 않음:** `reviewlens/SKILL.md` 경로에 파일이 있는지 확인합니다. `reviewlens/reviewlens/SKILL.md`처럼 중첩된 상태가 아니어야 합니다.
- **서브 에이전트가 실행되지 않음:** 호스트에서 서브 에이전트를 제공하지 않을 수 있습니다. 이 경우 별도 단계 검토로 전환하며, 독립 검증을 했다고 주장하지 않습니다.
- **Spec 문서가 없음:** Spec 검토를 건너뛰고 미평가로 표시합니다. 다른 리뷰는 계속 진행합니다.
- **비교 대상이 없음:** Git 기준 브랜치를 알려주거나 미커밋 변경사항을 준비해야 합니다. 스킬이 임의의 기준점을 선택해서는 안 됩니다.
- **권한:** 읽기에 필요한 저장소 접근 권한만 허용하고, 외부 스킬과 쉘 명령은 설치 전에 확인하세요. 실제 권한 제어는 Claude Code/Codex의 실행 환경이 담당합니다.
- **중복 명령:** Claude Code 단독 스킬과 플러그인이 함께 설치되어 있는지 확인합니다.

참고: [Claude Code 스킬](https://code.claude.com/docs/en/skills), [Claude Code 마켓플레이스](https://code.claude.com/docs/en/plugin-marketplaces), [Codex 스킬](https://developers.openai.com/codex/skills).
