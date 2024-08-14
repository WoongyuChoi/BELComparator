import pandas as pd
from custom_exceptions import MissingColumnsError, InvalidBELValuesError

class BELComparator:
    def __init__(self, inno_df, pw_df, bel_values):
        self.inno_df = inno_df
        self.pw_df = pw_df
        self.bel_values = bel_values

    @staticmethod
    def load_csv(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise e

    @staticmethod
    def parse_bel_values(bel_text):
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
        required_inno_columns = ['POL_NO', 'RIDER_PRD_CODE', 'INIT_V_CHECK', 'LOA_CODE']
        missing_inno_columns = [col for col in required_inno_columns if col not in self.inno_df.columns]
        if missing_inno_columns:
            raise MissingColumnsError(f"Innolink CSV 파일에 '{', '.join(missing_inno_columns)}' 컬럼이 없습니다.")

        required_pw_columns = ['POL_NO', 'RIDER_PRD_CODE', 'INIT_V_CHECK', 'LOA_CODE', 'BEL']
        missing_pw_columns = [col for col in required_pw_columns if col not in self.pw_df.columns]
        if missing_pw_columns:
            raise MissingColumnsError(f"Pathwise CSV 파일에 '{', '.join(missing_pw_columns)}' 컬럼이 없습니다.")

        if len(self.bel_values) != len(self.inno_df):
            raise InvalidBELValuesError(f"입력된 BEL 값의 개수({len(self.bel_values)})가 Innolink CSV 파일의 행 개수({len(self.inno_df)})와 일치하지 않습니다.")

        self.inno_df.columns = [col.upper() for col in self.inno_df.columns]
        self.pw_df.columns = [col.upper() for col in self.pw_df.columns]
        self.inno_df['INNOLINC_BEL'] = self.bel_values

    def compare_bel(self):
        try:
            # 병합 수행
            merged_df = pd.merge(
                self.pw_df,
                self.inno_df[['POL_NO', 'RIDER_PRD_CODE', 'INIT_V_CHECK', 'LOA_CODE', 'INNOLINC_BEL']],
                on=['POL_NO', 'RIDER_PRD_CODE', 'INIT_V_CHECK', 'LOA_CODE'],
                how='outer'
            )

            merged_df['DIFF'] = merged_df['BEL'] - merged_df['INNOLINC_BEL']

            # INDEX를 계산
            def calculate_index(row):
                matching_indices = self.inno_df.index[
                    (self.inno_df['POL_NO'] == row['POL_NO']) &
                    (self.inno_df['RIDER_PRD_CODE'] == row['RIDER_PRD_CODE']) &
                    (self.inno_df['INIT_V_CHECK'] == row['INIT_V_CHECK']) &
                    (self.inno_df['LOA_CODE'] == row['LOA_CODE'])
                ]
                return matching_indices[0] if not matching_indices.empty else None

            merged_df['INDEX'] = merged_df.apply(calculate_index, axis=1)

            merged_df['ROW'] = merged_df.index

            # NaN을 'NaN' 문자열로 대체하여 처리
            merged_df['INDEX'] = merged_df['INDEX'].apply(lambda x: int(x) if pd.notnull(x) else 'NaN')

            merged_df['POL_NO'] = merged_df['POL_NO'].astype(str)
            merged_df['RIDER_PRD_CODE'] = merged_df['RIDER_PRD_CODE'].astype(str)
            merged_df['PATHWISE_BEL'] = merged_df['BEL'].apply(lambda x: f"{x:.6f}" if pd.notna(x) else "")
            merged_df['INNOLINC_BEL'] = merged_df['INNOLINC_BEL'].apply(lambda x: f"{x:.6f}" if pd.notna(x) else "")
            merged_df['DIFF'] = merged_df['DIFF'].apply(lambda x: f"{x:.6f}" if pd.notna(x) else "")

            result = merged_df[['ROW', 'INDEX', 'POL_NO', 'RIDER_PRD_CODE', 'PATHWISE_BEL', 'INNOLINC_BEL', 'DIFF']]
            return result
        except Exception as e:
            raise e
