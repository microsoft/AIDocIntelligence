import logging
import json

from docintelligence import crack_invoice
from companylookup import company_match
from gptvision import scan_invoice_with_gpt

model_confidence_threshhold = 0.8 # read from env var

# Function to extract address components
def extract_address_components(address_value):
    # check for None values
    components = {
        'Street': address_value.street_address,
        'City': address_value.city,
        'Zip Code': address_value.postal_code
    }
    return {k: v for k, v in components.items() if v}  # Ensure no None values

def validate_po_number(invoice_data: dict) -> bool:
    # customer_id = invoice_data.get("CustomerId")
    # if customer_id and customer_id.get("confidence") > model_confidence_threshhold:
    #     return True
    
    purchase_order = invoice_data.get("PurchaseOrder")
    if purchase_order and purchase_order.get("confidence") > model_confidence_threshhold:
        return True
    
    return False


def ingest_invoice(invoice: bytes) -> dict:
    """ Manage the orchestration of invoice processing """
    # todo: add logging
    
    # call the document analyze and poll for completion using pre-built invoice model
    invoice_data_dict = crack_invoice(invoice)

    # check the data dictionary for PO, or Company code. If any of these are found, it writes all the data and 
    # their corresponding confidence scores, along with the number of pages in the document, to the suggested company file 
    # in `.csv` format. If DI didn't extract anything for a data element, write `NONE` in that position.
    # and exit

    # TODO: for now just dumping the invoice fields data
    # but we probably want to include more processing metadta
    # such as the candidate companies and their confidence scores
    if validate_po_number(invoice_data_dict):
        candidateprocess_dict = {'process':'PONUMBER', 'purchaseorder':invoice_data_dict.get('PurchaseOrder').get('valueString')}
        return {'candidate_process':candidateprocess_dict, 'invoice_data': invoice_data_dict}
    
    ## move to company metadata search
    company_candidates = company_match(
        invoice_data_dict.get('CustomerName'), 
        invoice_data_dict.get('CustomerAddress').get('valueAddress'))
    
    if ( len(company_candidates) > 0):
        candidateprocess_dict = {'process':'COMPANY_MATCH', 'company_candidates':company_candidates}
        return {'candidate_process':candidateprocess_dict, 'invoice_data': invoice_data_dict}

    # no dice from cracked document data, move to GPT-4o
    gptscan_data_dict = scan_invoice_with_gpt(invoice)

    # todo: default to manual intervention

    return {}