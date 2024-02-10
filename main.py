import os
import sys
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA
from langchain_community.embeddings import LlamaCppEmbeddings
# from services.webex_ws_bootstrap import WebexMessage
from webexteamssdk import WebexTeamsAPI
from webex_ws_bootstrap import WebexMessage

template = """Instruction:
You are an AI assistant for answering questions about the provided context.
You are given the following extracted parts of a long document and a question. Provide a detailed answer.
If you don't know the answer, just say "I'm a OktaOps based AI, and that is outside of my capabilities." Don't try to make up an answer.
=======
{context}
=======
Question: {question}
Output:\n"""

QA_PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])

# Load Phi-2 model locally
MODEL_PATH = "/Users/apal2/.cache/lm-studio/models/TheBloke/phi-2-GGUF/phi-2.Q8_0.gguf"

DATA_FOLDER = "data"

USE_WEBEX = True

MY_BOT_TOKEN = os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")

def read_data_from_directory(directory_path)-> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
        )
    """Reads all PDF files from the given directory and returns their contents."""
    loaded_document: List[Document] = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            pdf = PyPDFLoader(file_path).load()
            for doc in pdf:
                loaded_document.append(doc)
            
        elif filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)
            md = UnstructuredMarkdownLoader(file_path).load()
            for doc in md:
                loaded_document.append(doc)
        else:
            print(f"File {filename} is not a PDF or Markdown file. Skipping...")
    documents = text_splitter.split_documents(loaded_document)
    return documents

# Load the model
data = read_data_from_directory(DATA_FOLDER)

# embeddings = LlamaCppEmbeddings(model_path=model_path)

# create the open-source embedding function
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# Equivalent to SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

store = FAISS.from_documents(data, embeddings)


llm = LlamaCpp(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_gpu_layers=1,
    n_batch=30,
    n_threads=8,   
    temperature=0.9,
    
)

# Load the model    
# RetrievalQA   
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=store.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": QA_PROMPT},
    verbose= True ,
)

def process_message(message_obj):  # Process messages that the bot receives.
    # Access incoming message content with: message_obj.personEmail, message_obj.text, etc. Example API msg at the end of this code.
    #___ incoming message contains the word 'hello'
    if "hello" in message_obj.text.lower():
        msg_result = api.messages.create(toPersonEmail=message_obj.personEmail, markdown="# Hello to you to!")
    else:
        result = qa_chain({"query": message_obj.text.lower()})
        result["result"]
        msg_result = api.messages.create(toPersonEmail=message_obj.personEmail, markdown=result["result"])
    return msg_result

if USE_WEBEX:   
    if MY_BOT_TOKEN is None:
        print("**ERROR** environment variable 'MY_BOT_TOKEN' not set, stopping.")
        sys.exit(-1)
     # TODO: Add a check for the bot token
    api = WebexTeamsAPI(access_token=MY_BOT_TOKEN)       
    webex = WebexMessage(access_token=MY_BOT_TOKEN, on_message=process_message)
    webex.run()

else:
    while True:
        # ask the user for their question
        new_question = input("What can I get you?: ")

        if new_question == "exit":
            break
        result = qa_chain({"query": new_question})
        print("Answer : = "+result["result"])
        print("You can find more details at : "+result["source_documents"][0].metadata["source"])
# cleanup
store.delete_collection()