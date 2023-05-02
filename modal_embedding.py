from modal import Image, SharedVolume, Stub
from src.embedding_utils import embed_queries
import torch
MOUNTED_DIR = 'PubFind'

import os

stub = Stub("PubFind")

# *create_package_mounts(["ControlNet"]),
volume = SharedVolume().persist("PubFind")

PubFind_image = Image.debian_slim() \
    .pip_install("transformers", "InstructorEmbedding", "torch", "sentence-transformers")

CACHE_PATH = '/root/instructorXL_model'


@stub.function(gpu='A10G',
               image=PubFind_image,
               shared_volumes={CACHE_PATH: volume}
               )
def get_question_embedding(queries, model_root):
    from InstructorEmbedding import INSTRUCTOR
    print(f'CUDA available" {torch.cuda.is_available()}')
    model = INSTRUCTOR('hkunlp/instructor-xl', cache_folder=model_root)
    print('Have model')

    question_embeddings = embed_queries(queries, model)
    print('Have embeddings')
    return question_embeddings
