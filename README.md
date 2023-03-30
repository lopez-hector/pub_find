# PubFind

Pubfind is an application built to answer researcher's questions from a corpus of scientific papers. Answers are 
formulated from the texts most relevant to the question. By providing citations and original source texts, it enables 
you to quickly find documents that are relevant to answering your question.

Pubfind is designed to build a semantic search index over a directory that includes a corpus of scientific papers you 
want to study. It works best for diving into a focused group of papers, rather than ALL of the papers in existence. 

To setup, you must create a **study_directory** for your subset of papers. In the study_directory create a **pdfs** 
directory that contains all of your pdf formatted science papers inside. Before you can start perusing the scientific articles
you must first provide citations for each file. You can cre

├── study_directory   
│   ├── pdfs  
│       ├──file1.pdf  
│       ├──file2.pdf  
│   ├── citations.json  

The app can be run via the recommend Flask App.

```flask run```

It can also be run via the command line (run.py). Modify the question in run.py to your needs.    

```python main.py```


