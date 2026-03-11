import streamlit as st
import pandas as pd

st.title("📦 Etiquetas com Scanner e ATS válidas")

# Upload dos arquivos
arquivo_romaneio = st.file_uploader("Suba o arquivo de Romaneio (CSV)", type="csv")
arquivo_ats = st.file_uploader("Suba o arquivo de Planejamento ATS (CSV)", type="csv")

# Input do usuário (scanner preenche e Enter dispara)
codigo_pacote = st.text_input("Bipe ou digite o código do pacote (SPX TN)", key="pacote")

if arquivo_romaneio and arquivo_ats and codigo_pacote:
    df_romaneio = pd.read_csv(arquivo_romaneio)
    df_ats = pd.read_csv(arquivo_ats)

    ats_permitidas = df_ats['AT/TO'].astype(str).unique().tolist()

    pacote_info = df_romaneio[df_romaneio['SPX TN'].astype(str) == codigo_pacote]

    if not pacote_info.empty:
        cep = pacote_info['Zipcode'].values[0]
        cabeca_cep = str(pacote_info['Cabeça de CEP'].values[0])

        # Procurar no planejamento ATS pelo Cabeça de CEP
        planejamento_cep = df_ats[df_ats['cep'].astype(str) == cabeca_cep]

        if not planejamento_cep.empty:
            at_planejado = str(planejamento_cep['AT/TO'].values[0])
            rota_planejada = planejamento_cep['Gaiola'].values[0]

            if at_planejado in ats_permitidas:
                at_final = at_planejado
                rota_final = rota_planejada
            else:
                at_final = ats_permitidas[0]
                rota_final = df_ats.loc[df_ats['AT/TO'] == at_final, 'Gaiola'].values[0]
        else:
            # Se não encontrar no planejamento, usa ranking do romaneio
            grupo_cep = df_romaneio[df_romaneio['Cabeça de CEP'].astype(str) == cabeca_cep]
            rota_counts = grupo_cep['Corridor Cage'].value_counts()
            rota_final = rota_counts.idxmax()
            at_final = ats_permitidas[0]

            st.write("📊 Ranking de rotas para Cabeça de CEP", cabeca_cep)
            st.write(rota_counts)

        etiqueta_txt = f"""PACOTE: {codigo_pacote}
CEP: {cep}
Cabeça de CEP: {cabeca_cep}
Rota: {rota_final}
AT: {at_final}"""

        etiqueta_html = f"""
        <style>
        .etiqueta {{
            width: 8cm; height: 4cm;
            border: 2px solid black; padding: 10px;
            font-family: Arial, sans-serif;
            text-align: center;
        }}
        .rota {{
            font-size: 42px;  /* bem grande para destaque */
            font-weight: bold;
            margin: 20px 0;
        }}
        .linha-inferior {{
            font-size: 12px;
            font-weight: bold;
            margin-top: 15px;
        }}
        </style>
        <div class="etiqueta">
            <div class="rota">{rota_final}</div>
            <div class="linha-inferior">{at_final} | {codigo_pacote}</div>
        </div>
        """

        # Mostra a visualização da etiqueta
        st.markdown(etiqueta_html, unsafe_allow_html=True)

        # Botão para imprimir
        st.markdown("<button onclick='window.print()'>🖨️ Imprimir</button>", unsafe_allow_html=True)

        # Botão para baixar
        etiqueta_txt = f"""{rota_final}
        {at_final} | {codigo_pacote}"""
        st.download_button("⬇️ Baixar etiqueta", etiqueta_txt, file_name=f"etiqueta_{codigo_pacote}.txt")
