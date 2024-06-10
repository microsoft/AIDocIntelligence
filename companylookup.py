import os
import abc
import pandas as pd
from fuzzywuzzy import process
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
    def dict_has_required_fields(self, invoice_data_dict: dict) -> bool:
        return

class FuzzyCompanyName_PostCode_City_RefineByStreetAndHouse_MatchStrategy(MatchStrategy):
    
    def dict_has_required_fields(self, invoice_data_dict: dict) -> bool:
        customer_name = invoice_data_dict.get('CustomerName')
        address_components = invoice_data_dict.get('CustomerAddress').get('valueAddress')

        return (
            customer_name.get("valueString") and customer_name.get('confidence') > 0.8
            and invoice_data_dict.get('CustomerAddress').get('confidence') > 0.8
            and address_components.get('streetAddress')
            and address_components.get('city'))
    
    def fuzzy_search_combined(query, df, threshold=80, limit=10):
        matches = process.extract(query, df['Combined'], limit=limit, scorer=fuzz.token_set_ratio)
        results = [df.iloc[match[2]] for match in matches if match[1] >= threshold]
        return results    

    def refine_results(initial_results, address_queries, threshold=80):
        refined_results = initial_results
        for column, query in zip(address_queries.keys(), address_queries.values()):
            refined_results = [record for record in refined_results if fuzz.token_sort_ratio(record[column], query) >= threshold]
        return refined_results

    def append_final_results_to_matches(final_results):
        matches = []
        for record in final_results:
            matches.append({'company_code': record['Code'], 'company_name': record['Name']})
        return matches

    def combine_name_address(row):
        name_parts = filter(None, [row['Name'], row['Name 1'], row['Name 2'], row['Postal Code'], row['City']])
        return ' '.join(name_parts)

    def execute(self, df: pd.DataFrame, invoice_data_dict: dict) -> list:
        matches = []

        company_name = invoice_data_dict.get('CustomerName').get('valueString')
        address_components = invoice_data_dict.get('CustomerAddress').get('valueAddress')
        
        #Combine Column for Initial Search
        df['Combined'] = df.apply(self.combine_name_address, axis=1)
                                
        #Query the column by company name, postal Code and City
        initial_query = ' '.join(filter(None, company_name.casefold(),address_components.get('postalCode').casefold(),address_components.get('city').casefold()))
   
        #Get the Initial Search resuult
        initial_results = self.fuzzy_search_combined(initial_query, df)

        #Define the refine search components
        refine_components = {
            'Street': ' '.join(filter(None, address_components.get('house').casefold(),address_components.get('streetAddress').casefold()))
        }

        #Refine the Initial Search Result 
        final_results = self.refine_results(initial_results, refine_components)

        #Append the refined result to matches 
        matches = self.append_final_results_to_matches(final_results)

        return matches

class FuzzyCompanyName_FuzzyStreet_ExactCity_ExactPostal_MatchStrategy(MatchStrategy):
    def dict_has_required_fields(self, invoice_data_dict: dict) -> bool:
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

        company_name = invoice_data_dict.get('CustomerName').get('valueString')
        address_components = invoice_data_dict.get('CustomerAddress').get('valueAddress')

        # Iterate over the rows in the DataFrame
        # TODO: is there a better way besides the brute force loop?
        # for company lookup this is probably fine but if more volume is expected than move to a database
        for index, row in df.iterrows():
            # Compare the company name and address with the input
            name_match_ratio = fuzz.ratio(row['Name'].casefold(), company_name.casefold())
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
    def dict_has_required_fields(self, invoice_data_dict: dict) -> bool:
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

        company_name = invoice_data_dict.get('CustomerName').get('valueString') 
        address_components = invoice_data_dict.get('CustomerAddress').get('valueAddress')

        # Iterate over the rows in the DataFrame
        # TODO: is there a better way besides the brute force loop?
        # for company lookup this is probably fine but if more volume is expected than move to a database
        for index, row in df.iterrows():
            # Compare the company name and address with the input
            name_match = row['Name'].casefold() == company_name.casefold()
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

    def match_companies(self, invoice_data_dict: dict) -> list:
        # Read the CSV file
        # TODO: validate we have a company name and address data before proceeding
        # TODO: can we read this once and cache?
        df = pd.read_csv(os.environ['COMPANY_FILE_PATH'], dtype={'Postal Code':str}, keep_default_na=False)

        return self.strategy.execute(df, invoice_data_dict)
        