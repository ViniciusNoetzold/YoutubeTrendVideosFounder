# 🚀 YouTube Trend & Content Founder

> **Caçador de Tendências, Extrator de Palavras-Chave, Curador de Referências e Gerador de Roteiros IA para Criadores de Conteúdo do YouTube.**

Aplicação web completa desenvolvida para automatizar a pesquisa de conteúdo no YouTube, identificar oportunidades de alta relevância no seu nicho e gerar títulos virais, conceitos de thumbnail, ganchos de retenção e roteiros completos com **IA da NVIDIA (NVIDIA NIM)**, integrada ao fluxo de produção semanal (**Segunda / Terça / Quarta**).

---

## 🎯 Principais Funcionalidades

- 🔍 **Menu de Nichos & Busca Personalizada:** Navegue por categorias populares (Tecnologia & IA, Games, Curiosidades, Finanças, Saúde/Fitness, Negócios, etc.) ou pesquise qualquer subnicho específico.
- 📈 **Tendências em Tempo Real:**
  - **Google Trends Diário (Brasil):** Tópicos mais buscados no dia com volume aproximado e notícias correlatas.
  - **YouTube Autocomplete Live:** Mineração dos termos reais que os usuários estão digitando na barra de pesquisa do YouTube neste instante.
- 🎬 **Vídeos de Referência:** Lista de vídeos em alta com visualizações, canais, data de publicação, miniatura e link direto para assistir ou usar como base para novos roteiros.
- 🧠 **Inteligência de SEO & Tags (NVIDIA AI):**
  - Palavras-chave principais e termos de cauda longa.
  - Tags formatadas e prontas para copiar e colar no YouTube Studio.
  - 5 Temas validados com ganchos de 5 segundos e ângulos exclusivos.
- ✍️ **Gerador de Conteúdo & Roteiros IA:**
  - **5 Títulos Virais de Alto CTR** com fórmulas testadas.
  - **Conceitos Visuais de Thumbnail** com descrição de elementos, texto de sobreposição e prompts para IAs de imagem.
  - **Gancho Inicial (0 a 15s)** focado em retenção nos primeiros segundos.
  - **Roteiro Estruturado Completo** (com marcações de tempo e instruções de gravação/edição/SFX), exportável em `.md` ou `.txt`.
- 📅 **Quadro de Produção Semanal (Segunda / Terça / Quarta):**
  - **Segunda-feira:** Pesquisar palavras-chaves • Estudar temas • Roteiro
  - **Terça-feira:** Finalizar roteiro • Edição
  - **Quarta-feira:** Terminar Edição • Thumbnail e Título • Publicar 🚀

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) (Python 3.11)
- **Inteligência Artificial:** NVIDIA NIM API (OpenAI-compatible)
- **Scraper / APIs:** YouTube Feeds, Google Trends RSS & YouTube Suggest API
- **Banco de Dados Local:** SQLite
- **Frontend:** Single Page Application moderna com [Tailwind CSS](https://tailwindcss.com/) & [Lucide Icons](https://lucide.dev/)

---

### Deploy no Render.com

O projeto está configurado para deploy imediato no [Render.com](https://render.com/):

- **Build Command**: `./build.sh` (ou `pip install -r requirements.txt`)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment**: Python `3.11.8`

> 💡 **Nota sobre o Start Command no Render**: Se o Render preencher por padrão `gunicorn your_application.wsgi`, o projeto já conta com um adaptador integrado (`your_application/wsgi.py`) para evitar erros, mas o comando recomendado é `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

---

## ⚡ Execução Local

### Pré-requisitos
- Python 3.10 ou superior instalado no sistema.

### 1. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar a Aplicação
No Windows, basta dar dois cliques em `start.bat` ou executar:
```bash
python run.py
```

Acesse no navegador: **http://localhost:8000**

---

## 📁 Estrutura do Projeto

```
YoutubeTrendVideosFounder/
├── app/
│   ├── services/
│   │   ├── ai_service.py       # Integração com NVIDIA NIM (Llama 3.2, Mistral, Gemma)
│   │   ├── database.py         # Persistência SQLite local (Tarefas, Ideias, Roteiros)
│   │   └── scraper.py          # Coleta de dados do YouTube e Google Trends
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Estilos customizados e tema dark
│   │   ├── js/
│   │   │   └── app.js          # Lógica interativa do frontend
│   │   └── index.html          # Interface web Single Page Application
│   ├── config.py               # Configurações de API e nichos padrão
│   └── main.py                 # Servidor FastAPI e rotas da API
├── requirements.txt            # Dependências do projeto
├── run.py                      # Script de inicialização com navegador automático
├── start.bat                   # Atalho para inicialização com 1 clique no Windows
└── README.md
```

---

## 📄 Licença
Este projeto está sob a licença MIT. Sinta-se livre para usar e customizar para o seu canal!
