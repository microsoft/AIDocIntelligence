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

class MatchStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, df: pd.DataFrame, company_name: str, address_components: dict) -> list:
        return

class FuzzyCompanyName_FuzzyStreet_ExactCity_ExactPostal_MatchStrategy(MatchStrategy):
    def execute(self, df: pd.DataFrame, company_name: str, address_components: dict) -> list:

        matches = []

        # Iterate over the rows in the DataFrame
        # TODO: is there a better way besides the brute force loop?
        # for company lookup this is probably fine but if more volume is expected than move to a database
        for index, row in df[df.Name.str.startswith('Mediabrands')].iterrows():
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
    def execute(self, df: pd.DataFrame, company_name: str, address_components: dict) -> list:

        matches = []

        # Iterate over the rows in the DataFrame
        # TODO: is there a better way besides the brute force loop?
        # for company lookup this is probably fine but if more volume is expected than move to a database
        for index, row in df[df.Name.str.startswith('Mediabrands')].iterrows():
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
        

# def company_match(company_name: str, address_components: dict) -> list:
#     # Read the CSV file
#     # TODO: validate we have a company name and address data before proceeding
#     # TODO: can we read this once and cache?
#     df = pd.read_csv(os.environ['COMPANY_FILE_PATH'], dtype={'Postal Code':str}, keep_default_na=False)

#     matches = []

#     # Iterate over the rows in the DataFrame
#     # TODO: is there a better way besides the brute force loop?
#     # for company lookup this is probably fine but if more volume is expected than move to a database
#     for index, row in df[df.Name.str.startswith('Mediabrands')].iterrows():
#         # Compare the company name and address with the input
#         name_match_ratio = fuzz.ratio(row['Name'].casefold(), company_name.get('valueString').casefold())
#         street_match_ratio = fuzz.ratio(row['Street'], address_components.get('houseNumber') + ' ' + address_components.get('road'))
#         city_match = address_components.get('city').casefold() == row['City'].casefold()        
#         state_match = True # address_components.get('state').casefold() == row['Region'].casefold() # TODO: state abbreviations? non-US addresses?
#         postal_match = address_components.get('postalCode') == row['Postal Code'] # TODO: is this US specific??

#         # If the match is above a certain threshold, add the company to the list of matches
#         # TODO: make the threshold configurable
#         # TODO: does this matching logic make sense?
#         if name_match_ratio > 80 and street_match_ratio > 80 and city_match and state_match and postal_match:
#             matches.append({'company_code': row['Code'], 'company_name': row['Name']})

#     return matches