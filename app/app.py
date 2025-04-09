from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc
import models
import database
import resources
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import uvicorn


app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/static"), name="static")  

LLM_URL = os.getenv('LLM_URL', "http://192.168.1.69:11434/api/generate")
# Inicializa la base de datos
models.Base.metadata.create_all(bind=database.engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic
class PromptBase(BaseModel):
    title: str
    prompt:  Optional[str] = None

class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    id: int

    class Config:
        orm_mode = True

class RequestBase(BaseModel):
    model: Optional[str] = None
    url: Optional[str] = None
    response: Optional[str] = None
    prompt: Optional[str] = None
    text: Optional[str] = None


class RequestCreate(RequestBase):
    pass

class Request(RequestBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

@app.get("/", response_class=HTMLResponse)
async def html_ini():
    try:
        with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")  

# Rutas para Prompts
@app.post("/prompts/", response_model=Prompt)
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    db_prompt = models.Prompt(**prompt.dict())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@app.get("/list_prompts")
def list_prompts(db: Session = Depends(get_db)):
    prompts = db.query(models.Prompt).all()
    return [{
        "id": prompt.id,
        "name": prompt.title
    } for prompt in prompts]

@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: int, updated_prompt: PromptCreate, db: Session = Depends(get_db)):
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    for key, value in updated_prompt.dict().items():
        setattr(prompt, key, value)

    db.commit()
    db.refresh(prompt)
    return prompt


@app.delete("/prompts/{prompt_id}", response_model=Prompt)
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    db.delete(prompt)
    db.commit()
    return prompt

# Rutas para Requests

@app.post("/text_to_url")
def text_to_url(request: dict):
    if not request.get("text"):
        raise HTTPException(status_code=400, detail="Text is required")
    
    text = request["text"]
    if text.startswith("http"):
        return {"text": get_text_url(text)}
    return {"text": text}

@app.get("/prompt/{prompt_id}")
def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {
        "id": prompt.id,
        "content": prompt.prompt or ""
    }

@app.get("/list_models")
def list_models():
    try:
        response = resources.call_api_get(LLM_URL.replace('/generate', '/tags'))
        if response and 'models' in response:
            return [{
                "id": model['name'],
                "name": f"{model['name']} ({model['details'].get('parameter_size', 'Unknown size')})"
            } for model in response['models']]
        return []
    except Exception as e:
        print(f"Error fetching models: {str(e)}")
        return []

@app.post("/generate")
def generate(request: dict, db: Session = Depends(get_db)):
    import time
    start_time = time.time()
    
    if not request.get("text") or not request.get("prompt") or not request.get("model"):
        raise HTTPException(status_code=400, detail="Text, prompt and model are required")
    
    # Construir el prompt completo
    full_prompt = f"{request['prompt']}\n\nTexto: {request['text']}"
    
    # Llamar a la API de Gemini
    response_text = call_llms_api(full_prompt,request['model'])
    
    # Calcular tiempo transcurrido
    elapsed_time = round(time.time() - start_time, 2)
    
    return {
        "generated_text": response_text,
        "elapsed_time": elapsed_time
    }

def get_text_url(url):
    if 'youtube' in url:
        response = resources.get_subtitles(url)
    else:    
        text_web = resources.get_text_of_web(url)
        response = "'" + text_web['title'] + "\n" + text_web['text'] + "'"
    return response



def call_llms_api(prompt,model):

    url = LLM_URL
    data = { "model": model,"prompt": prompt, "stream": False}

    response = resources.call_api_post(url,data)
    result = response["response"]
    return result  
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")   