import logging
import json
import datetime
import os

from docintelligence import crack_invoice
import companylookup
from gptvision import scan_invoice_with_gpt

model_confidence_threshhold = os.environ.get("MODEL_CONFIDENCE_THRESHHOLD", 0.8)
candidateprocess_dict = {}

#
def attempt_company_lookup_strategies(invoice_data_dict: dict) -> dict:
    """ Attempt to match the company name and address to known companies using various strategies """

    global candidateprocess_dict

    # this list has all the strategies we want to try
    # as soon as one returns candidates we exit
    match_strategies = [
        companylookup.ExactCompanyName_FuzzyStreet_ExactCity_ExactPostal_MatchStrategy(),
        companylookup.FuzzyCompanyName_FuzzyStreet_ExactCity_ExactPostal_MatchStrategy(),
        companylookup.FuzzyCompanyName_PostCode_City_RefineByStreetAndHouse_MatchStrategy()]

    for match_strategy in match_strategies:
        # only execute this strategy if we have the required data
        if ( not match_strategy.dict_has_required_fields(invoice_data_dict) ):
            continue

        # create a matcher engine with this strategy
        matcher = companylookup.CompanyMatcher(match_strategy)

        # execute matcher
        company_candidates = matcher.match_companies(invoice_data_dict)
        
        # if we found candidates then we return and stop processing other strategies
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
    purchase_order = invoice_data.get("PurchaseOrder") or None
    if purchase_order and purchase_order.get("confidence") > model_confidence_threshhold:
        return True
    
    return False

def validate_gpt_invoice_data(invoice_data: dict) -> bool:
    # the GPT-4o data does not guarantee it will match 
    # the DI schema so we need to validate and possibly
    # scrub
    return True

def process_extracted_invoice_data(invoice_data_dict: dict) -> dict:
    global candidateprocess_dict
    # check the data dictionary for PO, or Company code. If any of these are found, it writes all the data and 
    # their corresponding confidence scores, along with the number of pages in the document, to the suggested company file 
    # in `.csv` format. If DI didn't extract anything for a data element, write `NONE` in that position.
    # and exit

    # PO Number is a special case because we immediately exit
    # since it doesn't return a list of candidates we won't
    # make it a company strategy
    if validate_po_number(invoice_data_dict):
        candidateprocess_dict["process"] = 'PONUMBER'
        candidateprocess_dict["purchaseorder"] = invoice_data_dict.get('PurchaseOrder').get('valueString')
        candidateprocess_dict["execution_end"] = datetime.datetime.now().isoformat()
        return {'candidate_process':candidateprocess_dict, 'invoice_data': invoice_data_dict}
    
    ## move to company metadata search
    company_candidates = attempt_company_lookup_strategies(invoice_data_dict)
    if ( company_candidates ):
        return company_candidates
    
    return None

def ingest_invoice(invoice: bytes) -> dict:
    """ Manage the orchestration of invoice processing """
    # TODO: add logging
    
    global candidateprocess_dict
    candidateprocess_dict = {
    'process':'',
    'strategy':'',
    'purchaseorder':'',
    'company_candidates':[],
    'execution_start': datetime.datetime.now().isoformat(),
    'execution_end': None}

    # call the document analyze and poll for completion using pre-built invoice model
    di_invoice_data_dict = crack_invoice(invoice)

    results = process_extracted_invoice_data(di_invoice_data_dict)

    if results:
        return results

    # no dice from cracked document data, move to GPT-4o
    gpt_invoice_data_dict = scan_invoice_with_gpt(invoice)

    results = process_extracted_invoice_data(gpt_invoice_data_dict)

    if results:
        return results

    # TODO: failover to manual intervention
    candidateprocess_dict["execution_end"] = datetime.datetime.now().isoformat()

    # in case of no matches we return the Doc Intelligence invoice data
    return {'candidate_process':candidateprocess_dict, 'invoice_data': di_invoice_data_dict}
