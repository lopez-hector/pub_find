import os

os.environ['ROOT_DIRECTORY'] = './appel'
os.environ['MODEL_ROOT'] = MODEL_ROOT = './instructorXL_model'

from src.main import initialize_docstore, get_answers
from src.embedding import embed_questions
import modal


def main(question, force_rebuild=False, use_modal=True):
    # create a docstore that stays updated with the filesystem
    # it is rebuilt if pdfs are deleted and items are added when new files are detected
    docs, model = initialize_docstore(force_rebuild=force_rebuild)

    queries = [question]

    print('embedding')
    question_embeddings = embed_questions(queries, MODEL_ROOT, use_modal=os.environ['MODAL'])

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
