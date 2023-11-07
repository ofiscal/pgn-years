# PURPOSE: Read and format data from the two tabs of
# `input/Homologacion.xlsx`,
# which associates names of entities and sectors with 2-digit keys.
# That's useful because the keys, unlike the names, don't change.

import pandas as pd
import re
from   typing import Dict, List, Set
#
import python.extract_excel.lib as extract_excel
import python.lib               as lib


input_file = "input/Homologacion.xlsx"
(year_min, year_max) = (2023, 2024)
year_range = range ( year_min, year_max + 1 )
sheet_year_preface = "PGN 2023 C"

assert (
  # PTIFALL: the homologacion sheet names read here
  # are only used in this test --
  # but later code only makes sense if it passes.
  extract_excel.read_sheet_names (
    input_file = input_file,
    sheet_year_preface = sheet_year_preface, )
  == [ sheet_year_preface + str(n)
       for n in year_range ] )

def drop_deleted_rows_and_column (
    df : pd.DataFrame ) -> pd.DataFrame:
  """Deleted agency/sector information appears to be redundant.
This drops it."""
  return ( df . copy ()
           [ df ["deleted"] == 0 ]
           . drop ( columns = "deleted" ) )

def mk_homologacion_years () -> Dict [ int, pd.DataFrame ]:
  """This extracts the raw tables from the two tabs of `Homologacion.xlsx`.
Those tables mix sectors and entities."""
  tabs = {}
  for year in year_range:
    df = pd.read_excel (
      io         = input_file,
      sheet_name = sheet_year_preface + str(year),
      usecols    = range(0,5), )
    df ["year"] = year
    df ["deleted"] = df ["deleted"] . fillna ( 0 ) . astype (int)
    df = drop_deleted_rows_and_column ( df )
    tabs[year] = df
    assert ( # PITFALL: A bit tricky. This assertion depends on two facts:
             # That the first year extracted is `year_min`,
             # and that the assignment to `tabs[year]` precedes the assertion.
      ( tabs[year].columns
        == tabs[year_min].columns )
      . all () )
  return tabs

def extract_sectors_or_entities (
    tabs : Dict [ int, pd.DataFrame ],
    kind_of_thing : str, # Either the string "entity" or the string "sector"
) -> pd.DataFrame:
  acc = {}
  for year in year_range:
    df = ( tabs [year]
           [["year",
             kind_of_thing + " code",
             kind_of_thing + " name",
             ]] )
    df = df [ # If it's missing either of these columns, drop the row.
      (~ df [kind_of_thing + " code"] . isnull() ) &
      (~ df [kind_of_thing + " name"] . isnull() ) ]
    df [kind_of_thing + " code"] = \
      df [kind_of_thing + " code" ] . astype (int)
    df [kind_of_thing + " name"] = \
      lib . sanitize_string_series (
        df [kind_of_thing + " name"] )
    acc [year] = df
  return pd.concat ( acc.values (),
                     axis = "rows" )
