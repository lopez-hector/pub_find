from typing import List, Optional, Tuple, Union
from functools import reduce
import re
from .utils import maybe_is_text, maybe_is_truncated
from .qaprompts import distill_chain, qa_chain, edit_chain
from dataclasses import dataclass
from .readers import read_doc
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings


@dataclass
class Answer:
    """A class to hold the answer to a question."""

    question: str
    answer: str
    context: str
    references: str
    formatted_answer: str


class Docs:
    """A collection of documents to be used for answering questions."""

    def __init__(self, chunk_size_limit: int = 3000) -> None:
        self.docs = dict()
        self.chunk_size_limit = chunk_size_limit
        self.keys = set()
        self._faiss_index = None

    def add(
        self,
        path: str,
        citation: str,
        key: Optional[str] = None,
        disable_check: bool = False,
    ) -> None:
        """Add a document to the collection."""
        if path in self.docs:
            raise ValueError(f"Document {path} already in collection.")
        if key is None:
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
        suffix = ""
        while key + suffix in self.keys:
            # move suffix to next letter
            if suffix == "":
                suffix = "a"
            else:
                suffix = chr(ord(suffix) + 1)
        key += suffix
        self.keys.add(key)

        """
            texts - list of strings of length chunk_chars for this document
            self.docs - dict that contain a dict for each document
                keys: texts: broken up doc into chunk_chars
                metadata: describing the chuncks
                key: author year descriptor
        """
        texts, metadata = read_doc(path, citation, key, chunk_chars=4000, overlap=50)
        # loose check to see if document was loaded
        if not disable_check and not maybe_is_text("".join(texts)):
            raise ValueError(
                f"This does not look like a text document: {path}. Path disable_check to ignore this error."
            )

        # save current doc to class var docs
        self.docs[path] = dict(texts=texts, metadata=metadata, key=key)

        if self._faiss_index is not None:
            self._faiss_index.add_texts(texts, metadatas=metadata)

    # to pickle, we have to save the index as a file
    def __getstate__(self):
        if self._faiss_index is None:
            self._build_faiss_index()
        state = self.__dict__.copy()
        state["_faiss_index"].save_local("faiss_index")
        del state["_faiss_index"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._faiss_index = FAISS.load_local("faiss_index", OpenAIEmbeddings())


    def _build_faiss_index(self):
        """
            langchain.vectorstores.FAISS
                from_texts(texts[list], embeddings bases, metadatas)
               This is a user-friendly interface that:
               Embeds documents.
               Creates an in memory docstore.
               Initializes the FAISS database
           """
        if self._faiss_index is None:
            # self.docs: keys: unique paths values: dict(keys=texts, metadata, key)
            # use reduce function to concatenate ALL doc texts and metadata from path related dict to list
            # each entry in list [len == # docs] is a list [len == NoCharsinText / chunk_chars]
            texts = reduce(
                lambda x, y: x + y, [doc["texts"] for doc in self.docs.values()], []
            )
            metadatas = reduce(
                lambda x, y: x + y, [doc["metadata"] for doc in self.docs.values()], []
            )

            # build faiss_index
            self._faiss_index = FAISS.from_texts(
                texts, OpenAIEmbeddings(), metadatas=metadatas
            )

    def get_evidence(self, question: str, k: int = 3, max_sources: int = 5):
        """

        :param question:
        :param k:
        :param max_sources:
        :return:
                context_str
                - (author, year): distilled text \n\n ...
                - Valid Keys: (author, year), ...
        """
        context = []
        if self._faiss_index is None:
            self._build_faiss_index()  # Builds with OpenAIEmbeddings

        # want to work through indices but less k
        # self._faiss_index = FAISS.from_texts(texts, OpenAIEmbeddings(), metadatas=metadatas)

        # this is a method on the FAISS datastore
        # converts query to OpenAI Embedding, performs search for k nearest neighbors
        # these docs are filtered
        docs = self._faiss_index.max_marginal_relevance_search(
            question, k=k, fetch_k=5 * k
        )

        """
            For each nearest neighbor grab the distill relevant information from nearest
            neighbors using the question/query.
            CAUTION: Several calls to LLM in this loop
        """
        for doc in docs:
            c = (
                doc.metadata["key"],
                doc.metadata["citation"],
                distill_chain.run(question=question, context_str=doc.page_content),
            )
            if "Not applicable" not in c[-1]:
                context.append(c)
            if len(context) == max_sources:
                break

        """
            Create context_str
                - (author, year): distilled text \n\n ...
                - Valid Keys: (author, year), ...
        """
        context_str = "\n\n".join(
            [f"{k}: {s}" for k, c, s in context if "Not applicable" not in s]
        )
        valid_keys = [k for k, c, s in context if "Not applicable" not in s]

        if len(valid_keys) > 0:
            context_str += "\n\nValid keys: " + ", ".join(valid_keys)

        return context_str, {k: c for k, c, s in context}

    def query(
        self,
        query: str,
        k: int = 5,
        max_sources: int = 5,
        max_tokens: int = -1,
        length_prompt: str = "about 100 words",
    ):
        """
        Called after adding documents to class.

        :param max_tokens:
        :param query:
        :param k:
        :param max_sources:
        :param length_prompt:
        :return:
        """

        context_str, citations = self.get_evidence(query, k=k, max_sources=max_sources)

        if len(context_str) < 10:
            answer = "I cannot answer this question due to insufficient information."
        else:
            '''
                LLM Call - 1 per question answer
            '''
            answer = qa_chain(max_tokens=max_tokens).run(
                question=query, context_str=context_str, length=length_prompt
            )[1:]
            if maybe_is_truncated(answer):
                answer = edit_chain.run(question=query, answer=answer)

        # make bibliography
        bib = dict()
        for key, citation in citations.items():
            # do check for whole key (so we don't catch Callahan2019a with Callahan2019)
            skey = key.split(" ")[0]
            if skey + " " in answer or skey + ")" in answer:
                bib[skey] = citation
        bib_str = "\n\n".join(
            [f"{i+1}. ({k}): {c}" for i, (k, c) in enumerate(bib.items())]
        )
        formatted_answer = f"Question: {query}\n\n{answer}\n"
        if len(bib) > 0:
            formatted_answer += f"\nReferences\n\n{bib_str}\n"
        return Answer(
            answer=answer,
            question=query,
            formatted_answer=formatted_answer,
            context=context_str,
            references=bib_str,
        )
