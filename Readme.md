# Unit parser
This repo contains a small script that extracts units from the `units.html` file (found on http://vocab.nerc.ac.uk/collection/P06/current/) and converts a selected few (defined at the top of `main.py`) into a sparql query. This query has been added to the `app-shmdoc-osoc-poc` repo, which is read into the database using the migrations service. 

## More units?
When you want more units, you can add the ones you want to the `supported_units` list in `main.py`. Be carefull, because sparql queries have a maximum length, which you can reach quite easily. It is also possible to generate a query to add all the units from the `units.html` file, but this query is of course way too long. 

## Adding to shmdoc
Once you've created a query for units, you can add it to `app-shmdoc-osoc-poc/data/files`, so the migration service can add them. Here again a warning: Be sure to check your query is not to long. 