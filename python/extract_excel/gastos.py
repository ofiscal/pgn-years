# PURPOSE: Read, format data from the `gastos` tabs of
# `input/Ley_PGN_2013-2022.xlsx`.
#
# THE "LEVEL" CONCEPT:
# The original data conflates three kinds of objects of interest as rows:
# an agency's spending in one of the three spending categories,
# an agency, and a sector (which contains agencies).
# (It also conflates some totals among those rows,
# which we don't care about.)
# Of those objects we care about,
# the spending items what I'm calling are level 0,
# agencies level 1, and sectors level 2.

import pandas as pd
import re
from   typing import Dict, List, Set, Tuple
#
import python.extract_excel.lib as lib


input_file = "input/Ley_PGN_2013-2022.xlsx"
(year_min, year_max) = (2013, 2022)
year_range = range ( year_min, year_max + 1 )
sheet_year_preface = "Ley PGN Gasto " # The trailing space is important.

assert (
  # PTIFALL: the gasto sheet names read here
  # are only used in this test --
  # but later code only makes sense if it passes.
  lib.read_sheet_names (
    input_file = input_file,
    sheet_year_preface = sheet_year_preface, )
  == [ sheet_year_preface + str(n)
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
    df = (
      trim_header (
        year = year,
        df = pd.read_excel (
          io         = input_file,
          sheet_name = sheet_year_preface + str(year) ) )
      . rename ( columns =
                 { "CONCEPTO"            : "name",
                   "APROPIACIÓN INICIAL" : "cop" } ) )
    acc [year] = df
  return acc

def verify_column_names ( dfs : Dict [ int, pd.DataFrame ] ):
  c = dfs [year_min] . columns
  for k in dfs.keys():
    if not (dfs[k].columns == c) . all():
      raise ValueError ( "Column names for year " + str(k) +
                         " do not match those of the first year." )

def collect_pgn_years ( dfs : Dict [ int, pd.DataFrame ]
                       ) -> pd.DataFrame:
  acc = pd.DataFrame ()
  for year in dfs.keys():
    df = dfs [ year ]
    df ["year"] = year
    acc = pd.concat ( [ acc, df ],
                      axis = "rows" )
  return acc

matches_to_level_0_items : List [ Tuple [ str,
                                          List [ str ] ] ] = [
  ( "servicio.*deuda", [
    "SERVICIO DE LA DEUDA PUBLICA NACIONAL",     # to drop (see drop_totals)
    "SERVICIO DE LA DEUDA PÚBLICA NACIONAL",     # to drop (see drop_totals)
    "Servicio de la Deuda",               ] ),   # to keep
  ( "inversi.n",       [ "Inversión"      ] ),   # to keep
  ( "funcionamiento",  [ "Funcionamiento" ] ), ] # to keep

matches_to_total_general : List [ Tuple [ str,
                                          List [ str ] ] ] = [
  ( "total.*general",  [ "Total general"  ] ) ]  # to drop (see drop_totals)

def verify_string_matches ( gastos : pd.DataFrame ):
  """This is a safety harness, required because the government
might change the names of sectors or entities in the future,
such that one of them matches one of these regexes.
That would lead to our treating it the wrong way.
To avoid such a silent error creeping in via future changes to the data,
this verifies that the only regex matches are of the kind we intend."""
  for (regex, matches) in [ *matches_to_level_0_items,
                            *matches_to_total_general ]:
    if not ( pd.Series ( matches )
             . equals (
               pd.Series ( gastos [ "name" ]
                           [ gastos["name"]
                             . str.match ( ".*" + regex + ".*",
                                           case = False ) ]
                           . unique() )
               . sort_values ()
               . reset_index ( drop=True ) ) ):
      raise ValueError ( "verify_string_matches(): "
                         + "Unexpected matches found to the regex \""
                         + regex + "\"." )

# TODO: We could keep this information instead,
# using it as a check on the other information.
def drop_totals ( gastos : pd.DataFrame ) -> pd.DataFrame:
  return gastos [
    ( ~ gastos [ "name" ] . str.match (
      "Total general" ) ) &
    ( ~ gastos [ "name" ] . str.match (
      "SERVICIO DE LA DEUDA P.BLICA NACIONAL" ) ) ]

def mk_gastos () -> pd.DataFrame:
  """Yields a data set with year, name, and COP value.
PITFALL: The `name` field is still raw --
it mixes sectors, entities and the three kinds of spending
(funcionamiento, inversion and deuda)."""
  dfs : Dict [ int, pd.DataFrame ] = \
    mk_pgn_years ()
  verify_column_names ( dfs )
  gastos =  collect_pgn_years ( dfs ) [["year", "name", "cop"]]
  verify_string_matches ( gastos )
  return drop_totals ( gastos )
