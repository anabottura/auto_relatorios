import pandas as pd
import auto_graphs
import auto_maps
import requests
from unidecode import unidecode
import math

# Functions

def round_half_up(n, decimals=0):
    multiplier = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier

def select_categories(df):
    df = df.sort_values(ascending=False)
    if df.iloc[0]/df.sum()>0.8:
        cat = [df.index[0]]
    else:
        cat = df.index[:2]
    
    return cat

def get_apex_data(url):
    r = requests.get(url)
    json = r.json()
    return pd.DataFrame(json['items'])

def process_data(nome_area_risco, sigla_area):

    nome_area = unidecode(nome_area_risco.upper())
    
    fator_telhados = {'R1':2.05, 'R2':1.55, 'R3':1.0, 'R4':1.0}
    
    gerar_graficos = True
    gerar_mapas = True
    
    # Data to receive from appex

    url_area = f'https://uzu2spnwitelgca-db202004101957.adb.sa-saopaulo-1.oraclecloudapps.com/ords/areas_risco/Relatorios_dem/area?nome_var={nome_area}&sigla_var={sigla_area}'
    url_ficha = f'https://uzu2spnwitelgca-db202004101957.adb.sa-saopaulo-1.oraclecloudapps.com/ords/areas_risco/Relatorios_dem/fichas?nome_var={nome_area}&sigla_var={sigla_area}'
    url_telhados = f'https://uzu2spnwitelgca-db202004101957.adb.sa-saopaulo-1.oraclecloudapps.com/ords/areas_risco/Relatorios_dem/telhados?nome_var={nome_area}&sigla_var={sigla_area}'
    url_levantamento = f'https://uzu2spnwitelgca-db202004101957.adb.sa-saopaulo-1.oraclecloudapps.com/ords/areas_risco/Relatorios_dem/levantamento?nome_var={nome_area}&sigla_var={sigla_area}'
    
    mapa_uma_area = get_apex_data(url_area)
    mapa_uma_area.columns = [col.upper() for col in mapa_uma_area.columns]
    dados_fichas_uma_area = get_apex_data(url_ficha)
    dados_fichas_uma_area.columns = [col.upper() for col in dados_fichas_uma_area.columns]
    telhados = get_apex_data(url_telhados)
    levantamento = get_apex_data(url_levantamento)
    
    
    if mapa_uma_area.empty | dados_fichas_uma_area.empty:
        print("Dados não encontrados no sistema para geração do relatório.")
        return {}, {}, {}
    
    if telhados.empty:
        print("Dados de estimativa de telhados não encontrados no sistema.")
    else:
        telhados.columns = ['ID_FICHA', 'RHD_NOME', 'RHD_SIGLA', 'SETOR', 'CLASS_AREA', 'GPS_LAT_FICHA', 'GPS_LONG_FICHA', 'ORIGEM']
        telhados['CLASS_AREA'] = telhados['CLASS_AREA'].str.upper()
        telhados['ID_FICHA'] = telhados['ID_FICHA'] + 10000000 # pode ser que precise mudar
    
    
    # path to save images
    save_images = '/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/html_outputs/images'

    colours = pd.Series({'R1':'#4FC26A','R2':'#F0E113','R3':'#FF8801','R4':'#BF243C'})
    colours.name = 'colours'
    colours.index.name = 'grau_risco'

    dados_fichas_uma_area = dados_fichas_uma_area.replace([r'\s*SIM\s*',r'\s*N[AÃ]O\s*'], ['SIM', 'NÃO'], regex=True)

    ############################################################################################
    # MAPS

    # Get data for maps of area
    new_gdf = auto_maps.process_map_data(mapa_uma_area)
    
    if telhados.empty:
        dados_todas_fichas = dados_fichas_uma_area
    else:
        dados_todas_fichas = pd.concat([dados_fichas_uma_area, telhados])
    
    geometria_fichas = dados_todas_fichas.merge(new_gdf, left_on='SETOR', right_on='RHD_SETOR') #todas as fichas
    # Crianças
    df_area = dados_fichas_uma_area
    df_criancas_area = df_area[(~df_area['CRIANCA_CSA'].isna()) & (df_area['CRIANCA_CSA']!=0)]
    geometria_criancas = df_criancas_area.merge(new_gdf[['COR', 'RHD_SETOR']], left_on='SETOR', right_on='RHD_SETOR')
    # Idosos
    df_idoso_area = df_area[(~df_area['IDOSO_CSA'].isna()) & (df_area['IDOSO_CSA']!=0)]
    geometria_idoso = df_idoso_area.merge(new_gdf[['COR', 'RHD_SETOR']], left_on='SETOR', right_on='RHD_SETOR')
    # PCDs
    df_pcds_area = df_area[(~df_area['PCD_CSA'].isna()) & (df_area['PCD_CSA']!=0)]
    geometria_pcds = df_pcds_area.merge(new_gdf[['COR', 'RHD_SETOR']], left_on='SETOR', right_on='RHD_SETOR')
    # Problemas estruturais
    df_probl_area = df_area[df_area['PROB_ESTRU_CSA'] == 'SIM']
    geometria_probl = df_probl_area.merge(new_gdf[['COR', 'RHD_SETOR']], left_on='SETOR', right_on='RHD_SETOR')
    # # Moradias acabadas
    # df_acab_area = df_area[df_area['ACAB_CSA'].str.contains('REVESTIDO', na=False)]
    # geometria_acab = df_acab_area.merge(new_gdf[['COR', 'RHD_SETOR']], left_on='SETOR', right_on='RHD_SETOR')
    # # Pavimentos
    # df_pav_area = df_area[(~df_area['NPVTO_CSA'].isna()) & (df_area['NPVTO_CSA']!=0)]
    # geometria_pavmto = df_pav_area.merge(new_gdf[['COR', 'RHD_SETOR']], left_on='SETOR', right_on='RHD_SETOR')

    # # get mapas
    mapas = {}
    mapas['setores'] = auto_maps.generate_mapa_setores(new_gdf, f'{save_images}/mapa_setores', regenerate=gerar_mapas)
    mapas['moradias'] = auto_maps.generate_points_mapa(new_gdf, geometria_fichas, f'{save_images}/mapa_moradias', regenerate=gerar_mapas)
    mapas['criancas'] = auto_maps.generate_points_mapa(new_gdf, geometria_criancas, f'{save_images}/mapa_criancas', icon='child', regenerate=gerar_mapas)
    mapas['idosos'] = auto_maps.generate_points_mapa(new_gdf, geometria_idoso, f'{save_images}/mapa_idosos', icon='old', regenerate=gerar_mapas)
    mapas['pcds'] = auto_maps.generate_points_mapa(new_gdf, geometria_pcds, f'{save_images}/mapa_pcds', icon='pcd', regenerate=gerar_mapas)
    mapas['problemas'] = auto_maps.generate_points_mapa(new_gdf, geometria_probl, f'{save_images}/mapa_probl', icon='probl', regenerate=gerar_mapas)
    # mapa_acabadas = auto_maps.generate_points_mapa(new_gdf, geometria_acab, f'{save_images}/mapa_acab', icon='acab', regenerate=gerar_mapas)
    # mapa_pavimentos = auto_maps.generate_points_mapa(new_gdf, geometria_pavmto, f'{save_images}/mapa_pavimentos', icon='pav', regenerate=gerar_mapas)

    ################################################################################################
    # GRAPHS
    
    # DADOS MORADORES
    
    areas_fichas_casas_uma_area = dados_fichas_uma_area
    areas_fichas_casas_uma_area = areas_fichas_casas_uma_area.fillna('NÃO DISPONÍVEL')
    # dados_fichas_uma_area = dados_fichas_uma_area.fillna('NÃO DISPONÍVEL')
    
    # Get data for Moradias x Setor
    dados_setor_moradias = levantamento[['setor', 'moradias']]
    dados_setor_moradias.columns = ['Setor','Quantidade de Moradias']

    # Get data for Moradias x Risco
    dados_risco_moradias = levantamento[['grau_risco', 'moradias']].groupby('grau_risco').sum().reset_index()
    dados_risco_moradias.columns = ['Risco','Quantidade de Moradias']
    dados_risco_moradias = pd.merge(dados_risco_moradias, colours, left_on='Risco', right_index=True)
    
    # Get data for Moradores x Setor
    dados_setor_moradores = levantamento[['setor', 'moradores']]
    dados_setor_moradores.columns = ['Setor','Quantidade de Moradores']
    dados_setor_moradores['Quantidade de Moradores'] = dados_setor_moradores['Quantidade de Moradores'].astype(int)
    
    # Get data for Moradores x Risco
    risco_df_moradores = pd.merge(colours.reset_index()['grau_risco'], levantamento[['grau_risco', 'moradores']].groupby('grau_risco').sum().reset_index(), how='left')
    risco_df_moradores.fillna(0, inplace=True)
    risco_df_moradores['moradores'] = risco_df_moradores['moradores'].astype(int)
    risco_df_moradores.set_index('grau_risco').to_dict()['moradores']
    
    # Get data for Uso dos Imóveis
    uso_csa = areas_fichas_casas_uma_area.groupby('USO_CSA', dropna=False)['ID_FICHA'].count()
    uso_csa = uso_csa.sort_values(ascending=False)

    # Get data for Acabemento das Moradias
    acab_csa = areas_fichas_casas_uma_area.groupby('ACAB_CSA', dropna=False)['ID_FICHA'].count()
    acab_csa = acab_csa.sort_values(ascending=False)

    # Get data for Tipologia Moradias
    tipologia_csa = areas_fichas_casas_uma_area.groupby('TIPO_CSA', dropna=False)['ID_FICHA'].count()
    tipologia_csa = tipologia_csa.sort_values(ascending=False)

    # Get data for Tipo de piso
    piso_csa = areas_fichas_casas_uma_area.groupby('PISO_CSA', dropna=False)['ID_FICHA'].count()
    piso_csa = piso_csa.sort_values(ascending=False)

    # Get data for Tipo de cobertura
    areas_fichas_casas_uma_area['TELHADO_CSA'] = areas_fichas_casas_uma_area['TELHADO_CSA'].str.upper()
    areas_fichas_casas_uma_area['TELHADO_CSA'] = areas_fichas_casas_uma_area['TELHADO_CSA'].str.strip()
    telhado_csa = areas_fichas_casas_uma_area.groupby('TELHADO_CSA', dropna=False)['ID_FICHA'].count()
    telhado_csa = telhado_csa.sort_values(ascending=False)

    #Get data for Riscos estruturais
    probl_csa = areas_fichas_casas_uma_area.groupby('PROB_ESTRU_CSA', dropna=False)['ID_FICHA'].count()
    probl_csa = probl_csa.sort_values(ascending=False)
    # probl_csa.index = [i.replace(' ', '') if not pd.isnull(i) else i for i in probl_csa.index]

    # Get data for numero de pavimentos
    areas_fichas_casas_uma_area['NPVTO_CSA'] = areas_fichas_casas_uma_area['NPVTO_CSA'].replace(0, 1)
    npavmto_csa = areas_fichas_casas_uma_area.groupby('NPVTO_CSA', dropna=False)['ID_FICHA'].count()
    npavmto_csa2 = npavmto_csa.reset_index()
    npavmto_csa2.columns = ['Número de pavimentos','Quantidade de Moradias']

    graficos = {}
    graficos['moradias_setor'] = auto_graphs.graph_setor_moradias(dados_setor_moradias, f'{save_images}/setor_moradias.png', regenerate=gerar_graficos)
    graficos['moradores_setor'] = auto_graphs.graph_setor_moradores(dados_setor_moradores, f'{save_images}/setor_moradores.png', regenerate=gerar_graficos)
    graficos['moradias_risco'] = auto_graphs.graph_risco_moradias(dados_risco_moradias, f'{save_images}/risco_moradias.png', regenerate=gerar_graficos)
    graficos['uso_imoveis'] = auto_graphs.graph_percentages(uso_csa, 'Tipo de uso dos imóveis', f'{save_images}/uso_imoveis.png', regenerate=gerar_graficos)
    graficos['tipo_construcao'] = auto_graphs.graph_percentages(tipologia_csa, 'Tipologia das moradias',f'{save_images}/tipologia_imoveis.png', regenerate=gerar_graficos)
    graficos['n_pavimentos'] = auto_graphs.graph_n_pavimentos(npavmto_csa2, f'{save_images}/pav_imoveis.png', regenerate=gerar_graficos)
    graficos['acabamento_moradias'] = auto_graphs.graph_percentages(acab_csa, 'Nível do acabamento das moradias',f'{save_images}/acab_imoveis.png', regenerate=gerar_graficos)
    graficos['pisos'] = auto_graphs.graph_percentages(piso_csa, 'Tipo de piso', f'{save_images}/tipo_piso.png', regenerate=gerar_graficos)
    graficos['cobertura'] = auto_graphs.graph_percentages(telhado_csa, 'Tipo de cobertura',f'{save_images}/tipo_telhado.png', regenerate=gerar_graficos)
    graficos['problemas'] = auto_graphs.graph_percentages(probl_csa, 'Há riscos estruturais nas moradias?',f'{save_images}/probl_imoveis.png', regenerate=gerar_graficos)

    ################################################################################################
    # OTHER DATA
    dados = {}
    
    dados['text_r3r4'] = ''
    dados['obs_area'] = ''
    dados['subprefeitura'] = mapa_uma_area.iat[0,10]
    dados['hierarquia_area'] = int(mapa_uma_area.iat[0,9])
    dados['data_censo_inicial'] = pd.to_datetime(dados_fichas_uma_area['DT_FICHA_DATE']).min().date().strftime('%d/%m/%Y') # ver de onde pegar esse
    dados['data_censo_final'] = pd.to_datetime(dados_fichas_uma_area['DT_FICHA_DATE']).max().date().strftime('%d/%m/%Y') # ver de onde pegar esse
    dados['moradias_fdte'] = dados_setor_moradias['Quantidade de Moradias'].sum()
    dados['moradias_defesa'] = mapa_uma_area['N_MORADIAS'].iat[0]
    # dados['total_moradores_1'] = moradores_r1+moradores_r2+moradores_r3+moradores_r4
    dados['total_moradores_2'] = dados_setor_moradores['Quantidade de Moradores'].sum()
    dados['total_familias'] = levantamento['familias'].sum()
    dados['total_criancas'] = levantamento['criancas'].sum()
    dados['total_idosos'] = levantamento['idosos'].sum()
    dados['total_pcds'] = levantamento['pcds'].sum()
    dados['fichas_sem_id'] = dados_fichas_uma_area['ID_ENTREVISTADO_FICHA'].isna().sum() + \
                    dados_fichas_uma_area['ID_CSA_FICHA'].isna().sum()
                    
    ## Gerando tabela com numero de moradores e moradias em cada risco
    risco_df_moradias = dados_risco_moradias.drop(columns='colours')
    risco_df_moradias.columns = ['grau_risco', 'moradias']
    dados['risco_df'] = risco_df_moradores.merge(risco_df_moradias, how='left').set_index('grau_risco')
    dados['risco_df'].columns = ['Habitantes', 'Moradias']
    dados['risco_df'].fillna(0, inplace=True)
    dados['risco_df']['Habitantes'] = dados['risco_df']['Habitantes'].astype(int)
    dados['risco_df'] = dados['risco_df'][['Moradias', 'Habitantes']]
    
    # Generating text data
    numeros = ['um', 'dois', 'tres', 'quatro']
    nome_riscos = ', '.join([s for s in dados_risco_moradias['Risco'][:-1]])+' e '+list(dados_risco_moradias['Risco'])[-1]

    value_change_moradias = (dados['moradias_fdte']/dados['moradias_defesa']-1)*100
    if value_change_moradias > 0:
        sign_change_moradias = f'apresentou um aumento de {abs(value_change_moradias):.1f}%'
    elif value_change_moradias < 0:
        sign_change_moradias = f'apresentou um decréscimo de {abs(value_change_moradias):.1f}%'
    else:
        sign_change_moradias = 'não apresentou mudança'

    uso_csa_maioria = ' e '.join(select_categories(uso_csa)).lower()
    list_pav = [numeros[int(n)-1] for n in select_categories(npavmto_csa) if n != 'NÃO DISPONÍVEL']
    n_pav_maioria = ' ou '.join(list_pav).lower()
    palavra = 'pavimentos'
    if len(list_pav) == 1 and 'um' in list_pav:
        palavra = palavra[:-1]

    tipo_csa_maioria = ' e '.join(select_categories(tipologia_csa)).lower()
    telhado_csa_maioria = ' e '.join(select_categories(telhado_csa)).lower()

    cols = [c for c in acab_csa.index if not pd.isnull(c) and 'REVESTIDO' in c]
    if len(cols) == 0:
        acab_csa_percent = 0
    else:
        acab_csa_percent = acab_csa[cols].iat[0]/acab_csa.sum()
    
    cols = [c for c in piso_csa.index if not pd.isnull(c) and 'REVESTIDO' in c]
    if len(cols) == 0:
        piso_csa_percent = 0
    else:
        piso_csa_percent = piso_csa[cols].iat[0]/piso_csa.sum()
    casa_revestidas = (acab_csa_percent+piso_csa_percent)*100/2

    probl_csa_sim = probl_csa['SIM']/probl_csa.sum()*100

    dados['texto_carac_area'] = f"Trata-se de uma área com {numeros[len(dados_risco_moradias)-1]} \
                        classificações de risco ({nome_riscos}), \
                        localizada na subprefeitura {dados['subprefeitura']}. \
                        Possui uma média de {(dados['total_moradores_2']/dados['total_familias']):.0f} pessoas por família. \
                        O número de moradias da área {sign_change_moradias} quando comparado aos relatórios da Defesa Civil.\
                        Os imóveis são em maioria de uso {uso_csa_maioria} de {n_pav_maioria} {palavra}, \
                        feitos de {tipo_csa_maioria} com cobertura de {telhado_csa_maioria} \
                        e aproximadamente {casa_revestidas:.1f}% possuem acabamento em piso e parede. \
                        Quanto a problemas estruturais, {probl_csa_sim:.1f}% das moradias apresentam algum deles \
                        (trincas/rachaduras, afundamento de piso, infiltração de água)."
    
    return mapas, graficos, dados