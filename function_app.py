import azure.functions as func
import datetime
import json
import logging
import pandas

from orchestrator import ingest_invoice

app = func.FunctionApp()

@app.blob_trigger(arg_name="invoiceblob", path="invoices",
                               connection="ARTIFACT_STORAGE") 
@app.blob_input(
    arg_name="companylistingcsv", path="metadata/comp_plant_addr.csv", connection="ARTIFACT_STORAGE")
@app.blob_output(arg_name="outputblob",
                path="results/{rand-guid}.json",
                connection="ARTIFACT_STORAGE")
def new_invoice_file(
    invoiceblob: func.InputStream, 
    companylistingcsv: func.InputStream,
    outputblob: func.Out[str]):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {invoiceblob.name} Blob Size: {invoiceblob.length} bytes")
    
    df = pandas.read_csv(companylistingcsv, dtype={'Postal Code':str}, keep_default_na=False)
    results = ingest_invoice(invoiceblob.read(), df)

    # do something with results
    outputblob.set(json.dumps(results))

    return

