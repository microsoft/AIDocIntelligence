def scan_invoice_with_gpt(invoice: bytes) -> dict:
    # create a GPT-4o client
    # https://learn.microsoft.com/en-us/python/api/overview/azure/ai-documentintelligence-readme?view=azure-python-
    # https://platform.openai.com/docs/guides/vision
    # We currently support PNG (.png), JPEG (.jpeg and .jpg), WEBP (.webp), and non-animated GIF (.gif).

    # experiment with extraction of single data points from invoice per prompt
    # or an expansive prompt to extract all data points
    # do we get key name standardization as with DI?
    # convert each PDF page To image?
    return {}