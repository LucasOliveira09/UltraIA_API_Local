# UltraGeminiAI API

Uma API construída com **FastAPI** e **Playwright** que permite automatizar a interação com o Google Gemini extraindo seu poder de IA através de scraping. Ela suporta isolamento de contexto para requisições únicas e conversas contínuas mantendo o histórico, além de contar com um painel (dashboard) frontend embutido.

---

## ⚠️ Aviso Importante Antes de Iniciar
**Você deve FECHAR TODAS as instâncias do Google Chrome** que estejam abertas no seu computador antes de tentar iniciar a API. O Playwright precisa assumir o controle do navegador para se comunicar com a sessão do usuário de maneira apropriada, e não conseguirá iniciar se o navegador já estiver aberto.

---

## 🛠️ Pré-requisitos

Certifique-se de ter o seguinte instalado em sua máquina:
- **Python 3.8** ou superior.
- Navegador **Google Chrome** instalado na máquina.

## 🚀 Como Instalar e Configurar

1. **Abra o terminal** e navegue até a pasta do projeto `UltraIA_API`:
   ```bash
   cd caminho/para/geminiScrapper/UltraIA_API
   ```

2. **Crie e ative um ambiente virtual (Recomendado)**:
   ```bash
   python -m venv venv
   # Ative o ambiente virtual no Windows:
   venv\Scripts\activate
   ```

3. **Instale as dependências** do projeto através do `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Instale os navegadores necessários para o Playwright**:
   ```bash
   playwright install chromium
   ```

## 🎮 Como Iniciar a Aplicação

Depois de seguir os passos de instalação e **garantir que o Google Chrome esteja completamente fechado**, você pode iniciar a API de duas maneiras:

**Opção 1: Usando o arquivo Batch (Mais fácil no Windows)**
Basta dar dois cliques no arquivo `start.bat` na pasta do projeto, ou executá-lo no terminal:
```bash
start.bat
```

**Opção 2: Iniciando manualmente pelo Python**
Com o ambiente virtual ativado, execute:
```bash
python main.py
```

Você verá as mensagens no terminal indicando:
> Iniciando API...
> Scraper inicializado e pronto para requisições.

A API estará rodando no endereço `http://0.0.0.0:8000`.

## 🌐 Usando a Aplicação

- **Dashboard Integrado**: Abra o navegador e acesse [http://localhost:8000/dashboard](http://localhost:8000/dashboard) para interagir com a interface gráfica da aplicação.
- **Documentação Interativa (Swagger)**: Acesse [http://localhost:8000/docs](http://localhost:8000/docs) para testar os endpoints da API diretamente do navegador.

## 📖 Documentação da API

Para detalhes técnicos sobre os endpoints (como `/api/ultragemineai/ask` e `/api/ultragemineai/chat`), parâmetros, como funcionam as requisições (stateful e stateless) e as configurações de perfil (Profile), por favor consulte o arquivo completo [`API_DOCS.md`](./API_DOCS.md) presente neste repositório.
