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
