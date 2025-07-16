from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtCore import QTime,QTimer
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *

import sys
import os 
import time 

import speech_recognition as sr
from translate import Translator


Servicio = False
palabras_a_reemplazar = []           #Lista de palabras funables


class Hilo(QThread):
    lbl_detect = pyqtSignal(str)
    lbl_detect_in = pyqtSignal(str)

    def run(self):
        self.hilo_corriendo = True
        while self.hilo_corriendo ==True:

            global numDevice                        #Variable global que contiene el indice del micro seleccionado
            global nameDevice                       #Variable global que contiene el índice del micro seleccionado
            global palabras_a_reemplazar             #Variable global que contiene la lista de palabras funables 

            with open('Funable.txt', 'r') as archivo:               #Carga las palabras del archivo de texto a una varibale
                palabras_a_reemplazar = archivo.read().splitlines() #Realiza la lectura 


            r = sr.Recognizer()                     #objeto de sr para reconocer la voz
            #sr.Microphone(device_index = numDevice) #Seleccion de servicio seleccionado por defecto 0
            sr.Microphone()
        
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)         #Auto ajusta el ruido ambiental 
                audio = r.listen(source)                   #Escucha la entrada 
                try:
                    text = r.recognize_google(audio, language='es-MX') #Se realiza el reconocimiento de voz y se guarda en varibale
                    for palabra in palabras_a_reemplazar:               #Se realiza el filtrado de palabras funables
                        text = text.replace(palabra,"*"*len(palabra))   #Se remplaza la palabra funable 
                    self.lbl_detect_in.emit(text)
                    trad = Translator(from_lang ="es",to_lang ="en")    #Se cargan los parametros de traduccion
                    txt = text
                    res = trad.translate(txt)                           #Se envia la traduccion 
                    self.lbl_detect.emit(res)
                except sr.UnknownValueError:                            #En caso de no entender el audio 
                    self.lbl_detect.emit("No se pudo entender el audio :( intente nuevamente")
                except sr.RequestError as e:                            #En caso de tener problemas de conexion 
                    self.lbl_detect.emit("Error de Solicitud")

    def stop(self):                     
        self.hilo_corriendo = False
        self.quit()



class GUI(QMainWindow): 
    numDevice = 0
    nameDevice = None
     
    
    def __init__(self):
        super(GUI, self).__init__()
        uic.loadUi("ventanita.ui",self)
        self.setWindowTitle("Sustitulos Eziristas")
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.btnInicio.clicked.connect(self.activarBotonDetener) #para relacionar la funcion con el btn 
        self.btnDetener.clicked.connect(self.activarBotonInicio)
        self.btnDetener.setEnabled(False)                       #Btn deshabilitado
        self.TextoPredicho.setReadOnly(True)
        self.SalidaTraducida.setReadOnly(True)

        self.actionIniciar.triggered.connect(self.activarBotonDetener)
        self.actionDetener.triggered.connect(self.activarBotonInicio)
        self.actionSalir.triggered.connect(self.salirApp)
        
        self.actionTexto.triggered.connect(self.FontDialog)
        self.actionColor_Texto.triggered.connect(self.SelectColorFont)
        self.actionFondo.triggered.connect(self.SelectColorBG)
        self.actionLista_de_palabras_funables.triggered.connect(self.AbirTxt)

        self.HiloDeTrabajo = Hilo()
        self.HiloDeTrabajo.lbl_detect.connect(self.Actualizar_lbl)
        self.HiloDeTrabajo.lbl_detect_in.connect(self.Actualizar_lbl_Entrada)

        r = sr.Recognizer()
        self.comboBoxMicros.addItems(sr.Microphone.list_microphone_names())
        self.btnSeleccionEntrada.clicked.connect(self.seleccionComboBox)

        ##*--------CARGAR TXT
        with open('Funable.txt', 'r') as archivo:               #Carga las palabras del archivo de texto a una varibale
            palabras_a_reemplazar = archivo.read().splitlines() #Realiza la lectura 

        Servicio = False

    def salirApp(self):
        self.close()

    def AbirTxt(self):              #Funcion para abir el archivo de lista de palabras funables
        path = "Funable.txt"        #Carga la ruta de las palabras 
        if os.path.exists(path):    #Si existe la ruta 
            os.startfile(path)      #Abre el archivo


    def seleccionComboBox(self):
        global numDevice
        global nameDevice

        r = sr.Recognizer()

        micro = self.comboBoxMicros.currentText();      #Obtiene el microfono seleccionado
        self.lblMicroInput.setText(micro)               #Envia la seleccion al lbl
        nameDevice = micro                              #Renombra el servicio ocupado
        numDevice = sr.Microphone.list_microphone_names().index(micro)  #Obtiene el indice del micro seleccioado 

    def activarBotonDetener(self):
        global Servicio
        self.btnDetener.setEnabled(True)
        self.btnInicio.setEnabled(False)
        self.lblEstado.setText("Estado: Activo")
        self.lblEstado.setStyleSheet("background-color: #a0f99d")

        self.actionDetener.setEnabled(True)
        self.actionIniciar.setEnabled(False)
        self.btnSeleccionEntrada.setEnabled(False)  #Desactiva el boton de seleccion de entrada
        self.comboBoxMicros.setEnabled(False)       #Desactiva el combox de seleccion de microfono

        self.actionTexto.setEnabled(False)
        self.actionColor_Texto.setEnabled(False)
        self.actionFondo.setEnabled(False)

        Servicio = True

        self.HiloDeTrabajo.start()
        

    def activarBotonInicio(self):
        global Servicio
        self.btnDetener.setEnabled(False)               #Activa el boton DETENER
        self.btnInicio.setEnabled(True)                 #Desctiva el botron Inicio (o al revez xddd )
        self.lblEstado.setText("Estado: Desactivado")   #Envia a lbl el estado actual del programa
        self.lblEstado.setStyleSheet("background-color: #f57a7a")

        self.actionDetener.setEnabled(False)            #Activa el menu boton DETENER
        self.actionIniciar.setEnabled(True)             #deactiva el menu boton INICIO
        self.btnSeleccionEntrada.setEnabled(True)       #Activa el boton de Seleccionar entrada
        self.comboBoxMicros.setEnabled(True)            #Activa el combox de seleccion de microfono

        self.actionTexto.setEnabled(True)               #Activa el menu boton para cambiar texto
        self.actionColor_Texto.setEnabled(True)         #Activa el menu boton para cambar color texto
        self.actionFondo.setEnabled(True)               #Activa el menu boton para cambiar el color fondo

        self.HiloDeTrabajo.stop()
        Servicio = False 

    
    def FontDialog(self):
        (fuente, ok) = QFontDialog.getFont()        #Variable que obtiene una fuente seleccioanada

        if ok:                                      #si se selecciona cambiar 
            self.TextoPredicho.setFont(fuente)      #Cambia a la nueva fuente
            self.SalidaTraducida.setFont(fuente)    #cambiar a la nueva fuente
            self.TextoPredicho.setText("Prueba")    #Envia una prueba para probar la nueva fuente
            self.SalidaTraducida.setText("Prueba")  #Envia una prueba para probar la nueva fuente 

    def SelectColorFont(self):
        color = QColorDialog.getColor()             #Variable para seleccionar un color 
        self.TextoPredicho.setTextColor(color)      #Envia el color seleccionado para la fuente 
        self.SalidaTraducida.setTextColor(color)    #Envia el color seleccioado para la funte
        self.TextoPredicho.setText("Prueba")        #Envía una prueba para ver el nuevo color seleccioado
        self.SalidaTraducida.setText("Prueba")      #Envia una prueba para ver el nuevo color selccionado 

    def SelectColorBG(self):                        #Funcion para cambiar el color del fondo (Aun no sirve )
        colorBG = QColorDialog.getColor()           #Obtiene un color seleccionado 
        #self.TextoPredicho.setBackgroundRole(colorBG)
        #self.SalidaTraducida.setBackground(colorBG)

    def Actualizar_lbl(self,texto):
        self.SalidaTraducida.setText(texto)

    def Actualizar_lbl_Entrada(self,texto):
        self.TextoPredicho.setText(texto)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    INTERFAZ = GUI()
    INTERFAZ.setFixedSize(INTERFAZ.size())
    INTERFAZ.show()
    sys.exit(app.exec_())
