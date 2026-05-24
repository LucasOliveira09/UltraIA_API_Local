from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
from gemini_scraper import GeminiScraper, LimitReachedException
from contextlib import asynccontextmanager
import sys
import os
import shutil

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
    return {
        "active_profile": scraper.profile_name, 
        "available_profiles": list(set(profiles)),
        "is_logged_in": getattr(scraper, 'is_logged_in', False)
    }

@app.post("/api/settings/profile/create")
async def create_profile(request: ProfileRequest):
    try:
        profile_path = os.path.join(os.getcwd(), request.profile_name)
        os.makedirs(profile_path, exist_ok=True)
        return {"status": "success", "message": f"Perfil {request.profile_name} criado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings/profile")
async def set_profile(request: ProfileRequest):
    try:
        await scraper.switch_profile(request.profile_name)
        return {
            "status": "success", 
            "active_profile": scraper.profile_name,
            "is_logged_in": getattr(scraper, 'is_logged_in', False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings/login/{profile_name}")
async def login_profile(profile_name: str):
    try:
        print(f"Recebida solicitação de login manual para {profile_name}...")
        await scraper.manual_login(profile_name)
        # Após fechar o login, tenta reinicializar invisível
        await scraper.initialize(profile_name=profile_name, headless=True)
        return {"status": "success", "message": f"Login concluído. Perfil {profile_name} ativo e invisível."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/settings/profile/{profile_name}")
async def delete_profile(profile_name: str):
    try:
        if profile_name == scraper.profile_name:
            raise HTTPException(status_code=400, detail="Não é possível excluir o perfil em uso no momento.")
            
        profile_path = os.path.join(os.getcwd(), profile_name)
        if os.path.exists(profile_path) and profile_name.startswith("chrome_profile"):
            shutil.rmtree(profile_path)
            return {"status": "success", "message": f"Perfil {profile_name} excluído."}
        else:
            raise HTTPException(status_code=404, detail="Perfil não encontrado ou caminho inválido.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_with_rotation(prompt: str, is_stateless: bool):
    max_retries = 5 # Tenta em até 5 contas diferentes
    for attempt in range(max_retries):
        try:
            return await scraper.ask_gemini(prompt, is_stateless=is_stateless)
        except LimitReachedException as e:
            print(f"[{attempt+1}/{max_retries}] Limite atingido na conta {scraper.profile_name}!")
            
            profiles = [d for d in os.listdir() if d.startswith("chrome_profile") and os.path.isdir(d)]
            if "chrome_profile" not in profiles:
                profiles.append("chrome_profile")
                
            if len(profiles) <= 1:
                raise HTTPException(status_code=503, detail="Limite atingido e não há outros perfis para rotação.")
                
            # Busca o próximo perfil na lista
            current_index = profiles.index(scraper.profile_name) if scraper.profile_name in profiles else 0
            next_profile = profiles[(current_index + 1) % len(profiles)]
            
            print(f"Rotacionando para: {next_profile}...")
            await scraper.switch_profile(next_profile)
            print("Tentando enviar o prompt novamente no novo perfil...")
            
    raise HTTPException(status_code=503, detail="Todos os perfis atingiram o limite.")

@app.post("/api/ultragemineai/ask")
async def ask(request: PromptRequest):
    print(f"[/ask] Recebida requisição stateless (tiro-único)...")
    response_text = await execute_with_rotation(request.prompt, is_stateless=True)
    return {"response": response_text}

@app.post("/api/ultragemineai/chat")
async def chat(request: PromptRequest):
    print(f"[/chat] Recebida requisição stateful (mantendo contexto)...")
    response_text = await execute_with_rotation(request.prompt, is_stateless=False)
    return {"response": response_text}

if __name__ == "__main__":
    import uvicorn
    # Roda a API na porta 8000. 
    # reload=True foi removido no Windows para evitar o NotImplementedError com Playwright.
    uvicorn.run(app, host="0.0.0.0", port=8000)
