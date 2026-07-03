import os
import json
import streamlit as st
from openai import OpenAI

# 1. Configuração da Página Web e Estilo Visual Altamente Humanizado
st.set_page_config(page_title="etuka.helpy - O Teu Tutor Humano", page_icon="🎓", layout="centered")

# Injeção de CSS personalizado para criar um ambiente de conversa caloroso e limpo
st.markdown("""
    <style>
    /* Fundo suave e confortável para leitura prolongada */
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* Título principal elegante e acolhedor */
    h1 {
        color: #0F172A !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px !important;
    }
    
    /* Barra Lateral com design minimalista e focado no Logótipo */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Centralizar e estilizar o teu Logótipo Oficial Degradê */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        text-align: center;
        display: flex;
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        border-radius: 24px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        background-color: #FFFFFF;
        padding: 8px;
        border: 1px solid #E2E8F0;
    }
    
    /* Caixas de Chat Humanizadas (Estilo Bolhas de Conversa Reais) */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 18px !important;
        margin-bottom: 16px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    
    /* Botão de reiniciar sutil e elegante */
    .stButton>button {
        background-color: #F1F5F9 !important;
        color: #475569 !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #E2E8F0 !important;
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa o cliente OpenAI através da tua chave de API nos Secrets
api_key_segura = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key_segura)

FICHEIRO_HISTORICO = "historico_estudo.json"

# 2. Painel Lateral Minimalista (Sidebar)
with st.sidebar:
    # Exibe o teu logótipo oficial guardado de forma estável
    logo_oficial_etuka = "https://imgur.com"
    st.image(logo_oficial_etuka, width=130)
    
    st.markdown("<h3 style='text-align: center; color: #0F172A; margin-top:0;'>etuka.helpy</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 14px;'>O teu explicador particular disponível sempre que precisares.</p>", unsafe_allow_html=True)
    st.divider()
    
    # Seletor simples de foco de estudo
    disciplina_selecionada = st.selectbox(
        "📚 Escolhe a matéria:",
        ["Matemática", "História", "Ciências / Biologia", "Programação (Python)", "Geral"]
    )
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🗑️ Limpar Conversa Atual"):
        if os.path.exists(FICHEIRO_HISTORICO):
            os.remove(FICHEIRO_HISTORICO)
        if "mensagens" in st.session_state:
            del st.session_state.mensagens
        st.rerun()

# 3. Engenharia de Prompt Focada em Humanização, Empatia e Apoio Emocional
PROMPT_BASE = (
    "Tu és o 'etuka.helpy', um tutor e explicador humano de {disciplina}, extremamente caloroso, paciente e empático. "
    "Tu não falas como um computador frio ou uma lista de tópicos. Tu falas como um mentor atencioso ou um irmão mais velho que adora ensinar.\n"
    "As tuas diretrizes de conversação estritas são:\n"
    "1. NUNCA dês a resposta final de forma direta ou mecânica. O teu objetivo é fazer o aluno aprender com orgulho.\n"
    "2. Se o estudante disser que tem dificuldades ou demonstrar frustração, valida primeiro as suas emoções (ex: 'Eu compreendo perfeitamente, a matemática pode parecer um bicho de sete cabeças ao início, mas vamos resolver isto juntos, passo a passo').\n"
    "3. Usa uma linguagem simples, natural, acolhedora e cheia de incentivo. Evita termos técnicos sem os explicares primeiro com uma analogia da vida real.\n"
    "4. Termina as tuas respostas de forma leve, fazendo apenas UMA pergunta simples de cada vez para guiar o raciocínio do aluno.\n"
    "5. Responde sempre em português de Portugal fluído, humano e caloroso."
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

# Mantém o prompt do sistema sempre atualizado com a matéria correta
if len(st.session_state.mensagens) > 0 and isinstance(st.session_state.mensagens, list):
    if isinstance(st.session_state.mensagens[0], dict) and st.session_state.mensagens[0].get("role") == "system":
        st.session_state.mensagens[0]["content"] = prompt_final

# 6. Cabeçalho Principal do Website Minimalista
st.title("Conversa com o teu Tutor")
st.markdown("<p style='text-align: center; color: #64748B; margin-top: -10px;'>Diz-me qual é a tua dúvida. Estou aqui para te apoiar em cada passo!</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 7. Renderizar Histórico de Chat (Estilo Conversa Humana)
for msg in st.session_state.mensagens:
    if isinstance(msg, dict) and msg.get("role") != "system":
        # Usa avatares nativos elegantes para simular pessoas reais
        avatar_tipo = "👤" if msg["role"] == "user" else "🎓"
        with st.chat_message(msg["role"], avatar=avatar_tipo):
            st.markdown(msg["content"])

# 8. Caixa de Entrada de Chat de Conversa Direta
if pergunta_estudante := st.chat_input(f"Conversar sobre {disciplina_selecionada}..."):
    if not api_key_segura:
        st.error("Erro: A tua chave OPENAI_API_KEY não foi configurada nos Secrets do Streamlit.")
    else:
        # Exibe instantaneamente a mensagem do utilizador
        with st.chat_message("user", avatar="👤"):
            st.markdown(pergunta_estudante)
        st.session_state.mensagens.append({"role": "user", "content": pergunta_estudante})
        
        # Gera a resposta da IA com um efeito humano de digitação/carregamento
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("A ler a tua mensagem..."):
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
                        st.error("⚠️ Nota de Configuração: O teu site está pronto e lindo! Só precisas de ir ao teu painel da OpenAI (://openai.com), clicar em 'Add credits' e carregar $5 para ativar as respostas de texto do teu tutor.")
                    else:
                        st.error(f"Erro de comunicação: {e}")
