import pandas as pd
from bel_comparator.custom_exceptions import MissingColumnsError, InvalidBELValuesError

class BELComparator:
    def __init__(self, inno_df, pw_df, bel_values):
        self.inno_df = inno_df
        self.pw_df = pw_df
        self.bel_values = bel_values
        
    @staticmethod
    def parse_bel_values(bel_text):
        """입력된 BEL 텍스트를 파싱하여 숫자 리스트로 반환합니다."""
        bel_lines = bel_text.strip().splitlines()
        bel_values = []
        for line in bel_lines:
            line = line.strip()
            try:
                # BEL이라는 문자열은 무시하고 숫자만 처리
                if line and not line.isalpha():
                    bel_values.append(float(line))
            except ValueError:
                continue  # 변환이 안 되는 경우 무시
        if not bel_values:
            raise InvalidBELValuesError("잘못된 BEL 값이 입력되었습니다.")
        return bel_values

    def validate_and_prepare_data(self):
        """데이터 유효성을 검사하고 필요한 컬럼을 준비합니다."""
        required_inno_columns = ['POL_NO', 'RIDER_PRD_CODE', 'INIT_V_CHECK', 'LOA_CODE']
        missing_inno_columns = [col for col in required_inno_columns if col not in self.inno_df.columns]
        if missing_inno_columns:
            raise MissingColumnsError(f"Innolink CSV 파일에 '{', '.join(missing_inno_columns)}' 컬럼이 없습니다.")

        required_pw_columns = ['POL_NO', 'RIDER_PRD_CODE', 'INIT_V_CHECK', 'LOA_CODE', 'BEL']
        missing_pw_columns = [col for col in required_pw_columns if col not in self.pw_df.columns]
        if missing_pw_columns:
            raise MissingColumnsError(f"Pathwise CSV 파일에 '{', '.join(missing_pw_columns)}' 컬럼이 없습니다.")

        # BEL 값의 개수가 inno_df의 행 개수보다 적으면 NaN으로 채움
        if len(self.bel_values) < len(self.inno_df):
            self.bel_values.extend([pd.NA] * (len(self.inno_df) - len(self.bel_values)))

        # BEL 값의 개수가 많으면 잘라냄
        self.bel_values = self.bel_values[:len(self.inno_df)]

        self.inno_df.columns = [col.upper() for col in self.inno_df.columns]
        self.pw_df.columns = [col.upper() for col in self.pw_df.columns]
        self.inno_df['INNOLINC_BEL'] = self.bel_values

    def calculate_index(self, row):
        """주어진 행에서 일치하는 인덱스를 계산합니다."""
        matching_indices = self.inno_df.index[
            (self.inno_df['POL_NO'] == row['POL_NO']) &
            (self.inno_df['RIDER_PRD_CODE'] == row['RIDER_PRD_CODE']) &
            (self.inno_df['INIT_V_CHECK'] == row['INIT_V_CHECK']) &
            (self.inno_df['LOA_CODE'] == row['LOA_CODE'])
        ]
        return matching_indices[0] if not matching_indices.empty else None

    def format_column(self, value):
        """열의 값을 포맷팅합니다."""
        return f"{value:.6f}" if pd.notna(value) else ""

    def format_diff_column(self, value):
        """DIFF 열의 값을 포맷팅합니다."""
        return f"{value:.6f}" if pd.notna(value) else 'NaN'

    def compare_bel(self):
        """Innolink와 Pathwise 데이터를 비교하여 결과를 반환합니다."""
        try:
            # Innolink 데이터와 Pathwise 데이터를 병합합니다.
            merged_df = pd.merge(
                self.pw_df,
                self.inno_df[['POL_NO', 'RIDER_PRD_CODE', 'INIT_V_CHECK', 'LOA_CODE', 'INNOLINC_BEL']],
                on=['POL_NO', 'RIDER_PRD_CODE', 'INIT_V_CHECK', 'LOA_CODE'],
                how='outer'
            )

            # Pathwise BEL 값이 없는 행을 필터링하여 제거합니다.
            merged_df = merged_df[merged_df['BEL'].notna()]

            # BEL 비교 및 기타 계산을 수행합니다.
            merged_df['DIFF'] = merged_df['BEL'] - merged_df['INNOLINC_BEL']
            merged_df['INDEX'] = merged_df.apply(self.calculate_index, axis=1)
            merged_df['ROW'] = merged_df.index

            # NaN 처리 및 포맷팅
            merged_df['INDEX'] = merged_df['INDEX'].apply(lambda x: int(x) if pd.notnull(x) else 'NaN')
            merged_df['POL_NO'] = merged_df['POL_NO'].astype(str)
            merged_df['RIDER_PRD_CODE'] = merged_df['RIDER_PRD_CODE'].astype(str)
            merged_df['PATHWISE_BEL'] = merged_df['BEL'].apply(self.format_column)
            merged_df['INNOLINC_BEL'] = merged_df['INNOLINC_BEL'].apply(self.format_column)
            merged_df['DIFF'] = merged_df['DIFF'].apply(self.format_diff_column)

            # 최종 결과를 반환합니다.
            result = merged_df[['ROW', 'INDEX', 'POL_NO', 'RIDER_PRD_CODE', 'PATHWISE_BEL', 'INNOLINC_BEL', 'DIFF']]
            return result
        except Exception as e:
            raise e
