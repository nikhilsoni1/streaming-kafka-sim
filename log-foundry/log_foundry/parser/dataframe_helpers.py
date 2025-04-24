# DataFrame helper functions
import pandas as pd
import warnings


def apply_typecasts(df: pd.DataFrame, typecasts: dict) -> pd.DataFrame:
    """
    Applies typecasts to DataFrame columns based on provided typecast dictionary.

    Parameters:
        df (pd.DataFrame): Input DataFrame.
        typecasts (dict): Dictionary mapping column names to pandas dtypes.

    Returns:
        pd.DataFrame: The DataFrame with typecasts applied where possible.
    """
    for col, dtype in typecasts.items():
        if (dtype is not None) and (col in df.columns):
            try:
                df[col] = df[col].astype(dtype)
            except Exception as e:
                warnings.warn(f"Failed to cast column '{col}' to '{dtype}': {e}")
        elif (dtype is None) and (col in df.columns):
            warnings.warn(f"No dtype mapping found for column '{col}'. Skipping typecast.")
            continue
    return df

