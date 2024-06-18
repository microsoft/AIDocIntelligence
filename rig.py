from orchestrator import ingest_invoice
from dotenv import load_dotenv
import json
import sys
import os
import pandas
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
import glob

def handle_file(filename):
    with open(filename, "rb") as f:
        if ( os.path.getsize(filename) > 4000000):
            return # free tier max doc size is 4MB
        print (f'******* Starting {filename} *******\n')
        with open(f'{root}{Path(filename).stem}.json', 'w', encoding='utf-8') as g:
            json.dump(ingest_invoice(filename, f, companies_df), g, ensure_ascii=False, indent=2)
        print (f'******* Completed {filename} *******\n')

# def run_test():
    
#     fsarg = os.fsencode(sys.argv[1])
#     batchstamp = f'{datetime.now():%Y%m%d_%H%M%S}'
    
#     if ( os.path.isdir(fsarg)):
#         root = f'{sys.argv[1]}{os.sep}processed{os.sep}{batchstamp}{os.sep}'
#         Path(root).mkdir(parents=True, exist_ok=True)

        
#         pool = ThreadPool(4)
#         results = pool.map(handle_file, my_array)

#         for file in os.listdir(fsarg)[0:100]:
#             filename = os.fsdecode(file)
#             if filename.endswith(".pdf"): 
#                 handle_file(root, filename, f, df)
#                 continue
#             else:
#                 continue
#     elif ( os.path.isfile(fsarg)):
#         with open(fsarg, "rb") as f:            
#             print(json.dumps(ingest_invoice(f.read(),df), indent=2))

load_dotenv(override=True)
companies_df = pandas.read_csv(os.environ["COMPANY_FILE_PATH"], dtype={'Postal Code':str}, keep_default_na=False)
fsarg = os.fsencode(sys.argv[1])
batchstamp = f'{datetime.now():%Y%m%d_%H%M%S}'

if ( not os.path.isdir(fsarg)):
    print ('bad directory')
    exit()

root = f'{sys.argv[1]}{os.sep}processed{os.sep}{batchstamp}{os.sep}'
Path(root).mkdir(parents=True, exist_ok=True)

print(f'Starting batch {batchstamp}')
pool = ThreadPool(10)
results = pool.map(handle_file, glob.glob(sys.argv[1] + '/*.pdf'))

# run this at command line with python -m rig C:\temp\ipg-inv (path to pdf invoices)