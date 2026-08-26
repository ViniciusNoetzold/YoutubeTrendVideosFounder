import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from app.config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODELS
from app.services.database import get_setting

def get_active_api_key() -> str:
    stored = get_setting('nvidia_api_key')
    return stored if stored else NVIDIA_API_KEY

def call_nvidia_llm(messages: List[Dict[str, str]], max_tokens: int = 1800, temperature: float = 0.7) -> str:
    api_key = get_active_api_key()
    url = f"{NVIDIA_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    last_error = None
    for model in NVIDIA_MODELS:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                if content:
                    return content
        except Exception as e:
            last_error = str(e)
            continue
            
    if last_error:
        raise Exception(f"Erro na API NVIDIA: {last_error}")
    return "Sem resposta da IA."

def clean_json_response(text: str) -> dict:
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except Exception:
        s = text.find("{")
        e = text.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(text[s:e+1])
            except Exception:
                pass
    return {"raw_text": text}

def analyze_niche_and_keywords(niche_name: str, trending_titles: List[str], user_subniche: str = "") -> Dict[str, Any]:
    titles_summary = "\n".join([f"- {t}" for t in trending_titles[:12]])
    system_prompt = """Você é o maior estrategista de crescimento e SEO para YouTube do Brasil.
Sua missão é analisar o nicho e os vídeos em alta para extrair palavras-chave de alto volume, tags e temas virais.
Responda EXCLUSIVAMENTE em formato JSON com o seguinte formato:
{
  "niche_summary": "Resumo do momento atual desse nicho no YouTube",
  "core_keywords": ["Palavra-chave 1", "Palavra-chave 2", "Palavra-chave 3", "Palavra-chave 4", "Palavra-chave 5"],
  "long_tail_keywords": ["Como fazer X passo a passo", "O que ninguém te conta sobre Y", "Top 5 melhores Z em 2025", "Segredo para conseguir W"],
  "youtube_tags": "tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10, tag11, tag12",
  "hot_topics": [
    {
      "topic": "Nome do Tema Viral",
      "angle": "Ângulo único e diferenciado para gravar",
      "why_viral": "Por que o público vai clicar e assistir até o fim",
      "hook_idea": "Gancho inicial de 5 segundos para prender a atenção"
    }
  ],
  "content_gaps": ["Oportunidade que concorrentes estão esquecendo", "Subtema em ascensão no algoritmo"]
}"""

    user_prompt = f"""Nicho do Canal: {niche_name}
Subnicho / Foco específico: {user_subniche or 'Geral do nicho'}

Vídeos em alta e referências encontradas hoje:
{titles_summary or 'Análise ampla do nicho com base no algoritmo do YouTube'}

Gere a análise completa de SEO, Palavras-Chave e Ideias de Conteúdo."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    raw = call_nvidia_llm(messages, max_tokens=1500, temperature=0.7)
    parsed = clean_json_response(raw)
    if "raw_text" in parsed and not "core_keywords" in parsed:
        parsed = {
            "niche_summary": f"Análise estratégica para {niche_name}",
            "core_keywords": [niche_name, f"{niche_name} dicas", f"{niche_name} tutorial", f"melhores {niche_name}", f"{niche_name} 2025"],
            "long_tail_keywords": [f"como começar em {niche_name}", f"segredos de {niche_name}", f"o que não te contam sobre {niche_name}"],
            "youtube_tags": f"{niche_name}, youtube, tutorial, dicas, como fazer, passo a passo, 2025, canal, video viral",
            "hot_topics": [
                {
                    "topic": f"Guia Definitivo de {niche_name}",
                    "angle": "Passo a passo prático para iniciantes e avançados",
                    "why_viral": "Alta busca por tutoriais completos e diretos ao ponto",
                    "hook_idea": "Se você fizer apenas isso hoje, vai mudar seus resultados..."
                }
            ],
            "content_gaps": [f"Estudos de caso reais de {niche_name}"],
            "raw_analysis": parsed.get("raw_text", "")
        }
    return parsed

def generate_video_package(niche: str, topic_or_title: str, reference_urls: str = "") -> Dict[str, Any]:
    system_prompt = """Você é um roteirista e estrategista sênior do YouTube especializado em canais de alto engajamento.
Crie um pacote completo de produção de vídeo (Títulos de alto CTR, conceitos visuais de Thumbnail, Hook e Estrutura).
Responda EXCLUSIVAMENTE em formato JSON com o seguinte schema:
{
  "titles": [
    "Título 1 (Curiosidade / Mistério)",
    "Título 2 (Como Fazer / Promessa Forte)",
    "Título 3 (Alerta / Não Cometa Esse Erro)",
    "Título 4 (Lista / Top Revelações)",
    "Título 5 (Provocativo / Polêmico)"
  ],
  "thumbnail_concepts": [
    {
      "concept_title": "Conceito 1 - Alto Contraste & Curiosidade",
      "visual_description": "Descrição detalhada dos elementos visuais, fundo, iluminação, cores contrastantes e expressão facial",
      "text_overlay": "TEXTO CURTO (máx 3-4 palavras)",
      "ai_prompt": "Prompt em inglês para gerar imagem no Midjourney/DALL-E"
    },
    {
      "concept_title": "Conceito 2 - Comparação Antes/Depois ou Revelação",
      "visual_description": "Elemento em destaque com seta ou círculo vermelho sutil e comparação visual",
      "text_overlay": "NÃO FAÇA ISSO!",
      "ai_prompt": "Prompt em inglês para gerar imagem no Midjourney/DALL-E"
    }
  ],
  "hook_script_15s": "Fala exata palavra por palavra para os primeiros 15 segundos para prender 100% da audiência",
  "structure_outline": [
    "00:00 - Gancho & Quebra de Padrão",
    "00:15 - A Grande Promessa & Por que você precisa ver até o fim",
    "01:00 - Bloco 1: O problema que ninguém percebe",
    "03:00 - Bloco 2: A solução prática passo a passo",
    "05:30 - Bloco 3: Dica bônus de ouro / Revelação",
    "07:00 - Chamada para Ação (CTA) & Próximo Vídeo"
  ],
  "retention_tactics": [
    "Inserir corte de zoom nos primeiros 8 segundos",
    "Criar um open loop no minuto 01:00 que só é revelado no minuto 05:00",
    "Usar b-rolls e sonoplastia a cada 4 a 6 segundos"
  ],
  "cta_prompt": "Pergunta provocativa para a audiência responder nos comentários e disparar o algoritmo"
}"""

    user_prompt = f"""Nicho: {niche}
Tema do Vídeo / Ideia: {topic_or_title}
Links de referência: {reference_urls or 'Nenhum'}

Gere o pacote viral de Títulos, Thumbnails, Gancho e Estrutura de Retenção."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    raw = call_nvidia_llm(messages, max_tokens=1500, temperature=0.7)
    return clean_json_response(raw)

def generate_full_script(niche: str, title: str, notes_or_outline: str = "", tone: str = "dinâmico e envolvente") -> str:
    system_prompt = f"""Você é um roteirista profissional de YouTube que escreve roteiros prontos para leitura em teleprompter ou fala natural.
Tom do vídeo: {tone}.
Escreva um roteiro completo, detalhado e pronto para gravação em português.

Divida o roteiro em seções claras:
1. [00:00 - 00:15] GANCHO INICIAL (Com instruções visuais e sonoras)
2. [00:15 - 00:45] INTRODUÇÃO & OPEN LOOP
3. [00:45 - 03:00] TÓPICO 1 - A REVELAÇÃO DO PROBLEMA
4. [03:00 - 05:30] TÓPICO 2 - O PASSO A PASSO / CONTEÚDO PRINCIPAL
5. [05:30 - 07:30] TÓPICO 3 - O ERRO QUE TODOS COMETEM E O SEGREDO FINAL
6. [07:30 - 08:30] CONCLUSÃO & CHAMADA PARA AÇÃO (CTA)

Inclua entre colchetes [INSTRUÇÕES DE GRAVAÇÃO/EDIÇÃO/SFX] para orientar o criador durante a gravação e a edição na terça-feira."""

    user_prompt = f"""Nicho: {niche}
Título do Vídeo: {title}
Detalhes adicionais / Estrutura: {notes_or_outline or 'Desenvolva de forma completa e profunda com exemplos práticos.'}

Escreva o roteiro completo agora."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return call_nvidia_llm(messages, max_tokens=1800, temperature=0.7)
