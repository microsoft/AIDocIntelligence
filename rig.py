from orchestrator import ingest_invoice
from dotenv import load_dotenv
import json
import sys
import os

def run_test():
    load_dotenv()

    directory = os.fsencode(sys.argv[1])

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".pdf"): 
            with open(sys.argv[1] + '\\' + filename, "rb") as f:
                print ('******* ' + filename + ' *******\n')
                print(json.dumps(ingest_invoice(f), indent=2))
                print ('\n\n')
            continue
        else:
            continue

run_test()