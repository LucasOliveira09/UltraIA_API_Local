import os
import asyncio
from playwright.async_api import async_playwright, BrowserContext, Page

class GeminiScraper:
    def __init__(self):
        self.playwright = None
        self.browser_context: BrowserContext = None
        self.page: Page = None
        self.profile_name = "chrome_profile"
        self.user_data_dir = os.path.join(os.getcwd(), self.profile_name)
        self.request_count = 0

    async def initialize(self, profile_name: str = None):
        if profile_name:
            self.profile_name = profile_name
            self.user_data_dir = os.path.join(os.getcwd(), self.profile_name)
            
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        print("Iniciando navegador com perfil local (na pasta chrome_profile)...")
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=False, # Precisa ser False para permitir o login manual
            channel="chrome",
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ],
            ignore_default_args=["--enable-automation"]
        )
        
        # Usa a primeira aba ou cria uma nova
        pages = self.browser_context.pages
        self.page = pages[0] if pages else await self.browser_context.new_page()
        
        print("Navegando para o Gemini...")
        await self.page.goto("https://gemini.google.com/app", wait_until="networkidle")
        
        print("Aguardando você logar (se necessário) e o input do chat aparecer...")
        # Espera o input de chat carregar por 5 minutos para dar tempo de você fazer login manualmente
        try:
            await self.page.wait_for_selector('div[contenteditable="true"]', timeout=300000)
            print("Login detectado e Gemini pronto para uso!")
        except Exception as e:
            print("Aviso: Tempo limite para login excedido ou falha ao carregar o chat. Verifique o navegador.")

    async def close(self):
        if self.browser_context:
            await self.browser_context.close()
            self.browser_context = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def switch_profile(self, new_profile_name: str):
        print(f"Trocando para o perfil: {new_profile_name}...")
        if self.browser_context:
            await self.browser_context.close()
            self.browser_context = None
        await self.initialize(profile_name=new_profile_name)

    async def ask_gemini(self, prompt: str, is_stateless: bool = True) -> str:
        input_selector = 'div[contenteditable="true"]'
        
        if is_stateless:
            self.request_count += 1
            if self.request_count >= 20:
                print("Reciclando a aba do Gemini para aliviar a memória (limite de 20 requisições atingido)...")
                await self.page.goto("https://gemini.google.com/app", wait_until="networkidle")
                await self.page.wait_for_selector(input_selector, timeout=60000)
                self.request_count = 0
                
            final_prompt = f"[System: Ignore todo o contexto e mensagens anteriores. Aja como uma API de processamento de dados. Retorne EXATAMENTE e APENAS o resultado para o prompt abaixo, sem saudações, sem confirmações como 'Claro!', sem tags Markdown adicionais e sem explicações extras.]\n\n[User Prompt]:\n{prompt}"
        else:
            final_prompt = prompt
        
        print(f"Limpando e enviando prompt (Stateless: {is_stateless}) | Tamanho: {len(final_prompt)} chars...")
        # Clica para focar e limpa se tiver algo
        await self.page.click(input_selector)
        await self.page.fill(input_selector, "")
        
        # Digita o prompt novo
        await self.page.fill(input_selector, final_prompt)
        await asyncio.sleep(0.5)
        
        # Captura o texto da última resposta antes de enviar a nova pergunta
        old_last_text = ""
        try:
            old_responses = await self.page.locator('message-content').all_inner_texts()
            if old_responses:
                old_last_text = old_responses[-1].strip()
        except Exception:
            pass

        # Pressiona Enter para enviar (o Gemini pode requerer Enter no teclado)
        await self.page.press(input_selector, "Enter")

        print("Aguardando geração da resposta (modo dinâmico e rápido)...")
        
        # Um pequeno tempo para a interface registrar o envio e iniciar o carregamento
        await asyncio.sleep(1)
        
        last_text = ""
        unchanged_count = 0
        max_attempts = 600 # Timeout máximo de 300 segundos (5 minutos) para prompts colossais (600 tentativas de 0.5s)
        
        for _ in range(max_attempts):
            try:
                responses = await self.page.locator('message-content').all_inner_texts()
                if not responses:
                    # Fallback genérico
                    responses = await self.page.locator('.model-response-text').all_inner_texts()
                
                if responses:
                    current_text = responses[-1].strip()
                    
                    # Só começamos a validar se o texto for diferente da requisição anterior
                    if current_text and current_text != old_last_text:
                        if current_text == last_text:
                            unchanged_count += 1
                            # Se o texto ficou congelado/igual por 4 verificações seguidas (2 segundos),
                            # significa que a IA parou de digitar e terminou a resposta!
                            if unchanged_count >= 4:
                                return current_text
                        else:
                            # A IA ainda está digitando, atualiza o último texto salvo e zera o contador
                            last_text = current_text
                            unchanged_count = 0
            except Exception:
                pass
            
            # Aguarda meio segundo antes de checar de novo
            await asyncio.sleep(0.5)
            
        # Se der timeout mas pegou algum texto, retorna o que conseguiu
        if last_text:
            return last_text
            
        return "Erro: Tempo limite atingido ao aguardar a geração da resposta."
