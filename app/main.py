from fastapi import FastAPI,UploadFile,File,FastAPI
from secrets import token_hex
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from pydantic import BaseModel
import uvicorn,os,threading

app = FastAPI(title="Upload file using FastAPI")
embeddings_model = OpenAIEmbeddings(openai_api_key="AI KEY")


@app.post("/upload")

async def upload(file:UploadFile = File(...)):



    file_ext=file.filename.split(".").pop()
    file_name=token_hex(10)
    file_path=f"{file_name}.{file_ext}"
    with open(file_path,"wb") as f:
        content=await file.read()
        f.write(content)


    
    os.environ['OPENAI_API_KEY'] = "AI KEY"
    raw_documents = PyPDFLoader(f'{file_path}').load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)
    Chroma.from_documents(documents, OpenAIEmbeddings(), persist_directory="./chroma_db")
    return {"success":True, "file_path":file.filename,"message":f"The {file.filename} has been successfully loaded into the database."}





class Item(BaseModel):
    ai_query: str


@app.post("/query/")
async def create_item(query: Item):
    os.environ['OPENAI_API_KEY'] = "AI KEY"

    query=str(query)
    start_index = query.find("ai_query= ") + len("ai_query= ")
    end_index = query.find('"', start_index)
    name_value = query[start_index+1:end_index]

    db = Chroma(persist_directory="./chroma_db", embedding_function=OpenAIEmbeddings())
    docs = db.similarity_search(name_value)
    print(docs[0].page_content)   
    return  {"success":True, "search":name_value,"message":docs[0].page_content}




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True)