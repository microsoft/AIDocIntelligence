import azure.functions as func
import datetime
import json
import logging

from app import ingest_invoice

app = func.FunctionApp()

@app.route(route="http_invoice")
def http_test(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Invoice processing triggered.')

    # This orchestration will be triggered by a new document in a blob
    # storage account. For now we are HTTP triggered to test functionality
    # https://learn.microsoft.com/en-us/azure/azure-functions/functions-event-grid-blob-trigger?pivots=programming-language-python

    # the blob trigger will pass the blob name to the function
    ingest_invoice()

    return func.HttpResponse("Invoice processing complete.")


@app.blob_trigger(arg_name="myblob", path="invoices",
                               connection="18bf28_STORAGE") 
def new_invoice_file(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name} Blob Size: {myblob.length} bytes")
    
    results = ingest_invoice(myblob.read())

    # do something with results

    return

