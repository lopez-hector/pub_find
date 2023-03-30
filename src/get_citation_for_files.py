from paperqa.utils import get_citations
import os
import json

ROOT_DIRECTORY = ' '
FILE_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'pdfs')
CITATIONS_FILE = os.path.join(ROOT_DIRECTORY, 'citations.json')

path = FILE_DIRECTORY
files = [os.path.join(FILE_DIRECTORY, f) for f in os.listdir(FILE_DIRECTORY)]
#TODO: add get citations into workflow
# check if we're updating existing citations.json
if os.path.exists(path):
    print('loading existing citations file')
    with open(path) as f:
        citations_dict = json.load(f)

new_citations_dict = get_citations(files)



# look for sources where a citation wasn't found.
# will need to create these manually
for k, v in citations_dict.items():
    if 'none' in v.lower():
        citations_dict[k] = None
    print(f'{k}: \n{v}\n\n', '-'*50)

# save citations.json
with open(CITATIONS_FILE, 'w') as f:
    json.dump(citations_dict, f, indent=4)
