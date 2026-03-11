import streamlit as st
import pandas as pd

st.title("📦 Etiquetas com Scanner e ATS válidas")

# Upload dos arquivos
arquivo_romaneio = st.file_uploader("Suba o arquivo de Romaneio (CSV)", type="csv")
arquivo_ats = st.file_uploader("Suba o arquivo de Planejamento ATS (CSV)", type="csv")

# Botão para baixar modelo de planejamento ATS
modelo_ats = pd.DataFrame({
    "cep": ["00000-000", "11111-111"],
    "AT/TO": ["AT001", "AT002"],
    "Gaiola": ["C-01", "C-02"]
})
st.download_button(
    "⬇️ Baixar modelo de Planejamento ATS",
    modelo_ats.to_csv(index=False),
    file_name="modelo_planejamento_ATS.csv",
    mime="text/csv"
)

# Botão para baixar modelo de romaneio
modelo_romaneio = pd.DataFrame({
    "SPX TN": ["123456789", "987654321"],
    "Zipcode": ["07000-000", "08000-000"],
    "Cabeça de CEP": ["07000", "08000"],
    "Corridor Cage": ["C-01", "C-02"]
})
st.download_button(
    "⬇️ Baixar modelo de Romaneio",
    modelo_romaneio.to_csv(index=False),
    file_name="modelo_romaneio.csv",
    mime="text/csv"
)

# Input do usuário
codigo_pacote = st.text_input("Bipe ou digite o código do pacote (SPX TN)", key="pacote")

if arquivo_romaneio and arquivo_ats and codigo_pacote:
    # 🔑 Lê arquivos já forçando tudo como string
    df_romaneio = pd.read_csv(arquivo_romaneio, dtype=str)
    df_romaneio.columns = df_romaneio.columns.str.strip()

    df_ats = pd.read_csv(arquivo_ats, dtype=str)
    df_ats.columns = df_ats.columns.str.strip()

    # Remove espaços extras dos valores
    df_romaneio = df_romaneio.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_ats = df_ats.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    ats_permitidas = df_ats['AT/TO'].unique().tolist()

    # Verifica se a coluna existe
    if "SPX TN" in df_romaneio.columns:
        pacote_info = df_romaneio[df_romaneio['SPX TN'] == codigo_pacote]
    else:
        st.error("⚠️ O arquivo de romaneio não contém a coluna 'SPX TN'.")
        st.write("Colunas encontradas:", df_romaneio.columns.tolist())
        pacote_info = pd.DataFrame()

    if not pacote_info.empty:
        cep = pacote_info['Zipcode'].values[0]
        cabeca_cep = pacote_info['Cabeça de CEP'].values[0]
    else:
        cabeca_cep = st.text_input("Pacote não encontrado. Informe a Cabeça de CEP:", key="cabeca_manual")
        cep = "N/A"

    if cabeca_cep:
        planejamento_cep = df_ats[df_ats['cep'] == cabeca_cep]

        if not planejamento_cep.empty:
            at_final = planejamento_cep['AT/TO'].values[0]
            rota_final = planejamento_cep['Gaiola'].values[0]
        else:
            grupo_cep = df_romaneio[df_romaneio['Cabeça de CEP'] == cabeca_cep]
            if not grupo_cep.empty:
                rota_counts = grupo_cep['Corridor Cage'].value_counts()
                rota_final = rota_counts.idxmax()
            else:
                rota_final = "N/A"
            at_final = ats_permitidas[0]

        etiqueta_html = f"""
        <style>
        .etiqueta {{
            width: 8cm; height: 4cm;
            border: 2px solid black; padding: 10px;
            font-family: Arial, sans-serif;
            text-align: center;
        }}
        .rota {{
            font-size: 42px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .linha-inferior {{
            font-size: 14px;
            font-weight: bold;
            margin-top: 15px;
        }}
        </style>
        <div class="etiqueta">
            <div class="rota">{rota_final}</div>
            <div class="linha-inferior">{at_final} | {codigo_pacote}</div>
        </div>
        """

        st.markdown(etiqueta_html, unsafe_allow_html=True)
       st.markdown("""
            <script>
            function imprimir() {
                window.print();
            }
            </script>
            
            <button onclick="imprimir()" style="
            padding:10px 20px;
            font-size:16px;
            background-color:#4CAF50;
            color:white;
            border:none;
            border-radius:5px;
            cursor:pointer;">
            🖨️ Imprimir
            </button>
            """, unsafe_allow_html=True)

        etiqueta_txt = f"""{rota_final}
{at_final} | {codigo_pacote}"""
        st.download_button("⬇️ Baixar etiqueta", etiqueta_txt, file_name=f"etiqueta_{codigo_pacote}.txt")
