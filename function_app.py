import azure.functions as func
import datetime
import json
import logging
import pandas
import os

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from orchestrator import ingest_invoice
from pathlib import Path
from datetime import datetime

app = func.FunctionApp()

@app.blob_trigger(
    arg_name="invoiceblob", 
    path="invoices-inbox/{filename}",
    connection="ARTIFACT_STORAGE") 
@app.blob_input(
    arg_name="companylistingcsv", 
    path="metadata/comp_plant_addr.csv", 
    connection="ARTIFACT_STORAGE")
@app.blob_output(
    arg_name="outputblob",
    path="invoices-results/{filename}-{rand-guid}.json",
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
    invoice_blob_bytes = invoiceblob.read()
    results = ingest_invoice(invoice_blob_bytes, df)

    # do something with results
    outputblob.set(json.dumps(results))

    # copy to processed container
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('ARTIFACT_STORAGE'))
    # TODO: container name should be soft-coded here
    container_client = blob_service_client.get_container_client("invoices-processed")
    container_client.upload_blob(f'{Path(invoiceblob.name).stem}_{datetime.now():%Y%m%d_%H%M%S.%f}{Path(invoiceblob.name).suffix}', invoice_blob_bytes)

    # TODO: container name should be soft-coded here
    blob_client = blob_service_client.get_blob_client("invoices-inbox",Path(invoiceblob.name).name)
    blob_client.delete_blob()

    return

