import pandas as pd
import re
from   typing import Dict, List, Set
#
import python.extract_excel.gastos        as excel_gastos
import python.extract_excel.homologacion  as homologacion


gastos   = excel_gastos . mk_gastos ()
tabs     = homologacion . mk_homologacion_years ()
sectors  = homologacion . extract_sectors_or_entities ( tabs, "sector" )
entities = homologacion . extract_sectors_or_entities ( tabs, "entity" )
del(tabs)

gastos.to_csv ( "gastos.csv",
                index = False )
