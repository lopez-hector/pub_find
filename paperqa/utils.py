import math
import string
from tqdm import tqdm
from langchain.chains import LLMChain
import os, datetime


def maybe_is_text(s, thresh=2.5):
    if len(s) == 0:
        return False
    # Calculate the entropy of the string
    entropy = 0
    for c in string.printable:
        p = s.count(c) / len(s)
        if p > 0:
            entropy += -p * math.log2(p)

    # Check if the entropy is within a reasonable range for text
    if entropy > thresh:
        return True
    return False


def maybe_is_code(s):
    if len(s) == 0:
        return False
    # Check if the string contains a lot of non-ascii characters
    if len([c for c in s if ord(c) > 128]) / len(s) > 0.1:
        return True
    return False


def strings_similarity(s1, s2):
    if len(s1) == 0 or len(s2) == 0:
        return 0
    # break the strings into words
    s1 = set(s1.split())
    s2 = set(s2.split())
    # return the similarity ratio
    return len(s1.intersection(s2)) / len(s1.union(s2))


def maybe_is_truncated(s):
    punct = [".", "!", "?", '"']
    if s[-1] in punct:
        return False
    return True


def maybe_is_html(s):
    if len(s) == 0:
        return False
    # check for html tags
    if "<body" in s or "<html" in s or "<div" in s:
        return True


from .readers import parse_pdf
import tiktoken


def get_input_tokens(list_of_filenames, model='text-embedding-ada-002'):
    encoding = tiktoken.encoding_for_model(model)
    total_tokens = 0

    docs_processed = {}

    for doc in tqdm(list_of_filenames):
        try:
            texts, _ = parse_pdf(doc, 'None', 'None', chunk_chars=3000)
            num_tokens = 0
            for text in texts:
                encoded_text = encoding.encode(text)
                num_tokens += len(encoded_text)

            docs_processed[doc] = num_tokens
        except:
            docs_processed[doc] = False

    total_tokens = sum(docs_processed.values())

    return total_tokens, docs_processed



from langchain.llms import OpenAI, OpenAIChat


def get_citations(list_of_filenames):

    from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate, \
        SystemMessagePromptTemplate, SystemMessage

    system_message = SystemMessage(content="You are a scholarly researcher that answers in an unbiased, scholarly tone."
                                           "You sometimes refuse to answer if there is insufficient information.")

    citation_prompt = HumanMessagePromptTemplate.from_template(
        "Return a possible citation for the following text. Do not include URLs. "
        "Citation should be in MLA format. Do not summarize"
        "the text. Only return the citation with the DOI.\n"

        "text: {text}\n\n"
        "Citation:"
        "If a citation cannot be determined from the text return None."
    )

    llm = OpenAIChat(temperature=0.1, max_tokens=512, model_name='gpt-3.5-turbo')

    chat_prompt = ChatPromptTemplate.from_messages([system_message, citation_prompt])
    cite_chain = LLMChain(prompt=chat_prompt, llm=llm)

    # peak first chunk
    path_citation = {}
    for path in list_of_filenames:
        texts, _ = parse_pdf(path, "", "", chunk_chars=500, peak=True)
        print(texts, '\n')
        citation = cite_chain.run(texts)

        if len(citation) < 3 or "Unknown" in citation or "insufficient" in citation:
            citation = f"Unknown, {os.path.basename(path)}, {datetime.now().year}"

        path_citation[path] = citation

    return path_citation
