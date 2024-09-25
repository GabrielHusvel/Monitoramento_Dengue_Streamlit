
import pandas as pd
import os
import streamlit as st
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import glob
import matplotlib.pyplot as plt
import csv
import requests
from bs4 import BeautifulSoup 

st.set_page_config(page_title='Monitoramento de Dengue no Brasil ao Longo do Tempo.',
                page_icon='🦟',
                layout='wide')
st.markdown(f'''<style>.stApp {{background-color: #212325;}}</style>''', unsafe_allow_html=True)


@st.cache_data
def carregar_dataset():
    
    try:
        # Tente ler cada parte do dataset
        df = pd.read_csv(f'data_sus/df_dengue_2023_2024.csv')
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado.")
    return df  # Retorna um DataFrame vazio se o arquivo não for encontrado

# Carregar o dataset
df = carregar_dataset()
    

# Menu de seleção de doenças
doenca = "Dengue"
# Abas para o conteúdo
abas = st.tabs(["Análise por Município", "Informações e Sintomas", "Dados Epidemiológicos"])

# Aba 1: Análise por Município
with abas[0]:
    st.title(f"Análise da Situação do Município - {doenca}")

    # Converter a coluna 'data_week' para datetime, caso ainda não tenha sido convertida
    df['data_week'] = pd.to_datetime(df['data_week'], errors='coerce')

    # Selecionar município do usuário
    municipio_usuario = st.selectbox("Selecione seu município", sorted(df['municipio'].astype(str).unique()))
    
    # Comparação com outros municípios do estado
    estado_usuario = df[df['municipio'] == municipio_usuario]['estado'].values[0]
    df_estado = df[df['estado'] == estado_usuario]

    # Definir a data máxima (convertida corretamente para datetime)
    data_maxima = df_estado['data_week'].max()

    # Botões para escolha do período
    filtro_periodo = st.radio("Filtrar por", ('Último Mês', 'Último Ano'))

    if filtro_periodo == 'Último Mês':
        data_inicial = data_maxima - pd.DateOffset(months=1)
    elif filtro_periodo == 'Último Ano':
        data_inicial = data_maxima - pd.DateOffset(years=1)

    # Filtro baseado no período selecionado
    df_filtrado = df_estado[(df_estado['data_week'] >= data_inicial) & (df_estado['data_week'] <= data_maxima)]

    # Calcular o índice de risco
    df_filtrado['risco_dengue'] = (
        df_filtrado['casos_est'] * 0.1 + 
        df_filtrado['casos'] * 0.3 + 
        df_filtrado['incidência_100khab'] * 0.1 + 
        df_filtrado['disseminação'] * 5
    )

    # Determinar a cor com base no risco (vermelho, amarelo, verde)
    def definir_cor(risco):
        if risco > 7:
            return [255, 0, 0, 160]  # Vermelho (risco alto)
        elif 1 < risco <= 6.99:
            return [255, 255, 0, 160]  # Amarelo (risco moderado)
        else:
            return [0, 255, 0, 160]  # Verde (risco baixo)
    
    df_filtrado['cor'] = df_filtrado['risco_dengue'].apply(definir_cor)
    st.write('''O mapa corresponde a opção de um mês                            
             Vermelho (risco alto)
             Amarelo (risco moderado)
             Verde (risco baixo)''')

    # Mapa interativo com Pydeck
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df_filtrado,
        get_position='[longitude, latitude]',
        get_radius='5000',  # Ajuste para evitar sobreposição
        get_fill_color='cor',
        pickable=True,
        auto_highlight=True,
        tooltip=True
    )

    view_state = pdk.ViewState(
        latitude=df_filtrado['latitude'].mean(),
        longitude=df_filtrado['longitude'].mean(),
        zoom=6
    )

    # Exibição do mapa
    r = pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state,
        
        tooltip={
            'html': '<b>Município:</b> {municipio}<br><b>Casos:</b> {casos}<br><b>Est. Casos:</b> {casos_est}<br><b>Disseminação:</b> {disseminação}<br><b>Temperatura:</b> {tempmed}°C<br><b>Umidade:</b> {umidmed}%',
            'style': {'color': 'white'}
        }
    )
    st.pydeck_chart(r)

    # Criar um dataframe separado para destacar o município selecionado e os extremos (mínimo e máximo) do estado
    df_min_max = df_filtrado.groupby('data_week').agg({
        'casos': ['min', 'max'],
        'incidência_100khab': ['min', 'max'],
        'disseminação': ['min', 'max'],
        'umidmed': ['min', 'max'],
        'umidmin': ['min', 'max'],
        'umidmax': ['min', 'max'],
        'tempmed': ['min', 'max'],
        'tempmin': ['min', 'max'],
        'tempmax': ['min', 'max']
    }).reset_index()

    # Adicionar os dados do município escolhido
    df_municipio_selecionado = df_filtrado[df_filtrado['municipio'] == municipio_usuario]

    # Gráfico de linha com destaque no município selecionado
    fig = go.Figure()

    # Adicionar a linha do município selecionado
    fig.add_trace(go.Scatter(x=df_municipio_selecionado['data_week'], y=df_municipio_selecionado['casos'],
                             mode='lines+markers', name=f'{municipio_usuario} - Casos', line=dict(color='red', width=4)))

    # Adicionar a linha dos casos mínimos do estado
    fig.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('casos', 'min')],
                             mode='lines', name='Casos Mínimos (Estado)', line=dict(color='green', dash='dash')))

    # Adicionar a linha dos casos máximos do estado
    fig.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('casos', 'max')],
                             mode='lines', name='Casos Máximos (Estado)', line=dict(color='blue', dash='dash')))

    # Adicionar título e rótulos
    fig.update_layout(title=f'Comparação de Incidência de Casos {estado_usuario}',
                      xaxis_title='Semana',
                      yaxis_title='Número de Casos',
                      legend_title='Municípios')

    st.plotly_chart(fig)


    # Gráfico de linha para Casos Estimados (casos_est)
    fig_casos_est = go.Figure()

    # Adicionar a linha do município selecionado
    fig_casos_est.add_trace(go.Scatter(x=df_municipio_selecionado['incidência_100khab'], y=df_municipio_selecionado['incidência_100khab'],
                                    mode='lines+markers', name=f'{municipio_usuario} - Incidência de casos a cada 100k de habitantes', line=dict(color='red', width=4)))

    # Adicionar a linha dos casos estimados mínimos do estado
    fig_casos_est.add_trace(go.Scatter(x=df_min_max['incidência_100khab'], y=df_min_max[('incidência_100khab', 'min')],
                                    mode='lines', name='Incidência Mínima (Estado)', line=dict(color='green', dash='dash')))

    # Adicionar a linha dos casos estimados máximos do estado
    fig_casos_est.add_trace(go.Scatter(x=df_min_max['incidência_100khab'], y=df_min_max[('incidência_100khab', 'max')],
                                    mode='lines', name='Casos Incidência Máxima (Estado)', line=dict(color='blue', dash='dash')))

    # Adicionar título e rótulos
    fig_casos_est.update_layout(title=f'Comparação de Casos Estimados no Estado {estado_usuario}',
                                xaxis_title='Semana',
                                yaxis_title='Casos Estimados',
                                legend_title='Municípios')

    st.plotly_chart(fig_casos_est)


    # Gráfico de linha para Temperatura Média (tempmed)
    fig_tempmed = go.Figure()

    # Adicionar a linha do município selecionado
    fig_tempmed.add_trace(go.Scatter(x=df_municipio_selecionado['data_week'], y=df_municipio_selecionado['tempmed'],
                                    mode='lines+markers', name=f'{municipio_usuario} - Temperatura Média', line=dict(color='red', width=4)))

    # Adicionar a linha da temperatura mínima do estado
    fig_tempmed.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('tempmin', 'min')],
                                    mode='lines', name='Temperatura Mínima (Estado)', line=dict(color='green', dash='dash')))

    # Adicionar a linha da temperatura máxima do estado
    fig_tempmed.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('tempmax', 'max')],
                                    mode='lines', name='Temperatura Máxima (Estado)', line=dict(color='blue', dash='dash')))

    # Adicionar título e rótulos
    fig_tempmed.update_layout(title=f'Comparação de Temperatura Média no Estado {estado_usuario}',
                            xaxis_title='Semana',
                            yaxis_title='Temperatura Média (°C)',
                            legend_title='Municípios')

    st.plotly_chart(fig_tempmed)


    # Gráfico de linha para Umidade Média (umidmed)
    fig_umidmed = go.Figure()

    # Adicionar a linha do município selecionado
    fig_umidmed.add_trace(go.Scatter(x=df_municipio_selecionado['data_week'], y=df_municipio_selecionado['umidmed'],
                                    mode='lines+markers', name=f'{municipio_usuario} - Umidade Média', line=dict(color='red', width=4)))

    # Adicionar a linha da umidade mínima do estado
    fig_umidmed.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('umidmin', 'min')],
                                    mode='lines', name='Umidade Mínima (Estado)', line=dict(color='green', dash='dash')))

    # Adicionar a linha da umidade máxima do estado
    fig_umidmed.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('umidmax', 'max')],
                                    mode='lines', name='Umidade Máxima (Estado)', line=dict(color='blue', dash='dash')))

    # Adicionar título e rótulos
    fig_umidmed.update_layout(title=f'Comparação de Umidade Média no Estado {estado_usuario}',
                            xaxis_title='Semana',
                            yaxis_title='Umidade Média (%)',
                            legend_title='Municípios')

    st.plotly_chart(fig_umidmed)


    # Gráfico de linha para Disseminação (disseminação)
    fig_disseminacao = go.Figure()

    # Adicionar a linha do município selecionado
    fig_disseminacao.add_trace(go.Scatter(x=df_municipio_selecionado['data_week'], y=df_municipio_selecionado['disseminação'],
                                        mode='lines+markers', name=f'{municipio_usuario} - Disseminação', line=dict(color='red', width=4)))

    # Adicionar a linha da disseminação mínima do estado
    fig_disseminacao.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('disseminação', 'min')],
                                        mode='lines', name='Disseminação Mínima (Estado)', line=dict(color='green', dash='dash')))

    # Adicionar a linha da disseminação máxima do estado
    fig_disseminacao.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('disseminação', 'max')],
                                        mode='lines', name='Disseminação Máxima (Estado)', line=dict(color='blue', dash='dash')))

    # Adicionar título e rótulos
    fig_disseminacao.update_layout(title=f'Comparação de Disseminação no Estado {estado_usuario}',
                                xaxis_title='Semana',
                                yaxis_title='Disseminação',
                                legend_title='Municípios')

    st.plotly_chart(fig_disseminacao)

    

    # Mostrar o ranking dos municípios mais afetados (usando a combinação município-estado)
    df_filtrado['municipio_estado'] = df_filtrado['municipio'] + ' - ' + df_filtrado['estado']
    df_rank = df_filtrado[['municipio_estado', 'risco_dengue']].sort_values(by='risco_dengue', ascending=False)
    st.write("Ranking dos municípios mais afetados:", df_rank)    



# Aba 2: Informações e Sintomas
with abas[1]:
    st.title(f"Informações e Sintomas - {doenca}")

    # Fazer scraping da página de dengue, por exemplo
    if doenca == "Dengue":
        HEADER = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'}
        url = 'https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/d/dengue'
        response = requests.get(url, headers=HEADER, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extrair informações sobre sintomas
        informacoes = soup.find_all('p')
        for info in informacoes:
            st.write(info.get_text())


# Dados epidemiologicos
with abas[2]:
    st.title(f"🦟Monitoramento de Dengue no Brasil ao Longo do Tempo.🦟")

    # Incorporar o Power BI no Streamlit
    st.components.v1.iframe("https://app.powerbi.com/view?r=eyJrIjoiYzQyOTI4M2ItZTQwMC00ODg4LWJiNTQtODc5MzljNWIzYzg3IiwidCI6IjlhNTU0YWQzLWI1MmItNDg2Mi1hMzZmLTg0ZDg5MWU1YzcwNSJ9&pageName=ReportSectionbd7616200acb303571fc", height=600)


    st.write('Here you need uplooad the csv with data from 2010 to 2024. \nHas customizable graphics and an interactive map. \n Google Drive Data link: https://drive.google.com/drive/folders/19OGg_d3S9L6wc99I3FZxc5Mn9Ba-jXos?usp=drive_link \n DropBox Data Link: https://www.dropbox.com/scl/fo/wuwb1zpcxuvvlnyfrkcpf/AIBXL31_YW6QpjbWKyG-v2s?rlkey=8vzsj4lddvx5sh61ce8hl2df1&st=zvb71bzb&dl=0')

    uploaded_file = st.file_uploader('Faça o upload do arquivo da região desejada.')
    if uploaded_file:
        @st.cache_data
        def load_data(uploaded_file):
            df = pd.read_csv(uploaded_file)
            return df
        
        df = load_data(uploaded_file)       
        st.write('Dados carregados com sucesso!')

        # Certifique-se de que a coluna 'estado' seja do tipo string e remova valores nulos
        df['estado'] = df['estado'].astype(str)
        df = df[df['estado'].notna()]

    else:
        st.write('Nenhum arquivo foi carregado.')

    
    # Multiselect para selecionar as colunas desajas
    selected_columns = st.multiselect("Selecione as colunas. :)", df.columns.tolist(), default=df.columns.tolist())

    # Multiselect para selecionar os estados, ordenados alfabeticamente
    selected_estado = st.multiselect(" Selecione os estados.", sorted(df['estado'].astype(str).unique()))
    df_filtrado = df[(df['estado'].isin(selected_estado))]

    # Multiselect para selecionar os municípios, ordenados alfabeticamente
    selected_municipio = st.multiselect("Selecione os municípios.", sorted(df_filtrado['municipio'].astype(str).unique()), default=sorted(df_filtrado['municipio'].astype(str).unique()))
    df_filtrado = df_filtrado[(df_filtrado['municipio'].isin(selected_municipio))]
    st.write('Dados filtrados:/n')
    st.write(len(df_filtrado), ' Registros')
    st.dataframe(df_filtrado[selected_columns])


    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(df_filtrado)
    # Baixar csv
    st.download_button(
        label='Baixar dados filtrados',
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv',
    )

    if selected_municipio:
        # Converter a coluna para o tipo datetime
        df_filtrado['data_week'] = pd.to_datetime(df_filtrado['data_week'])

        # Selecionar o intervalo de datas para visualização
        data_inicial = st.date_input('Data inicial', value=df_filtrado['data_week'].min(), min_value=df_filtrado['data_week'].min(), max_value=df_filtrado['data_week'].max())
        data_final = st.date_input('Data final', value=df_filtrado['data_week'].max(), min_value=df_filtrado['data_week'].min(), max_value=df_filtrado['data_week'].max())

        # Filtrar os dados para o intervalo de datas selecionado
        dados_filtrados = df_filtrado[(df_filtrado['data_week'] >= pd.to_datetime(data_inicial)) & (df_filtrado['data_week'] <= pd.to_datetime(data_final))]

        # Agrupar os dados por município e somar os casos e a estimativa de casos
        dados_agrupados = dados_filtrados.groupby(['municipio', 'latitude', 'longitude']).agg(
            casos=('casos', 'sum'),
            casos_est=('casos_est', 'sum'),
            tempmed=('tempmed', 'mean'),  # Somar as temperaturas médias
            umidmed=('umidmed', 'mean')   # Somar as umidades médias
        ).reset_index()

        # Limitar o número de casas decimais de tempmed e umidmed
        dados_agrupados['tempmed'] = dados_agrupados['tempmed'].round(2)
        dados_agrupados['umidmed'] = dados_agrupados['umidmed'].round(2)

    # Verificar se há dados após a filtragem
    if selected_municipio:

        # Criar o mapa interativo
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=dados_agrupados,
            get_position='[longitude, latitude]',  # Coordenadas corretas
            get_radius=9000,  # Ajustar o tamanho dos pontos
            get_fill_color='[255, 0, 0, 160]',  # Vermelho translúcido
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=-15.7801,  # Posição central do Brasil
            longitude=-47.9292,
            zoom=4,
            pitch=50
        )

        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{municipio} Casos: {casos} Estimativa: {casos_est} Temp: {tempmed} nUmidade: {umidmed} %"}
        )

        st.pydeck_chart(r)


        # Evolução dos casos ao longo do tempo
        fig = px.line(dados_filtrados, x='data_week', y='casos', color='municipio', title='Evolução dos casos ao longo do tempo')
        st.plotly_chart(fig)

        # Temperatura ao longo do tempo
        fig = px.line(dados_filtrados, x='data_week', y='tempmed', color='municipio', title='Temperatura ao longo do tempo')
        st.plotly_chart(fig)
        
        # Úmidade ao longo do tempo
        fig = px.line(dados_filtrados, x='data_week', y='umidmed', color='municipio', title='Úmidade ao longo do tempo')
        st.plotly_chart(fig)
    
    
    if selected_municipio:   
        # Seletor de colunas
        colunas = dados_filtrados.columns.tolist()

        # Gráfico de barras
        st.subheader('Gráfico de Barras')
        x_col_barra = st.selectbox('Para o eixo X indico selecionar data, municipios ou estados', colunas, key='x_barra')
        y_col_barra = st.selectbox('Para o eixo Y indico selecionar uma coluna numérica ', colunas, key='y_barra')

        if x_col_barra and y_col_barra:
            grafico_barra = px.bar(dados_filtrados, x=x_col_barra, y=y_col_barra, title=f'Gráfico de Barras: {x_col_barra} vs {y_col_barra}')
            st.plotly_chart(grafico_barra)


        # Gráfico de pizza 
        st.subheader('Gráfico de Pizza')
        pie_col = st.selectbox('Selecione a coluna para os valores, indico selecionar uma coluna numérica', colunas, key='pie')
        pie_col_names = st.selectbox('Selecione a coluna para os nomes como data, municipios ou estados', colunas, key='pie_names')

        if pie_col and pie_col_names:
            grafico_pizza = px.pie(dados_filtrados, values=pie_col, names=pie_col_names, title=f'Gráfico de Pizza: {pie_col_names} - {pie_col}')
            st.plotly_chart(grafico_pizza)
            

        # Histograma
        st.subheader('Histograma')
        x_col_histo = st.selectbox('Selecione o eixo x, indico selecionar uma coluna categórica', colunas, key='x_histo')
        y_col_histo = st.selectbox('Selecione o eixo Y, indico selecionar uma coluna numérica', colunas, key='y_histo')
        grafico_histograma = px.histogram(dados_filtrados, x=x_col_histo, y=y_col_histo, nbins=200, )
        st.plotly_chart(grafico_histograma)


