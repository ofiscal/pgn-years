# What these data are

## Homologacion.xlsx

This describes how sectors and entities correspond over time.
An entity might have its name or its sector change.
A sector might have its name change.
Both entities and sectors can appear and disappear.

Fortunately, each entity is assigned a code at birth which never changes.
The first two digits of that code are determined by
the sector it belongs to at birth.

### PITFALL: Disappearing entities

Red items in `Homologacion.xlsx`
disappear in the year in which they are red.
But extracting formatting information from an Excel spreadsheet via Pandas
is either difficult or impossible, depending on the information in question.
Therefore I manually added a "deleted" column to both tabs of the spreadsheet.
Where it is 1, the entity no longer exists starting in that year.
That is, it is 1 for the first year in which it does *not* exist.
Otherwise it is missing.

## Ley_PGN_2013-2022.xlsx

For each year, this provides two spreadsheets: gastos and renta (ingresos).
We are concerned with gastos.
The rows of the gastos tables do NOT all represent the same kind of thing.
Some are an entity's spending on one of the three spending categories:
deuda, inversión and funcionamiento.
Some are an entity's total spending.
Some are total spending in a sector.
One is total spending.

Each sector and agency name must be propogated to everything pertaining to it.
After that, all those totals can be discarded --
or better yet, kept, but only to use as a check on our work.
