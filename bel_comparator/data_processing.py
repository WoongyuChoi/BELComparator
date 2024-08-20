import pandas as pd
from bel_comparator import BELComparator
from bel_comparator.custom_exceptions import MissingColumnsError, InvalidBELValuesError
import bel_comparator.utils as utils

def compare_bel(inno_df, pw_df, bel_values, progress_bar, log_to_console):
    """Innolink와 Pathwise 데이터를 비교하여 결과를 반환하는 함수"""
    try:
        comparator = BELComparator(inno_df, pw_df, bel_values)
        comparator.validate_and_prepare_data()

        progress_bar.setMaximum(len(pw_df))
        progress_bar.setValue(0)

        result = comparator.compare_bel()

        for row_idx in range(len(result)):
            progress_bar.setValue(row_idx + 1)

        return result
    except (MissingColumnsError, InvalidBELValuesError) as e:
        log_to_console(f"오류 발생: {str(e)}")
        return None
    except Exception as e:
        log_to_console(f"예기치 않은 오류 발생: {str(e)}")
        return None

def calculate_error_count(result, adjustment_factor, exclude_na):
    """에러 카운트를 계산하는 함수"""
    error_count = 0
    for _, row in result.iterrows():
        try:
            diff_value = abs(float(row['DIFF'])) if utils.is_valid_float(row['DIFF']) else None

            if exclude_na:
                # N/A 제외가 체크된 경우, NaN 또는 'NaN' 문자열이 아닌 경우에만 오류로 간주
                if diff_value is not None and diff_value > adjustment_factor:
                    error_count += 1
            else:
                # N/A 제외가 체크되지 않은 경우, NaN 또는 'NaN' 문자열 포함하여 오류로 간주
                if (row['DIFF'] == 'NaN') or pd.isna(row['DIFF']) or (diff_value is not None and diff_value > adjustment_factor):
                    error_count += 1

        except ValueError:
            error_count += 1
    
    return error_count
