from orchestrator import ingest_invoice
from dotenv import load_dotenv
import json
import sys
import os
import pandas

def run_test():
    load_dotenv(override=True)

    fsarg = os.fsencode(sys.argv[1])

    if ( os.path.isdir(fsarg)):
        for file in os.listdir(fsarg):
            filename = os.fsdecode(file)
            if filename.endswith(".pdf"): 
                with open(sys.argv[1] + os.sep + filename, "rb") as f:
                    print ('******* ' + filename + ' *******\n')
                    print(json.dumps(ingest_invoice(f), indent=2))
                    print ('\n\n')
                continue
            else:
                continue
    elif ( os.path.isfile(fsarg)):
        with open(fsarg, "rb") as f:
            df = pandas.read_csv(os.environ["COMPANY_FILE_PATH"], dtype={'Postal Code':str}, keep_default_na=False)
            print(json.dumps(ingest_invoice(f.read(),df), indent=2))

run_test()