import pandas as pd
import os
import streamlit as st
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import json
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


# Dataset inicial
df = pd.DataFrame({
    'municipio': ['Municipio1', 'Municipio2'],
    'casos_est': [110, 160],
    'casos_est_min': [100, 150],
    'casos_est_max': [120, 170],
    'casos': [100, 150],
    'proba_disse>1': [0.2, 0.5],
    'incidência_100khab': [50, 75],
    'disseminação': [0.9, 1.0],
    'população': [10000, 15000],
    'tempmin': [20.0, 22.0],
    'umidmax': [80, 85],
    'umidmed': [70, 75],
    'umidmin': [60, 65],
    'tempmed': [25.0, 26.0],
    'tempmax': [30.0, 32.0],
    'estado': ['Estado1', 'Estado2'],
    'longitude': [-51.9253, -49.9253],
    'latitude': [-14.2350, -12.2350],
    'data_week': ['2024-01-01', '2024-02-01']
})


# Modelo Pydantic para validação de entrada
# Modelo para incluir todas as colunas
class Item(BaseModel):
    municipio: str
    casos_est: int
    casos_est_min: int
    casos_est_max: int
    casos: int
    proba_disse: float
    incidência_100khab: float
    disseminação: float
    população: int
    tempmin: float
    umidmax: int
    umidmed: int
    umidmin: int
    tempmed: float
    tempmax: float
    estado: str
    longitude: float
    latitude: float
    data_week: str

# Read (leitura de um município específico)
@app.get('/items/{municipio}')
def read_item(municipio: str):
    global df
    result = df[df['municipio'] == municipio]
    if not result.empty:
        return result.to_dict(orient='records')[0]
    return {"error": "Item não encontrado"}

# Create (criação de novos registros)
@app.post('/items')
def create_item(item: Item):
    global df
    new_row = pd.DataFrame([item.dict()])
    df = pd.concat([df, new_row], ignore_index=True)
    return df.to_dict(orient='records')

# Delete (remoção de registros)
@app.delete('/items/{municipio}')
def delete_item(municipio: str):
    global df
    df = df[df['municipio'] != municipio]
    return df.to_dict(orient='records')

# Update (atualização de registros)
@app.put('/items/{municipio}')
def update_item(municipio: str, new_item: Item):
    global df
    df.loc[df['municipio'] == municipio, df.columns] = new_item.dict().values()
    return df[df['municipio'] == municipio].to_dict(orient='records')[0]

# Configuração da página
st.set_page_config(page_title='Monitoramento de Doenças no Brasil', page_icon='🦟', layout='wide')
st.markdown(f'''<style>.stApp {{background-color: #212325;}}</style>''', unsafe_allow_html=True)

diase = st.sidebar.selectbox(
    'Escolha a doença',[ 'Dengues', 'Gripes - Opção em desenvolvimento'])

if diase == 'Gripes':

    # Título do Dashboard
    st.title("Monitoramento Epidemiológico de Gripes - Brasil")
    
    
    
    # # Função para carregar CSVs
    # @st.cache_data
    # def carregar_dados():
    #     df_municipios = pd.read_csv('data_sus/infogripe-master/Dados/InfoGripe/base_territorial/tabela_municipio_macsaud.csv')
    #     df_serie_temporal = pd.read_csv('data_sus/infogripe-master/Dados/InfoGripe/base_territorial/serie_temporal_com_estimativas_recentes.csv', sep=';')
    #     df_serie_sem_filtro = pd.read_csv('data_sus/infogripe-master/Dados/InfoGripe/base_territorial/dados_semanais_faixa_etaria_sexo_virus_sem_filtro_sintomas.csv', sep=';')
    #     df_territorios = pd.read_csv('data_sus/infogripe-master/Dados/InfoGripe/base_territorial/tabela_municipio_macsaud.csv')
    #     df_dados_virus = pd.read_csv('data_sus/infogripe-master/Dados/InfoGripe/base_territorial/dados_semanais_faixa_etaria_sexo_virus.csv', sep=';')
    #     df_virus_sem_filtro = pd.read_csv('data_sus/infogripe-master/Dados/InfoGripe/base_territorial/dados_semanais_faixa_etaria_sexo_virus_sem_filtro_sintomas.csv', sep=';')
        
    #     return df_municipios, df_serie_temporal, df_serie_sem_filtro, df_territorios, df_dados_virus, df_virus_sem_filtro

    # # Carregar os dados
    # df_municipios, df_serie_temporal, df_serie_sem_filtro, df_territorios, df_dados_virus, df_virus_sem_filtro = carregar_dados()

    # # Barra lateral com filtros
    # st.sidebar.header('Filtros')
    # uf_selecionada = st.sidebar.selectbox('Selecione a UF', df_serie_temporal['Unidade da Federação'].unique())
    # ano_epidemiologico = st.sidebar.selectbox('Selecione o Ano Epidemiológico', df_serie_temporal['Ano epidemiológico'].unique())
    # semana_epidemiologica = st.sidebar.selectbox('Selecione a Semana Epidemiológica', df_serie_temporal['Semana epidemiológica'].unique())

    # # Filtro por faixa etária e sexo
    # sexo = st.sidebar.selectbox('Sexo', df_dados_virus['sexo'].unique())
    # faixa_etaria = st.sidebar.multiselect('Faixa Etária', ['< 2 anos', '0-4 anos', '5-9 anos', '10-19 anos', '20-29 anos', '30-39 anos', '40-49 anos', '50-59 anos', '60+ anos'])

    # # Filtrando os dados
    # df_filtrado = df_serie_temporal[(df_serie_temporal['Unidade da Federação'] == uf_selecionada) & 
    #                                 (df_serie_temporal['Ano epidemiológico'] == ano_epidemiologico) & 
    #                                 (df_serie_temporal['Semana epidemiológica'] == semana_epidemiologica)]

    # # Exibição dos dados filtrados
    # st.write("Dados Filtrados:")
    # st.dataframe(df_filtrado)

    
    # # Gráfico de casos ao longo do tempo
    # fig_casos = px.line(df_filtrado, x='Semana epidemiológica', y='Casos semanais reportados até a última atualização', title='Casos Semanais Reportados')
    # st.plotly_chart(fig_casos)

    # # Mapas interativos
    # st.write("Mapa Interativo:")
    # fig_mapa = px.scatter_mapbox(df_municipios, lat="latitude", lon="longitude", hover_name="municipio",
    #                             hover_data=["Populacao", "DS_NOMEPAD_macsaud"],
    #                             color_discrete_sequence=["fuchsia"], zoom=3, height=400)
    # fig_mapa.update_layout(mapbox_style="open-street-map")
    # fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # st.plotly_chart(fig_mapa)

    # # Comparação de casos entre diferentes períodos
    # st.write("Comparação de Casos entre Períodos:")
    # periodo1 = st.sidebar.selectbox('Selecione o Primeiro Período', df_serie_temporal['Semana epidemiológica'].unique(), key='p1')
    # periodo2 = st.sidebar.selectbox('Selecione o Segundo Período', df_serie_temporal['Semana epidemiológica'].unique(), key='p2')

    # df_comparacao = df_serie_temporal[df_serie_temporal['Semana epidemiológica'].isin([periodo1, periodo2])]
    # fig_comparacao = px.bar(df_comparacao, x='Semana epidemiológica', y='Casos semanais reportados até a última atualização', color='Semana epidemiológica',
    #                         barmode='group', title='Comparação de Casos entre Períodos')
    # st.plotly_chart(fig_comparacao)
    
    

    # # Função para carregar os datasets
    # @st.cache_data
    # def load_data(file_path):
    #     return pd.read_csv(file_path)

    # # Carregar os dados
    # estados_estimativas_fx_etaria = load_data('data_sus\infogripe-master\Dados\InfoGripe\estados_serie_estimativas_fx_etaria_sem_filtro_febre.csv')
    # capitais_tendencia = load_data('data_sus/infogripe-master/Dados/InfoGripe/capitais_serie_estimativas_tendencia_sem_filtro_febre.csv')
    # casos_semanais_virus = load_data('data_sus/infogripe-master/Dados/InfoGripe/casos_semanais_fx_etaria_virus_sem_filtro_febre.csv')
    # obitos_virus = load_data('data_sus/infogripe-master/Dados/InfoGripe/obitos_semanais_fx_etaria_virus_sem_filtro_febre.csv')

    # # Sidebar para Filtros
    # st.sidebar.header("Filtros")
    # selected_state = st.sidebar.selectbox("Selecione o Estado", estados_estimativas_fx_etaria["DS_UF_SIGLA"].unique())
    # selected_epiweek = st.sidebar.slider("Semana Epidemiológica", min_value=int(estados_estimativas_fx_etaria['epiweek'].min()), 
    #                                     max_value=int(estados_estimativas_fx_etaria['epiweek'].max()), value=(1, 52))

    # # Filtrando os dados com base nos filtros escolhidos
    # filtered_data = estados_estimativas_fx_etaria[
    #     (estados_estimativas_fx_etaria["DS_UF_SIGLA"] == selected_state) & 
    #     (estados_estimativas_fx_etaria["epiweek"].between(selected_epiweek[0], selected_epiweek[1]))
    # ]

    # # Exibir uma tabela com os dados filtrados
    # st.subheader("Dados Filtrados")
    # st.dataframe(filtered_data)

    # # Gráfico de Tendências (Plotly)
    # st.subheader("Tendência de Casos Estimados")
    # fig = px.line(
    #     filtered_data,
    #     x='epiweek',
    #     y='mediana_da_estimativa',
    #     labels={'mediana_da_estimativa': 'Casos Estimados'},
    #     title=f"Tendência de Casos no Estado {selected_state}"
    # )
    # st.plotly_chart(fig)

    # # Gráfico de Barras para Distribuição por Faixa Etária
    # st.subheader("Distribuição de Casos por Faixa Etária")
    # fig_fx = px.bar(
    #     filtered_data,
    #     x='fx_etaria',
    #     y='casos_notificados',
    #     title="Casos Notificados por Faixa Etária",
    #     labels={'fx_etaria': 'Faixa Etária', 'casos_notificados': 'Casos Notificados'}
    # )
    # st.plotly_chart(fig_fx)

    # # Mapa Interativo com Pydeck
    # st.subheader("Mapa de Distribuição de Casos")
    # st.map(filtered_data[['latitude', 'longitude']]) 

    # # Exibir Métricas de Casos e Óbitos
    # st.subheader("Métricas de Casos e Óbitos")
    # total_cases = filtered_data["casos_notificados"].sum()
    # st.metric(label="Total de Casos Notificados", value=total_cases)

    # total_deaths = obitos_virus[(obitos_virus['SG_UF_NOT'] == selected_state)]['SRAG'].sum()
    # st.metric(label="Total de Óbitos por SRAG", value=total_deaths)

    # # Abas para Visualizar diferentes aspectos
    # tab1, tab2, tab3 = st.tabs(["Estimativas por Estado", "Tendências de Capitais", "Casos e Óbitos por Faixa Etária"])

    # # Aba 1 - Estimativas por Estado
    # with tab1:
    #     st.write("Dados de Estimativas por Estado")
    #     st.dataframe(filtered_data)

    # # Aba 2 - Tendências de Capitais
    # with tab2:
    #     st.write("Dados de Tendência de Capitais")
    #     st.dataframe(capitais_tendencia)

    # # Aba 3 - Casos e Óbitos por Faixa Etária
    # with tab3:
    #     st.write("Dados de Casos e Óbitos por Faixa Etária")
    #     st.dataframe(casos_semanais_virus)

    # # Filtros por Datas
    # st.sidebar.date_input("Selecione a Data", [])



if diase == 'Dengues':
    
    # Funções para interagir com FastAPI
    def get_item(municipio):
        response = requests.get(f"http://127.0.0.1:8000/items/{municipio}")
        return response.json()

    def create_item(item):
        response = requests.post("http://127.0.0.1:8000/items", json=item)
        return response.json()

    def update_item(municipio, item):
        response = requests.put(f"http://127.0.0.1:8000/items/{municipio}", json=item)
        return response.json()

    def delete_item(municipio):
        response = requests.delete(f"http://127.0.0.1:8000/items/{municipio}")
        return response.json()

        
    # Função para carregar o dataset com cache
    @st.cache_data
    def carregar_dataset():
        try:
            df = pd.read_csv('data_sus/df_dengue_2023_2024.csv')
        except FileNotFoundError:
            st.error("Arquivo não encontrado.")
            df = pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
        return df

    # Função para definir a cor com base no índice de risco
    def definir_cor(risco):
        if risco > 7:
            return [255, 0, 0, 160]  # Vermelho (risco alto)
        elif 1 < risco <= 6.99:
            return [255, 255, 0, 160]  # Amarelo (risco moderado)
        else:
            return [0, 255, 0, 160]  # Verde (risco baixo)

    # Função para plotar o mapa interativo
    def plotar_mapa(df):
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[longitude, latitude]',
            get_radius='3000',
            get_fill_color='cor',
            pickable=True,
            auto_highlight=True,
        )
        view_state = pdk.ViewState(
            latitude=df['latitude'].mean(),
            longitude=df['longitude'].mean(),
            zoom=6
        )
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={
            'html': '<b>Município:</b> {municipio}<br><b>Casos:</b> {casos}<br><b>Est. Casos:</b> {casos_est}<br><b>Disseminação:</b> {disseminação}<br><b>Temperatura:</b> {tempmed}°C<br><b>Umidade:</b> {umidmed}%',
            'style': {'color': 'white'}
        })
        st.pydeck_chart(r)

    # Função para plotar gráficos interativos
    def plotar_graficos(df_municipio, df_min_max, municipio_usuario, estado_usuario):
        fig = go.Figure()
        # Adiciona a linha do município selecionado
        fig.add_trace(go.Scatter(x=df_municipio['data_week'], y=df_municipio['casos'],
                                mode='lines+markers', name=f'{municipio_usuario} - Casos', line=dict(color='red', width=4)))
        # Linha dos casos mínimos do estado
        fig.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('casos', 'min')],
                                mode='lines', name='Casos Mínimos (Estado)', line=dict(color='green', dash='dash')))
        # Linha dos casos máximos do estado
        fig.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('casos', 'max')],
                                mode='lines', name='Casos Máximos (Estado)', line=dict(color='blue', dash='dash')))
        # Configurações do layout
        fig.update_layout(title=f'Comparação de Incidência de Casos {estado_usuario}', xaxis_title='Semana',
                        yaxis_title='Número de Casos', legend_title='Municípios')
        st.plotly_chart(fig)


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



    # Configurações para o Selenium com Firefox
    def setup_selenium():
        options = Options()
        options.headless = True 
        driver = webdriver.Firefox(options=options)
        return driver

    # Função para filtrar notícias relacionadas à dengue
    def is_dengue_related(title, description):
        keywords = ['dengue', 'zika', 'chikungunya', 'mosquito']
        return any(keyword.lower() in title.lower() or keyword.lower() in description.lower() for keyword in keywords)

    # Função para organizar visualização das notícias
    def show_news_column(news_data, column_title):
        with st.expander(column_title):
            for news in news_data:
                st.markdown(f"**[{news['title']}]({news['link']})**")
                st.write(news['date'])
                st.write(news['description'])


    # Função para fazer scraping da página
    def scrape_dengue_info():
        driver = setup_selenium()
        url = 'https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/d/dengue'
        
        # Acessar a página
        driver.get(url)
        
        # Esperar que a página carregue completamente
        time.sleep(5)  # Ajuste esse tempo de espera conforme necessário

        # Encontrar todos os parágrafos com informações
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        
        # Extrair o texto e armazenar em uma lista
        dengue_info = [p.text for p in paragraphs]
        
        # Fechar o driver
        driver.quit()
        
        # Retornar as informações coletadas
        return dengue_info

    # Função para fazer scraping da CNN (notícias gerais)
    def scrape_cnn_news():
        driver = setup_selenium()
        url = 'https://www.cnnbrasil.com.br/tudo-sobre/dengue/'
        driver.get(url)
        time.sleep(5)  # Ajuste esse tempo de espera conforme necessário
        
        news_elements = driver.find_elements(By.CLASS_NAME, 'home__list__item')
        news_data = []
        for element in news_elements:
            title = element.find_element(By.TAG_NAME, 'h3').text
            link = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            date = element.find_element(By.CLASS_NAME, 'home__title__date').text
            description = element.find_element(By.TAG_NAME, 'a').get_attribute('title')
            if is_dengue_related(title, description):
                news_data.append({'title': title, 'link': link, 'date': date, 'description': description})
        
        driver.quit()
        return news_data

    # Função para fazer scraping das notícias do estado e município (G1)
    def scrape_g1_news(state, city=None):
        driver = setup_selenium()
        search_query = f"dengue {state}" + (f" {city}" if city else "")
        url = f"https://g1.globo.com/busca/?q={search_query}"
        driver.get(url)
        time.sleep(5)
        
        news_elements = driver.find_elements(By.CLASS_NAME, 'widget--info')
        news_data = []
        for element in news_elements:
            title = element.find_element(By.CLASS_NAME, 'widget--info__title').text
            link = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            description = element.find_element(By.CLASS_NAME, 'widget--info__description').text
            date = element.find_element(By.CLASS_NAME, 'widget--info__meta').text
            if is_dengue_related(title, description):
                news_data.append({'title': title, 'link': link, 'date': date, 'description': description})
        
        driver.quit()
        return news_data

    # Função para exibir as notícias no Streamlit
    def display_news(news, title):
        st.write(f"### {title}")
        for item in news:
            st.write(f"**{item['title']}**")
            st.write(f"[Link]({item['link']})")
            st.write(f"*Publicado em: {item['date']}*")
            st.write("---")
    # Carregar o dataset
    df = carregar_dataset()

    # Se o dataset foi carregado corretamente
    if not df.empty:
        # Aba de seleção de funcionalidades
        abas = st.tabs(["Análise por Município", "Informações e Notícias", "Dados Epidemiológicos", "API - Opção em desenvolvimento"])

        # Aba 1: Análise por Município
        with abas[0]:
            st.title("🦟Análise da Situação do Município - Dengue🦟")
            
            # Conversão e tratamento dos dados
            df['data_week'] = pd.to_datetime(df['data_week'], errors='coerce')
            municipio_usuario = st.selectbox("Selecione seu município", sorted(df['municipio'].unique()))
            estado_usuario = df[df['municipio'] == municipio_usuario]['estado'].values[0]
            df_estado = df[df['estado'] == estado_usuario]
            data_maxima = df_estado['data_week'].max()
            filtro_periodo = st.radio("Filtrar por", ('Último Mês', 'Último Ano'))
            
            # Definir o período de filtragem
            data_inicial = data_maxima - pd.DateOffset(months=1) if filtro_periodo == 'Último Mês' else data_maxima - pd.DateOffset(years=1)
            df_filtrado = df_estado[(df_estado['data_week'] >= data_inicial) & (df_estado['data_week'] <= data_maxima)].copy()

            
            # Calcular risco e aplicar cor
            df_filtrado.loc[:, 'risco_dengue'] = df_filtrado['casos_est'] * 0.1 + df_filtrado['casos'] * 0.3 + df_filtrado['incidência_100khab'] * 0.1 + df_filtrado['disseminação'] * 5
            df_filtrado.loc[:, 'cor'] = df_filtrado['risco_dengue'].apply(definir_cor)
            
            # Mostrar mapa interativo
            st.write("O mapa corresponde à opção de um mês.")
            plotar_mapa(df_filtrado)
            
            # Criar e exibir gráficos
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

            df_municipio_selecionado = df_filtrado[df_filtrado['municipio'] == municipio_usuario]
            plotar_graficos(df_municipio_selecionado, df_min_max, municipio_usuario, estado_usuario)

        # Aba 2: Informações e Sintomas
        with abas[1]:

            # Exibir as notícias no Streamlit
            st.title("🔍Notícias e informações sobre Dengue🔍")

            # Infomação
            if st.button("Informações sobre Dengue"):
                try:
                    informacoes = scrape_dengue_info()
                    
                    # Exibir as informações no Streamlit
                    for info in informacoes:
                        st.write(info)
            
                except Exception as e:
                    st.error(f"Erro ao carregar informações: {e}") 
                        

            # CNN: Notícias gerais
            if st.button("Carregar notícias gerais"):
                try:
                    cnn_news = scrape_cnn_news()
                    if cnn_news:
                        show_news_column(cnn_news, "Notícias Gerais")
                    else:
                        st.write("Nenhuma notícia encontrada.")
                except Exception as e:
                    st.error(f"Erro ao carregar notícias gerais: {e}")



            if st.button("Carregar notícias por estado e município"):
                try:
                    state_news = scrape_g1_news(estado_usuario)
                    city_news = scrape_g1_news(estado_usuario, municipio_usuario) if municipio_usuario else []
                    
                    if state_news:
                        show_news_column(state_news, f"Notícias no estado: {estado_usuario}")
                    else:
                        st.write(f"Nenhuma notícia encontrada para o estado {estado_usuario}.")
                    
                    if city_news:
                        show_news_column(city_news, f"Notícias no município: {municipio_usuario}")
                    elif municipio_usuario:
                        st.write(f"Nenhuma notícia encontrada para o município {municipio_usuario}.")
                
                except Exception as e:
                    st.error(f"Erro ao carregar notícias do estado ou município: {e}")


        # Aba 3: Dados Epidemiológicos
        with abas[2]:
            
            st.title(f"📊Dados Epidemiológicos📊")
            # Incorporar o Power BI no Streamlit
            st.components.v1.iframe("https://app.powerbi.com/view?r=eyJrIjoiYzQyOTI4M2ItZTQwMC00ODg4LWJiNTQtODc5MzljNWIzYzg3IiwidCI6IjlhNTU0YWQzLWI1MmItNDg2Mi1hMzZmLTg0ZDg5MWU1YzcwNSJ9&pageName=ReportSectionbd7616200acb303571fc", height=600)


            st.write('Here you need upload the csv with data from 2010 to 2024. \nHas customizable graphics and an interactive map. \n Google Drive Data link: https://drive.google.com/drive/folders/19OGg_d3S9L6wc99I3FZxc5Mn9Ba-jXos?usp=drive_link \n DropBox Data Link: https://www.dropbox.com/scl/fo/wuwb1zpcxuvvlnyfrkcpf/AIBXL31_YW6QpjbWKyG-v2s?rlkey=8vzsj4lddvx5sh61ce8hl2df1&st=zvb71bzb&dl=0')

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
            
                # Multiselect para selecionar as colunas desajas
                selected_columns = st.multiselect("Selecione as colunas. :)", df.columns.tolist(), default=df.columns.tolist())

                # Multiselect para selecionar os estados, ordenados alfabeticamente
                selected_estado = st.multiselect(" Selecione os estados.", sorted(df['estado'].astype(str).unique()))
                df_filtrado = df[(df['estado'].isin(selected_estado))]

                # Multiselect para selecionar os municípios, ordenados alfabeticamente
                selected_municipio = st.multiselect("Selecione os municípios.", sorted(df_filtrado['municipio'].astype(str).unique()), default=sorted(df_filtrado['municipio'].astype(str).unique()))
                df_filtrado = df_filtrado[(df_filtrado['municipio'].isin(selected_municipio))]
                st.write('Dados filtrados:')
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

            else:
                st.write('Nenhum arquivo foi carregado.')

        #API
        with abas[3]:
            # Streamlit UI
            st.title("Gerenciar Dados de Dengue com FastAPI")

            # Entrada de dados
            municipio = st.text_input("Digite o nome do município")

            # Buscar dados do município
            if st.button("Buscar Município"):
                item = get_item(municipio)
                st.write(item)

            # Adicionar novo município
            st.subheader("Adicionar novo município")
            new_municipio = st.text_input("Nome do novo município")
            casos_est = st.number_input("Estimativa de casos", min_value=0)
            casos_est_min = st.number_input("Mínimo de estimativa de casos", min_value=0)
            casos_est_max = st.number_input("Máximo de estimativa de casos", min_value=0)
            casos = st.number_input("Número de casos", min_value=0)
            proba_disse = st.number_input("Probabilidade de disseminação > 1", min_value=0.0)
            incidência_100khab = st.number_input("Incidência por 100k habitantes", min_value=0.0)
            disseminação = st.number_input("Disseminação", min_value=0.0)
            população = st.number_input("População", min_value=0)
            tempmin = st.number_input("Temperatura mínima", min_value=0.0)
            umidmax = st.number_input("Umidade máxima", min_value=0)
            umidmed = st.number_input("Umidade média", min_value=0)
            umidmin = st.number_input("Umidade mínima", min_value=0)
            tempmed = st.number_input("Temperatura média", min_value=0.0)
            tempmax = st.number_input("Temperatura máxima", min_value=0.0)
            estado = st.text_input("Estado")
            longitude = st.number_input("Longitude", format="%.5f")
            latitude = st.number_input("Latitude", format="%.5f")
            data_week = st.date_input("Data da semana")

            # Botão para adicionar
            if st.button("Adicionar"):
                item = {
                    "municipio": new_municipio,
                    "casos_est": casos_est,
                    "casos_est_min": casos_est_min,
                    "casos_est_max": casos_est_max,
                    "casos": casos,
                    "proba_disse": proba_disse,
                    "incidência_100khab": incidência_100khab,
                    "disseminação": disseminação,
                    "população": população,
                    "tempmin": tempmin,
                    "umidmax": umidmax,
                    "umidmed": umidmed,
                    "umidmin": umidmin,
                    "tempmed": tempmed,
                    "tempmax": tempmax,
                    "estado": estado,
                    "longitude": longitude,
                    "latitude": latitude,
                    "data_week": str(data_week)
                }
                response = create_item(item)
                st.write(response)

            # Atualizar município
            st.subheader("Atualizar dados do município")
            if st.button("Atualizar Município"):
                item = {
                    "municipio": municipio,
                    "casos_est": casos_est,
                    "casos_est_min": casos_est_min,
                    "casos_est_max": casos_est_max,
                    "casos": casos,
                    "proba_disse": proba_disse,
                    "incidência_100khab": incidência_100khab,
                    "disseminação": disseminação,
                    "população": população,
                    "tempmin": tempmin,
                    "umidmax": umidmax,
                    "umidmed": umidmed,
                    "umidmin": umidmin,
                    "tempmed": tempmed,
                    "tempmax": tempmax,
                    "estado": estado,
                    "longitude": longitude,
                    "latitude": latitude,
                    "data_week": str(data_week)
                }
                response = update_item(municipio, item)
                st.write(response)

            # Deletar município
            if st.button("Deletar Município"):
                response = delete_item(municipio)
                st.write(response)
