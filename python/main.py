import numpy as np
import pandas as pd
import re
from   typing import Dict, List, Set
#
import python.extract_excel.gastos        as excel_gastos
import python.extract_excel.homologacion  as homologacion


tabs     = homologacion . mk_homologacion_years ()
sectors  = homologacion . extract_sectors_or_entities ( tabs, "sector" )
entities = homologacion . extract_sectors_or_entities ( tabs, "entity" )
del (tabs)

gastos = excel_gastos . mk_gastos ()

for (df, field) in [ (sectors,  "sector" ),
                     (entities, "entity" ), ]:
  gastos = gastos.merge (
    right = df [[ field + " name",
                  field + " code", ]],
    how = "left", # important! don't throw anything away if unmatched
    on = field + " name" )
del (df, field)

gastos . describe ()

# PITFALL: The code below is repetitive.
# The algorithm for defining `matched` and `unmatched`
# are extremely similar, except for
# a series negation symbol (~) in `matched`.
# This redundancy could be factored out, but that would only
# replace the danger that the passages get out of sync
# with the danger of not understanding the code.

if True: # isolate matched sectors and entities
  matched = {}
  for level in ["sector", "entity"]:
    matched[level] = (
      gastos [ ~ gastos [level + " code"]
               . isnull () ]
      [[ "year",
         level + " name",
         level + " code" ]]
      . copy ()
      . drop_duplicates ()
      . sort_values ( [ level + " name", "year" ] ) )
  del (level)

if True: # isolate unmatched sectors and entities
  unmatched = {}
  for level in ["sector", "entity"]:
    unmatched[level] = (
      gastos [ gastos [level + " code"]
               . isnull () ]
      [[ "year",
         level + " name",
         level + " code" ]]
      . copy ()
      . drop_duplicates ()
      . sort_values ( [ level + " name", "year" ] ) )
  del (level)

for (df, filename) in [
    (sectors,               "sectors"            ),
    (entities,              "entities"           ),
    (gastos,                "gastos"             ),
    (matched["sector"],     "matched_sectors"    ),
    (matched["entity"],     "matched_entities"   ),
    (unmatched["sector"],   "unmatched_sectors"  ),
    (unmatched["entity"],   "unmatched_entities" ),

    # PITFALL | TODO: The next two data sets only make sense if
    # entities and sectors with the same name are in fact the same.
    ( ( unmatched["sector"]
        . drop ( columns = "year" )
        . drop_duplicates () ),
      "unmatched_sectors_yearless"  ),
    ( ( unmatched["entity"]
        . drop ( columns = "year" )
        . drop_duplicates () ),
      "unmatched_entities_yearless"  ),
]:
  df . to_excel ( filename + ".xlsx",
                  index = False )
del(df, filename)

# us = unmatched["sector"]
# ue = unmatched["entity"]
