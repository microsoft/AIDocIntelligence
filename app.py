import logging
from docintelligence import crack_invoice
from companylookup import fuzzy_company_match
from gptvision import scan_invoice_with_gpt

# Function to extract address components
def extract_address_components(address_value):
    # check for None values
    components = {
        'Street': address_value.street_address,
        'City': address_value.city,
        'Zip Code': address_value.postal_code
    }
    return {k: v for k, v in components.items() if v}  # Ensure no None values

def ingest_invoice(invoice: bytes) -> dict:
    # todo: add logging
    
    # call the document analyze and poll for completion using pre-built invoice model
    invoice_data_dict = crack_invoice(invoice)

    # check the data dictionary for PO, or Company code. If any of these are found, it writes all the data and 
    # their corresponding confidence scores, along with the number of pages in the document, to the suggested company file 
    # in `.csv` format. If DI didn't extract anything for a data element, write `NONE` in that position.
    # and exit

    ## move to company metadata search
    # todo: validate these fields are available in dict
    company_match_data_dict = fuzzy_company_match(
        invoice_data_dict.get('VendorName'),
        extract_address_components(invoice_data_dict.get('VendorAddress')))

    # todo: if we got what we need from company match write json file and exit

    # no dice from cracked document data, move to GPT-4o
    gptscan_data_dict = scan_invoice_with_gpt(invoice)

    # todo: if we got what we need from company match write json file and exit

    # todo: default to manual intervention

    return True