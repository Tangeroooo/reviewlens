# Case B 코드 품질 부분 검토

검토 범위에서 실제 defect 후보와 근거 있는 코드 품질 advisory는 모두 0건이다. 두 호출부에 중복되어 있던 retry 조건을 `policy.is_retryable()` 하나로 옮겼고, 공개 함수의 입력·출력과 순서를 유지한다. 별도 추상화나 상태를 추가하지 않아 요청에 비례하는 변경이다.

이 문서는 General의 Q1–Q5만 맡은 읽기 전용 부분 검토다. 완전한 ReviewLens 검토, 독립 감사, 별도 Spec/Performance 검토를 수행했다는 뜻은 아니다.

## 범위와 근거

- 저장소: `/tmp/reviewlens-quality-trial/case-b`
- base: `42a7eb3067215787e75bdbf07e110d3f0f136cfd`
- target 및 확인된 HEAD: `67275ef31815db82d5945dd0196173c0cb7c2b7b`
- 사전 계획: `/tmp/reviewlens-quality-trial/b-plan.md`; 코드 파일 목록과 diff를 열기 전에 작성했다.
- 요구사항: `REQUEST.md:3–9`. 재시도 조건의 중앙화, 두 공개 함수의 시그니처·출력·입력 순서 보존, 유효한 job 입력, 작은 메모리 내 목록, 외부 저장 형식·plugin·향후 가변 정책 불필요가 명시되어 있다.
- 발견 방법: `rg --files`, 지정 base/target의 `git diff`, base의 `git show`, `rg -n 'retry|attempt|state|policy|select|status' --glob '*.py' --glob '*.md' .`.
- 발견한 전체 Python 소스 4개와 `REQUEST.md`를 읽었다. 변경 파일은 `api.py`, `policy.py`, `queue_selection.py`이고, 기존 `test_policy.py`는 그대로다. target 대비 작업 파일 diff가 없다. 처음부터 존재한 미추적 `__pycache__/`는 읽거나 변경하지 않았다.

## Q1–Q5 coverage

| ID | 상태 | 실제 조사 범위와 근거 | 결과 및 반증 | 실행 상태 / 미확인 경계 |
|---|---|---|---|---|
| Q1 | inspected | base의 두 inline 조건과 target `api.py:4–5`, `queue_selection.py:4–5`, `policy.py:1–2`; 공개 함수를 호출하는 `test_policy.py:14–28` | `is_retryable(job, retry_limit)` 이름이 bool 판단을 드러내며 조건은 한 함수의 한 식이다. 호출부에서 mapping/filtering 목적도 직접 보인다. 멀리 떨어진 분기나 opaque flag를 해독해야 하는 경로가 없다. 줄바꿈 선호만으로 지적하지 않는다. | 기존 3개 공개 경로 테스트 통과. 저장소 밖 호출부는 제공되지 않아 조사하지 않았다. |
| Q2 | inspected | 테스트의 job 목록 → 두 공개 함수 → 공통 predicate → 상태 행 또는 ID 목록; 각 함수의 인자·반환값과 전체 본문 | predicate는 재시도 판단만, API는 결과 행 구성만, queue는 ID 선택만 맡는다. limit는 명시적으로 전달되고 전역 입력·숨은 부수효과·호출 순서 요구가 없다. 기존 공개 시그니처가 그대로다. | 동일한 테스트에서 두 소비자 출력 검증. 외부 API 서버나 실제 queue 서비스는 이 fixture에 없다. |
| Q3 | inspected | `policy.py:2`의 job 키 읽기, `api.py:5` 및 `queue_selection.py:5`의 ID 읽기, `test_policy.py:7–12,26`의 생산자 표현과 base의 동일 표현 | 기존 dictionary를 그대로 읽고 새 mutable 상태·병렬 필드·인덱스 표현을 만들지 않는다. API가 새 결과 dictionary를 생성하는 동작도 기존과 같다. 별도 dataclass나 검증 계층을 도입해야 할 현재 비용을 찾지 못했다. | 출력과 순서는 테스트로 확인. 입력 불변성 전용 assertion은 없으며, 소스에서 쓰기 연산이 없음을 확인했다. 비정상 입력은 명시된 범위 밖이다. |
| Q4 | inspected | 전체 Python 파일의 import/호출 검색, 신규 `policy.py` 전체, REQUEST.md의 의존성·확장 요구 제약 | 직접 import된 공통 함수는 실제 소비자 두 곳을 가진다. 공통 모듈은 API와 queue 중 하나가 다른 하나에 의존하지 않게 한다. 무사용 hook, wrapper 연쇄, mode/config, 새 외부 의존성이 없다. 두 줄짜리 모듈이라는 이유만으로 제거하면 중앙화 요구를 거스른다. | 실제 import와 두 호출 경로가 테스트에서 실행됨. plugin/배포 환경 검증은 수행하지 않았으며 요구사항에도 없다. |
| Q5 | inspected | 저장소 전체 Python/Markdown 정책 검색; base 두 조건 → target 한 조건; `test_policy.py` 전체의 assertion과 fixture | 정책 변경 지점이 두 곳에서 `policy.py:2` 한 곳으로 줄었다. 기존 테스트가 mock 없이 두 실제 호출부와 공유 함수를 실행하며 정상·비대상 상태·한계값·순서·빈 목록·limit 0을 검증한다. 환경 설정이나 별도 서비스 없이 판단을 실행할 수 있어 추가 seam 필요성이 없다. | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v` 실행, 3개 통과. 직접 helper 테스트, attempts가 limit보다 큰 값, 중복 ID의 별도 테스트는 없지만 기존 의미를 그대로 추출한 이 변경의 구체적 회귀나 테스트 장애로 보지 않았다. |

계획했던 변경 책임·호출자·생산/소비 표현·관련 정책·기존 테스트를 모두 확인했다. 저장소에는 위 네 Python 파일 외의 package나 별도 정책 구현이 발견되지 않았다. 호출 경계는 fixture에 실제 존재하는 테스트 → 공개 함수 → predicate → 반환값까지다. 범위 밖 운영 시스템이나 제공되지 않은 호출부까지 확인했다는 주장은 하지 않는다.

## Advisory 후보

없음. portable advisory 형식으로 제출할 만큼 현재의 이해 비용·유지보수 비용과 최소 수정안을 함께 뒷받침하는 후보가 없다. 제안 수를 채우기 위한 타입 도입, 파일 병합, 줄바꿈, helper 전용 테스트는 제안하지 않는다.

## Defect 후보

없음. 정의된 유효 입력에서 base의 `state == "failed" and attempts < retry_limit` 조건을 그대로 옮겼다. list comprehension도 동일한 순회와 출력 형식을 유지한다. 별도의 결함 탐색 역할까지 수행한 결과로 확대 해석하면 안 된다.

## 검토 후 배제한 가설과 반증

- **공통 함수가 불필요한 간접 호출이다:** 두 실제 소비자와 명시적인 중앙화 요구가 있다. 의존 방향도 각각 `policy`로 향하므로 현재 중복 정책 제거 비용에 비례한다.
- **dictionary 대신 명명된 상태 타입이 필요하다:** 변경 전부터 사용하던 키 기반 입력이고 값의 갱신이나 새로운 표현 간 동기화가 없다. 현재 유지보수 비용이 입증되지 않는다.
- **입력 검증이 빠졌다:** `REQUEST.md:6–7`이 필수 키와 nonnegative integer를 보장하며 검증을 이번 변경 범위에서 제외한다.
- **helper 직접 테스트 부재가 테스트 불가능성을 뜻한다:** 기존 테스트는 mock 없이 두 공개 함수를 거쳐 실제 helper를 실행한다. 정책과 공개 출력·순서를 함께 검증하는 현재 seam이 있다.
- **조건 추출로 출력이나 순서가 바뀐다:** 두 caller의 comprehension 구조와 결과 생성 방식은 유지되고 조건 식도 동일하다. `test_policy.py:14–19`는 입력 순서에 맞춘 모든 상태 행과 `["a", "e"]` 선택 순서를 비교한다.

## 실제 실행한 테스트

작업 디렉터리: `/tmp/reviewlens-quality-trial/case-b`

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v

test_disabled_retry (test_policy.RetryPolicyTests) ... ok
test_empty (test_policy.RetryPolicyTests) ... ok
test_status_and_selection (test_policy.RetryPolicyTests) ... ok

Ran 3 tests in 0.000s
OK
```

exit code는 0이다. target 테스트만 실행했다. base 테스트는 내용을 읽었지만 별도 checkout/실행하지 않았다. 소스 파일을 수정하거나 테스트를 추가하지 않았다.

## 남은 한계

검사는 Q1–Q5 코드 품질에 한정했고, 독립된 오류 처리·보안·성능·동시성·Spec 감사를 수행하지 않았다. 테스트 통과는 가능한 입력 전체의 증명이 아니다.

외부 호출자·실서비스 환경은 확인하지 않았다. 제공된 작은 메모리 목록과 유효 입력 계약 안에서는 추가로 보고할 구체적 위험을 발견하지 못했다.
