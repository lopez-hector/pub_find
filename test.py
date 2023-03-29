import json
from paperqa import Docs
import pickle
import os

docs_pickle_path = "/Users/hectorlopezhernandez/PycharmProjects/paper-qa/paper-qa/appel_docs"

pickled_questions = open('/Users/hectorlopezhernandez/PycharmProjects/paper-qa/paper-qa'
                         '/questions_wildfire_embeddings.pkl',
                         'rb')
# ["Could you explain how hydrogels can be used for wildfire prevention?"]
# ["What are yield stress fluids?",
#             "How would you determine if a fluid is injectable?"]
queries = ["Could you explain how hydrogels can be used for wildfire prevention?"]
query_vectors = pickle.load(pickled_questions)

length_prompt = 'about 50 words'
max_tokens = 50

ADD = False
citations = json.load(open('/Users/hectorlopezhernandez/PycharmProjects/paper-qa/h_resources/Danielle_Papers'
                           '/citaions_danielle.json'))
file_paths = []

# instantiate Docs
if not os.path.exists(docs_pickle_path):
    docs = Docs()
else:
    print('opening')
    with open(docs_pickle_path, "rb") as f:
        docs = pickle.load(f)
    for i, query in enumerate(queries):
        answer = docs.query(query, embedding=query_vectors[i], length_prompt=length_prompt)
        print(answer.formatted_answer)

# add files
if ADD:
    for doc in file_paths:
        citation = citations[doc]
        try:
            docs.add(doc, citation)
        except ValueError:
            print('Moving to next file.')

    with open(docs_pickle_path, "wb") as f:
        pickle.dump(docs, f)
