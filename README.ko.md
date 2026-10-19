# ReviewLens

**불변식을 의심하고 반례를 검증하는 적대적 코드 리뷰 스킬입니다. 범용 코드부터 Rust·시스템·데이터베이스까지 지원합니다.**

ReviewLens는 **Claude Code와 OpenAI Codex**에서 사용할 수 있는 [Agent Skill](https://agentskills.io/specification)입니다. 코드의 변경 범위를 파악하고 필요한 리뷰 관점만 선택합니다. 서브 에이전트가 지원되는 환경에서는 독립적인 리뷰와 Finding 검증을 수행하며, 지원되지 않는 환경에서는 단계별 검토로 전환합니다.

[English README (default)](README.md) · [영어 설치 안내](docs/INSTALL.md) · [한국어 설치 안내](docs/INSTALL.ko.md)

## 주요 특징

| 관점 | 검토 내용 | 실행 조건 |
| --- | --- | --- |
| **General / Standards** | 정확성, 설계, 테스트, 하위 호환성, 저장소 코딩 규칙 | 항상 |
| **Spec** | 요구사항 미구현, 의도하지 않은 동작 변경 | 실제 명세가 있을 때 |
| **Rust** | Unsafe 불변식, 소유권, FFI, panic, lock, Rust 관용구 | Rust 변경 시 |
| **Systems** | Async/Cancellation, Backpressure, 메모리 예산, DB 정합성·복구 | 관련 시스템 코드 변경 시 |

일반 변경은 **Standard**(발견용 리뷰 1~3회), `unsafe`·Storage Recovery·인증·동시성 등 고위험 변경은 **Adversarial** 모드로 검토합니다. Adversarial은 독립 **Challenger** 리뷰(서브 에이전트 지원 시)와 모든 실질적 결함 후보의 반증 검증을 추가합니다. Spec 결과와 기술/규칙 검토는 별도로 보고합니다.

### 검토 정책

- **프로덕션 `unwrap()`/`expect()` 금지**: 원칙적으로 사용하지 않으며, 단순 규칙 위반과 실제 panic 위험을 구분합니다. 테스트 코드는 예외입니다.
- **`parking_lot`**: 기계적으로 권장하지 않습니다. Lock 경합, poisoning, 비동기 경계, 의존성 비용과 기존 관례를 검토합니다.
- **`tracing`**: 프로젝트에서 사용하는 로깅 체계를 따릅니다. 특정 crate로의 교체를 강제하지 않습니다.
- **Finding**: 불변식, 변경 위치, 재현 조건·실행 경로, 영향, 기존 방어 로직, 수정·테스트 방향을 요구합니다. 반증되거나 미확인인 가설은 확정 버그로 보고하지 않습니다.
- Rust 이외의 언어도 General/Spec 리뷰로 검토할 수 있습니다.

## 리뷰 강도 선택

- **Standard**: 일반적인 PR의 정확성·설계·요구사항·필요한 Rust/Systems 검토.
- **Adversarial**: 실제 불변식을 식별하고, 충돌/취소/재시도/크래시 등 반례를 찾으며, 독립 검증과 Coverage를 기록. 고위험 변경에 자동 적용하거나 명시적으로 요청 가능.

```text
/reviewlens:reviewlens origin/main 대비 이 Segment 변경을 적대적으로 검토해줘.
$reviewlens Adversarial mode로 Rust 동시성·복구 실패 경로를 검증해줘.
```

Challenger가 증거를 제시한 가설도 Validator 검증 전에는 확정 결함이 아닙니다. **코드 확인과 실제 테스트 실행을 구분**해 보고하도록 했습니다. 실제 버그 탐지율 평가 방법은 [한국어 평가 가이드](docs/EVALUATION.ko.md)를 참고하세요.

## 빠른 설치

GitHub에 저장소가 게시된 후 다음 명령을 사용할 수 있습니다.

```bash
# Claude Code + Codex, 현재 프로젝트에 설치
npx skills add Tangeroooo/reviewlens --skill reviewlens -a claude-code -a codex
```

Claude Code의 네이티브 플러그인과 전용 서브 에이전트를 사용하려면 대신 다음을 사용합니다.

```text
/plugin marketplace add Tangeroooo/reviewlens
/plugin install reviewlens@reviewlens-marketplace
```

호출은 Claude Code 플러그인 `/reviewlens:reviewlens`, 단독 스킬 `/reviewlens`, Codex `$reviewlens`입니다. **동일한 Claude Code 환경에 플러그인과 단독 스킬을 중복 설치하지 않는 것을 권장합니다.**

[한국어 전체 설치 가이드](docs/INSTALL.ko.md)에서 글로벌 설치, 수동 설치, 검증, 문제 해결을 다룹니다.

## 설계

```text
변경사항/리뷰 범위 확인
         |
  General / Standards
  Spec (명세가 있으면)
  Rust + Systems (관련 코드라면)
  Challenger (Adversarial에서만)
         |
  후보 Finding 통합
         |
  독립 반증 검증 (가능한 경우)
         |
  확인된 결함 + 검토 Coverage
```

스킬 핵심 파일은 `SKILL.md`, `agents/`의 두 개의 프롬프트 계약, `references/`의 세 문서로 총 **6개**입니다. Claude Code 플러그인 메타데이터와 전용 Agent 어댑터는 별도로 제공됩니다. 별도 서버나 패키지를 실행하지 않습니다.

## v0.2.0 변경사항

6개 핵심 파일은 유지하면서 적대적 Challenger 역할, 불변식/실패 가설 추적, 강화된 Rust·Storage 실패 매트릭스, 검증된 Finding과 미확인 가설의 구분을 추가했습니다. 구조 검증 테스트는 실제 리뷰 탐지율을 증명하지 않습니다.

## GitHub 게시 (유지보수자 전용)

압축을 해제한 저장소 루트에서 `gh`를 **Tangeroooo 개인 계정**으로 인증한 뒤 다음을 실행할 수 있습니다.

```bash
bash scripts/publish.sh
```

스크립트는 GitHub 로그인 계정과 GitHub.com 호스트를 검증하며, 이미 존재하는 저장소/원격 또는 다른 저장소의 하위 폴더에서는 실행을 거부합니다. 테스트 통과 후 **해당 커밋에 한정하여** 개인 계정용 no-reply 작성자와 커미터를 사용합니다. 회사 계정이나 전역 Git 작성자 정보를 사용하지 않습니다.

## 출처와 라이선스

Trail of Bits, NVIDIA Switchyard, Matt Pocock, Google Engineering Practices, obra Superpowers의 **설계 개념과 검토 관점**을 참고했습니다. 원본 프롬프트를 그대로 조합하거나 복사하지 않았습니다. 출처와 각 프로젝트의 라이선스는 [SOURCES.md](docs/SOURCES.md)에 설명합니다. ReviewLens의 독립적으로 작성한 파일은 [MIT](LICENSE)입니다.

대상 저장소: **[Tangeroooo/reviewlens](https://github.com/Tangeroooo/reviewlens)**.
