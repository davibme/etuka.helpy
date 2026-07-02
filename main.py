import os
import json
import streamlit as st
from openai import OpenAI

# 1. Configuração Visual da Página Web
st.set_page_config(page_title="EduBuddy Pro - Tutor IA", page_icon="🎓", layout="centered")

# Procura a chave nas configurações seguras do site (Secrets) ou no computador local
api_key_segura = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key_segura)

FICHEIRO_HISTORICO = "historico_estudo.json"

# 2. Painel Lateral (Sidebar)
with st.sidebar:
    st.image("https://flaticon.com", width=100)
    st.title("EduBuddy Pro")
    st.markdown("O teu explicador particular disponível 24/7.")
    st.divider()
    
    disciplina_selecionada = st.selectbox(
        "📚 Escolhe a Disciplina:",
        ["Matemática", "História", "Ciências / Biologia", "Programação (Python)", "Geral"]
    )
    st.success(f"Modo atual: **{disciplina_selecionada}**")
    st.divider()
    
    if st.button("🔄 Reiniciar Tudo"):
        if os.path.exists(FICHEIRO_HISTORICO):
            os.remove(FICHEIRO_HISTORICO)
        if "mensagens" in st.session_state:
            del st.session_state.mensagens
        st.rerun()

# 3. Engenharia de Prompt Dinâmica
PROMPT_BASE = (
    "Tu és o 'EduBuddy', um tutor de estudos para o ensino secundário especialista em {disciplina}. "
    "As tuas regras estritas de funcionamento são:\n"
    "1. NUNCA dês a resposta final de um problema diretamente.\n"
    "2. Explica conceitos complexos usando analogias e pistas inteligentes baseadas em {disciplina}.\n"
    "3. Faz perguntas socráticas curtas para guiar o estudante passo a passo a descobrir a resposta sozinho.\n"
    "4. Responde sempre em português de Portugal com um tom paciente, jovem e motivador."
)
prompt_final = PROMPT_BASE.format(disciplina=disciplina_selecionada)

# 4. Funções de Gestão de Ficheiro (Correção das Listas)
def carregar_historico_disco():
    if os.path.exists(FICHEIRO_HISTORICO):
        with open(FICHEIRO_HISTORICO, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if isinstance(dados, list):
                return dados
    return [{"role": "system", "content": prompt_final}]

def guardar_historico_disco(dados_historico):
    with open(FICHEIRO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(dados_historico, f, ensure_ascii=False, indent=4)

# 5. Inicialização da Memória da Sessão Web (Garante que é uma lista estruturada)
if "mensagens" not in st.session_state or not isinstance(st.session_state.mensagens, list):
    st.session_state.mensagens = carregar_historico_disco()

# Garante que o primeiro item (system prompt) se mantém atualizado como um dicionário válido
if st.session_state.mensagens and isinstance(st.session_state.mensagens, list):
    st.session_state.mensagens[0] = {"role": "system", "content": prompt_final}

# 6. Cabeçalho Principal do Website
st.title(f"🎓 EduBuddy: Tutor de {disciplina_selecionada}")
if len(st.session_state.mensagens) > 1:
    st.caption("Progresso guardado com sucesso!")
else:
    st.caption("Coloca as tuas dúvidas. Dou pistas, tu fazes a magia!")

# 7. Renderizar Histórico de Chat
for msg in st.session_state.mensagens:
    if isinstance(msg, dict) and msg.get("role") != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. Caixa de Entrada de Chat e Processamento da IA
if pergunta_estudante := st.chat_input(f"Diz-me a tua dúvida sobre {disciplina_selecionada}..."):
    if not api_key_segura:
        st.error("Erro: A chave OPENAI_API_KEY não foi configurada nos Secrets.")
    else:
        with st.chat_message("user"):
            st.markdown(pergunta_estudante)
        st.session_state.mensagens.append({"role": "user", "content": pergunta_estudante})
        
        with st.chat_message("assistant"):
            with st.spinner("A preparar uma pista pedagógica..."):
                resposta = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.mensagens
                )
                resposta_tutor = resposta.choices.message.content
                st.markdown(resposta_tutor)
                
        st.session_state.mensagens.append({"role": "assistant", "content": resposta_tutor})
        guardar_historico_disco(st.session_state.mensagens)



