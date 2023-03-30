from src.main import initialize_docstore, get_model, get_answers, embed_queries


def main(force_rebuild=False):
    # create a docstore that stays updated with the filesystem
    # it is rebuilt if pdfs are deleted and items are added when new files are detected
    docs, model = initialize_docstore(force_rebuild=force_rebuild)

    queries = ['How to prevent wildfires using hydrogels?']

    print('embedding')
    if not model:
        model = get_model()
    question_embeddings = embed_queries(queries, model)

    print('getting answers')
    answers = get_answers(docs, queries, question_embeddings)

    for answer in answers:
        print(answer.formatted_answer)


main(force_rebuild=True)
