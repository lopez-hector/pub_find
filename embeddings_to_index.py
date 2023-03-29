import os
import pickle
from paperqa import Docs
from tqdm import tqdm

embeddings_path = '/Users/hectorlopezhernandez/PycharmProjects/paper-qa/paper-qa/embeddings'
save_doc_path = '/Users/hectorlopezhernandez/PycharmProjects/paper-qa/paper-qa'
pickle_path = open('/Users/hectorlopezhernandez/PycharmProjects/paper-qa/paper-qa/appel_docs', 'wb')
index_path = os.path.join(save_doc_path, 'appel_faiss_index')

files = os.listdir(embeddings_path)

docs = Docs(index_path=index_path)

for no_files, f in enumerate(files):
    filepath = os.path.join(embeddings_path, f)

    with open(filepath, 'rb') as fb:
        processed_file = pickle.load(fb)

    file_path = f[:-15] + '.pdf'
    print(f'Adding: {file_path}')

    # parse processed file
    splits = processed_file[0]
    file_embeddings = processed_file[1]
    # todo add opportunity to update the citation here.
    metadatas = processed_file[2]  # dict(citation=citation, dockey= key, key=f"{key} pages {pg}",)
    num_tokens = processed_file[3]

    if len(metadatas[-1].keys()) < 3:
        metadatas[-1] = metadatas[-2]

    # add to doc class
    docs.add_from_embeddings(path=file_path,
                             texts=splits,
                             text_embeddings=file_embeddings,
                             metadatas=metadatas)



print(f'added: {no_files}')
pickle.dump(docs, pickle_path)
    # 
    # docs.add_from_embeddings(f[:-4], texts=splits, embeddings=file_embeddings,
    #                          metadatas=metadatas)
