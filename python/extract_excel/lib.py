import pandas as pd
import re
from   typing import Dict, List, Set


def read_sheet_names (
    input_file : str,
    sheet_year_preface : str, # The string that precedes the year in the name of each relevant sheet. (We assume nothing follows the year.)
) -> List [str]:
  gasto_re = re.compile ( sheet_year_preface + ".*" )
  sheet_names = [
    s for str_or_int in ( pd.ExcelFile ( input_file )
                          . sheet_names )
    if ( # Since sheet_names can return strings or ints
         s := str(str_or_int) )
    if gasto_re.match ( s ) ]
  return sheet_names
