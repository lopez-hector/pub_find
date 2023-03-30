from paperqa.utils import get_citations
import os
import json

ROOT_DIRECTORY = ' '
FILE_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'pdfs')
CITATIONS_FILE = os.path.join(ROOT_DIRECTORY, 'citations.json')

path = FILE_DIRECTORY
files = [os.path.join(FILE_DIRECTORY, f) for f in os.listdir(FILE_DIRECTORY)]

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