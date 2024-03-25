# import  jpype
# import  asposecells
# jpype.startJVM() 
# from asposecells.api import Workbook

# workbook = Workbook("/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/html_outputs/images/mapa_setores.html")
# workbook.save("Output.png")
# jpype.shutdownJVM()

from html2image import Html2Image
import pathlib
import os
hti = Html2Image()

# hti = Html2Image(size=(1440, 900))

print(os.path.basename('/Users/anacarolinabotturabarros/PycharmProjects/auto_relatorios/data/images/mapa_setores.html'))
hti.screenshot(html_file='/Users/anacarolinabotturabarros/PycharmProjects/auto_relatorios/data/images/mapa_setores.html', save_as='test.png')

# import imgkit

# options = {
#     "enable-local-file-access": 1,
#     # 'disable-smart-width': 1,
#     # 'crop-w': 1440,
#     # 'crop-h': 900,
#     # 'format': 'png',
#     # 'width': 2880,
#     'height':1800,
#     # 'disable-smart-shrinking': 1
#     # 'window-status': 'imdone'
#     # 'zoom': 3
    
# }

# with open('/Users/anacarolinabotturabarros/PycharmProjects/auto_relatorios/data/images/mapa_setores.html') as f:
#     imgkit.from_file(f, 'test2.png', options=options)