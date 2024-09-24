import os
import pandas as pd

# Função para listar todos os arquivos CSV em um diretório
def listar_arquivos_csv(diretorio):
    return [f for f in os.listdir(diretorio) if f.endswith('.csv')]

# Função para processar e modificar os arquivos CSV
def limpar_linhas_csv(diretorio):
    # Listando todos os arquivos CSV no diretório
    arquivos_csv = listar_arquivos_csv(diretorio)
    
    for arquivo in arquivos_csv:
        # Caminho completo do arquivo
        caminho_arquivo = os.path.join(diretorio, arquivo)
        
        # Lendo o arquivo CSV em um DataFrame 
        df = pd.read_csv(caminho_arquivo)
        # Removendo a primeira coluna (ou qualquer outra coluna específica)
        df.drop(index=7, inplace=True)
        df.drop(index=8, inplace=True)
        df.drop(index=9, inplace=True)
        df.drop(index=10, inplace=True)
        df.drop(index=11, inplace=True)
        df.drop(index=16, inplace=True)
        df.drop(index=17, inplace=True)
        df.drop(index=18, inplace=True)
        df.drop(index=23, inplace=True)
        df.drop(index=24, inplace=True)
        df.drop(index=25, inplace=True)
        df.drop(index=26, inplace=True)
        df.drop(index=27, inplace=True)
        df.drop(index=28, inplace=True)
        # Salvando o DataFrame modificado de volta no arquivo CSV
        df.to_csv(caminho_arquivo, index=False)
        print(f"Arquivo {arquivo} modificado e salvo com novas colunas.")

# Especificando o diretório onde estão os arquivos CSV
diretorio_csv = '..\data_sus\PySUS\infodengue'

# Chamando a função para processar os arquivos CSV
limpar_linhas_csv(diretorio_csv)




# Função para listar todos os arquivos CSV em um diretório
def listar_arquivos_csv(diretorio):
    return [f for f in os.listdir(diretorio) if f.endswith('.csv')]

# Função para processar e modificar os arquivos CSV
def invert_lines_columns(diretorio):
    # Listando todos os arquivos CSV no diretório
    arquivos_csv = listar_arquivos_csv(diretorio)
    
    for arquivo in arquivos_csv:
        # Caminho completo do arquivo
        caminho_arquivo = os.path.join(diretorio, arquivo)
        
        # Lendo o arquivo CSV em um DataFrame sem cabeçalhos
        df = pd.read_csv(caminho_arquivo)
        
        # Primeiro, vamos transpor o DataFrame
        df = df.T

        # Agora, transformar a primeira linha (originalmente a primeira coluna) em cabeçalho
        df.columns = df.iloc[0]  # Define a primeira linha como nomes das colunas

        # Remover a linha que virou o cabeçalho
        df = df[1:].reset_index(drop=True)

        # Salvando o DataFrame modificado de volta no arquivo CSV
        df.to_csv(caminho_arquivo, index=False)
        print(f"Arquivo {arquivo} modificado e salvo com novas colunas.")

# Especificando o diretório onde estão os arquivos CSV
diretorio_csv = '..\data_sus\PySUS\infodengue'

# Chamando a função para processar os arquivos CSV
invert_lines_columns(diretorio_csv)




# Função para listar todos os arquivos CSV em um diretório
def listar_arquivos_csv(diretorio):
    return [f for f in os.listdir(diretorio) if f.endswith('.csv')]

# Função para processar e modificar os arquivos CSV
def orientacao_media(diretorio):
    # Listando todos os arquivos CSV no diretório
    arquivos_csv = listar_arquivos_csv(diretorio)
    
    for arquivo in arquivos_csv:
        # Caminho completo do arquivo
        caminho_arquivo = os.path.join(diretorio, arquivo)
        
        # Lendo o arquivo CSV em um DataFrame
        df = pd.read_csv(caminho_arquivo)
        df = df.sort_values(['data_iniSE'])
        df['tempmin'].fillna(df['tempmin'].median(), inplace=True)
        df['umidmax'].fillna(df['umidmax'].median(), inplace=True)
        df['umidmed'].fillna(df['umidmed'].median(), inplace=True)
        df['umidmin'].fillna(df['umidmin'].median(), inplace=True)
        df['tempmed'].fillna(df['tempmed'].median(), inplace=True)
        df['tempmax'].fillna(df['tempmax'].median(), inplace=True)
        


        # Salvando o DataFrame modificado de volta no arquivo CSV
        df.to_csv(caminho_arquivo, index=False)
        print(f"Arquivo {arquivo} modificado e salvo com novas colunas.")

# Especificando o diretório onde estão os arquivos CSV
diretorio_csv = '..\data_sus\PySUS\infodengue'

# Chamando a função para processar os arquivos CSV
orientacao_media(diretorio_csv)


