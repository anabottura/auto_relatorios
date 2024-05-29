import htmltools as ht
from datetime import date

def create_header_table(nome_area, sigla_area, sp_logo):
    # Criação da tabela do headerconda 

    table_header = ht.tags.table(id='id_table_header',style=("height:40mm; width:180mm; margin-left:auto; margin-right:auto"))
    
    header_p = ht.tags.style(".header_p {font-size:2.5mm; margin: 1mm 0 1mm 2mm}")
    header_h1 = ht.tags.style(".header_h1 {font-size:3mm; font-weight:bold; margin: 2mm 0 2mm 2mm}")
    
    # table_header.children.append(header_p)
    
    tr1 =  create_tr([ht.tags.td(ht.tags.p("RELATÓRIO DEMOGRÁFICO", style="font-weight:bold; margin: 2mm 0;"),
                      style="width:50%; background-color:rgb(10,84,133);color: white;font-weight:bold;text-align:center",
                      colspan=4
                      )])
    
    tr2 = create_tr([ht.tags.td(ht.tags.div(ht.tags.img(src=sp_logo, alt='logo SP', style="height:15mm; width:15mm;"),
                                            style="text-align: center;"), colspan=2),
                     ht.tags.td(ht.tags.p("EMISSÃO:", class_='header_h1')),
                     ht.tags.td(ht.tags.p("REVISÃO:", class_='header_h1'))])
    
    tr3 = create_tr([ht.tags.td(ht.tags.p("EMITENTE:", class_='header_h1'),
                                ht.tags.p("FDTE", class_='header_p'), colspan=2),
                     ht.tags.td(ht.tags.p(date.today().strftime("%d/%m/%Y"), class_='header_p'), style="text-align:center"),
                     ht.tags.td(ht.tags.p("R02", class_='header_p'), style="text-align:center")])
    
    tr4 = create_tr([ht.tags.td(ht.tags.p("LOCAL:", class_='header_h1'),
                                ht.tags.p(f"{nome_area} ({sigla_area})", class_='header_p'), colspan=2),
                     ht.tags.td(ht.tags.p("COORDENAÇÃO:", class_='header_h1'),
                                ht.tags.p("Eng. Henrique Campelo", class_='header_p'), colspan=2)])
    
    tr5 = create_tr([ht.tags.td(ht.tags.p("OBJETO:", class_='header_h1'),
                                ht.tags.p("Relatório de Vistoria de Campo", class_='header_p'), colspan=2),
                     ht.tags.td(ht.tags.p("CREA:", class_='header_h1'),
                                ht.tags.p("5061886894-SP", class_='header_p'), colspan=2)])
    
    trs_header = [tr1, tr2, tr3, tr4, tr5]
    table_header.children = ht.TagList(table_header.children, header_p, header_h1, *trs_header)
    
    return table_header

def create_tr(td_list):
    tr_header = ht.tags.tr()

    tr_header.children = ht.TagList(tr_header.children, *td_list)
    
    return tr_header