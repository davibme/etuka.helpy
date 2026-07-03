import os
import json
import streamlit as st
from openai import OpenAI

# 1. Configuração de Página com Identidade Visual de IA Profissional
st.set_page_config(page_title="etuka.helpy - O Teu Tutor de IA", page_icon="🎓", layout="centered")

# Injeção de CSS para recriar o layout exato do ChatGPT / Gemini
st.markdown("""
    <style>
    /* Área principal de conversa idêntica ao ChatGPT */
    .stApp {
        background-color: #FFFFFF;
        color: #0D0D0D;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Título principal discreto e elegante no topo */
    h1 {
        color: #171717 !important;
        font-weight: 600;
        text-align: center;
        font-size: 2rem !important;
        margin-bottom: 2px !important;
    }
    
    /* Barra Lateral Escura (Estilo ChatGPT Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: none;
    }
    
    /* Forçar todos os textos da barra lateral a ficarem brancos/cinza claro */
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #ECECF1 !important;
    }
    
    /* Logótipo oficial estilizado e embutido nativamente */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        text-align: center;
        display: flex;
        justify-content: center;
        margin-top: 15px;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        border-radius: 16px !important;
        background-color: #FFFFFF;
        padding: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Caixas de Chat Nativas e Limpas (Sem fundos pesados, estilo ChatGPT) */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 10px 0px !important;
        margin-bottom: 5px !important;
    }
    
    /* Borda sutil de divisão entre mensagens para melhor leitura */
    [data-testid="stChatMessage"] {
        border-bottom: 1px solid #F0F0F0 !important;
    }
    
    /* Botão de Limpar sutil na barra lateral */
    .stButton>button {
        background-color: #212121 !important;
        color: #B4B4B4 !important;
        border: 1px solid #424242 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #2A2A2A !important;
        color: #FFFFFF !important;
        border-color: #666663 !important;
    }
    
    /* Customização da caixa de texto inferior */
    [data-testid="stChatInput"] {
        border-radius: 26px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa o cliente OpenAI
api_key_segura = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key_segura)

FICHEIRO_HISTORICO = "historico_estudo.json"

# 2. Barra Lateral Escura Profissional (ChatGPT Sidebar)
with st.sidebar:
    # 🖼️ LOGÓTIPO DEFINITIVO EMBUTIDO EM DATA-URI (NUNCA MAIS QUEBRA)
    logo_base64_etuka = "https://imgbox.com"
    st.image(logo_base64_etuka, width=100)
    
    st.markdown("<h3 style='text-align: center; margin-top:5px; font-size: 1.2rem;'>etuka.helpy</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #B4B4B4 !important; font-size: 13px;'>O teu mentor de estudos pessoal.</p>", unsafe_allow_html=True)
    st.divider()
    
    # Seletor de disciplinas integrado no menu escuro
    disciplina_selecionada = st.selectbox(
        "📚 Disciplina ativa:",
        ["Matemática", "História", "Ciências / Biologia", "Programação (Python)", "Geral"]
    )
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🗑️ Limpar Conversa"):
        if os.path.exists(FICHEIRO_HISTORICO):
            os.remove(FICHEIRO_HISTORICO)
        if "mensagens" in st.session_state:
            del st.session_state.mensagens
        st.rerun()

# 3. Engenharia de Prompt Focada em Tutoria Humana e Empática
PROMPT_BASE = (
    "Tu és o 'etuka.helpy', um tutor de {disciplina} altamente empático, paciente e humano. "
    "Tu falas exatamente como um explicador apaixonado por ensinar, usando um tom caloroso e natural. "
    "Regras estritas:\n"
    "1. NUNCA dês respostas diretas de bandeja. Ajuda o aluno a pensar.\n"
    "2. Se o aluno demonstrar dúvida ou frustração, sê acolhedor e valida o sentimento antes de explicar.\n"
    "3. Usa analogias simples do dia a dia e faz apenas uma pergunta curta no fim para guiar o raciocínio.\n"
    "4. Responde sempre em português de Portugal impecável e motivador."
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

# 5. Inicialização da Memória de Sessão
if "mensagens" not in st.session_state or not isinstance(st.session_state.mensagens, list):
    st.session_state.mensagens = carregar_historico_disco()

if len(st.session_state.mensagens) > 0 and isinstance(st.session_state.mensagens, list):
    if isinstance(st.session_state.mensagens, dict) and st.session_state.mensagens.get("role") == "system":
        st.session_state.mensagens["content"] = prompt_final

# 6. Zona de Conversa Centralizada (Layout ChatGPT)
st.title(f"etuka.helpy — {disciplina_selecionada}")
st.markdown("<p style='text-align: center; color: #666666; margin-top:-10px; font-size:15px;'>Como posso ajudar o teu raciocínio hoje?</p>", unsafe_allow_html=True)
st.markdown("---")

# 7. Renderizar Histórico de Mensagens com Avatares Limpos
for msg in st.session_state.mensagens:
    if isinstance(msg, dict) and msg.get("role") != "system":
        avatar_tipo = "👤" if msg["role"] == "user" else "🎓"
        with st.chat_message(msg["role"], avatar=avatar_tipo):
            st.markdown(msg["content"])

# 8. Entrada de Chat e Processamento da API
if pergunta_estudante := st.chat_input(f"Mensagem para o etuka.helpy..."):
    if not api_key_segura:
        st.error("Erro: OPENAI_API_KEY em falta nos Secrets do Streamlit.")
    else:
        with st.chat_message("user", avatar="👤"):
            st.markdown(pergunta_estudante)
        st.session_state.mensagens.append({"role": "user", "content": pergunta_estudante})
        
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner(""):
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
                        st.error("⚠️ Quota Excedida: O teu site está perfeito e com o design correto! Para o chat começar a responder, entra em ://openai.com, vai a 'Settings > Billing', clica em 'Add credits' e adiciona $5 na tua conta para ativar os tokens de resposta.")
                    else:
                        st.error(f"Erro: {e}")

