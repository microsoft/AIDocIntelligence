import logging
import json
import datetime

from docintelligence import crack_invoice
import companylookup
from gptvision import scan_invoice_with_gpt

model_confidence_threshhold = 0.8 # read from env var
candidateprocess_dict = {}

#
def attempt_company_lookup_strategies(invoice_data_dict: dict) -> dict:
    """ Attempt to match the company name and address to known companies using various strategies """

    global candidateprocess_dict

    # this list has all the strategies we want to try
    # as soon as one returns candidates we exit
    match_strategies = [
        companylookup.ExactCompanyName_FuzzyStreet_ExactCity_ExactPostal_MatchStrategy(),
        companylookup.FuzzyCompanyName_FuzzyStreet_ExactCity_ExactPostal_MatchStrategy()]

    for match_strategy in match_strategies:
        matcher = companylookup.CompanyMatcher(match_strategy)

        company_candidates = matcher.match_companies(
            invoice_data_dict.get('CustomerName'), 
            invoice_data_dict.get('CustomerAddress').get('valueAddress'))
        
        if ( len(company_candidates) > 0):
            candidateprocess_dict["process"] = 'COMPANY_MATCH'
            candidateprocess_dict["strategy"] = match_strategy.__class__.__name__
            candidateprocess_dict["company_candidates"] = company_candidates
            candidateprocess_dict["execution_end"] = datetime.datetime.now().isoformat()
            return {'candidate_process':candidateprocess_dict, 'invoice_data': invoice_data_dict}
        
    return None
    
def validate_po_number(invoice_data: dict) -> bool:
    # customer_id = invoice_data.get("CustomerId")
    # if customer_id and customer_id.get("confidence") > model_confidence_threshhold:
    #     return True
    
    # TODO: is there any format to PO number we could verify?
    purchase_order = invoice_data.get("PurchaseOrder")
    if purchase_order and purchase_order.get("confidence") > model_confidence_threshhold:
        return True
    
    return False


def ingest_invoice(invoice: bytes) -> dict:
    """ Manage the orchestration of invoice processing """
    # TODO: add logging
    
    global candidateprocess_dict
    candidateprocess_dict = {
    'process':'',
    'strategy':'',
    'purchaseorder':'',
    'candidates':[],
    'execution_start': datetime.datetime.now().isoformat(),
    'execution_end': None}

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
        candidateprocess_dict["process"] = 'PONUMBER'
        candidateprocess_dict["purchaseorder"] = invoice_data_dict.get('PurchaseOrder').get('valueString')
        candidateprocess_dict["execution_end"] = datetime.datetime.now().isoformat()
        return {'candidate_process':candidateprocess_dict, 'invoice_data': invoice_data_dict}
    
    ## move to company metadata search
    company_candidates = attempt_company_lookup_strategies(invoice_data_dict)
    if ( company_candidates ):
        return company_candidates

    # no dice from cracked document data, move to GPT-4o
    gptscan_data_dict = scan_invoice_with_gpt(invoice)

    # todo: default to manual intervention
    candidateprocess_dict["execution_end"] = datetime.datetime.now().isoformat()
    return {'candidate_process':candidateprocess_dict, 'invoice_data': invoice_data_dict}