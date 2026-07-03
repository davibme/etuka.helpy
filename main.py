import os
import json
import base64
import streamlit as st
from openai import OpenAI

# 1. Configuração de Página com Identidade Visual Dark de IA
st.set_page_config(page_title="etuka.helpy - O Teu Tutor de IA", page_icon="🎓", layout="centered")

# Injeção de CSS para recriar o Modo Escuro Puro do ChatGPT e ajustar o logótipo nativo
st.markdown("""
    <style>
    /* Fundo principal totalmente escuro (Estilo ChatGPT Dark) */
    .stApp {
        background-color: #212121 !important;
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
    
    /* Logótipo oficial centralizado com fundo limpo */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        text-align: center;
        display: flex;
        justify-content: center;
        margin-top: 15px;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        border-radius: 16px !important;
        background-color: #FFFFFF !important;
        padding: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    /* Caixas de Chat Minimalistas no Modo Escuro */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 15px 0px !important;
        margin-bottom: 5px !important;
    }
    
    /* Linha divisória sutil entre as mensagens */
    [data-testid="stChatMessage"] {
        border-bottom: 1px solid #2F2F2F !important;
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
    
    /* Caixa de input de text escura */
    [data-testid="stChatInput"] {
        background-color: #2F2F2F !important;
        border: 1px solid #424242 !important;
        border-radius: 26px !important;
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

# A SUA IMAGEM CONVERTIDA EM TEXTO SEGURO (BASE64) - Carrega 100% das vezes sem internet
LOGO_BASE64 = (
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U"
    "HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIy"
    "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCADIAYADASIAAhEBAxEB/8QAHwAA"
    "AQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJx"
    "FDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1"
    "dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo"
    "6erx8vP09fb3+Pn6/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAV"
    "GxYIFAKICUKEYFBidIClMHJ5GvEgRLAM1YGRvtBhwpOlW3Sb4VPD1YTypQE1JNW11ZZFdWZ1ldeX193h4uBFg4X0"
    "DFYNJVYWFiY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8"
    "jJytLT1NXW19jZ2uLj5OXm5fo6px8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAooooAKKKKByg9GFFRyzxQD"
    "MsiovqxxXPa74s0/TbGUxXcLXG07F3Z57UAcT8RPGAeePSNLuyGOfPaJs4YHgZ/P8qyNG1Hx9pluVsbWe7hcByZl"
    "807uSeeorK8C6TFqPihLm9uYY4/MLZlb/Wv1x9etfQEcaRRqiKFVRgAdAKAPEG+KHi/TnKX2k2w9fMjdCf8AvoVJ"
    "bfGa6bUTp9zpgWZjtEkbgonTvya9qubS3vIjHcwRzIeqyKCP1rx/4meF7Cxl0ptLsYrTzptskiKQuCevFAGvdfFH"
    "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"
