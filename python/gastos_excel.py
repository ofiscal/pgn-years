# PURPOSE: Read, format data from the `gastos` tabs of
# `input/Ley_PGN_2013-2022.xlsx`.

import pandas as pd
import re
from   typing import Dict, List, Set


input_file = "input/Ley_PGN_2013-2022.xlsx"
(year_min, year_max) = (2013, 2022)
year_range = range ( year_min, year_max + 1 )
sheet_year_preface = "Ley PGN Gasto " # The trailing space is important.

def mk_sheet_names () -> List [str]:
  gasto_re = re.compile ( sheet_year_preface + ".*" )
  sheet_names = [
    s for str_or_int in ( pd.ExcelFile ( input_file )
                          . sheet_names )
    if ( # Since sheet_names can return strings or ints
         s := str(str_or_int) )
    if gasto_re.match ( s ) ]
  return sheet_names

assert ( mk_sheet_names () ==
         # PTIFALL: mk_sheet_names() is only called in this test --
         # but later code only makes sense if it passes.
         [ sheet_year_preface + str(n)
           for n in year_range ] )

def trim_header ( year : int,
                  df : pd.DataFrame ) -> pd.DataFrame:
  """If CONCEPTO is in row 3 or 4 of column 0, drop every row before it,
make the first row the column names, and then drop that row too.
Otherwise raise an Exception."""
  try:
    for row in [3,4]:
      if str(df.iloc[row,0]).strip() == "CONCEPTO":
        df = df.iloc[row:,:]
    assert str(df.iloc[0,0]).strip() == "CONCEPTO"
    df.columns = pd.Index ( # Because indices and series are different types.
      df.iloc[0] . apply ( str.strip ) )
    df = df[1:]
  except Exception:
    raise ValueError ( "trim_header confused at year " + str(year) )
  return df

def mk_pgn_years () -> Dict [ int, pd.DataFrame ]:
  acc = {}
  for year in year_range:
    df = trim_header (
      year = year,
      df = pd.read_excel (
        io         = input_file,
        sheet_name = sheet_year_preface + str(year) ) )
    acc [year] = df
  return acc

def verify_column_names ( dfs : Dict [ int, pd.DataFrame ] ):
  c = dfs [year_min] . columns
  for k in dfs.keys():
    if not (dfs[k].columns == c) . all():
      raise ValueError ( "Column names for year " + str(k) +
                         " do not match those of the first year." )

def unify ( dfs : Dict [ int, pd.DataFrame ]
            ) -> pd.DataFrame:
  acc = pd.DataFrame ()
  for year in dfs.keys():
    df = dfs [ year ]
    df ["year"] = year
    acc = pd.concat ( [ acc, df ],
                      axis = "rows" )
  return acc

def raw_trimmed_unified_data () -> pd.DataFrame:
  """Yields a data set with year, name, and COP value.
PITFALL: The `name` field is still raw --
it mixes sectors, entities and the three kinds of spending
(funcionamiento, inversion and deuda)."""
  dfs : Dict [ int, pd.DataFrame ] = \
    mk_pgn_years ()
  verify_column_names ( dfs )
  return unify ( dfs )
