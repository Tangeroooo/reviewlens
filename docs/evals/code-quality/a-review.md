# case-a 코드 품질 검토

핵심 결론: retry 판정의 공유는 구현되었고, 검사한 공개 API 결과에서 실제 버그 후보는 발견하지 않았다. 다만 필요한 Boolean 대신 7칸짜리 위치 기반 list를 전달하면서 두 호출자가 필드 순서를 알아야 하는 유지보수 비용이 생겼다. 이를 하나의 advisory로 제안한다.

범위는 General worker의 Q1–Q5 품질 점검이다. 전체 ReviewLens, 독립 audit, 별도 Spec/Performance/Security 검토를 완료했다는 의미가 아니다. 근거 요구사항은 REQUEST.md:3–9이며 비교는 base `42a7eb3067215787e75bdbf07e110d3f0f136cfd` → target `c70a8fca8b9c66e61e7210f298fdbeacc039cf99`이다. 코드 탐색 전 계획은 `/tmp/reviewlens-quality-trial/a-plan.md`에 기록했다.

## 항목별 coverage

| ID | 상태 | 검사 근거와 결과 | 실제 범위·미검사 경계 | 실행 상태 |
| --- | --- | --- | --- | --- |
| Q1 | inspected | api.py:7–8, queue_selection.py:7–9의 실행 조건과 출력은 inspect_job의 [0] 및 [6] 의미를 policy.py:2–9에서 확인해야 이해된다. base는 id와 조건이 호출 지점에 직접 드러났다. A-1에 통합한다. | 변경 함수 전체와 공개 API를 호출하는 test_policy.py 전체를 읽었다. 다른 저장소의 소비자는 접근 범위 밖이다. | 공개 API 테스트 3개 통과. 가독성 판단은 소스 비교이다. |
| Q2 | inspected | 두 공개 함수가 job/retry_limit를 공급하고 helper 반환값 중 id와 retryable만 소비한다. policy.py는 기존 job 필드와 중간 판정까지 반환한다. 판정용 interface가 job 복사 및 내부 필드 배치를 함께 노출한다. A-1에 통합한다. | api.py, queue_selection.py, policy.py 전체 및 입력 요구사항을 확인. hidden global/외부 side effect는 없다. | 두 공개 소비자를 기존 테스트로 실행. |
| Q3 | inspected | list 생산은 policy.py:2–10 한 곳, 읽기는 api.py:8, queue_selection.py:8–9이다. 위치 1–5는 읽히지 않으며 4/5의 부분 판정과 6의 최종 판정이 각각 계산된다. 필드 위치를 생산자와 두 소비자가 맞춰야 한다. A-1에 통합한다. | 모든 Python 파일에서 반환값 사용과 갱신을 검색. 반환 후 mutation, 공유 lifecycle, 영속 format은 발견하지 못했다. REQUEST.md:8도 format 제약이 없다고 명시한다. 잘못된 상태가 실제 도달한다고 주장하지 않는다. | 기존 테스트는 소비 결과를 검증하며 list 내부를 직접 검증하지 않는다. |
| Q4 | inspected | 공유 policy module 자체는 요청된 중복 제거를 수행한다. 문제는 공유 module의 존재가 아니라 현재 호출자가 쓰지 않는 5개 필드까지 전달하는 interface이다. 확장 hook, mode, dependency는 없다. A-1로 한정한다. | 세 implementation 파일의 import와 helper 호출 전부, REQUEST.md:8–9의 plugin/확장성 불필요 조건을 확인. | 구조 판단은 소스 검사. 테스트 3개 통과. |
| Q5 | inspected | base에 두 번 있던 최종 retry 조건은 target policy.py:9 한 곳으로 모였다. 두 공개 함수는 명시적인 입력만 받으므로 별도 환경 setup 없이 테스트 가능하다. test_policy.py:6–28은 두 소비자의 실제 결과를 검증한다. 별도 advisory 없음. | `rg --files`, target `git ls-tree`, 모든 Python 파일의 retry/policy/eligible/queue/status/import/def 검색으로 fixture 전체의 구현·호출·테스트를 조사했다. 다른 독립 구현이나 환경 의존 seam은 없다. | 정상/경계/상태 제외/순서/빈 입력/limit=0을 포함한 기존 3개 테스트 통과. |

계획한 fixture 내 범위는 모두 조사했다. 조사 파일은 REQUEST.md, api.py, policy.py, queue_selection.py, test_policy.py의 5개이며, base의 api.py/queue_selection.py/test_policy.py를 직접 읽고 target diff와 비교했다. 새 policy.py는 diff로 전체를 확인했다. 범위 밖 history, sibling case, 평가/정답 자료와 다른 worker 산출물은 열지 않았다.

## 유지보수 advisory

ID / associated Q or other coverage IDs: A-1 / Q1, Q2, Q3, Q4

Changed location and related callers/sites: policy.py:1–10의 inspect_job 반환값; api.py:7–8의 status_rows; queue_selection.py:7–9의 retry_ids.

Present comprehension or maintenance cost: retry 판정을 이해하려면 두 호출 지점의 숫자 6을 helper의 일곱 번째 필드와 연결해야 한다. id도 기존 job에서 얻을 수 있는데 새 반환값의 위치 0에 의존한다. 두 소비자는 위치 1–5를 사용하지 않는다. 필드 배치를 수정할 때 생산자와 두 소비자의 숫자 인덱스를 함께 점검해야 하며, 부분 판정 두 개와 최종 판정은 현재 동일 비교식을 반복해서 표현한다. 실제 출력 오류나 도달 가능한 불일치 상태를 주장하는 것은 아니다.

Base -> target evidence and counterevidence: base의 두 공개 함수는 각자 `job["state"] == "failed" and job["attempts"] < retry_limit`를 계산했다. target은 최종 판정을 policy.py:9로 공유했으므로 정책 중앙화 자체는 개선이다. 그러나 새 7칸 list 및 숫자 인덱스는 base에 없던 표현 계약이다. 전체 fixture 검색상 다른 helper 소비자나 중간 필드 이용자는 없다. REQUEST.md:8–9는 영속/wire format, plugin API, 미래 configurable rule 요구가 없다고 명시한다. list는 함수 내부에서 만들어져 읽기만 하므로 mutation 버그의 근거는 없고, 공개 결과 테스트도 통과한다.

Minimal behavior-preserving correction: helper를 `is_retryable(job, retry_limit)`로 두고 기존 최종 비교의 Boolean만 반환한다. status_rows는 `job["id"]`와 helper 결과로 출력 row를 만들고, retry_ids는 helper 결과가 참일 때 `job["id"]`를 추가한다. 두 공개 signature와 순서, 결과는 유지한다. 별도 class/dataclass, 추가 dependency, 설정은 필요 없다.

Tradeoff / why retaining the current design might be appropriate: 내부 helper 및 두 호출 지점을 함께 수정해야 한다. 중간 판정 자료를 실제 소비하는 진단 기능이나 고정된 외부 record 계약이 있다면 구조화된 결과를 유지할 이유가 있지만, 허용된 fixture의 호출자와 요구사항에서는 그런 근거를 발견하지 못했다. 단순 필드 이름 추가보다 Boolean 반환이 현재 필요한 계약에 가깝다. 소스는 수정하지 않았다.

Status: proposed advisory

## 결함 후보와 반증

결함 후보: 0개. 검토한 유효 입력 조건에서 helper의 최종 판정은 요구된 식과 동일하다. 두 공개 함수는 입력 순서대로 한 번 순회하며 기존 결과 shape를 유지한다. 이 결론을 전체 correctness 검증으로 확대하지 않는다.

검토 후 배제한 가설:

- 숫자 인덱스가 현재 잘못된 필드를 읽는다: 배제. [0]은 id, [6]은 정확한 retry Boolean이다.
- 부분 판정 필드의 중복 때문에 현재 결과가 어긋난다: 배제. 현재 비교식은 일치하며 부분 필드는 소비되지 않는다. 문제는 유지보수 비용이다.
- list의 가변성 때문에 현재 공유 상태가 오염된다: 배제. 반환값을 수정하거나 저장하는 호출자는 없다.
- helper가 queue에서 이전보다 먼저 모든 필드를 읽으므로 누락된 필드 예외가 새 버그다: 요구사항 밖. REQUEST.md:6–7은 id/state/attempts 존재와 정수 범위를 보장한다. 입력 검증 추가를 요구하지 않는다.
- 새 helper 때문에 테스트가 어려워졌다: 배제. 기존 공개 API 테스트가 실제 helper를 거치며 mock/환경 setup이 없다.

## 실제 테스트와 남은 한계

Actually tested: `/tmp/reviewlens-quality-trial/case-a`에서 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v` 실행. 종료 코드 0, `Ran 3 tests`, `OK`.

- test_status_and_selection: failed이고 limit 미만인 두 작업 선택, limit와 같은 attempts 제외, running/done 제외, status row 및 queue의 입력 순서와 전체 결과 검증.
- test_empty: 두 공개 함수의 빈 결과 검증.
- test_disabled_retry: retry_limit=0에서 두 공개 함수가 retry를 허용하지 않음 검증.

Inspected: baseline/target 소스, 공개 함수 호출자 전체, 기존 테스트의 assertion. HEAD가 지정 target인 것을 확인했다. `git status --short`에서 untracked `__pycache__/`가 관찰되었으며 열거나 수정하지 않았다. 이번 테스트에는 bytecode 쓰기를 비활성화했다.

Not inspected / material unknowns: fixture 밖 소비자, 전체 ReviewLens 항목, 성능 측정, 독립 반박 검토는 범위 밖이다. baseline 테스트 실행, 신규 테스트 작성, 광범위한 입력 생성은 하지 않았다. 별도 test-gap advisory를 정당화할 구체적인 변경 계약의 누락은 이 품질 점검에서 찾지 못했다. 테스트 통과는 모든 유효 입력을 증명하지 않는다.

생략한 작업: 코드 수정, dependency 설치, network, 다른 agent 위임, 전체 audit.
남은 위험: A-1은 현재 실패의 증거가 아닌 표현 계약의 유지보수 비용이며, 외부 소비자는 확인하지 않았다.
