import os

os.environ['ROOT_DIRECTORY'] = './appel'
os.environ['MODEL_ROOT'] = MODEL_ROOT = './instructorXL_model'

from src.main import initialize_docstore, get_model, get_answers
from src.embedding_utils import embed_queries
from modal_embedding import stub, get_question_embedding


def main(question, force_rebuild=False):
    # create a docstore that stays updated with the filesystem
    # it is rebuilt if pdfs are deleted and items are added when new files are detected
    docs, model = initialize_docstore(force_rebuild=force_rebuild)

    queries = [question]

    print('embedding')
    # if not model:
    #     with stub.run():
    #         model = modal_get_model.call(model_root=MODEL_ROOT)
    #
    # question_embeddings = embed_queries(queries, model)
    with stub.run():
        question_embeddings = get_question_embedding.call(queries, MODEL_ROOT)

    print('getting answers')
    answers = get_answers(docs, queries, question_embeddings)

    for answer in answers:
        print(answer.formatted_answer)


if __name__ == '__main__':
    import argparse

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Question and answer")
    # Define the command-line arguments using the add_argument() method
    parser.add_argument("question", type=str, help="Your name")

    args = parser.parse_args()
    print(f'Question: {args.question}')
    main(question=args.question, force_rebuild=False)
