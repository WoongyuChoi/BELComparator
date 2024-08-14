
# BELComparator

**BELComparator**는 Innolink와 Pathwise CSV 파일 간의 BEL (Best Estimate Liabilities) 값을 비교하기 위한 Python 기반 도구입니다. 이 응용 프로그램은 PyQt5로 구축된 사용자 친화적인 GUI를 통해 CSV 파일을 쉽게 로드하고, BEL 값을 입력하여 비교할 수 있도록 합니다.

## 기능

- **CSV 파일 로드:** 비교를 위해 Innolink 및 Pathwise CSV 파일을 로드합니다.
- **BEL 값 입력:** 비교를 위해 BEL 값을 수동으로 입력할 수 있습니다.
- **비교 결과:** Pathwise와 Innolink BEL 값 간의 차이를 비교하여 표시합니다.
- **인덱스 매핑:** Innolink와 Pathwise 데이터 세트 간의 행 인덱스를 식별하고 매핑합니다.
- **오류 처리:** 누락된 열이나 행 수 불일치와 같은 일반적인 문제에 대한 포괄적인 오류 처리를 제공합니다.

## 설치

1. **저장소 복제:**

   ```bash
   git clone https://github.WoongyuChoi/BELComparator.git
   cd BELComparator
   ```

2. **필요한 종속성 설치:**

   Python 3.7+가 설치되어 있는지 확인하십시오. 그런 다음 필요한 패키지를 설치하십시오:

   ```bash
   pip install -r requirements.txt
   ```

3. **응용 프로그램 실행:**

   ```bash
   python main.py
   ```

## 사용 방법

1. **CSV 파일 로드:** GUI를 사용하여 Innolink 및 Pathwise CSV 파일을 로드합니다.
2. **BEL 값 입력:** 제공된 텍스트 영역에 BEL 값을 입력합니다.
3. **BEL 비교:** "Compare BEL" 버튼을 클릭하여 비교를 수행합니다.
4. **결과 보기:** 결과는 테이블에 표시되며, BEL 값 간의 차이를 보여줍니다.

## 라이센스

이 프로젝트는 MIT 라이센스에 따라 라이센스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하십시오.
