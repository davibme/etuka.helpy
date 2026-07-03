import os
import json
import streamlit as st
from openai import OpenAI

# 1. Configuração da Página Web e Estilo Visual Avançado (Efeito UAU)
st.set_page_config(page_title="etuka.helpy - Interface Premium", page_icon="⚡", layout="centered")

# Injeção de CSS personalizado para transformar o layout e estilizar o novo logotipo
st.markdown("""
    <style>
    /* Mudar a cor de fundo principal e o tipo de letra */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Customização do cabeçalho principal */
    h1 {
        color: #38BDF8 !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        text-align: center;
        text-shadow: 0px 4px 12px rgba(56, 189, 248, 0.2);
    }
    
    /* Estilização da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 2px solid #334155;
    }
    
    /* Forçar a imagem do logotipo na barra lateral a ficar redonda e centralizada */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        text-align: center;
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        border-radius: 50% !important;
        border: 3px solid #38BDF8;
        object-fit: cover;
        box-shadow: 0px 0px 15px rgba(56, 189, 248, 0.4);
        background-color: white; /* Garante fundo limpo para o logo transparente */
        padding: 5px;
    }
    
    /* Deixar as caixas de chat com cantos arredondados e sombras modernas */
    [data-testid="stChatMessage"] {
        background-color: #1E293B !important;
        border-radius: 16px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Mudar o aspeto dos botões */
    .stButton>button {
        background-color: #38BDF8 !important;
        color: #0F172A !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0px 0px 15px rgba(56, 189, 248, 0.5) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa o cliente OpenAI
api_key_segura = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key_segura)

FICHEIRO_HISTORICO = "historico_estudo.json"

# --- SISTEMA DE GAMIFICAÇÃO ---
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "nivel" not in st.session_state:
    st.session_state.nivel = 1

# 2. Painel Lateral Premium (Sidebar)
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #38BDF8;'>⚡ etuka.helpy</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>O teu ecossistema de estudo inteligente</p>", unsafe_allow_html=True)
    st.divider()
    
    # 🖼️ LOGOTIPO OFICIAL INTEGRADO DEFINITIVAMENTE NO CÓDIGO
    # Se você quiser permitir trocar temporariamente por outra imagem, o botão continua aqui abaixo
    imagem_carregada = st.file_uploader("Alterar logótipo atual:", type=["png", "jpg", "jpeg"])
    
    # URL da imagem que você acabou de enviar (armazenada de forma estável na web para o seu app)
    logo_oficial_etuka = "https://githubusercontent.com" 
    # Caso falte a imagem na nuvem temporariamente, usamos um fallback idêntico carregado diretamente
    logo_final = imagem_carregada if imagem_carregada else "https://imgur.com"
    
    st.image(logo_final, width=120)
    st.divider()
    
    st.subheader("🏆 Painel do Jogador")
    st.metric(label="Nível", value=f"{st.session_state.nivel}")
    st.progress(min(st.session_state.xp % 100 / 100, 1.0))
    st.caption(f"✨ {st.session_state.xp} XP totais acumulados.")
    st.divider()
    
    disciplina_selecionada = st.selectbox(
        "📚 Escolhe o teu foco:",
        ["Matemática", "História", "Ciências / Biologia", "Programação (Python)", "Geral"]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reiniciar Tudo"):
        if os.path.exists(FICHEIRO_HISTORICO):
            os.remove(FICHEIRO_HISTORICO)
        st.session_state.xp = 0
        st.session_state.nivel = 1
        if "mensagens" in st.session_state:
            del st.session_state.mensagens
        st.rerun()

# 3. Engenharia de Prompt Dinâmica
PROMPT_BASE = (
    "Tu és o 'etuka.helpy', a IA de tutoria mais inovadora e divertida do mundo para estudantes. "
    "Tu não és um robô aborrecido. Tu és dinâmico, usas emojis, contas piadas intelectuais e assumes a especialidade em {disciplina}.\n"
    "Regras estritas de funcionamento:\n"
    "1. NUNCA dês a resposta final de bandeja. Cria desafios!\n"
    "2. Explica a matéria com analogias loucas do dia a dia ou referências à cultura pop (filmes, jogos, séries).\n"
    "3. Termina SEMPRE a tua resposta com um pequeno desafio ou pergunta socrática para o aluno responder.\n"
    "4. Responde em português de Portugal com energia máxima e entusiasmo."
)
prompt_final = PROMPT_BASE.format(disciplina=disciplina_selecionada)

# 4. Funções de Gestão de Ficheiro
def carregar_historico_disco():
    if os.path.exists(FICHEIRO_HISTORICO):
        try:
            with open(FICHEIRO_HISTORICO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list):
                    return dados
        except:
            pass
    return [{"role": "system", "content": prompt_final}]

def guardar_historico_disco(dados_historico):
    with open(FICHEIRO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(dados_historico, f, ensure_ascii=False, indent=4)

# 5. Inicialização da Memória da Sessão Web
if "mensagens" not in st.session_state or not isinstance(st.session_state.mensagens, list):
    st.session_state.mensagens = carregar_historico_disco()

if len(st.session_state.mensagens) > 0 and isinstance(st.session_state.mensagens, list):
    if isinstance(st.session_state.mensagens, dict) and st.session_state.mensagens.get("role") == "system":
        st.session_state.mensagens["content"] = prompt_final

# 6. Cabeçalho Principal do Website
st.title(f"🚀 etuka.helpy: {disciplina_selecionada}")
st.markdown("<p style='text-align: center; color: #94A3B8;'>Resolve os mistérios da matéria, acumula pontos e domina o conhecimento!</p>", unsafe_allow_html=True)

# 7. Renderizar Histórico de Chat Premium
for msg in st.session_state.mensagens:
    if isinstance(msg, dict) and msg.get("role") != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. Caixa de Entrada de Chat e Processamento da IA
if pergunta_estudante := st.chat_input(f"Desafia o etuka.helpy em {disciplina_selecionada}..."):
    if not api_key_segura:
        st.error("Erro: Configura a tua OPENAI_API_KEY nos Secrets.")
    else:
        with st.chat_message("user"):
            st.markdown(pergunta_estudante)
        st.session_state.mensagens.append({"role": "user", "content": pergunta_estudante})
        
        st.session_state.xp += 15
        if st.session_state.xp >= st.session_state.nivel * 100:
            st.session_state.nivel += 1
            st.toast("🎉 PARABÉNS! Subiste de nível no teu conhecimento!", icon="🔥")
            st.balloons()
            
        with st.chat_message("assistant"):
            with st.spinner("🚀 O etuka.helpy está a processar a tua resposta..."):
                try:
                    resposta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.mensagens
                    )
                    resposta_tutor = resposta.choices.message.content
                    st.markdown(resposta_tutor)
                    st.session_state.mensagens.append({"role": "assistant", "content": resposta_tutor})
                    guardar_historico_disco(st.session_state.mensagens)
                except Exception as e:
                    if "insufficient_quota" in str(e) or "RateLimitError" in str(e):
                        st.error("⚠️ Erro de Saldo: A tua chave OpenAI está ativa, mas a conta não tem fundos. Vai a ://openai.com, clique em 'Add credits' e adicione $5 para ativar as respostas do chat.")
                    else:
                        st.error(f"Erro na API: {e}")
