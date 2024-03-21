import  jpype
import  asposecells
jpype.startJVM() 
from asposecells.api import Workbook

workbook = Workbook("/Users/anabottura/PycharmProjects/FDTE/auto_relatorios/data/html_outputs/images/mapa_setores.html")
workbook.save("Output.png")
jpype.shutdownJVM()