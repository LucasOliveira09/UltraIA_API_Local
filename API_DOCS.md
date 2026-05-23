# UltraGeminiAI - API Documentation

Esta documentação detalha todas as rotas disponíveis na sua API, seus comportamentos técnicos (stateful vs stateless) e exemplos de payload (JSON) para que você possa consumir o sistema através do Postman, de scripts externos ou de outras automações.

---

## 1. Rotas de Geração (IA)

### `POST /api/ultragemineai/ask`
A rota **Stateless** (Tiro Único), desenhada para perguntas isoladas, extrações diretas e geração de imagens.

*   **Comportamento:** Ao bater nesta rota, o seu `prompt` é invisivelmente envelopado em uma instrução restrita de sistema (`"Ignore todo o contexto anterior..."`). Isso força o Gemini a responder de forma fria e esquecer qualquer regra que tenha sido dita antes.
*   **Performance:** A cada 20 requisições feitas nesta rota, o robô atualiza a página (`F5`) por baixo dos panos. Isso evita o vazamento de memória (RAM) no seu servidor ou no Docker, mantendo as automações ultrarrápidas mesmo após horas de uso.
*   **Timeout:** Espera até 5 minutos (300 segundos) pela digitação da IA.

**Exemplo de Request (Body -> raw -> JSON):**
```json
{
  "prompt": "Gere um título chamativo de YouTube para um vídeo sobre Buracos Negros."
}
```

**Exemplo de Response:**
```json
{
  "response": "O Abismo Devorador: A Verdade Aterrorizante dos Buracos Negros"
}
```

---

### `POST /api/ultragemineai/chat`
A rota **Stateful** (Roteirista / Cadeia contínua), estritamente desenhada para roteiros que precisam ser feitos em partes, mantendo a memória da IA viva.

*   **Comportamento:** O seu `prompt` é enviado exatamente como você o escreveu. Nenhuma instrução de "esquecimento" é adicionada. Isso permite que você envie as regras gigantes do "Bloco 1" e, nos próximos requests, envie apenas comandos curtos como *"Prossiga para o Bloco 2"*, com o Gemini se lembrando ativamente das diretrizes do Bloco 1.
*   **Performance:** Esta rota NÃO atualiza a página automaticamente, para garantir que o contexto do chat longo nunca seja quebrado durante a sua geração.
*   **Timeout:** Espera até 5 minutos (300 segundos) pela digitação da IA (ideal para blocos de roteiro de 3.000 palavras).

**Exemplo de Request (Body -> raw -> JSON):**
```json
{
  "prompt": "Prossiga para o Bloco 2."
}
```

**Exemplo de Response:**
```json
{
  "response": "A desconstrução da nossa intuição começa no século XX, quando a luz das estrelas nos traiu..."
}
```

---

## 2. Rotas de Configuração (Engine & Perfis)

Estas rotas gerenciam os "cérebros" do navegador. Um Perfil (`chrome_profile_xxx`) é basicamente uma pasta que contém os cookies e a sessão de login de uma conta específica do Google.

### `GET /api/settings/profiles`
Lista qual conta está ativa no momento e quais outras contas já estão salvas/criadas na máquina.

**Exemplo de Response:**
```json
{
  "active_profile": "chrome_profile",
  "available_profiles": [
    "chrome_profile",
    "chrome_profile_trabalho",
    "chrome_profile_canal"
  ]
}
```

---

### `POST /api/settings/profile`
Troca a conta (perfil) que o robô está usando no momento.
*   **Comportamento:** Se você enviar um nome de perfil que já existe, ele carrega o perfil e a sessão daquela conta. Se enviar um nome novo (ex: `chrome_profile_teste`), a API criará uma nova pasta local, abrirá o navegador limpo e deixará você logar numa nova conta do Google.

**Exemplo de Request (Body -> raw -> JSON):**
```json
{
  "profile_name": "chrome_profile_trabalho"
}
```

**Exemplo de Response:**
```json
{
  "status": "success",
  "active_profile": "chrome_profile_trabalho"
}
```

---

## 3. Rota Visual (Frontend)

### `GET /` e `GET /dashboard/`
Se você tentar acessar a API pelo navegador de internet (Chrome, Safari, etc) em `http://localhost:8000`, a API não te retornará um código em JSON. Ao invés disso, ela abrirá um **Painel de Controle Gráfico** onde você pode testar as rotas `/ask` e `/chat` visualmente e gerenciar seus perfis com o clique de botões, sem precisar do Postman.
