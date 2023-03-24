import json
from paperqa import Docs
import pickle
import os
pickle_path = "danielle_docs.pkl"
ADD = False
length_prompt = 'about 25 words'
max_tokens = 50
citations = json.load(open('Danielle_Papers/citaions_danielle.json'))
file_paths = []
query = "Describe a polymer?"

# instantiate Docs
if not os.path.exists(pickle_path):
    docs = Docs()
else:
    print('opening')
    with open(pickle_path, "rb") as f:
        docs = pickle.load(f)

# add files
if ADD:
    for doc in file_paths:
        citation = citations[doc]
        try:
            docs.add(doc, citation)
        except ValueError:
            print('Moving to next file.')

    with open(pickle_path, "wb") as f:
        pickle.dump(docs, f)


answer = docs.query(query, length_prompt=length_prompt)
print(answer.formatted_answer)
