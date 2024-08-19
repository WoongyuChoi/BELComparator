import pandas as pd
from bel_comparator import BELComparator
from bel_comparator.custom_exceptions import MissingColumnsError, InvalidBELValuesError

def compare_bel(inno_df, pw_df, bel_values, progress_bar, log_to_console, adjustment_factor):
    """Innolink와 Pathwise 데이터를 비교하여 결과를 반환하는 함수"""
    try:
        comparator = BELComparator(inno_df, pw_df, bel_values)
        comparator.validate_and_prepare_data()

        progress_bar.setMaximum(len(pw_df))
        progress_bar.setValue(0)

        result = comparator.compare_bel()
        error_count = 0

        for row_idx, row in result.iterrows():
            try:
                # 조정계수 적용: DIFF가 조정계수보다 작으면 일치하는 것으로 간주
                diff_value = abs(float(row['DIFF']))
                log_to_console(f"DIFF: {diff_value}, Adjustment Factor: {adjustment_factor}")
                # 조정계수 적용: DIFF가 조정계수보다 크면 오류로 간주
                if pd.isna(row['DIFF']) or diff_value > adjustment_factor:
                    error_count += 1
            except ValueError:
                error_count += 1

            # ProgressBar 업데이트
            progress_bar.setValue(row_idx + 1)

        return result, error_count
    except (MissingColumnsError, InvalidBELValuesError) as e:
        log_to_console(f"오류 발생: {str(e)}")
        return None, 0
    except Exception as e:
        log_to_console(f"예기치 않은 오류 발생: {str(e)}")
        return None, 0
