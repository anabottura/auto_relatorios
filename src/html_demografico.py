from criar_header import create_header_table
from data_processing import *
import pandas as pd
import htmltools as ht
import pathlib
from math import floor
import pdfkit

# Functions

def mm_to_px(v_mm, dpi=96):
    
    px_per_mm = dpi/25.4
    
    return floor(v_mm*px_per_mm)

def gerar_tabela_risco(risco_df):
    
    estilo_tabela = ht.tags.style(".risco_th {background-color: #AFAFAF; height:8mm} \
                                  .risco_td{font-size:3.5mm; height:5mm} \
                                  .risco_tr:nth-child(even) {background-color: #f2f2f2;} \
                                  .risco_th, .risco_td {\
                                      border:1px solid #dddddd; \
                                      text-align:center; \
                                      padding:2mm;}")
    
    w = mm_to_px(75)
    tabela_risco = ht.tags.table(style=(f" box-sizing: border-box; margin:0")) #width:{w};
    
    tr_h = ht.tags.tr(
        ht.tags.th("Setor", style='width:10mm', class_='risco_th'),
        ht.tags.th("Moradias", class_='risco_th'),
        ht.tags.th("Habitantes",  class_='risco_th')
    )
    
    trs = []
    for risco in range(1,5):
        
        Rrisco = f'R{risco}'
        
        tr = ht.tags.tr(
            ht.tags.td(Rrisco, class_='risco_td'),
            ht.tags.td(f"{risco_df.at[Rrisco, 'Moradias']:.0f}", class_='risco_td'),
            ht.tags.td(f"{risco_df.at[Rrisco, 'Habitantes']:.0f}", class_='risco_td'),
            class_='risco_tr'
        )
        trs.append(tr)
        
    tabela_risco.children = ht.TagList(estilo_tabela, tr_h, trs)
    
    return tabela_risco

def generate_header(nome_area, sigla_area, logo_sp):

    h = mm_to_px(70)
    header = ht.tags.header(style='height:{h}px; padding:5mm; margin:0; box-sizing: border-box; page-break-before:always')
    # Add header content
    header_table = create_header_table(nome_area, sigla_area, logo_sp)
    header_table
    header.children = ht.TagList(header.children, header_table)
    
    return header
    
def generate_footer(logo_fdte):
    
    h = mm_to_px(30)
    footer = ht.tags.footer(style=f'height:{h}px; padding:0; margin:0; box-sizing:border-box;border:0; page-break-after: always;')
    footer_div = ht.div(ht.tags.img(src=pathlib.Path(logo_fdte).as_uri(), alt='logo FDTE', style='height:15mm'), style="text-align: center; margin-bottom: 0; padding: 0")
    footer.children.append(footer_div)
    
    return footer

def generate_page(conteudo, header_footer_info, d_height_mm=297, d_width_mm=210):
    
    d_height_px = mm_to_px(d_height_mm) #px
    d_width_px = mm_to_px(d_width_mm) #px
    
    # Criando o corpo da pagina
    arquivo = ht.tags.html(charset='latin1',style=f'height:{d_height_px}px; padding:0; margin:0; box-sizing: border-box;')
    head = ht.tags.head(ht.tags.meta(charset='utf-8'))
    
    # Criação do estilo geral da página 
    style_P0 = ht.tags.style("*{font-family: Arial, Helvetica, sans-serif;box-sizing: border-box;} \
                             td,tr,table {border:1px solid black;border-collapse:collapse;};")
    arquivo.children = ht.TagList(head,style_P0)
    
    
    corpo = ht.tags.body(class_='classe_body_P0',
                            id='id_body_P0',
                            style=f'height:{d_height_px}px; width:{d_width_px}px; margin:0; padding:0; border:0')
    
    # Criando outros elementos que fazem parte da pagina
    header = generate_header(header_footer_info['nome_area'],
                             header_footer_info['sigla_area'],
                             header_footer_info['logo_sp'])
    h = mm_to_px(197)
    main = ht.div(style=f'height:{h}px; width:100%; padding:0 15mm;  margin:0; box-sizing: border-box; border:1px solid white')
    footer = generate_footer(header_footer_info['logo_fdte'])
    
    main.children = ht.TagList(main.children, conteudo)
    corpo.children = ht.TagList(corpo.children, header, main, footer)
    
    arquivo.children = ht.TagList(arquivo.children,corpo)
    
    return arquivo

def generate_p0(nome_area_risco, sigla_area):
    
    # Gerando conteúdo da página
    
    texto_capa = [ht.tags.h1(ht.tags.strong("PMRR: PLANO MUNICIPAL DE REDUÇÃO DE RISCOS DA CIDADE DE SÃO PAULO"),
                             style="text-align: center; padding-top: 50mm"),
                  ht.tags.h3("RELATÓRIO DE PERFIL DEMOGRÁFICO",
                             style="text-align: center"),
                  ht.tags.p(ht.tags.i(f"Área de Risco: {nome_area_risco}"),
                            style="text-align:right; padding-top:50mm;"),
                  ht.tags.p(ht.tags.i(f"Sigla: {sigla_area}"),
                            style="text-align:right;")]
    
    h = mm_to_px(197)
    capa = ht.div(*texto_capa, style='height:{h}mm; width:100%; padding:0 5mm;  margin:0; border:0; box-sizing: border-box;')
    
    return capa

def generate_p1(nome_area, sigla_area, subprefeitura, hierarquia, data_censo_inicial, data_censo_final, mapa_setores):
    
    # criar estilos
    estilos_pagina = ht.tags.style(".texto_geral {font-size:3.5mm;} h1 {font-size:4mm; padding-top:5mm;}")
    
    # criar conteudo
    dados_iniciais = ht.tags.div(ht.tags.p(ht.tags.strong("Área de Risco: "), f"{nome_area}", class_='texto_geral'),
                                 ht.tags.p(ht.tags.strong("Sigla: "), f"{sigla_area}", class_='texto_geral'),
                                 ht.tags.p(ht.tags.strong("Subprefeitura: "), f"{subprefeitura}", class_='texto_geral'),
                                 ht.tags.p(ht.tags.strong("Hierarquia: "), f"{hierarquia}", class_='texto_geral'),
                                 ht.tags.p(ht.tags.strong("Data do censo: "), f"{data_censo_inicial} a {data_censo_final}", class_='texto_geral'),
                                 style='text-align:right; width:180mm; padding: 0; margin:0; ')
    
    ordered_sections = ht.tags.ol(style='width:180mm; padding: 0 0 0 5mm; margin: 0')
    
    item1 = ht.tags.li(ht.tags.h1("Localização da Área e setores de risco"),
                        ht.tags.div(ht.tags.img(src=pathlib.Path(mapa_setores).as_uri(), alt='Mapa da área', style='width:160mm; height:80mm; frameborder:0'), style='text-align:center;'),
                        style="width:175mm;font-size:4mm;")
    
    item2 = ht.tags.li(ht.tags.h1("Caracterização da área"),
                        ht.tags.p(texto_carac_area, class_='texto_geral', style='text-align:justify; line-height:6mm'),
                        style="width:175mm; font-size:4mm")
    
    ordered_sections.children = ht.TagList(item1, item2)
    
    conteudo = [estilos_pagina, dados_iniciais, ordered_sections]
    
    return conteudo

def generate_p2(risco_df, grafico_moradias_risco):
    
    # criar estilos
    estilos_pagina = ht.tags.style(".texto_geral {font-size:3.5mm;} \
                                   li {font-size:4mm; padding:0; margin:0; box-sizing:border-box;} \
                                   li > h1 {font-size:4mm; padding-top:0; margin-top:0;} \
                                   ")
    
    ordered_sections = ht.tags.ol(start=3, style='width:180mm; padding: 0 0 0 5mm; margin: 0')
    
    item1 = ht.tags.li(ht.tags.h1("Caracterização dos habitantes"),
                        ht.tags.p(f"No último levantamento elaborado pela Defesa Civil, a área apresentava \
                                aproximadamente {moradias_defesa:.0f} moradias. O resultado deste censo resultou em {moradias_fdte:.0f} moradias \
                                com um total de {total_moradores:.0f} habitantes, \
                                sendo {total_criancas:.0f} crianças, \
                                {total_idosos:.0f} idosos e \
                                {total_pcds:.0f} pessoas com deficiência (PCDs).",
                                class_='texto_geral',
                                style='text-align:justify; line-height:6mm'), style='width:175mm;')
    
    tabela = gerar_tabela_risco(risco_df)
    
    h = mm_to_px(62)
    item2 = ht.tags.li(ht.tags.h1("Habitantes por setor de risco"),
                       ht.tags.div(ht.tags.div(tabela,
                                                style=f'display:inline-block; width:45%; padding: 35px 30px; box-sizing: border-box;'), # width:45%; height:{h}px; 
                                    ht.tags.div(ht.tags.img(src=pathlib.Path(grafico_moradias_risco).as_uri(),
                                                            alt='Grafico Moradias Risco',
                                                            style=f'height:{h-2}px; box-sizing: border-box;'),
                                                style=f'display:inline-block; width:45%; padding: 0 30px 0 30px; height:{h}px; box-sizing:border-box; '),
                                    style=f'height:{h}px; padding:0; margin:0; box-sizing: border-box'), #height:{h}px;
                        style='width:175mm;') #height:75mm; 
    
    h3 = mm_to_px(75)
    item3 = ht.tags.li(ht.tags.h1("Distribuição das moradias na Área de Risco"),
                       ht.tags.div(ht.tags.img(src=mapa_moradias,
                                               alt='Grafico Moradias Risco',
                                               style=f'height:{h3}px; box-sizing: border-box;'),
                                   style=f'width:100%; margin-left:auto; margin-right:auto; text-align:center;'), #height:{h3+10}px; 
                       style='width:175mm;') #height:90mm; 
    
    ordered_sections.children = ht.TagList(item1, item2, item3)
    
    conteudo = [estilos_pagina, ordered_sections]
    
    return conteudo

def generate_p3(graph_dict, title='Indicadores', start_item=6):
    
    # criar estilos
    estilos_pagina = ht.tags.style('h1 {font-size:4mm; padding-top:0;} \
        ol > li {counter-increment: item; font-size:4mm; padding:2mm 0} \
        ol ol > li {display: block;}\
        ol ol > li:before {content: counters(item, ".") " "; margin-left: -20px;} \
        ')
    
    subtitulos = []
    for key, item in graph_dict.items():
        
        subtitulo = ht.tags.li(key,
            ht.tags.div(ht.tags.img(src=item,
                                    alt=key,
                                    style='height:80mm;'),
                        style='width: 100%; margin-top:10px; margin-left:auto; margin-right:auto; text-align:center;'))

        subtitulos.append(subtitulo)
    
    ordered_sections = ht.tags.ol(start=start_item, style=f'counter-reset:item {start_item-1}; width:180mm; padding: 0 0 0 5mm; margin: 0')
    titulo = ht.tags.li(ht.tags.h1(title), ht.tags.ol(subtitulos, start=start_item, style=f'counter-reset:item'))
    ordered_sections.children = ht.TagList(estilos_pagina, titulo)
    
    return ordered_sections
    
def generate_p4(graph_dict, start_item=6, subitem=3):
    
    # criar estilos
    estilos_pagina = ht.tags.style('h1 {font-size:4mm; padding-top:0;} \
        ol > li {counter-increment: item; font-size:4mm; padding:2mm 0} \
        ol ol > li {display: block;}\
        ol ol > li:before {content: counters(item, ".") " "; margin-left: -20px;} \
        ')
    
    subtitulos = []
    for key, item in graph_dict.items():
        print(item)
        subtitulo = ht.tags.li(key,
            ht.tags.div(ht.tags.img(src=pathlib.Path(item).as_uri(),
                                    alt=key,
                                    style='height:80mm; box-sizing: border-box;'),
                        style='width: 100%; margin-top:10px; margin-left:auto; margin-right:auto; text-align:center;'))

        subtitulos.append(subtitulo)
    
    ordered_sections = ht.tags.ol(style=f'counter-reset: item {start_item-1}; list-style-type: none; width:180mm; padding: 0 0 0 5mm; margin: 0')
    titulo = ht.tags.li(ht.tags.ol(subtitulos, start=start_item, style=f'counter-reset: item {subitem-1};'))
    ordered_sections.children = ht.TagList(estilos_pagina, titulo)
    
    return ordered_sections

# Gerando documentos

def gerar_doc():
    """
    Função que gera o arquivo html
    """
    
    ## Tamanho do doc
    d_height_mm = 297 #mm
    d_width_mm = 210 #mm

    ## Informação pra gerar cabeçalho e rodapé
    header_footer_info = {'nome_area':nome_area_risco,
                        'sigla_area':sigla_area,
                        'logo_sp':logo_sp,
                        'logo_fdte':logo_fdte}

    ## Gerando tabela com numero de moradores e moradias em cada risco

    risco_df_moradias = {'R1': moradias_r1,'R2': moradias_r2,'R3': moradias_r3,'R4': moradias_r4}
    risco_df_moradores = {'R1': moradores_r1,'R2': moradores_r2,'R3': moradores_r3,'R4': moradores_r4}
    risco_df = pd.DataFrame({'Moradias': risco_df_moradias, 'Habitantes': risco_df_moradores})

    
    conteudo = []
    conteudo.append(generate_p0(nome_area_risco, sigla_area))
    conteudo.append(generate_p1(nome_area_risco, sigla_area, subprefeitura, hierarquia_area, data_censo_inicial, data_censo_final, mapa_setores))
    conteudo.append(generate_p2(risco_df, grafico_moradias_risco))
    
    graphs_p3 = {"Quantificação de moradias por setor de risco":grafico_moradias_setor,
              "Tipo de uso dos imóveis": grafico_uso_imoveis}
    
    graphs_p4 = {"Tipologia das construções": grafico_tipo_construcao,
                 "Quantidade de pavimentos": grafico_n_pavimentos}
    graphs_p5 =  {"Nível do acabamento das moradias": grafico_acabamento_moradias,
                 "Tipo de pisos": grafico_pisos}
    
    graphs_p6 = {"Tipo de coberturas": grafico_cobertura,
                 "Problemas estruturais": grafico_problemas}
    
    conteudo.append(generate_p3(graphs_p3))
    conteudo.append(generate_p4(graphs_p4))
    conteudo.append(generate_p4(graphs_p5, subitem=5))
    conteudo.append(generate_p4(graphs_p6, subitem=7))
    
    maps_p7 = {"Problemas estruturais": mapa_problemas,
               "Crianças": mapa_criancas}
    maps_p8 = {"Idosos": mapa_idosos,
               "PCDs": mapa_pcds}
    
    conteudo.append(generate_p3(maps_p7, title = 'Espacialização dos indicadores', start_item=7))
    conteudo.append(generate_p4(maps_p8, start_item=7))
    
    arquivos_html = []
    arquivos_txt = ''
    for i, page in enumerate(conteudo):
        arquivo = generate_page(page, header_footer_info, d_height_mm, d_width_mm)
    
        nome_arquivo = f'/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/html_outputs/{nome_area}_{sigla_area}_{i}.html'
        arquivo.save_html(nome_arquivo)
        arquivo_final_txt = str(arquivo)
        arquivos_html.append(nome_arquivo)
        arquivos_txt+=(arquivo_final_txt)
    
    return arquivos_html, arquivos_txt

def pdf_doc(arquivos):

    pdf_file = f'/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/html_outputs/{nome_area}_{sigla_area}.pdf'
    
    pdfkit.from_string(arquivos, pdf_file, options={
                                                "enable-local-file-access": True,
                                                #   'page-height': '297mm',
                                                #   'page-width': '210mm',
                                                #   'encoding': "latin-1",
                                                  'margin-top': '0px',
                                                  'margin-right': '0px',
                                                  'margin-bottom': '0px',
                                                  'margin-left': '0px',
                                                #   'viewport-size': '210mmx297mm',
                                                #   'dpi':'300',
                                                #   'no-outline': None,
                                                  'disable-smart-shrinking': None,
                                                #   'zoom':'1.24'
                                                  })

if __name__ == '__main__':
    html_files, html_txt = gerar_doc()
    pdf_doc(html_txt)