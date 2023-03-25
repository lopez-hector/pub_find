from paperqa.utils import get_input_tokens
import os
import json


json_name = 'erics_docs_tokenized'
if os.path.exists(json_name):
    docs_processed = json.load(open(json_name, 'r'))
    total_tokens = sum(docs_processed.values())
    for k in docs_processed:
        docs_processed[k] = (docs_processed[k], 
                             str(round(docs_processed[k]/total_tokens*100, 2)) + "%", 
                             '$' + str(round(docs_processed[k]*0.0004, 2)))
else:
    files = [os.path.join('pdfs', f) for f in os.listdir('pdfs')]
    total_tokens, docs_processed = get_input_tokens(files)
    
    with open(json_name, 'w') as f:
        json.dump(docs_processed, f, indent=4)
    
[print(f'{k}: {item}') for k, item in enumerate(sorted(docs_processed.items(), key=lambda x: x[1], reverse=False))]
print(f'Total tokens: {total_tokens}\nEstimated Price: {0.0004*total_tokens:.2f}')
