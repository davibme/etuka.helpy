import os
import json
import streamlit as st
from openai import OpenAI

# 1. Configuração de Página com Identidade Visual Dark de IA
st.set_page_config(page_title="etuka.helpy - O Teu Tutor de IA", page_icon="🎓", layout="centered")

# Injeção de CSS para recriar o Modo Escuro Puro do ChatGPT e estilizar tabelas e o fundo
st.markdown("""
    <style>
    /* Fundo principal com grelha de engenharia e brilho gradiente sutil */
    .stApp {
        background-color: #212121 !important;
        background-image: 
            radial-gradient(at 50% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px) !important;
        background-size: 100% 100%, 30px 30px, 30px 30px !important;
        color: #ECECF1 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Ajuste de todos os textos normais para branco/cinza claro */
    .stApp p, .stApp span, .stApp label {
        color: #ECECF1 !important;
    }
    
    /* Título principal discreto e elegante em branco */
    h1 {
        color: #FFFFFF !important;
        font-weight: 600;
        text-align: center;
        font-size: 2rem !important;
        margin-bottom: 2px !important;
    }
    
    /* Barra Lateral Escura Mais Profunda */
    [data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2F2F2F !important;
    }
    
    /* Garante textos corretos na barra lateral */
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #ECECF1 !important;
    }
    
    /* Caixas de Chat Minimalistas no Modo Escuro */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(4px);
    }
    
    /* ESTILIZAÇÃO COMPLETA PARA TABELAS EM MODO ESCURO */
    .stApp table {
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 15px 0 !important;
        color: #ECECF1 !important;
    }
    .stApp th {
        background-color: #2F2F2F !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 1px solid #424242 !important;
        padding: 10px !important;
        text-align: left !important;
    }
    .stApp td {
        border: 1px solid #424242 !important;
        padding: 10px !important;
        background-color: rgba(255, 255, 255, 0.01) !important;
    }
    .stApp tr:nth-child(even) td {
        background-color: rgba(255, 255, 255, 0.03) !important;
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
    
    /* Caixa de input de texto escura */
    [data-testid="stChatInput"] {
        background-color: #2F2F2F !important;
        border: 1px solid #424242 !important;
        border-radius: 26px !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.3);
    }
    [data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa o cliente OpenAI
api_key_segura = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key_segura)

FICHEIRO_HISTORICO = "historico_estudo.json"

# 2. Barra Lateral Escura Profissional (ChatGPT Sidebar)
with st.sidebar:
    st.markdown("<h3 style='text-align: center; margin-top:25px; font-size: 1.2rem;'>etuka.helpy</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #B4B4B4 !important; font-size: 13px;'>O teu mentor de estudos pessoal.</p>", unsafe_allow_html=True)
    st.divider()
    
    disciplina_selecionada = st.selectbox(
        "📚 Disciplina activa:",
        ["Matemática", "História", "Ciências / Biologia", "Programação (Python)", "Geral"]
    )
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🗑️ Limpar Conversa"):
        if os.path.exists(FICHEIRO_HISTORICO):
            os.remove(FICHEIRO_HISTORICO)
        if "mensagens" in st.session_state:
            del st.session_state.mensagens
        st.rerun()

# 3. Engenharia de Prompt Avançada — O Melhor Tutor de Estudos do Mundo (Neuroeducação)
PROMPT_BASE = (
    "Tu és o 'etuka.helpy', reconhecido como o melhor e mais avançado tutor de estudos do mundo na disciplina de {disciplina}. "
    "O teu objetivo não é apenas dar respostas, mas construir uma mente brilhante no estudante através de metodologias pedagógicas de elite.\n\n"
    "DIRETRIZES DE ATUAÇÃO:\n"
    "1. MÉTODO SOCRÁTICO E DESAFIO CONSTRUTIVO: Nunca entregues a solução final de caras. Quando o estudante pedir um resultado ou resolução, "
    "decompõe o problema em pequenos passos lógicos. Explica o conceito base e faz apenas UMA pergunta direcionada no fim para que ele descubra a resposta sozinho.\n"
    "2. TÉCNICA DE FEYNMAN (SIMPLICIDADE MÁXIMA): Se o estudante não perceber, explica a matéria como se estivesses a falar com uma criança de 10 anos. "
    "Usa analogias práticas, metáforas do quotidiano e exemplos visuais impressionantes.\n"
    "3. EMPATIA, MOTIVAÇÃO E PSICOLOGIA POSITIVA: Valida de forma calorosa as frustrações ou dificuldades do estudante (ex: 'É perfeitamente normal achares isto confuso ao início, eu estou aqui contigo!'). "
    "Celebra cada pequeno progresso de forma genuína para ativar a dopamina e a autoconfiança dele.\n"
    "4. ESTRUTURAÇÃO VISUAL DE ELITE: Sempre que organizares dados, cronologias, fórmulas ou comparações complexas, utiliza OBLIGATORIAMENTE tabelas estruturadas em Markdown, "
    "listas limpas por tópicos (bullet points) ou blocos de código destacados para maximizar a memorização visual.\n"
    "5. ADAPTABILIDADE CRÍTICA: Deteta o nível atual de conhecimento do estudante através das suas respostas e ajusta o tom, a velocidade e a complexidade do ensino de forma dinâmica.\n\n"
    "Regra linguística absoluta: Comunica sempre num português de Portugal (pt-PT) impecável, natural, motivador, livre de formalismos excessivos e focado na proximidade humana."
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

# 6. Zona de Conversa Centralizada (Layout ChatGPT Total Dark)
st.title(f"etuka.helpy — {disciplina_selecionada}")
st.markdown("<p style='text-align: center; color: #B4B4B4; margin-top:-10px; font-size:15px;'>Como posso ajudar o teu raciocínio hoje?</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #2F2F2F;'>", unsafe_allow_html=True)

# 7. Renderizar Histórico de Mensagens com Avatares Limpos
for msg in st.session_state.mensagens:
    if isinstance(msg, dict) and msg.get("role") != "system":
        avatar_tipo = "👤" if msg["role"] == "user" else "🎓"
        with st.chat_message(msg["role"], avatar=avatar_tipo):
            st.markdown(f"<span style='color: #ECECF1;'>{msg['content']}</span>", unsafe_allow_html=True)

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
                    st.markdown(f"<span style='color: #ECECF1;'>{resposta_tutor}</span>", unsafe_allow_html=True)
                    st.session_state.mensagens.append({"role": "assistant", "content": resposta_tutor})
                    guardar_historico_disco(st.session_state.mensagens)
                except Exception as e:
                    st.error(f"Ocorreu um erro na API da OpenAI: {e}")
