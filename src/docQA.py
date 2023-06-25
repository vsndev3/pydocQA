#!/usr/bin/python3

import typer
import textwrap

# 0xVs

from ctransformers.langchain import CTransformers
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from rich import print
from rich.prompt import Prompt
from rich.progress import track
from rich.progress import Progress
from rich.panel import Panel

app = typer.Typer()
device = "cpu"

@app.command()
def import_pdfs(dir: str = "./docs", embedding_model="./models/all-MiniLM-L6-v2",
                db="./vecdb", text_chunk_size : int = 512, text_chunk_overlap : int = 24):
    loader = DirectoryLoader(dir, glob="./*.pdf", loader_cls=PDFPlumberLoader, show_progress=True)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=text_chunk_size, chunk_overlap=text_chunk_overlap)
    docs = text_splitter.split_documents(documents)

    if len(docs) == 0:
        print("[bold red]:stop_sign: No PDF files found in directory  "+dir+".\nPlace your PDF files and run it again!\n[/bold red]")
        raise typer.Exit(code=-1)
    
    embeddings = HuggingFaceInstructEmbeddings(model_name=embedding_model, 
                                               model_kwargs={"device": device})
    for d in track(docs, description="Processing..."):
        try:
            db_existing  = FAISS.load_local(db, embeddings)
            newdb = FAISS.from_documents([d], embeddings)
            db_existing.merge_from(newdb)
            db_existing.save_local(db)
        except RuntimeError:
            newdb = FAISS.from_documents([d], embeddings)
            newdb.save_local(db)

@app.command()
def question(model_path: str = "./models/mpt-7b-instruct.ggmlv3.q5_0.bin",
             model_type='mpt',
             embedding_model="./models/all-MiniLM-L6-v2",
             db="./vecdb",
             search_breadth : int = 5, threads : int = 6, temperature : float = 0.4,
             reference_text_width : int = 320):
    embeddings = HuggingFaceInstructEmbeddings(model_name=embedding_model, 
                                               model_kwargs={"device": device})
    config = {'temperature': temperature, 'threads' : threads}
    llm = CTransformers(model=model_path, model_type=model_type, config=config)
    try:
        db = FAISS.load_local(db, embeddings)
    except RuntimeError:
        print("[bold red]:stop_sign: No documents added!\nUse [italic yellow]docQ.py import_pdfs /your/pdf/directory[/italic yellow] where the PDF files are present.\nYou can run multiple times with different directories, vector DB will be appended every time.\nPlace your PDF files and run it again!\n[/bold red]")
        raise typer.Exit(code=-1)

    retriever = db.as_retriever(search_kwargs={"k": search_breadth})
    memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever,
                                               memory=memory, return_source_documents=True)
    while True:
        query = Prompt.ask('[bright_yellow]\nQuestion[/bright_yellow] ')
        with Progress(transient=True) as progress:
            task = progress.add_task("[italic grey10]Analysing...[/italic grey10]", start=False, total=0)
            res = qa({"question": query})
            print("[spring_green4]"+res['answer']+"[/spring_green4]")
            if "source_documents" in res:
                print("\n[italic grey46]References[/italic grey46]:")
                for ref in res["source_documents"]:
                    refdata = "[grey19]"+textwrap.shorten(ref.page_content, width=reference_text_width, placeholder="...")+"[grey19]"
                    print(Panel(refdata, title=ref.metadata['source'], 
                                subtitle=str(ref.metadata['page']), border_style="grey0"))

if __name__ == "__main__":
    app()
