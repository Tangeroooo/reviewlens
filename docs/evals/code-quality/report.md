# 코드 품질 단계의 독립 적용 시험

2026-11-27. Q1–Q5와 advisory 분리가 실제 검토에서 작동하는지 작은 합성 변경 두 개로 확인했다. **전체 ReviewLens 검토나 이전 버전 대비 탐지율 benchmark는 아니다.**

## 입력과 검토 범위

- 공통 [base](base/REQUEST.md)는 상태 API와 queue 선택에서 retry 조건을 각각 계산한다. 요청은 두 공개 함수의 출력·순서를 유지하면서 정책을 중앙화하는 것이다.
- [case-a](case-a/policy.py)는 7칸 위치 기반 list를 반환하고 두 소비자가 `[0]`과 `[6]`을 읽는다. [case-b](case-b/policy.py)는 필요한 Boolean을 반환하는 공통 predicate를 사용한다. 주 agent가 만든 합성 사례이며 두 변형 모두 현재 출력은 맞도록 구성했다.
- 각 변경의 [refs](refs.json), 원본 스냅샷과 검토 전에 작성한 [기준](ground-truth.md)을 보존했다. 임시 Git 저장소의 commit ID이며 이 저장소의 commit을 뜻하지 않는다.
- 별도 새 문맥 worker 두 명에게 자신의 base/target, 사용자 요청, 관련 General/worker 지침만 주었다. 다른 변형·예상 답·기존 결과는 읽지 않도록 했다. 공유 파일시스템 접근 자체를 격리한 것은 아니다.
- 맡긴 역할은 General의 Q1–Q5 부분 검토다. 코드 탐색 전에 각각 [A 계획](a-plan.md), [B 계획](b-plan.md)을 기록하고 소스·호출자·테스트를 읽었다. 전체 스킬의 Spec/Performance/Challenger/독립 Coverage Auditor를 수행하도록 맡긴 시험이 아니다.

## 결과와 판정

| 사례 | Q1–Q5 | 품질 제안 | 실행 결함 후보 | 실제 실행 |
| --- | --- | --- | --- | --- |
| A | 모두 inspected | A-1 하나: 생산자와 두 소비자가 위치 인덱스를 맞추는 비용을 줄이도록 Boolean predicate 사용. Q1–Q4를 중복 제거 | 0 | 기존 공개 API 테스트 3개 통과 |
| B | 모두 inspected | 0. 공통 predicate와 두 소비자의 책임 분리가 현재 요구에 비례함 | 0 | 기존 공개 API 테스트 3개 통과 |

전체 근거·반증·한계는 [A 보고서](a-review.md), [B 보고서](b-review.md)에 있다. 평가자는 임의의 dataclass 도입, 작은 helper 제거, helper 전용 테스트를 의무화하지 않았다. A에서도 list의 가변성이 실제 오류를 일으킨다고 주장하지 않았고, Q5는 기존 공개 테스트 접점이 유지되어 별도 제안을 하지 않았다.

주 agent는 validator의 advisory 기준으로 A-1을 소스에 재대조했다. 실제 소비자는 두 곳이며 모두 0번 ID와 6번 판정만 사용한다. 나머지 위치를 소비하는 계약, wire format, plugin 확장 요구는 없다. 기존 정책 중앙화의 이점은 인정하면서 필요한 Boolean만 반환하면 현재의 필드 해독·배치 결합 비용을 줄일 수 있다. 공개 signature·결과·순서를 보존하며, 내부 helper와 두 호출자를 함께 바꿔야 하는 trade-off가 있다. 판정은 **supported advisory**이고 런타임 결함이나 병합 차단 사유로 올리지 않았다. 이는 코디네이터의 소스 확인이며 별도의 독립 validator 실행은 아니다.

## 재현과 검증

각 `base/`, `case-a/`, `case-b/` 디렉터리에서 다음을 실행한다.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v
```

검토 worker는 각 target의 3개 테스트를 실행했다. 저장소 보존 후 주 agent는 base와 두 target 각각에서 같은 3개 테스트를 실행해 통과를 확인했다. 소스 수정이나 새로운 의존성은 없다. base와 target 디렉터리를 비교하면 당시 diff를 재구성할 수 있고, [스냅샷 해시](verification.json)로 보존된 자료를 확인할 수 있다.

저장소의 기존 배포·coverage 검사 30개와 공식 skill validator를 실행했다. 이 검사는 패키지·계약·회계 처리를 검사하며 모델의 코드 품질 판단을 증명하지 않는다. Claude CLI가 설치되어 있지 않아 `claude plugin validate`는 실행하지 않았다.

## 남은 한계

지침에 나온 패턴에 가까운 작은 Python 사례 두 개다. 원본에서 좋은 품질 문제를 발견하는 일반적 능력, 실제 PR의 오탐률·개선 효과, 모든 Q 항목의 긍정 사례, Rust·동시성·성능 회귀 유지 여부는 독립 행동 평가하지 않았다. 기존 버전과의 통제 비교나 전체 review/audit 흐름도 수행하지 않았다. 개별 Q 기록을 작성한 결과와 실제 사람의 유지보수 시간 개선을 구분한다.
