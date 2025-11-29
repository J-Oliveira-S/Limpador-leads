import streamlit as st
import pandas as pd
from io import StringIO
from datetime import date, datetime 
import re 

# --- Configuração da Página ---
st.set_page_config(page_title="SDR Helper - ITECA", page_icon="🎯", layout="wide")

# ==============================================================================
# 🕵️ PROMPT SECRETO 
# ==============================================================================
PROMPT_IA = """
Organize os dados abaixo.
Formato: CSV.
Separador: PONTO E VÍRGULA (;).
NÃO inclua cabeçalho.
Ordem dos dados: Name; Company; Profession; Phone.
Se faltar dado, use "N/A".
Lista:
"""
# ==============================================================================

# --- FUNÇÃO DE LIMPEZA (BLINDAGEM GOOGLE SHEETS) ---
def sanitizar_google_sheets(valor):
    # 1. Converte para texto e remove espaços nas pontas
    valor = str(valor).strip()
    
    # 2. Se for vazio, retorna N/A
    if valor in ["", "nan", "None", "N/A", "null", "NaN"]:
        return "N/A"
    
    # 3. REMOVE TABS E ENTERS (Quebram a colagem)
    valor = re.sub(r'[\r\n\t]', ' ', valor)
    
    # 4. REMOVE O "=" DO INÍCIO (O pedido principal)
    # Se a célula começar com =, a gente deleta esse caractere
    if valor.startswith("="):
        valor = valor[1:] # Pega do segundo caractere em diante
        valor = valor.strip() # Remove espaços que possam ter sobrado depois do =

    # 5. O TRUQUE DO APÓSTROFO (')
    # Se, depois de limpar, o valor começar com "+", "-", ou "@", 
    # o Google Sheets AINDA pode tentar somar.
    # Colocamos um ' na frente. O Sheets esconde o ' e mostra o texto corretamente.
    if valor.startswith(("+", "-", "@")):
        valor = "'" + valor

    # 6. Limpa aspas duplas internas que confundem CSV
    valor = valor.replace('"', '') 
    
    return valor

# --- LÓGICA DE SAUDAÇÃO ---
def get_saudacao():
    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 12:
        return "Bom dia! ☀️"
    elif 12 <= hora_atual < 18:
        return "Boa tarde! 🚀"
    else:
        return "Boa noite! 🌙"

frase = get_saudacao()

# --- BARRA LATERAL ---
st.sidebar.header("1. Dados da Carga")

col_bni_chapter = st.sidebar.text_input("BNI Chapter", value="BNI Collaboration") 
col_address = st.sidebar.text_input("Address", value="Kovens Conference Center 3000 NE 151 St")
col_contact = st.sidebar.date_input("Contact Date", value=date.today())
col_sales_exec = st.sidebar.text_input("Sales Executive", value="Gabriel Khalil")
col_sdr = st.sidebar.text_input("SDR Owner", value="Jonathan Oliveira")

st.sidebar.markdown("---")

# --- ÁREA PRINCIPAL ---
st.title("🎯 Processador de Leads - ITECA")
st.markdown(f"### {frase}")
st.markdown("---") 

st.subheader("2. Cole o resultado da IA aqui:")
texto_input = st.text_area("Dados", height=150, label_visibility="collapsed") 

if st.button("⚡ Gerar Linhas do CRM"):
    if texto_input:
        try:
            # 1. LEITURA DOS DADOS DA IA
            df_input = pd.read_csv(StringIO(texto_input), sep=None, engine='python', header=None)

            # Blindagem de Estrutura
            df_input = df_input.iloc[:, :4]
            if str(df_input.iloc[0, 0]).lower() in ['name', 'nome', 'member name']:
                df_input = df_input.iloc[1:]
            
            while df_input.shape[1] < 4:
                df_input[df_input.shape[1]] = "N/A"

            # 2. APLICAÇÃO DA SANITIZAÇÃO (LINHA POR LINHA)
            df_input = df_input.applymap(sanitizar_google_sheets)

            # 3. MONTAGEM FINAL
            df_final = pd.DataFrame()
            df_final['Member Name'] = df_input.iloc[:, 0]
            df_final['Company'] = df_input.iloc[:, 1]
            df_final['Profession'] = df_input.iloc[:, 2]
            df_final['Phone'] = df_input.iloc[:, 3]

            # Dados fixos
            df_final['BNI Chapter'] = col_bni_chapter
            df_final['Address'] = col_address
            df_final['Contact'] = col_contact.strftime('%m/%d/%Y')
            df_final['Sales Executive'] = col_sales_exec
            df_final['SDR'] = col_sdr

            # 4. REORGANIZAÇÃO (9 Colunas)
            colunas_ordenadas = [
                'BNI Chapter', 'Address', 'Member Name', 'Company', 
                'Profession', 'Phone', 'Contact', 'Sales Executive', 'SDR'
            ]
            df_final = df_final[colunas_ordenadas]

            # 5. SAÍDA
            st.success(f"✅ {len(df_final)} leads blindados para o Google Sheets!")
            
            st.dataframe(df_final, hide_index=True)

            tsv_data = df_final.to_csv(index=False, sep='\t', header=False)
            
            st.text_area("3. Copie TUDO aqui e cole no Google Sheets:", 
                         value=tsv_data, 
                         height=250)

        except Exception as e:
            st.error("❌ Erro ao processar.")
            st.warning(f"Detalhe do erro: {e}")
    else:
        st.info("Aguardando dados da IA...")