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

gastos = (
  excel_gastos . mk_gastos ()
  . rename ( # for consistency with `sectors` and `entities` data sets
    columns = { "sector" : "sector name",
                "entity" : "entity name" } ) )

for (df, field) in [ (sectors,  "sector name" ),
                     (entities, "entity name" ), ]:
  gastos [field + " matched"] = (
    gastos [field] . str.upper ()
    . isin ( df [field] . str.upper () )
    . astype (int) )
del (df, field)

gastos . describe ()

# PITFALL: The code below is repetitive.
# The algorithm for defining `matched` and `unmatched`
# are extremely similar, except for
# a series negation symbol (~) in `unmatched`
# and maybe an upcoming a merge in `matched` (TODO)
# to include the sector or entity code.
# This redundancy could be factored out, but that would only
# replace the danger that the passages get out of sync
# with the danger of not understanding the code.

if True: # isolate matched sectors and entities
  matched = {}
  for level in ["sector", "entity"]:
    matched[level] = (
      gastos [ gastos [level + " name matched"]
               . astype ( bool ) ]
      [[ "year",
         level + " name",
         level + " name matched" ]] # kept only as a sanity check
      . copy ()
      . drop_duplicates () )
    matched[level] [ level + " code" ] = np.nan
  del (level)

if True: # isolate unmatched sectors and entities
  unmatched = {}
  for level in ["sector", "entity"]:
    unmatched[level] = (
      gastos [ ~ ( gastos [level + " name matched"]
                   . astype ( bool ) ) ]
      [[ "year",
         level + " name",
         level + " name matched" ]] # kept only as a sanity check
      . copy ()
      . drop_duplicates () )
    unmatched[level] [ level + " code" ] = np.nan
  del (level)

for (df, filename) in [
    (sectors,              "sectors"            ),
    (entities,             "entities"           ),
    (gastos,               "gastos"             ),
    (matched["sector"],    "matched_sectors"    ),
    (matched["entity"],    "matched_entities"   ),
    (unmatched["sector"],  "unmatched_sectors"  ),
    (unmatched["entity"],  "unmatched_entities" ), ]:
  df.to_excel ( filename + ".xlsx",
                index = False )
del(df, filename)
