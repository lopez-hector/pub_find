import os
from InstructorEmbedding import INSTRUCTOR
import json
from tqdm import tqdm
import re
from paperqa import readers, Docs
import pickle
from src.embedding import embed_file_chunks

ROOT_DIRECTORY = os.environ['ROOT_DIRECTORY']

FILE_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'pdfs')
EMB_DIR = os.path.join(ROOT_DIRECTORY, 'embeddings')
CITATIONS_FILE = os.path.join(ROOT_DIRECTORY, 'citations.json')
DOCS_FILE = os.path.join(ROOT_DIRECTORY, 'docs')
INDEX_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'index')


def get_model():
    model_root = 'embedding_models'
    model = INSTRUCTOR('hkunlp/instructor-xl', cache_folder=model_root)

    return model


def files_for_search(file_directory, delete_remove=True):
    # create embeddings directory if needed
    emb_dir = EMB_DIR
    if not os.path.exists(emb_dir):
        os.makedirs(emb_dir)

    files = [f[:-4] for f in os.listdir(file_directory)
             if f[-3:] == 'pdf' and 'cover' not in f.lower()]

    embedded_files = [f[:-4] for f in os.listdir(emb_dir) if f[-3:] == 'pkl']

    files_not_embedded = [f + '.pdf' for f in files if f not in embedded_files]

    # check if pdfs were removed. If so then we have to remove the embedding file as well
    files_embedded_but_no_longer_present = [f + '.pkl' for f in embedded_files if f not in files]

    files_removed = False
    if delete_remove and files_embedded_but_no_longer_present:
        files_removed = True
        print('Deleting')
        print(files_embedded_but_no_longer_present)
        for f in files_embedded_but_no_longer_present:
            remove_path = os.path.join(EMB_DIR, f)
            os.remove(remove_path)
    # print(files_embedded_but_no_longer_present)
    # print(files)
    # print('-'*50)
    # print(embedded_files)
    # print(len(files_not_embedded))
    return files_not_embedded, files_removed


def grab_key(citation):
    # get key for document
    try:
        author = re.search(r"([A-Z][a-z]+)", citation).group(1)
    except AttributeError:
        # panicking - no word??
        raise ValueError(
            f"Could not parse key from citation {citation}. Consider just passing key explicitly - e.g. docs.py (path, citation, key='mykey')"
        )
    try:
        year = re.search(r"(\d{4})", citation).group(1)
        if 1900 < int(year) < 2030:
            year = year
        else:
            year = ""
    except AttributeError:
        year = ""

    return f"{author}{year}"


def embed_files(files_to_embed, path_citations_map):
    os.makedirs(EMB_DIR, exist_ok=True)

    # get model
    parse_pdf = readers.parse_pdf

    for f in tqdm(files_to_embed):
        print(f'Processing: {f}')
        citation = path_citations_map[f]

        key = grab_key(citation)

        # get texts (splits) and metadata (citation, key, key_with_page)
        f_path = os.path.join(FILE_DIRECTORY, f)
        splits, metadatas = parse_pdf(f_path, key=key, citation=citation, chunk_chars=1200, overlap=100)

        file_embeddings, num_tokens = embed_file_chunks(splits, use_modal=os.environ['MODAL'])

        # save text chunks, file embeddings, metadatas, and num_tokens for each
        save_dict = [splits, file_embeddings, metadatas, num_tokens]

        path = os.path.join(EMB_DIR, f[:-3] + 'pkl')
        print(f'Saving embeddings to path: {path}')
        # save embeddings
        with open(path, 'wb') as fp:
            pickle.dump(save_dict, fp)


def compare_object_with_dir(docs):
    # check if there are files missing from docs
    files_in_docs = set(docs.docs)
    embeddings_in_directory = set([f[:-4] for f in os.listdir(EMB_DIR) if f[-3:] == 'pkl'])

    return embeddings_in_directory.difference(files_in_docs)


def update_embeddings(docs):
    """
    compare Docs contents with directory
    - add embeddings to docstore if needed
    """
    embedding_files_to_add = compare_object_with_dir(docs)
    citations = json.load(open(CITATIONS_FILE, 'r'))

    if len(embedding_files_to_add) == 0:
        print('Docstore is up to date')
        return
    else:
        # need to compare doc keys and set made from embedding directory
        print('Adding embedding_files_to_add')
        no_files = -1
        for no_files, f in enumerate(embedding_files_to_add):
            file_path = os.path.join(EMB_DIR, f + '.pkl')

            with open(file_path, 'rb') as fb:
                processed_file = pickle.load(fb)

            docs_filepath = f
            print(f'Adding: {docs_filepath}')

            # parse processed file
            splits = processed_file[0]
            file_embeddings = processed_file[1]
            # todo add opportunity to update the citation here.
            metadatas = processed_file[2]  # dict(citation=citation, dockey= key, key=f"{key} pages {pg}",)

            for metadata in metadatas:
                metadata['citation'] = citations[docs_filepath + '.pdf']

            num_tokens = processed_file[3]

            if len(metadatas[-1].keys()) < 3:
                metadatas[-1] = metadatas[-2]

            # add to doc class
            docs.add_from_embeddings(path=docs_filepath,
                                     texts=splits,
                                     text_embeddings=file_embeddings,
                                     metadatas=metadatas)
        print(f'added: {no_files}')

        with open(DOCS_FILE, 'wb') as fb:
            pickle.dump(docs, fb)

        return


def initialize_docstore(force_rebuild=False):
    # compare pdf files with embedding pkl files. If they don't match we can add or remove files
    files_to_embed, files_removed_bool = files_for_search(FILE_DIRECTORY)
    print(files_to_embed)

    # embed files
    if files_to_embed:
        print('Embedding New Files')
        # grab model from local or download if needed

        path_citations_map = json.load(open(CITATIONS_FILE, 'r'))
        embed_files(files_to_embed, path_citations_map)

        # double check that everything is embedded
        # remaining_files = files_for_search(FILE_DIRECTORY)

        # there may be an issue here where pkl takes a while to save to filesystem and the program continues executing

    # generate Doc or load Doc
    # if doc exists, and we haven't removed any files load the doc object
    if os.path.exists(DOCS_FILE) and not files_removed_bool and not force_rebuild:
        print('Loading DOCS')
        with open(DOCS_FILE, 'rb') as fb:
            docs = pickle.load(fb)
    else:  # if doc doesn't exist, or we have removed files create a new instance of the object
        print('creating new DOCS')
        docs = Docs(index_path=INDEX_DIRECTORY)

    # add embeddings
    update_embeddings(docs)

    return docs


def update_filenames():
    for f in os.listdir(EMB_DIR):
        old_path = os.path.join(EMB_DIR, f)
        new_path = os.path.join(EMB_DIR, f[:-15] + '.pkl')
        # print(new_path)
        os.rename(old_path, new_path)


def get_answers(docs, queries, question_embeddings):
    answers = []
    length_prompt = 'about 50 words'
    for query, embedding in zip(queries, question_embeddings):
        answers.append(docs.query(query, embedding=embedding, length_prompt=length_prompt, k=5))

    return answers
