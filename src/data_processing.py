import pandas as pd
import auto_graphs
import auto_maps
import seaborn as sns

# Functions

def get_moradores(areas_fichas_casas, a_risco, grau_risco):
    if grau_risco in areas_fichas_casas[(areas_fichas_casas['RG_RISCO'] == a_risco)]['CLASS_AREA'].unique():
        moradores_resp_risco = areas_fichas_casas[(areas_fichas_casas['RG_RISCO'] == a_risco)].groupby(['CLASS_AREA','ENTREVISTA_FICHA'], dropna=False)['QTDE_MORADORES_CSA'].sum()
        entrevistas_resp_risco = areas_fichas_casas[(areas_fichas_casas['RG_RISCO'] == a_risco)].groupby(['CLASS_AREA','ENTREVISTA_FICHA'], dropna=False)['ID_FICHA'].count()
        media_moradores_total = moradores_resp_risco.loc[:, 'SIM'].sum()/entrevistas_resp_risco.loc[:, 'SIM'].sum()
        if (grau_risco, 'SIM') in moradores_resp_risco.index:
            moradores_sim = moradores_resp_risco.loc[grau_risco, 'SIM']
            entrevista_sim = entrevistas_resp_risco.loc[grau_risco, 'SIM']
            media_moradores = moradores_sim/entrevista_sim
        else:
            moradores_sim = 0
            media_moradores = media_moradores_total
        if (grau_risco, 'NÃO') in entrevistas_resp_risco:
            entrevista_nao = entrevistas_resp_risco.loc[grau_risco, 'NÃO']
        else:
            entrevista_nao = 0
        total_moradores = round(media_moradores * entrevista_nao) + moradores_sim

    else:
        total_moradores = 0
    return total_moradores

def get_familias(areas_fichas_casas, a_risco):
    
    familias_resp_risco = areas_fichas_casas[(areas_fichas_casas['RG_RISCO'] == a_risco)].groupby(['ENTREVISTA_FICHA'], dropna=False)['QTDE_FAMILIAS_CSA'].sum()
    entrevistas_resp_risco = areas_fichas_casas[(areas_fichas_casas['RG_RISCO'] == a_risco)].groupby(['ENTREVISTA_FICHA'], dropna=False)['ID_FICHA'].count()
    familias_sim = familias_resp_risco.loc['SIM']
    entrevista_sim = entrevistas_resp_risco.loc['SIM']
    entrevista_nao = entrevistas_resp_risco.loc['NÃO']
    media_familias = familias_sim/entrevista_sim
    total_familias = round(media_familias * entrevista_nao) + familias_sim

    return total_familias

def get_moradias(dados_risco_moradias, grau_risco):
    
    if grau_risco in dados_risco_moradias.iloc[:,0].values:
        moradias_risco = dados_risco_moradias[dados_risco_moradias.iloc[:,0] == grau_risco].iat[0,1]
    else:
        moradias_risco = 0
    return moradias_risco

def select_categories(df):
    df = df.sort_values(ascending=False)
    if df.iloc[0]/df.sum()>0.8:
        cat = [df.index[0]]
    else:
        cat = df.index[:2]
    
    return cat

# Data to receive from appex

nome_area_risco = 'Morro da Lua'
sigla_area = 'CL-33'

gerar_graficos = True
gerar_mapas = True


area_cadastro = pd.read_excel("/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/apex_tables/area_cadastro-2.xlsx")
casa = pd.read_excel("/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/apex_tables/casa.xlsx")
ficha = pd.read_excel("/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/apex_tables/ficha.xlsx")
hierarquia = pd.read_excel("/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/apex_tables/hierarquia.xlsx")
mapa_areas = pd.read_excel("/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/apex_tables/mapa_areas_hidro_geo-2.xlsx")
base_defesa = pd.read_excel("/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/apex_tables/gh_nova_base.xlsx")

# fixed images
logo_fdte = '/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/html_outputs/images/logo_fdte.png'
logo_sp = '/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/html_outputs/images/logo_sp.png'

# path to save images
save_images = '/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/html_outputs/images'

colours = pd.Series({'R1':'#4FC26A','R2':'#F0E113','R3':'#FF8801','R4':'#BF243C'})
colours.name = 'colours'

nome_area = nome_area_risco.upper()

# processing tables
dados_fichas_areas = ficha.merge(area_cadastro,left_on='ID_AREA_FICHA', right_on='ID_CAD_AREA') # juntar dados das areas associadas as fichas
areas_fichas_casas = dados_fichas_areas.merge(casa, right_on='ID_CSA', left_on='ID_CSA_FICHA')
areas_fichas_casas = areas_fichas_casas.replace([r'\s*SIM\s*',r'\s*N[AÃ]O\s*'], ['SIM', 'NÃO'], regex=True)

# selecting data from specific area
dados_fichas_uma_area = dados_fichas_areas[dados_fichas_areas['RG_RISCO'] == nome_area]
mapa_uma_area = mapa_areas[mapa_areas['RHD_NOME']==nome_area]

############################################################################################
# MAPS

# Get data for maps of area
new_gdf = auto_maps.process_map_data(mapa_uma_area)
geometria_fichas = dados_fichas_areas.merge(new_gdf, left_on='SETOR', right_on='RHD_SETOR') #todas as fichas
# Crianças
df_area = areas_fichas_casas[areas_fichas_casas['RG_RISCO']==nome_area]
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
mapa_setores = auto_maps.generate_mapa_setores(new_gdf, f'{save_images}/mapa_setores', regenerate=gerar_mapas)
mapa_moradias = auto_maps.generate_points_mapa(new_gdf, geometria_fichas, f'{save_images}/mapa_moradias', regenerate=gerar_mapas)
mapa_criancas = auto_maps.generate_points_mapa(new_gdf, geometria_criancas, f'{save_images}/mapa_criancas', icon='child', regenerate=gerar_mapas)
mapa_idosos = auto_maps.generate_points_mapa(new_gdf, geometria_idoso, f'{save_images}/mapa_idosos', icon='old', regenerate=gerar_mapas)
mapa_pcds = auto_maps.generate_points_mapa(new_gdf, geometria_pcds, f'{save_images}/mapa_pcds', icon='pcd', regenerate=gerar_mapas)
mapa_problemas = auto_maps.generate_points_mapa(new_gdf, geometria_probl, f'{save_images}/mapa_probl', icon='probl', regenerate=gerar_mapas)
# mapa_acabadas = auto_maps.generate_points_mapa(new_gdf, geometria_acab, f'{save_images}/mapa_acab', icon='acab', regenerate=gerar_mapas)
# mapa_pavimentos = auto_maps.generate_points_mapa(new_gdf, geometria_pavmto, f'{save_images}/mapa_pavimentos', icon='pav', regenerate=gerar_mapas)

################################################################################################
# GRAPHS

areas_fichas_casas_uma_area = areas_fichas_casas[areas_fichas_casas['RG_RISCO'] == nome_area]
areas_fichas_casas_uma_area = areas_fichas_casas_uma_area.fillna('NÃO DISPONÍVEL')
# dados_fichas_uma_area = dados_fichas_uma_area.fillna('NÃO DISPONÍVEL')

# Get data for Moradias x Risco
dados_risco_moradias = dados_fichas_uma_area.groupby(["CLASS_AREA"]).count()['ID_FICHA'].reset_index()
dados_risco_moradias.columns = ['Risco','Quantidade de Moradias']
dados_risco_moradias = pd.merge(dados_risco_moradias, colours, left_on='Risco', right_index=True)

# Get data for Moradias x Setor
dados_setor_moradias = dados_fichas_uma_area.groupby(["SETOR"]).count()['ID_FICHA'].reset_index()
dados_setor_moradias.columns = ['Setor','Quantidade de Moradias']

# Get data for Uso dos Imóveis
uso_csa = areas_fichas_casas_uma_area.groupby('USO_CSA', dropna=False)['ID_FICHA'].count()
uso_csa = uso_csa.sort_values(ascending=False)

# Get data for Acabemento das Moradias
acab_csa = areas_fichas_casas_uma_area.groupby('ACAB_CSA', dropna=False)['ID_FICHA'].count()

# Get data for Tipologia Moradias
tipologia_csa = areas_fichas_casas_uma_area.groupby('TIPO_CSA', dropna=False)['ID_FICHA'].count()
tipologia_csa = tipologia_csa.sort_values(ascending=False)

# Get data for Tipo de piso
piso_csa = areas_fichas_casas_uma_area.groupby('PISO_CSA', dropna=False)['ID_FICHA'].count()
piso_csa = piso_csa.sort_values(ascending=False)

# Get data for Tipo de cobertura
telhado_csa = areas_fichas_casas_uma_area.groupby('TELHADO_CSA', dropna=False)['ID_FICHA'].count()
telhado_csa = telhado_csa.sort_values(ascending=False)

#Get data for Riscos estruturais
probl_csa = areas_fichas_casas_uma_area.groupby('PROB_ESTRU_CSA', dropna=False)['ID_FICHA'].count()
probl_csa = probl_csa.sort_values(ascending=False)
# probl_csa.index = [i.replace(' ', '') if not pd.isnull(i) else i for i in probl_csa.index]

# Get data for numero de pavimentos
npavmto_csa = areas_fichas_casas_uma_area.groupby('NPVTO_CSA', dropna=False)['ID_FICHA'].count()
npavmto_csa2 = npavmto_csa.reset_index()
npavmto_csa2.columns = ['Número de pavimentos','Quantidade de Moradias']


grafico_moradias_setor = auto_graphs.graph_setor_moradias(dados_setor_moradias, f'{save_images}/setor_moradias.png', regenerate=gerar_graficos)
grafico_moradias_risco = auto_graphs.graph_risco_moradias(dados_risco_moradias, f'{save_images}/risco_moradias.png', regenerate=gerar_graficos)
grafico_uso_imoveis = auto_graphs.graph_percentages(uso_csa, 'Tipo de uso dos imóveis', f'{save_images}/uso_imoveis.png', regenerate=gerar_graficos)
grafico_tipo_construcao = auto_graphs.graph_percentages(tipologia_csa, 'Tipologia das moradias',f'{save_images}/tipologia_imoveis.png', regenerate=gerar_graficos)
grafico_n_pavimentos = auto_graphs.graph_n_pavimentos(npavmto_csa2, f'{save_images}/pav_imoveis.png', regenerate=gerar_graficos)
grafico_acabamento_moradias = auto_graphs.graph_percentages(acab_csa, 'Nível do acabamento das moradias',f'{save_images}/acab_imoveis.png', regenerate=gerar_graficos)
grafico_pisos = auto_graphs.graph_percentages(piso_csa, 'Tipo de piso', f'{save_images}/tipo_piso.png', regenerate=gerar_graficos)
grafico_cobertura = auto_graphs.graph_percentages(telhado_csa, 'Tipo de cobertura',f'{save_images}/tipo_telhado.png', regenerate=gerar_graficos)
grafico_problemas = auto_graphs.graph_percentages(probl_csa, 'Há riscos estruturais nas moradias?',f'{save_images}/probl_imoveis.png', regenerate=gerar_graficos)

################################################################################################
# OTHER DATA

subprefeitura = hierarquia[hierarquia['NOME'] == nome_area].iat[0,2]
hierarquia_area = hierarquia[hierarquia['NOME'] == nome_area].iat[0,0]
data_censo_inicial = dados_fichas_uma_area['DT_FICHA_DATE'].min().date().strftime('%d/%m/%Y') # ver de onde pegar esse
data_censo_final = dados_fichas_uma_area['DT_FICHA_DATE'].max().date().strftime('%d/%m/%Y') # ver de onde pegar esse

moradias_fdte = dados_fichas_areas[dados_fichas_areas.RG_RISCO == nome_area]['ID_FICHA'].count()
moradias_defesa = base_defesa[base_defesa['area'] == nome_area]['moradias'].iat[0]
moradias_r1 = get_moradias(dados_risco_moradias, 'R1')
moradias_r2 = get_moradias(dados_risco_moradias, 'R2')
moradias_r3 = get_moradias(dados_risco_moradias, 'R3')
moradias_r4 = get_moradias(dados_risco_moradias, 'R4')
moradores_r1 = get_moradores(areas_fichas_casas, nome_area, 'R1')
moradores_r2 = get_moradores(areas_fichas_casas, nome_area, 'R2')
moradores_r3 = get_moradores(areas_fichas_casas, nome_area, 'R3')
moradores_r4 = get_moradores(areas_fichas_casas, nome_area, 'R4')
total_moradores = moradores_r1+moradores_r2+moradores_r3+moradores_r4
total_familias = get_familias(areas_fichas_casas, nome_area)
total_criancas = areas_fichas_casas[(areas_fichas_casas['RG_RISCO'] == nome_area)]['CRIANCA_CSA'].sum()
total_idosos = areas_fichas_casas[(areas_fichas_casas['RG_RISCO'] == nome_area)]['IDOSO_CSA'].sum()
total_pcds = areas_fichas_casas[(areas_fichas_casas['RG_RISCO'] == nome_area)]['PCD_CSA'].sum()
fichas_sem_id = dados_fichas_areas[(dados_fichas_areas['RG_RISCO'] == nome_area)]['ID_ENTREVISTADO_FICHA'].isna().sum() + \
                dados_fichas_areas[(dados_fichas_areas['RG_RISCO'] == nome_area)]['ID_CSA_FICHA'].isna().sum()

# Generating text data
numeros = ['um', 'dois', 'tres', 'quatro']
nome_riscos = ', '.join([s for s in dados_risco_moradias['Risco'][:-1]])+' e '+list(dados_risco_moradias['Risco'])[-1]

value_change_moradias = (moradias_fdte/moradias_defesa-1)*100
if value_change_moradias > 0:
    sign_change_moradias = f'apresentou um aumento de {abs(value_change_moradias):.1f}%'
elif value_change_moradias < 0:
    sign_change_moradias = f'apresentou um decréscimo de {abs(value_change_moradias):.1f}%'
else:
    sign_change_moradias = 'não apresentou mudança'

uso_csa_maioria = ' e '.join(select_categories(uso_csa)).lower()
list_pav = [numeros[int(n)-1] for n in select_categories(npavmto_csa)]
n_pav_maioria = ' ou '.join(list_pav).lower()
palavra = 'pavimentos'
if len(list_pav) == 1 and 'um' in list_pav:
    palavra = palavra[:-1]

tipo_csa_maioria = ' e '.join(select_categories(tipologia_csa)).lower()
telhado_csa_maioria = ' e '.join(select_categories(telhado_csa)).lower()

cols = [c for c in acab_csa.index if not pd.isnull(c) and 'REVESTIDO' in c]
acab_csa_percent = acab_csa[cols].iat[0]/acab_csa.sum()
cols = [c for c in piso_csa.index if not pd.isnull(c) and 'REVESTIDO' in c]
piso_csa_percent = piso_csa[cols].iat[0]/piso_csa.sum()
casa_revestidas = (acab_csa_percent+piso_csa_percent)*100/2

probl_csa_sim = probl_csa['SIM']/probl_csa.sum()*100

texto_carac_area = f"Trata-se de uma área com {numeros[len(dados_risco_moradias)-1]} \
                    classificações de risco ({nome_riscos}), \
                    localizada na subprefeitura {subprefeitura}. \
                    Possui uma média de {(total_moradores/total_familias):.0f} pessoas por família. \
                    O número de moradias da área apresentou um {sign_change_moradias} quando comparado aos relatórios da Defesa Civil.\
                    Os imóveis são em maioria de uso {uso_csa_maioria} de {n_pav_maioria} {palavra}, \
                    feitos de {tipo_csa_maioria} com cobertura de {telhado_csa_maioria} \
                    e aproximadamente {casa_revestidas:.1f}% possuem acabamento em piso e parede. \
                    Quanto a problemas estruturais, {probl_csa_sim:.1f}% das moradias apresentam algum deles \
                    (trincas/rachaduras, afundamento de piso, infiltração de água)."