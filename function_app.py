import azure.functions as func
import datetime
import json
import logging

from orchestrator import ingest_invoice

app = func.FunctionApp()

@app.blob_trigger(arg_name="invoice_blob", path="invoices",
                               connection="ARTIFACT_STORAGE") 
@app.blob_output(arg_name="outputblob",
                path="results/{rand-guid}.json",
                connection="ARTIFACT_STORAGE")
def new_invoice_file(invoice_blob: func.InputStream, outputblob: func.Out[str]):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {invoice_blob.name} Blob Size: {invoice_blob.length} bytes")
    
    results = ingest_invoice(invoice_blob.read())

    # do something with results
    outputblob.set(json.dumps(results))

    return

