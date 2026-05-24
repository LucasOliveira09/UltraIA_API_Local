import os
import asyncio
from playwright.async_api import async_playwright, BrowserContext, Page

class LimitReachedException(Exception):
    """Exceção customizada lançada quando a conta atinge o limite do Gemini Advanced."""
    pass

class GeminiScraper:
    def __init__(self):
        self.playwright = None
        self.browser_context: BrowserContext = None
        self.page: Page = None
        self.profile_name = "chrome_profile"
        self.user_data_dir = os.path.join(os.getcwd(), self.profile_name)
        self.request_count = 0
        self.is_logged_in = False

    async def initialize(self, profile_name: str = None, headless: bool = True):
        if profile_name:
            self.profile_name = profile_name
            self.user_data_dir = os.path.join(os.getcwd(), self.profile_name)
            
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        print(f"Iniciando navegador com perfil local ({self.profile_name}) no modo Headless={headless}...")
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
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
        await self.page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
        
        print("Aguardando input do chat aparecer (timeout de 15s)...")
        # Espera o input de chat carregar por 15 segundos para não travar a API
        try:
            await self.page.wait_for_selector('div[contenteditable="true"]', timeout=15000)
            self.is_logged_in = True
            print("Login detectado e Gemini pronto para uso!")
            
            # Tenta selecionar o Gemini Advanced
            try:
                print("Verificando qual modelo está selecionado...")
                
                # Procura pelo botão que contém a palavra "Flash" perto do prompt
                flash_btn = self.page.locator('button').filter(has_text="Flash").first
                
                if await flash_btn.is_visible():
                    print("Modelo 'Flash' detectado! Tentando mudar para 'Advanced'...")
                    await flash_btn.click(timeout=5000)
                    await asyncio.sleep(1)
                    
                    # Procura e clica na opção 'Advanced' ou 'Pro' no menu suspenso
                    advanced_option = self.page.locator('menuitem, li, div[role="option"], div[role="menuitem"]').filter(has_text="Advanced").first
                    pro_option = self.page.locator('menuitem, li, div[role="option"], div[role="menuitem"]').filter(has_text="Pro").first
                    
                    if await advanced_option.is_visible():
                        await advanced_option.click(timeout=3000)
                        print("Gemini Advanced selecionado com sucesso!")
                    elif await pro_option.is_visible():
                        await pro_option.click(timeout=3000)
                        print("Gemini Pro selecionado com sucesso!")
                    else:
                        print("Não foi possível encontrar a opção 'Advanced' ou 'Pro' no menu. Verifique se a conta tem assinatura ativa.")
                        await self.page.keyboard.press("Escape")
                else:
                    print("Botão 'Flash' não encontrado. Presumindo que já está no 'Advanced' ou a UI não o exibe.")
            except Exception as e:
                print(f"Não foi necessário ou não foi possível mudar para o Advanced: {e}")

        except Exception as e:
            self.is_logged_in = False
            print("Aviso: Tempo limite para login excedido ou falha ao carregar o chat. Verifique o navegador.")

    async def manual_login(self, profile_name: str):
        """Abre o Chrome no modo visual e aguarda o fechamento da página."""
        if self.browser_context:
            await self.browser_context.close()
            self.browser_context = None
            
        print(f"Iniciando Login Manual para o perfil: {profile_name}...")
        self.profile_name = profile_name
        self.user_data_dir = os.path.join(os.getcwd(), self.profile_name)
        
        if not self.playwright:
            self.playwright = await async_playwright().start()
            
        # Sempre visual
        context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=False,
            channel="chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"]
        )
        
        pages = context.pages
        page = pages[0] if pages else await context.new_page()
        
        print("Navegando para o Gemini para login manual...")
        await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
        
        print("Janela de login aberta. Faça o login. Feche a janela quando terminar.")
        try:
            # Aguarda a página ser fechada pelo usuário (evento 'close')
            await page.wait_for_event("close", timeout=0)  # timeout=0 significa aguardar indefinidamente
        except Exception as e:
            print(f"A janela foi fechada ou algo ocorreu: {e}")
            
        await context.close()
        print("Login manual concluído e contexto encerrado. O robô está pronto para rodar invisível.")

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
        if not getattr(self, 'is_logged_in', False):
            return "Erro: O perfil atual não está logado no Gemini ou a página não carregou. Por favor, selecione o perfil e clique em 'Fazer Login (Abrir Chrome)'."
            
        input_selector = 'div[contenteditable="true"]'
        
        if is_stateless:
            self.request_count += 1
            if self.request_count >= 20:
                print("Reciclando a aba do Gemini para aliviar a memória (limite de 20 requisições atingido)...")
                await self.page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
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
                # Verifica se houve limite
                body_text = await self.page.locator('body').inner_text()
                body_lower = body_text.lower()
                if "atingiu o limite" in body_lower or "reached your limit" in body_lower or "excedeu" in body_lower or "limite do gemini" in body_lower:
                    print("BLOQUEIO DETECTADO: Limite da conta atingido.")
                    raise LimitReachedException("Limite do Gemini Advanced atingido nesta conta.")

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
