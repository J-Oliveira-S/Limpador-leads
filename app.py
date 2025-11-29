import streamlit as st
import pandas as pd
from io import StringIO
from datetime import date, datetime # Import ajustado para pegar hora e data

# --- Configuração da Página ---
st.set_page_config(page_title="SDR Helper - ITECA", page_icon="🎯", layout="wide")

# --- LÓGICA DE SAUDAÇÃO (O Toque Especial) ---
def get_saudacao():
    hora_atual = datetime.now().hour
    
    # Imagens do Unsplash (Links diretos)
    if 5 <= hora_atual < 12:
        return "Bom dia, time! Vamos pra cima! ☀️", "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=800&q=80"
    elif 12 <= hora_atual < 18:
        return "Boa tarde! Foco total nos resultados! 🚀", "https://images.unsplash.com/photo-1595113316349-9fa4eb24f884?w=800&q=80"
    else:
        return "Boa noite! Ótimo descanso ou bom final de turno! 🌙", "https://images.unsplash.com/photo-1532074205216-d0e1f4b87368?w=800&q=80"

frase, imagem_url = get_saudacao()

# --- TÍTULO E IMAGEM ---
st.image(imagem_url, height=150) # Imagem de cabeçalho
st.title("🎯 Processador de Leads - ITECA")
st.markdown(f"### {frase}")
st.caption("Cole os dados brutos da IA e copie a linha perfeita para o CRM.")

# --- BARRA LATERAL (Inputs Fixos) ---
st.sidebar.header("1. Dados da Carga")

col_bni_chapter = st.sidebar.text_input("BNI Chapter", value="BNI Collaboration") 
col_address = st.sidebar.text_input("Address", value="Kovens Conference Center 3000 NE 151 St")
col_contact = st.sidebar.date_input("Contact Date", value=date.today())
col_sales_exec = st.sidebar.text_input("Sales Executive", value="Gabriel Khalil")
col_sdr = st.sidebar.text_input("SDR Owner", value="Jonathan Oliveira")

st.sidebar.markdown("---")
st.sidebar.caption("A coluna 'Status' será gerada em branco.")

# --- ÁREA DE PROMPT (Escondida) ---
with st.expander("🤫 Clique aqui para ver o Prompt Secreto (Obrigatório)"):
    st.code("""
    Organize os dados abaixo.
    Formato: CSV.
    Separador: PONTO E VÍRGULA (;).
    NÃO inclua cabeçalho.
    Ordem dos dados: Name; Company; Profession; Phone.
    Se faltar dado, use "N/A".
    Lista:
    """, language="text")

# --- ÁREA PRINCIPAL ---
st.subheader("2. Cole o resultado da IA aqui:")
texto_input = st.text_area("Cole o CSV (Name; Company; Profession; Phone)", height=150)

if st.button("⚡ Gerar Linhas do CRM"):
    if texto_input:
        try:
            # 1. LEITURA DOS DADOS DA IA
            df_input = pd.read_csv(StringIO(texto_input), sep=None, engine='python', header=None)

            # Blindagem: Pega apenas as 4 primeiras colunas e remove linhas de título se houver
            df_input = df_input.iloc[:, :4]
            # Verifica se a primeira célula parece um cabeçalho e remove
            if str(df_input.iloc[0, 0]).lower() in ['name', 'nome', 'member name']:
                df_input = df_input.iloc[1:]
            
            # Garante que não há colunas faltando na leitura
            while df_input.shape[1] < 4:
                df_input[df_input.shape[1]] = "N/A"

            # 2. CRIAÇÃO DO DATAFRAME FINAL 
            df_final = pd.DataFrame()
            
            # Primeiro: Dados que variam por linha (Vindos da IA)
            df_final['Member Name'] = df_input.iloc[:, 0]
            df_final['Company'] = df_input.iloc[:, 1]
            df_final['Profession'] = df_input.iloc[:, 2]
            df_final['Phone'] = df_input.iloc[:, 3]

            # Segundo: Injetamos os dados fixos (SideBar)
            df_final['BNI Chapter'] = col_bni_chapter
            df_final['Address'] = col_address
            df_final['Contact'] = col_contact.strftime('%m/%d/%Y')
            df_final['Sales Executive'] = col_sales_exec
            df_final['SDR'] = col_sdr
            df_final['Status'] = "" # Coluna vazia

            # Limpeza de espaços
            df_final = df_final.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

            # 3. REORGANIZAÇÃO VISUAL (Ordem do Google Sheets)
            colunas_ordenadas = [
                'BNI Chapter', 
                'Address', 
                'Member Name', 
                'Company', 
                'Profession', 
                'Phone', 
                'Contact', 
                'Sales Executive', 
                'SDR', 
                'Status'
            ]
            df_final = df_final[colunas_ordenadas]

            # 4. EXIBIÇÃO E DOWNLOAD
            st.success(f"✅ {len(df_final)} leads processados! Copie abaixo:")
            
            # Mostra a tabela para conferência
            st.dataframe(df_final, hide_index=True)

            # Gera o texto para copiar (Separado por TAB)
            tsv_data = df_final.to_csv(index=False, sep='\t', header=False)
            
            st.text_area("3. Copie TUDO aqui e cole no Google Sheets:", 
                         value=tsv_data, 
                         height=250)

        except Exception as e:
            st.error("❌ Erro ao processar.")
            st.warning(f"Detalhe do erro: {e}")
    else:
        st.info("Aguardando dados da IA...")