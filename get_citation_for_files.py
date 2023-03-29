from paperqa.utils import get_citations
import os
import json
path = 'appel_citations.json'
files = [os.path.join('pdfs', f) for f in os.listdir('pdfs')]

if not os.path.exists(path):
    pass
    citations_dict = get_citations(files)
    
else:
    print('opening')
    with open(path) as f:
        citations_dict = json.load(f)


for k, v in citations_dict.items():
    if 'none' in v.lower():
        citations_dict[k] = None
    print(f'{k}: \n{v}\n\n', '-'*50)

with open('appel_citations.json', 'w') as f:
    json.dump(citations_dict, f, indent=4)