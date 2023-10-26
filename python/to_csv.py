import pandas as pd
import re
from   typing import Dict, List, Set


input_file = "input/Ley_PGN_2013-2022.xlsx"
(year_min, year_max) = (2013, 2022)
year_range = range ( year_min, year_max + 1 )
sheet_year_preface = "Ley PGN Gasto " # The trailing space is important.

def mk_sheet_names () -> List [str]:
  gasto_re = re.compile ( sheet_year_preface + ".*" )
  sheet_names = [ s for s in ( pd.ExcelFile ( input_file )
                               . sheet_names )
                  if gasto_re.match ( s ) ]
  return sheet_names

assert ( mk_sheet_names () ==
         # PTIFALL: mk_sheet_names() is only called in this test --
         # but later code only makes sense if it passes.
         [ sheet_year_preface + str(n)
           for n in year_range ] )

def trim_header ( df : pd.DataFrame ) -> pd.DataFrame:
  """If CONCEPTO is in row 3 or 4 of column 0, drop every row before it.
  Otherwise fail."""
  for row in [3,4]:
    if str(df.iloc[row,0]).strip() == "CONCEPTO":
      df = df.iloc[row:,:]
  assert str(df.iloc[0,0]).strip() == "CONCEPTO"
  df.columns = df.iloc[0] . apply ( str.strip )
  df = df[1:]
  return df

def mk_pgn_years () -> Dict [ int, pd.DataFrame ]:
  acc = {}
  for year in year_range:
    print("loading " + str(year))
    df = trim_header (
      pd.read_excel (
        io         = input_file,
        sheet_name = sheet_year_preface + str(year) ) )
    acc [year] = df
  return acc

dfs = mk_pgn_years ()
