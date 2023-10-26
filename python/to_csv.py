import pandas as pd
import re
from   typing import Dict, List, Set


input_file = "input/Ley_PGN_2013-2022.xlsx"

gasto_re = re.compile ( "Ley PGN Gasto 20.*" )

(year_min, year_max) = (2013, 2022)

year_range = range ( year_min, year_max + 1 )

sheet_names = [ s for s in ( pd.ExcelFile ( input_file )
                        . sheet_names )
           if gasto_re.match ( s ) ]

assert sheet_names == [ "Ley PGN Gasto " + str(n)
                        for n in year_range ]

dfs : Dict [ int, pd.DataFrame ] = {}

for year in year_range:
  dfs [year] = pd.read_excel (
    io         = input_file,
    sheet_name = "Ley PGN Gasto " + str(year) )
