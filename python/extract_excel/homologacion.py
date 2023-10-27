# PURPOSE: Read and format data from the two tabs of
# `input/Homologacion.xlsx`,
# which associates names of entities and sectors with 2-digit keys.
# That's useful because the keys, unlike the names, don't change.

import pandas as pd
import re
from   typing import Dict, List, Set
#
import python.extract_excel.lib as lib


input_file = "input/Homologacion.xlsx"
(year_min, year_max) = (2023, 2024)
year_range = range ( year_min, year_max + 1 )
sheet_year_preface = "PGN 2023 C"

assert (
  # PTIFALL: the homologacion sheet names read here
  # are only used in this test --
  # but later code only makes sense if it passes.
  lib.read_sheet_names (
    input_file = input_file,
    sheet_year_preface = sheet_year_preface, )
  == [ sheet_year_preface + str(n)
       for n in year_range ] )

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
    tabs[year] = df
    assert ( # PITFALL: A bit tricky. This assertion depends on two facts:
             # That the first year extracted is `year_min`,
             # and that the assignment to `tabs[year]` precedes the assertion.
      ( tabs[year].columns
        == tabs[year_min].columns )
      . all () )
  return tabs
