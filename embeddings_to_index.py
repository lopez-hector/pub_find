import os
import pickle
embeddings_path = '/Users/hectorlopezhernandez/PycharmProjects/paper-qa/paper-qa/pkl_files'


for file in os.listdir(embeddings_path):
    filepath = os.path.join(embeddings_path, file)
    print(filepath)
    path_and_embedding = pickle.load(open(filepath, 'rb'))
    path = file[:-16]
    print(path, len(path_and_embedding[0]), len(path_and_embedding[1]))
    break

    # get first name and year from citation
    try:
        author = re.search(r"([A-Z][a-z]+)", citation).group(1)
    except AttributeError:
        # panicking - no word??
        raise ValueError(
            f"Could not parse key from citation {citation}. Consider just passing key explicitly - e.g. docs.py (path, citation, key='mykey')"
        )
    try:
        year = re.search(r"(\d{4})", citation).group(1)
    except AttributeError:
        year = ""
    key = f"{author}{year}"
