import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentAnalysisClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

def crack_invoice(invoice: bytes) -> dict:
    # create a doc intelligence client
    # https://learn.microsoft.com/en-us/python/api/overview/azure/ai-documentintelligence-readme?view=azure-python-preview

    """
    This code sample shows Prebuilt Invoice operations with the Azure Form Recognizer client library. 
    The async versions of the samples require Python 3.6 or later.

    To learn more, please visit the documentation - Quickstart: Document Intelligence (formerly Form Recognizer) SDKs
    https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-python
    """
    endpoint = os.environ("DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ("DOCUMENT_INTELLIGENCE_KEY")

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
        
    poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", invoice)
    invoice_data = poller.result()

    return invoice_data