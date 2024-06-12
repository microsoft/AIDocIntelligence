import azure.functions as func
import datetime
import json
import logging
import pandas
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from orchestrator import ingest_invoice

app = func.FunctionApp()

@app.blob_trigger(arg_name="invoiceblob", path="invoices/{filename}",
                               connection="ARTIFACT_STORAGE") 
@app.blob_input(
    arg_name="companylistingcsv", path="metadata/comp_plant_addr.csv", connection="ARTIFACT_STORAGE")
@app.blob_output(arg_name="outputblob",
                path="results/{filename}-{rand-guid}.json",
                connection="ARTIFACT_STORAGE")
def new_invoice_file(
    invoiceblob: func.InputStream, 
    companylistingcsv: func.InputStream,
    outputblob: func.Out[str]):

    # Configure OpenTelemetry to use Azure Monitor with the 
    # APPLICATIONINSIGHTS_CONNECTION_STRING environment variable.
    if ( "APPLICATIONINSIGHTS_CONNECTION_STRING" in os.environ ):
        configure_azure_monitor()

    logging.info(f"Python blob trigger function processed blob"
                f"Name: {invoiceblob.name} Blob Size: {invoiceblob.length} bytes")
    
    df = pandas.read_csv(companylistingcsv, dtype={'Postal Code':str}, keep_default_na=False)
    results = ingest_invoice(invoiceblob.read(), df)

    # do something with results
    outputblob.set(json.dumps(results))

    return

