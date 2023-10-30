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

for (term, matches) in [
    # This is a safety harness, required because the government
    # might change the names of sectors or entities in the future,
    # such that one of them matches one of these regexes.
    # That would lead to our treating it the wrong way.
    # To avoid such a silent error creeping in via future changes to the data,
    # this verifies that the only regex matches are of the kind we intend.
    ( "servicio.*deuda", [ "SERVICIO DE LA DEUDA PUBLICA NACIONAL",
                           "SERVICIO DE LA DEUDA PÚBLICA NACIONAL",
                           "Servicio de la Deuda", ] ),
    ( "inversi.n",       [ "Inversión" ] ),
    ( "funcionamiento",  [ "Funcionamiento" ] ),
    ( "total.*general",  ["Total general"] ) ]:
  assert (
    pd.Series ( matches )
    . equals (
      pd.Series ( gastos [ "name" ]
                  [ gastos["name"]
                    . str.match ( ".*" + term + ".*",
                                  case = False ) ]
                  . unique() )
      . sort_values ()
      . reset_index ( drop=True ) ) )
