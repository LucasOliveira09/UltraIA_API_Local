from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
from UltraIA_API.gemini_scraper import GeminiScraper
from contextlib import asynccontextmanager
import sys
import os

# Corrige o NotImplementedError do Playwright no Windows com Uvicorn/FastAPI
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

scraper = GeminiScraper()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializamos o navegador quando a API ligar
    print("Iniciando API...")
    try:
        await scraper.initialize()
        print("Scraper inicializado e pronto para requisições.")
    except Exception as e:
        print(f"Erro ao inicializar scraper: {e}")
        print("Certifique-se de que o Google Chrome esteja FECHADO antes de iniciar a API.")
    
    yield
    
    # Fechamos o navegador ao desligar a API
    print("Desligando API e fechando navegador...")
    await scraper.close()

app = FastAPI(title="UltraGeminiAI API", lifespan=lifespan)

os.makedirs("frontend", exist_ok=True)
app.mount("/dashboard", StaticFiles(directory="frontend", html=True), name="frontend")

class PromptRequest(BaseModel):
    prompt: str

class ProfileRequest(BaseModel):
    profile_name: str

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard/")

@app.get("/api/settings/profiles")
async def get_profiles():
    profiles = [d for d in os.listdir() if d.startswith("chrome_profile") and os.path.isdir(d)]
    if "chrome_profile" not in profiles:
        profiles.append("chrome_profile")
    return {"active_profile": scraper.profile_name, "available_profiles": list(set(profiles))}

@app.post("/api/settings/profile")
async def set_profile(request: ProfileRequest):
    try:
        await scraper.switch_profile(request.profile_name)
        return {"status": "success", "active_profile": scraper.profile_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ultragemineai/ask")
async def ask(request: PromptRequest):
    try:
        print(f"[/ask] Recebida requisição stateless (tiro-único)...")
        # Chamada síncrona/esperada, processa apenas 1 por vez com isolamento de contexto
        response_text = await scraper.ask_gemini(request.prompt, is_stateless=True)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ultragemineai/chat")
async def chat(request: PromptRequest):
    try:
        print(f"[/chat] Recebida requisição stateful (mantendo contexto)...")
        # Chamada contínua, sem envelopar o prompt com instruções de isolamento
        response_text = await scraper.ask_gemini(request.prompt, is_stateless=False)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Roda a API na porta 8000. 
    # reload=True foi removido no Windows para evitar o NotImplementedError com Playwright.
    uvicorn.run(app, host="0.0.0.0", port=8000)
