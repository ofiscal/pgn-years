# PURPOSE: Read, format data from the `gastos` tabs of
# `input/Ley_PGN_2013-2022.xlsx`.
#
# CHIEF DIFFICULTY: MIXED OBJECTS
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
  return ( acc
           . reset_index ( # remove duplicate index values
             drop = True ) )

if True: # Things to keep. [These are lists because in future data,
  # the number of matches might expand -- see `verify_string_matches`.]
  matches_for_agency_deuda          = ["Servicio de la Deuda"]
  matches_for_agency_inversion      = ["Inversión"]
  matches_for_agency_funcionamiento = ["Funcionamiento"]
  matches_for_agency_spending = [ *matches_for_agency_deuda,
                                  *matches_for_agency_inversion,
                                  *matches_for_agency_funcionamiento, ]

if True: # Things to drop.
  matches_for_redundant_deuda_totals = [
    "SERVICIO DE LA DEUDA PUBLICA NACIONAL",
    "SERVICIO DE LA DEUDA PÚBLICA NACIONAL", ]
  matches_for_redundant_totales_generales = ["Total general"]

regexes_and_matches : List [ Tuple [ str,
                                     List [ str ] ] ] = [
  ( "servicio.*deuda", ( # PITFALL: Matches some things we want,
                         # and some things we don't.
                      matches_for_redundant_deuda_totals +
                      matches_for_agency_deuda ) ),
  ( "inversi.n",      matches_for_agency_inversion      ),
  ( "funcionamiento", matches_for_agency_funcionamiento ),
  ( "total.*general", matches_for_redundant_totales_generales    ), ]

def verify_string_matches ( gastos : pd.DataFrame ):
  """This is a safety harness, required because the government
might change the names of sectors or entities in the future,
such that one of them matches one of these regexes.
That would lead to our treating it the wrong way.
To avoid such a silent error creeping in via future changes to the data,
this verifies that the only regex matches are of the kind we intend."""
  for (regex, matches) in regexes_and_matches:
    if not ( pd.Series ( matches )
             . sort_values ()
             . equals (
               pd.Series ( gastos [ "name" ]
                           [ gastos["name"]
                             . str.match ( ".*" + regex + ".*",
                                           case = False ) ]
                           . unique () )
               . sort_values ()
               . reset_index ( drop = True ) ) ):
      raise ValueError ( "verify_string_matches(): "
                         + "Unexpected matches found to the regex \""
                         + regex + "\"." )

# TODO ?? We could keep this information instead,
# using it as a check on the other information.
def drop_redundant_rows ( gastos : pd.DataFrame ) -> pd.DataFrame:
  return gastos [
    ( ~ gastos [ "name" ]
      . isin ( matches_for_redundant_totales_generales ) ) &
    ( ~ gastos [ "name" ]
      . isin ( matches_for_redundant_deuda_totals ) ) ]

def define_agency_items ( gastos : pd.DataFrame ) -> pd.DataFrame:
  df = gastos.copy () # This looks silly, but without using a copy, setting `gastos = define_agency_items ( gastos)` will trigger the Pandas warning, "A value is trying to be set on a copy of a slice from a DataFrame."
  df ["is agency item"] = (
    df ["name"]
    . isin ( matches_for_agency_spending )
    . astype ( int ) )
  return df

def identify_agency_and_sector_rows (
    gastos : pd.DataFrame ) -> pd.DataFrame:
  gastos["is agency"] = (
    ( ( gastos ["is agency item"]                == 0 ) &
      ( gastos ["is agency item"] . shift ( -1 ) > 0 ) )
    . astype ( int ) )
  gastos["is sector"] = (
    ( ( gastos ["is agency item"]                == 0 ) &
      ( gastos ["is agency"]                     == 0 ) &
      ( gastos ["is agency"] . shift ( -1 )      > 0 ) )
    . astype ( int ) )

  if True: # Verify that these three kinds partition the rows.
    kinds = gastos [[ "is agency item", "is agency", "is sector" ]]
    kinds_sum = kinds . sum ( axis = "columns" )
    assert kinds_sum.min () == 1
    assert kinds_sum.max () == 1

  return gastos

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
  return (
    identify_agency_and_sector_rows (
      define_agency_items (
        drop_redundant_rows (
          gastos ) ) ) )
