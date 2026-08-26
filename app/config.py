import os

# Default user-provided NVIDIA API Key
DEFAULT_NVIDIA_KEY = "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"
env_key = os.getenv("NVIDIA_API_KEY", "")

# If env key is not a valid nvapi key, use the user provided default
NVIDIA_API_KEY = env_key if (env_key and env_key.startswith("nvapi-")) else DEFAULT_NVIDIA_KEY
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Models with fallback
NVIDIA_MODELS = [
    "meta/llama-3.2-11b-vision-instruct",
    "google/diffusiongemma-26b-a4b-it",
    "meta/muse-glimmer-30b",
    "minimaxai/minimax-m3",
    "moonshotai/kimi-k3"
]

# Pre-configured popular niches
POPULAR_NICHES = [
    {"id": "tech_ia", "name": "Tecnologia & IA", "query": "inteligencia artificial ferramentas 2025 novidades tech", "icon": "cpu", "keywords": ["IA", "ChatGPT", "Automação", "Tech News", "Futuro"]},
    {"id": "games", "name": "Games & Gameplay", "query": "games gameplay lancamentos jogos segredos", "icon": "gamepad-2", "keywords": ["Lançamentos", "Dicas", "Gameplay", "Mods", "Easter Eggs"]},
    {"id": "curiosidades", "name": "Curiosidades & Mistérios", "query": "curiosidades misterios fatos desconhecidos historias", "icon": "sparkles", "keywords": ["Fatos Incríveis", "Mistérios", "Ciência", "História Oculta", "Top 10"]},
    {"id": "financas", "name": "Finanças & Investimentos", "query": "financas investimentos renda extra economia bolsa", "icon": "trending-up", "keywords": ["Investimentos", "Renda Extra", "Mercado Financeiro", "Economia", "Cripto"]},
    {"id": "desenvolvimento_pessoal", "name": "Produtividade & Hábitos", "query": "desenvolvimento pessoal produtividade habitos foco", "icon": "target", "keywords": ["Hábitos", "Produtividade", "Foco", "Mentalidade", "Rotina"]},
    {"id": "saude_fitness", "name": "Saúde, Treino & Nutrição", "query": "treino dieta alimentacao saude emagrecimento", "icon": "activity", "keywords": ["Treino", "Dieta", "Emagrecimento", "Hipertrofia", "Longevidade"]},
    {"id": "negocios_marketing", "name": "Negócios & Marketing", "query": "marketing digital negocios empreendedorismo vendas", "icon": "briefcase", "keywords": ["Vendas", "Tráfego Pago", "E-commerce", "Empreendedorismo", "Branding"]},
    {"id": "cinema_cultura", "name": "Cinema, Séries & Pop", "query": "filmes series cinema teorias analise", "icon": "film", "keywords": ["Crítica", "Teorias", "Trailers", "Análise de Filmes", "Cinema"]},
    {"id": "viagens_lifestyle", "name": "Viagens & Vlogs", "query": "viagem vlog dicas de viagem lugares incriveis", "icon": "compass", "keywords": ["Roteiros", "Dicas de Viagem", "Custo de Vida", "Lugares Secretos"]},
    {"id": "humor_cortes", "name": "Humor & Cortes", "query": "cortes podcast humor melhores momentos", "icon": "smile", "keywords": ["Melhores Momentos", "Cortes Virais", "Histórias Engraçadas", "Reações"]}
]

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "trends_app.db")
