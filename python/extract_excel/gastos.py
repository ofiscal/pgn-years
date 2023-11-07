# PURPOSE: Read, format data from the `gastos` tabs of
# `input/Ley_PGN_2013-2022.xlsx`.
#
# CHIEF DIFFICULTY: MIXED OBJECTS
# The original data conflates three kinds of objects of interest as rows:
# an entity's spending in one of the three spending categories,
# an entity, and a sector (which contains entities).
# (It also conflates some totals among those rows,
# which we don't care about.)
# Of those objects we care about,
# the spending items what I'm calling are level 0,
# entities level 1, and sectors level 2.
#
# TERMINOLOGY
# An "item" is, more precisely, an "entity item" --
# what some specific entity spent on
# funcionamiento, inversión or deuda (the "items").

import numpy as np
import pandas as pd
import re
from   typing import Dict, List, Set, Tuple
#
import python.extract_excel.lib as extract_excel
import python.lib               as lib


input_file = "input/Ley_PGN_2013-2022.xlsx"
(year_min, year_max) = (2013, 2022)
year_range = range ( year_min, year_max + 1 )
sheet_year_preface = "Ley PGN Gasto " # The trailing space is important.

assert (
  # PTIFALL: the gasto sheet names read here
  # are only used in this test --
  # but later code only makes sense if it passes.
  extract_excel.read_sheet_names (
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
  matches_for_entity_deuda          = ["Servicio de la Deuda"]
  matches_for_entity_inversion      = ["Inversión"]
  matches_for_entity_funcionamiento = ["Funcionamiento"]
  matches_for_entity_spending = [ *matches_for_entity_deuda,
                                  *matches_for_entity_inversion,
                                  *matches_for_entity_funcionamiento, ]

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
                      matches_for_entity_deuda ) ),
  ( "inversi.n",      matches_for_entity_inversion      ),
  ( "funcionamiento", matches_for_entity_funcionamiento ),
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

def define_entity_items ( gastos : pd.DataFrame ) -> pd.DataFrame:
  df = gastos.copy () # This looks silly, but without using a copy, setting `gastos = define_entity_items ( gastos)` will trigger the Pandas warning, "A value is trying to be set on a copy of a slice from a DataFrame."
  df ["is item"] = (
    df ["name"]
    . isin ( matches_for_entity_spending )
    . astype ( int ) )
  return df

def identify_entity_and_sector_rows (
    gastos : pd.DataFrame ) -> pd.DataFrame:
  gastos["is entity"] = (
    ( ( gastos ["is item"]                  == 0 ) &
      ( gastos ["is item"] . shift ( -1 )   >  0 ) )
    . astype ( int ) )
  gastos["is sector"]                       = (
    ( ( gastos ["is item"]                  == 0 ) &
      ( gastos ["is entity"]                == 0 ) &
      ( gastos ["is entity"] . shift ( -1 ) >  0 ) )
    . astype ( int ) )

  if True: # Verify that these three kinds partition the rows.
    kinds = gastos [[ "is item", "is entity", "is sector" ]]
    kinds_sum = kinds . sum ( axis = "columns" )
    assert kinds_sum.min () == 1
    assert kinds_sum.max () == 1

  return gastos

def define_entity_and_sector (
    gastos : pd.DataFrame ) -> pd.DataFrame:
  gastos = gastos.reset_index () # PITFALL: I don't know why this is needed.
    # It looks like it should not be, but casual inspection reveals that
    # without it the data becomes garbage after the first year.
  for s in ["sector","entity","item"]:
    gastos[s] = (
      pd.Series (
        np.where ( # if-then-else
          gastos["is " + s] == 1,
          gastos["name"],
          np.nan ) )
      . fillna ( method = "ffill" ) )
  return gastos [[ "year",
                   "is sector",
                   "is entity",
                   "is item",
                   "name",
                   "sector",
                   "entity",
                   "item",
                   "cop", ]]

def keep_entity_items (
    gastos : pd.DataFrame ) -> pd.DataFrame:
  return ( gastos
           [ gastos["is item"] == 1 ]
           [[ "year",
              "sector",
              "entity",
              "item",
              "cop", ]] )

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
  gastos = (
    keep_entity_items ( # PITFALL: This throws away a lot of information. The stage immediately preceding it, `define_entity_and_sector`, makes it easy to see what's going on.
      define_entity_and_sector (
        identify_entity_and_sector_rows (
          define_entity_items (
            drop_redundant_rows (
              gastos ) ) ) ) )
    . rename ( # for consistency with `sectors` and `entities`
               # data sets from `python.extract_excel.homologacion`
      columns = { "sector" : "sector name",
                  "entity" : "entity name" } ) )
  for column_name in ["sector name", "entity name"]:
    gastos [ column_name ] = \
      lib . sanitize_string_series (
        gastos [ column_name ] )
  return gastos
