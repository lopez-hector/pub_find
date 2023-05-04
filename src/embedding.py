import torch.cuda
import modal
from modal import Image, SharedVolume, Stub

MODAL_DEPLOYMENT = 'PubFind'

CACHE_PATH = '/root/instructorXL_model'

stub = Stub(MODAL_DEPLOYMENT)

# *create_package_mounts(["ControlNet"]),
volume = SharedVolume().persist(MODAL_DEPLOYMENT + '_volume')

pdfs_cache = '/root/volume'


@stub.function()
def add_pdfs_to_embed(file_paths):
    vol = modal.SharedVolume.lookup(MODAL_DEPLOYMENT + '_volume')
    for file_path in file_paths:
        vol.add_local_file(local_path=file_path, remote_path='/pdfs_to_embed/')


add_pdfs_to_embed(['/Users/hectorlopezhernandez/PycharmProjects/pub_find/appel/pdfs/Appel_ACIE_2012.pdf'])


def delete_pdfs_after_embedding(file_paths):
    modal.shared_volume.SharedVolumeHandle.remove_file(remote_path='/root/pdfs_to_embed/')


PubFind_image = Image.debian_slim() \
    .pip_install("transformers", "InstructorEmbedding", "torch", "sentence-transformers")


def embed_questions(queries, model_root, use_modal='false'):
    if use_modal.lower() == 'true':
        print('Using MODAL')
        f = modal.Function.lookup(MODAL_DEPLOYMENT, "get_question_embedding")
        question_embeddings = f.call(queries, model_root)
    else:
        print('Using Local Machine')
        question_embeddings = get_question_embedding(queries, model_root)

    return question_embeddings

    return wrapper


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
