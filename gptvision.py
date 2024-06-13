import os
import tempfile
import pymupdf
from openai import AzureOpenAI
import base64
import json

    # "valueAddress": {
    #   "houseNumber": "5454",
    #   "road": "BEETHOVEN STREET",
    #   "postalCode": "90066",
    #   "city": "LOS ANGELES",
    #   "state": "CA",
    #   "countryRegion": "USA",
    #   "streetAddress": "5454 BEETHOVEN STREET"
    # }

def scan_invoice_with_gpt(invoice: bytes) -> dict:
    # create a GPT-4o client
    # https://learn.microsoft.com/en-us/python/api/overview/azure/ai-documentintelligence-readme?view=azure-python-
    # https://platform.openai.com/docs/guides/vision
    # We currently support PNG (.png), JPEG (.jpeg and .jpg), WEBP (.webp), and non-animated GIF (.gif).
    images = convert_pdf_to_images(invoice)

    # this prompt tries to do a complete extraction in one shot
    prompt_structure = {
        "PurchaseOrder": {"valueString": "", "confidence": 100},
        "CustomerName": {"valueString": "", "confidence": 100},
        "CustomerAddress": {
            "valueAddress": {
                "houseNumber": "",
                "road": "",
                "city": "",
                "state": "",
                "postalCode": ""
            },
            "confidence": 100
        }
    }

    # TODO: quality of extract might be improved with more thorough prompting, perhaps with examples
    prompt = ("Extract the data from this invoice and return it as json. If a value is not present, provide an empty string. Do not format the response with markdown. Use the following structure: " + json.dumps(prompt_structure))

    messages_content = [
        {
            "type": "text",
            "text": prompt,
        }
    ]

    for image in images:
        messages_content.append(
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64.b64encode(image).decode('utf-8')}"
            }
        })

    oai_client = AzureOpenAI(
        # https://learn.microsoft.com/azure/ai-services/openai/reference#rest-api-versioning
        api_version="2024-02-01",
        # https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
        azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT")
    )

    api_response = oai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages= [
            {
                "role":"user",
                "content":messages_content
            }
        ]
    )

    # TODO: validate api_response

    return (json.loads(api_response.choices[0].message.content))

def convert_pdf_to_images(invoice: bytes) -> list:
    images = []

    # TODO: when run locally invoice is not a byte array
    # and this stream parameter throws an exception
    pdf_document = pymupdf.open(stream=invoice)
    for page_number in range(len(pdf_document)):  
        page = pdf_document.load_page(page_number)  
        image = page.get_pixmap().pil_tobytes(format="PNG")
        images.append(image)

    return images