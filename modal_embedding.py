import os
import torch.cuda
from modal import Image, SharedVolume, Stub

ROOT_DIRECTORY = './appel'
MODEL_ROOT = './instructorXL_model'

os.environ['ROOT_DIRECTORY'] = ROOT_DIRECTORY
os.environ['MODEL_ROOT'] = MODEL_ROOT

ROOT_DIRECTORY = os.environ['ROOT_DIRECTORY']
MODEL_ROOT = os.environ['MODEL_ROOT']
FILE_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'pdfs')
EMB_DIR = os.path.join(ROOT_DIRECTORY, 'embeddings')

stub = Stub("PubFind_2")

# *create_package_mounts(["ControlNet"]),
volume = SharedVolume().persist("PubFind")

PubFind_image = Image.debian_slim() \
    .pip_install("transformers", "InstructorEmbedding", "torch", "sentence-transformers")

CACHE_PATH = '/root/instructorXL_model'


@stub.function(gpu="A10G",
               image=PubFind_image,
               shared_volumes={CACHE_PATH: volume}
               )
def get_question_embedding(queries, model_root):
    from InstructorEmbedding import INSTRUCTOR
    print(f"GPU access is {'available' if torch.cuda.is_available() else 'Not Available'}")
    model = INSTRUCTOR('hkunlp/instructor-xl', cache_folder=model_root)
    print('Have model')

    question_embeddings = []

    for question in queries:
        question = 'Represent the scientific query for retrieving supporting documents; Input: ' + question
        embeds = model.encode(question)
        question_embeddings.append(embeds)

    print('Have embeddings')
    return question_embeddings

# @stub.function(gpu="A10G",
#                image=PubFind_image,
#                shared_volumes={CACHE_PATH: volume}
#                )
# def modal_embed_files(model, files_to_embed, path_citations_map):
#     parse_pdf = readers.parse_pdf
#
#     for f in tqdm(files_to_embed):
#         print(f'Processing: {f}')
#         citation = path_citations_map[f]
#
#         key = grab_key(citation)
#
#         # get texts (splits) and metadata (citation, key, key_with_page)
#         f_path = os.path.join(FILE_DIRECTORY, f)
#         splits, metadatas = parse_pdf(f_path, key=key, citation=citation, chunk_chars=1600, overlap=100)
#
#         # collect embeddings for all documents
#         file_embeddings = []
#         num_tokens = []
#
#         # encode each chunk
#         for split in tqdm(splits, mininterval=10):
#             split = 'Represent the scientific paragraph for retrieval; Input: ' + split
#             num_tokens.append(model.tokenize(split))
#             embeds = model.encode(split)
#             file_embeddings.append(embeds)
#
#         # save text chunks, file embeddings, metadatas, and num_tokens for each
#         save_dict = [splits, file_embeddings, metadatas, num_tokens]
#
#         path = os.path.join(EMB_DIR, f[:-3] + 'pkl')
#
#         with open(path, 'wb') as f:
#             pickle.dump(save_dict, f)
