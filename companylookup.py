import os
import abc
import pandas as pd
from fuzzywuzzy import fuzz

    # "valueAddress": {
    #   "houseNumber": "5454",
    #   "road": "BEETHOVEN STREET",
    #   "postalCode": "90066",
    #   "city": "LOS ANGELES",
    #   "state": "CA",
    #   "countryRegion": "USA",
    #   "streetAddress": "5454 BEETHOVEN STREET"
    # }

# TODO: currently each strategy loops through the whole dataframe
# at current volume that is acceptable but consider other alernatives
class MatchStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, df: pd.DataFrame, invoice_data_dict: dict) -> list:
        return
    
    @abc.abstractmethod
    def dict_has_required_fields(invoice_data_dict: dict) -> bool:
        return

class FuzzyCompanyName_FuzzyStreet_ExactCity_ExactPostal_MatchStrategy(MatchStrategy):
    def dict_has_required_fields(invoice_data_dict: dict) -> bool:
        customer_name = invoice_data_dict.get('CustomerName')
        address_components = invoice_data_dict.get('CustomerAddress').get('valueAddress')

        return (
            customer_name.get("valueString") and customer_name.get('confidence') > 0.8
            and invoice_data_dict.get('CustomerAddress').get('confidence') > 0.8
            and address_components.get('houseNumber')
            and address_components.get('road')
            and address_components.get('city')
            and address_components.get('postalCode'))
    
    def execute(self, df: pd.DataFrame, invoice_data_dict: dict) -> list:
        matches = []

        company_name = invoice_data_dict.get('CustomerName'), 
        address_components = invoice_data_dict.get('CustomerAddress').get('valueAddress')

        # Iterate over the rows in the DataFrame
        # TODO: is there a better way besides the brute force loop?
        # for company lookup this is probably fine but if more volume is expected than move to a database
        for index, row in df.iterrows():
            # Compare the company name and address with the input
            name_match_ratio = fuzz.ratio(row['Name'].casefold(), company_name.get('valueString').casefold())
            street_match_ratio = fuzz.ratio(row['Street'], address_components.get('houseNumber') + ' ' + address_components.get('road'))
            city_match = address_components.get('city').casefold() == row['City'].casefold()        
            state_match = True # address_components.get('state').casefold() == row['Region'].casefold() # TODO: state abbreviations? non-US addresses?
            postal_match = address_components.get('postalCode') == row['Postal Code'] # TODO: is this US specific??

            # If the match is above a certain threshold, add the company to the list of matches
            # TODO: make the threshold configurable
            # TODO: does this matching logic make sense?
            if name_match_ratio > 80 and street_match_ratio > 80 and city_match and state_match and postal_match:
                matches.append({'company_code': row['Code'], 'company_name': row['Name']})

        return matches

class ExactCompanyName_FuzzyStreet_ExactCity_ExactPostal_MatchStrategy(MatchStrategy):
    def dict_has_required_fields(invoice_data_dict: dict) -> bool:
        customer_name = invoice_data_dict.get('CustomerName')
        address_components = invoice_data_dict.get('CustomerAddress').get('valueAddress')

        return (
            customer_name.get("valueString") and customer_name.get('confidence') > 0.8
            and invoice_data_dict.get('CustomerAddress').get('confidence') > 0.8
            and address_components.get('houseNumber')
            and address_components.get('road')
            and address_components.get('city')
            and address_components.get('postalCode'))
    
    def execute(self, df: pd.DataFrame, invoice_data_dict: dict) -> list:

        matches = []

        company_name = invoice_data_dict.get('CustomerName'), 
        address_components = invoice_data_dict.get('CustomerAddress').get('valueAddress')


        # Iterate over the rows in the DataFrame
        # TODO: is there a better way besides the brute force loop?
        # for company lookup this is probably fine but if more volume is expected than move to a database
        for index, row in df.iterrows():
            # Compare the company name and address with the input
            name_match = row['Name'].casefold() == company_name.get('valueString').casefold()
            street_match_ratio = fuzz.ratio(row['Street'], address_components.get('houseNumber') + ' ' + address_components.get('road'))
            city_match = address_components.get('city').casefold() == row['City'].casefold()        
            state_match = True # address_components.get('state').casefold() == row['Region'].casefold() # TODO: state abbreviations? non-US addresses?
            postal_match = address_components.get('postalCode') == row['Postal Code'] # TODO: is this US specific??

            # If the match is above a certain threshold, add the company to the list of matches
            # TODO: make the threshold configurable
            # TODO: does this matching logic make sense?
            if name_match and street_match_ratio > 80 and city_match and state_match and postal_match:
                matches.append({'company_code': row['Code'], 'company_name': row['Name']})

        return matches

class CompanyMatcher():
    strategy: MatchStrategy

    def __init__(self, matching_strategy: MatchStrategy) -> None:
        self.strategy = matching_strategy

    def match_companies(self, company_name: str, address_components: dict) -> list:
        # Read the CSV file
        # TODO: validate we have a company name and address data before proceeding
        # TODO: can we read this once and cache?
        df = pd.read_csv(os.environ['COMPANY_FILE_PATH'], dtype={'Postal Code':str}, keep_default_na=False)

        return self.strategy.execute(df, company_name, address_components)
        