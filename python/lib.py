import pandas as pd


def sanitize_string_series ( s : pd.Series ) -> pd.Series:
  return remove_tildes_in_series (
    s . str.upper () )

def remove_tildes_in_series ( s : pd.Series ) -> pd.Series:
  return ( s
           . str.replace ( "Á","A" )
           . str.replace ( "É","E" )
           . str.replace ( "Í","I" )
           . str.replace ( "Ó","O" )
           . str.replace ( "Ú","U" )
           . str.replace ( "Ú","U" )
           . str.replace ( "Ñ","N" )
           . str.replace ( "Ü","U" ) )
