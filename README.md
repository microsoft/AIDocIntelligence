# Intelligent Document Processing with GPT Fallback

The use of Azure Document Intelligence and its pre-built models is a well-established method to crack unstructured documents. Nevertheless, there are always documents that it is unable to perform reilable extraction with. This process attempts to extract required data points for an invoice. If those elements are not found then we fall back to other means.
- Fuzzy matching against a list of known vales
- Use of GPT models to extract data

## Prerequisites for local dev
* Python 3.11
* Azure Functions Core Tools
* Azure Document Intelligence instance with endpoint and API key
* CSV that matches format Type, Code, Name, Name 1, Name 2, City, District, Postal Code, Street, House Number, Country Key, Region

## Environment Variables
* ARTIFACT_STORAGE
* DOCUMENT_INTELLIGENCE_ENDPOINT
* DOCUMENT_INTELLIGENCE_KEY
* COMPANY_FILE_PATH
* MODEL_CONFIDENCE_THRESHHOLD=0.8
* GPT4_API_KEY
* GPT4_ENDPOINT
* APPLICATIONINSIGHTS_CONNECTION_STRING

For local dev add these to a local.settings.json file 

## Storage account setup
The storage account should have three containers that the function app can write to:
1. invoices-inbox
2. invoices-results
3. invoices-processed

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
