import pandas as pd
from bel_comparator import BELComparator
from bel_comparator.custom_exceptions import MissingColumnsError, InvalidBELValuesError

def compare_bel(inno_df, pw_df, bel_values, progress_bar, log_to_console):
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
                if pd.isna(row['DIFF']) or float(row['DIFF']) != 0:
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
