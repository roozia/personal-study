# test-cases.md — LogViewer 테스트 케이스

단위 테스트 프레임워크 없이 검증 가능한 시나리오 중심으로 작성합니다.
각 테스트는 **준비(Given) → 실행(When) → 검증(Then)** 구조로 기술합니다.

---

## 1. LogViewerConfig — 설정 파일 로딩

### TC-01. 클래스패스에서 정상 로딩
```
Given : WEB-INF/classes/logviewer.properties 에 유효한 설정값 존재
When  : LogViewerConfig.load() 호출
Then  : 각 필드(filePath, fileEncoding, keywords, contextLines 등) 가 올바르게 파싱됨
```

### TC-02. 시스템 속성으로 외부 경로 지정
```
Given : JVM 실행 시 -Dlogviewer.config.path=/tmp/custom.properties 설정
        /tmp/custom.properties 에 유효한 설정값 존재
When  : LogViewerConfig.load() 호출
Then  : 클래스패스가 아닌 /tmp/custom.properties 를 읽어 설정값 반환
```

### TC-03. 설정 파일 없음
```
Given : 클래스패스에 logviewer.properties 없음, 시스템 속성도 미설정
When  : LogViewerConfig.load() 호출
Then  : IOException 발생
        메시지에 "설정 파일을 찾을 수 없습니다" 포함
```

### TC-04. 키워드 복수 파싱
```
Given : logviewer.condition.keywords=NullPointerException, user01 ,결제 처리 중단
When  : LogViewerConfig.load() 호출
Then  : getKeywords() == ["NullPointerException", "user01", "결제 처리 중단"]
        (앞뒤 공백 제거, 쉼표 구분)
```

### TC-05. contextLines 비정상값 → 기본값 적용
```
Given : logviewer.context.lines=abc  (숫자가 아닌 값)
When  : LogViewerConfig.load() 호출
Then  : getContextLines() == 10  (기본값)
```

### TC-06. contextLines 음수 → 0 으로 보정
```
Given : logviewer.context.lines=-5
When  : LogViewerConfig.load() 호출
Then  : getContextLines() == 0
```

---

## 2. LogExtractService — 조건 검증

### TC-07. 날짜·키워드 모두 미설정
```
Given : datetimeCondition = ""
        keywords = []
When  : extract() 호출
Then  : IOException 발생
        메시지에 "하나 이상을 설정해야 합니다" 포함
```

### TC-08. filePath 미설정
```
Given : filePath = ""
When  : extract() 호출
Then  : IOException 발생
        메시지에 "logviewer.file.path 설정이 비어 있습니다" 포함
```

### TC-09. 존재하지 않는 파일 경로
```
Given : filePath = "/app/logs/notexist.log"
        allowedBaseDir = "/app/logs/"
When  : extract() 호출
Then  : IOException 발생
        메시지에 "파일을 찾을 수 없습니다" 포함
```

### TC-10. 허용 디렉토리 외부 경로 접근 (Path Traversal)
```
Given : filePath = "/app/logs/../../etc/passwd"
        allowedBaseDir = "/app/logs/"
When  : extract() 호출
Then  : IOException 발생
        메시지에 "허용되지 않은 경로입니다" 포함
        (Paths.get().normalize() 이후에도 basedir 벗어나는 경우 차단)
```

### TC-11. allowedBaseDir 미설정 → 경로 검사 생략
```
Given : filePath = "/other/path/app.log"  (파일 실제 존재)
        allowedBaseDir = ""
When  : extract() 호출
Then  : 경로 차단 없이 파일 읽기 진행
```

---

## 3. LogExtractService — 매칭 로직 (matchLine)

아래 테스트에서 사용하는 샘플 로그 라인:
```
[2024-03-15 09:14:32] ERROR  PaymentService - NullPointerException: user01
```

### TC-12. 날짜 조건만 설정 — 매칭
```
Given : datetimeCondition = "2024-03-15 09:14"
        keywords = []
When  : 위 샘플 라인에 matchLine 적용
Then  : 반환값 == "2024-03-15 09:14"  (날짜 문자열 반환)
```

### TC-13. 날짜 조건만 설정 — 미매칭
```
Given : datetimeCondition = "2024-03-15 10:00"
        keywords = []
When  : 위 샘플 라인에 matchLine 적용
Then  : 반환값 == null
```

### TC-14. 키워드만 설정 — 단일 키워드 매칭
```
Given : datetimeCondition = ""
        keywords = ["user01"]
When  : 위 샘플 라인에 matchLine 적용
Then  : 반환값 == "user01"
```

### TC-15. 키워드만 설정 — 복수 키워드 OR, 첫 매칭 반환
```
Given : datetimeCondition = ""
        keywords = ["user99", "NullPointerException", "user01"]
When  : 위 샘플 라인에 matchLine 적용
Then  : 반환값 == "NullPointerException"  (목록 순서상 첫 매칭)
        (user99 는 미매칭, NullPointerException 은 매칭 → 즉시 반환)
```

### TC-16. 키워드만 설정 — 미매칭
```
Given : datetimeCondition = ""
        keywords = ["user99", "SQLException"]
When  : 위 샘플 라인에 matchLine 적용
Then  : 반환값 == null
```

### TC-17. 날짜 AND 키워드 — 둘 다 매칭
```
Given : datetimeCondition = "2024-03-15 09:14"
        keywords = ["user01"]
When  : 위 샘플 라인에 matchLine 적용
Then  : 반환값 == "user01"
```

### TC-18. 날짜 AND 키워드 — 날짜 매칭, 키워드 미매칭
```
Given : datetimeCondition = "2024-03-15 09:14"
        keywords = ["user99"]
When  : 위 샘플 라인에 matchLine 적용
Then  : 반환값 == null
```

### TC-19. 날짜 AND 키워드 — 키워드 매칭, 날짜 미매칭
```
Given : datetimeCondition = "2024-03-15 10:00"
        keywords = ["user01"]
When  : 위 샘플 라인에 matchLine 적용
Then  : 반환값 == null
```

---

## 4. LogExtractService — 블록 구성 (buildBlocks)

### TC-20. 단일 매칭, contextLines=3
```
Given : matches = [MatchResult(lineNumber=10, matchedKeyword="ERROR")]
        contextLines = 3
When  : buildBlocks 호출
Then  : blocks[0].startRow == 7
        blocks[0].endRow   == 13
        blocks[0].matchedKeywords == ["ERROR"]
```

### TC-21. 첫 번째 행 매칭 — startRow 가 1 미만 방지
```
Given : matches = [MatchResult(lineNumber=2, matchedKeyword="ERROR")]
        contextLines = 5
When  : buildBlocks 호출
Then  : blocks[0].startRow == 1   (max(1, 2-5) = 1)
        blocks[0].endRow   == 7
```

### TC-22. 복수 매칭 — 각각 블록 생성
```
Given : matches = [MatchResult(5, "A"), MatchResult(20, "B")]
        contextLines = 2
When  : buildBlocks 호출
Then  : blocks[0] = startRow=3, endRow=7, keywords=["A"]
        blocks[1] = startRow=18, endRow=22, keywords=["B"]
```

---

## 5. LogExtractService — 블록 병합 (mergeBlocks)

### TC-23. 겹치지 않는 블록 — 병합 없음
```
Given : blocks = [ExtractBlock(1, 5, ["A"]), ExtractBlock(10, 15, ["B"])]
When  : mergeBlocks 호출
Then  : merged.size() == 2
        merged[0] = startRow=1, endRow=5
        merged[1] = startRow=10, endRow=15
```

### TC-24. 겹치는 블록 — 하나로 병합
```
Given : blocks = [ExtractBlock(1, 10, ["A"]), ExtractBlock(8, 15, ["B"])]
When  : mergeBlocks 호출
Then  : merged.size() == 1
        merged[0].startRow == 1
        merged[0].endRow   == 15
        merged[0].matchedKeywords == ["A", "B"]
```

### TC-25. 인접 블록 (endRow+1 == 다음 startRow) — 병합
```
Given : blocks = [ExtractBlock(1, 9, ["A"]), ExtractBlock(10, 15, ["B"])]
        (overlapsOrAdjacent: 9+1 >= 10 → true)
When  : mergeBlocks 호출
Then  : merged.size() == 1
        merged[0].endRow == 15
```

### TC-26. 같은 키워드가 복수 블록에 걸쳐 나타날 때 중복 제거
```
Given : blocks = [ExtractBlock(1, 10, ["ERROR"]), ExtractBlock(8, 15, ["ERROR"])]
When  : mergeBlocks 호출
Then  : merged[0].matchedKeywords == ["ERROR"]  (중복 추가 없음)
```

### TC-27. 3개 블록 연속 병합
```
Given : blocks = [ExtractBlock(1,5,["A"]), ExtractBlock(4,9,["B"]), ExtractBlock(8,12,["C"])]
When  : mergeBlocks 호출
Then  : merged.size() == 1
        merged[0] = startRow=1, endRow=12, keywords=["A","B","C"]
```

---

## 6. LogExtractService — 출력 형식 (writeExtract)

### TC-28. 블록 헤더 형식 — 키워드 1개
```
Given : ExtractBlock(startRow=21, endRow=31, matchedKeywords=["user01"])
When  : buildHeader 호출
Then  : "========== [Row: 21-31 / Keyword: \"user01\"] =========="
```

### TC-29. 블록 헤더 형식 — 키워드 복수
```
Given : ExtractBlock(startRow=21, endRow=31, matchedKeywords=["user01", "NullPointerException"])
When  : buildHeader 호출
Then  : "========== [Row: 21-31 / Keyword: \"user01\", \"NullPointerException\"] =========="
```

### TC-30. 매칭 없음 → 안내 메시지 출력
```
Given : 조건에 매칭되는 행이 하나도 없는 로그 파일
When  : extract() 호출
Then  : 응답 본문 == "조건에 매칭되는 로그 라인이 없습니다."
        (다운로드 파일에 안내 문구만 포함)
```

### TC-31. 블록 endRow 가 파일 끝을 초과할 때 — EOF 에서 정상 종료
```
Given : 로그 파일 전체 20줄
        ExtractBlock(startRow=17, endRow=25)  (endRow > 실제 EOF)
When  : writeExtract 호출
Then  : 17~20번 줄까지만 출력되고 예외 없이 정상 종료
```

---

## 7. 종합 시나리오 (End-to-End)

아래 테스트에 사용하는 샘플 로그 파일 (`sample.log`, 총 30줄):
```
1  [2024-03-15 09:13:00] INFO   UserService    - 정상 처리
2  [2024-03-15 09:13:01] INFO   UserService    - 정상 처리
...
10 [2024-03-15 09:14:05] INFO   UserService    - 로그인 시도: user01
11 [2024-03-15 09:14:06] ERROR  AuthFilter     - 인증 실패: user01
12     at com.example.AuthFilter.doFilter(AuthFilter.java:88)
13 [2024-03-15 09:14:07] WARN   SessionManager - 세션 없음: user01
...
20 [2024-03-15 09:20:00] INFO   PaymentService - 결제 요청 시작
21 [2024-03-15 09:20:01] ERROR  PaymentService - NullPointerException
22     at com.example.PaymentService.process(PaymentService.java:132)
23 [2024-03-15 09:20:02] ERROR  PaymentService - 결제 처리 중단
...
30 [2024-03-15 09:25:00] INFO   UserService    - 정상 처리
```

### TC-32. 날짜 조건만 — 해당 시간대 전체 발췌
```
Given : datetimeCondition = "2024-03-15 09:14"
        keywords = []
        contextLines = 2
When  : extract() 호출
Then  : Row 8-15 범위가 발췌됨  (10, 11, 13번 줄 각각 ±2, 인접하여 병합)
        헤더: [Row: 8-15 / Keyword: "2024-03-15 09:14"]
```

### TC-33. 키워드만 — 복수 매칭, 각각 독립 블록
```
Given : datetimeCondition = ""
        keywords = ["user01", "NullPointerException"]
        contextLines = 1
When  : extract() 호출
Then  : 블록 1: Row 9-14  (10, 11, 13번 줄 ±1, 인접 병합)
                헤더에 "user01" 포함
        블록 2: Row 20-22  (21번 줄 ±1)
                헤더에 "NullPointerException" 포함
```

### TC-34. 날짜 AND 키워드 — 교집합만 발췌
```
Given : datetimeCondition = "2024-03-15 09:14"
        keywords = ["NullPointerException"]
        contextLines = 2
When  : extract() 호출
Then  : 발췌 결과 없음 (NullPointerException 은 09:20 시간대에만 존재)
        응답: "조건에 매칭되는 로그 라인이 없습니다."
```

### TC-35. 날짜 AND 키워드 — 교집합 발췌
```
Given : datetimeCondition = "2024-03-15 09:14"
        keywords = ["user01"]
        contextLines = 1
When  : extract() 호출
Then  : 10, 11, 13번 줄이 각각 ±1 발췌 후 인접 병합
        헤더에 "user01" 표시
        09:20 시간대의 user01 없으므로 추가 블록 없음
```

### TC-36. 전체 흐름 — 다운로드 응답 헤더 확인
```
Given : 유효한 설정, 1개 이상 매칭 존재
When  : /logDownload.do GET 요청
Then  : HTTP 200
        Content-Type: text/plain; charset=UTF-8
        Content-Disposition: attachment; filename="extract_yyyyMMdd_HHmmss.log"
        응답 본문에 ========== [Row: ... / Keyword: ...] ========== 헤더 포함
```

### TC-37. 설정 오류 — 오류 응답 확인
```
Given : logviewer.file.path 가 존재하지 않는 경로
When  : /logDownload.do GET 요청
Then  : HTTP 500
        응답 본문에 "[오류] 파일을 찾을 수 없습니다" 포함
```

---

## 수동 검증 절차

Java 단위 테스트 환경이 없을 때 아래 순서로 검증합니다.

1. `logviewer.properties` 에 실제 로그 파일 경로와 간단한 키워드 입력
2. Tomcat 기동 후 브라우저에서 `/logDownload.do` 접근
3. 다운로드된 파일을 텍스트 에디터로 열어 확인:
   - `========== [Row: N-M / Keyword: "..."] ==========` 헤더 존재
   - 헤더 직후 원본 로그 내용 포함
   - 블록 사이 빈 줄로 구분
4. 매칭 없는 조건으로 재시도 → `조건에 매칭되는 로그 라인이 없습니다.` 파일 다운로드 확인
5. 허용 디렉토리 외부 경로로 재시도 → HTTP 500 및 오류 메시지 확인
