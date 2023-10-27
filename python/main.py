import pandas as pd
import re
from   typing import Dict, List, Set
#
import python.extract_excel.gastos        as gastos
import python.extract_excel.homologacion  as homologacion


gastos   = gastos . raw_trimmed_unified_data ()
tabs     = homologacion.mk_homologacion_years ()
sectors  = homologacion.extract_sectors_or_entities ( tabs, "sector" )
entities = homologacion.extract_sectors_or_entities ( tabs, "entity" )
del(tabs)
