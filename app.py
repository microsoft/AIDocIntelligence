import logging

def ingest_invoice() -> bool:
    
    # fetch the file

    # create a doc intelligence client

    # call the document analyze and poll for completion using pre-built invoice model

    # analyze results

    # check the data dictionary for PO, or Company code. If any of these are found, it writes all the data and 
    # their corresponding confidence scores, along with the number of pages in the document, to the suggested company file 
    # in `.csv` format. If DI didn't extract anything for a data element, write `NONE` in that position.
    # and exit

    ## move to company metadata search

    # Fuzzy company name match, if acceptable confidence match then write
    # to suggested company file and exit
    # what is acceptable confidence match? eg 80
    # are there multiple companies of smiliar names? (eg mutinational)

    # fuzzy company address match, if acceptable confidence match then write
    # to suggested company file and exit
    # what address components should be used?

    # no dice from cracked document data, move to GPT-4o

    # experiment with extraction of single data points from invoice per prompt
    # or an expansive prompt to extract all data points
    # do we get key name standardization as with DI?
    return True