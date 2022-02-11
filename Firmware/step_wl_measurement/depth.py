import cv2           # Importar librerias de Opencv
import numpy as np   # Importar librerias de numpy para vectores y matrices
import pandas as pd  # Importar librerias de panda para exportar datos

# Importar funciones utilizadas en el algoritmo

import HSV_filter as hsv           # Funcion para mascara HSV
import shape_recognition as shape  # Funcion para identificacion de contornos
import triangulation as tri        # Funcion de estimacion de profundidad
import calibration


# Variables usadas para almacenar datos de ancho y largo de paso
dataxde = []
stepLgt_temp = []
distanceX_cm_temp = []
step_wid_Lgt = []

# Declaración de parametros intrinsecos de la stereocamara
B = 6             # Distancia entre las camara o Baseline [cm]
f = 6             # Distancia focal del lente [mm]
alpha = 49.7      # Campo de visión en el plano horizontal [grados]

# Abrir un par de imagenes stereo previamente recolectado

cap_right = cv2.VideoCapture('images/L5.avi')
cap_left = cv2.VideoCapture('images/R5.avi')

#=== Inicio de ciclo de captura y analizis de los fotogramas de video ===#

while True:

#============= Configuracion de dispositivos de video ============#

    # Captura de fotogramas recibidos de la estereocamara
    ret_right, frame_right = cap_right.read() 
    ret_left, frame_left = cap_left.read()


    # Calibración y rectificación de los fotogramas obtenidos 
    frame_right, frame_left = calibration.undistortRectify(frame_right, frame_left)


    # Si no se reciben imagenes de alguna de las entrada de video termina el algoritmo
    if ret_right == False or ret_left==False:
        break

    else:

        # Aplicacion de mascaras HSV color rojo sobre cada imagen estero
        mask_right = hsv.add_HSV_filter(frame_right, 1)
        mask_left = hsv.add_HSV_filter(frame_left, 0)

        # Identificiacion de contornos y retorno de los centroides de los dos 
        # marcadores de los talones identificados en cada imagen estereo
        circles_right = shape.find_circles(frame_right, mask_right)
        circles_left = shape.find_circles(frame_left, mask_left)


        # Si no se detecta ningun centroide en alguno de los frames se muestra m
        # ensaje indicando perdida de objetivo
        if np.all(circles_right) is None or np.all(circles_left) is None:
            cv2.putText(frame_right, "TRACKING LOST", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame_left, "TRACKING LOST", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Si los centroides de los marcadores son detectado se ejecuta el siguiente bloque
        else:

            # Extraccion de las coordenadas X e Y para los dos marcadores en cada imagen estereo
            centerL_frameR, centerR_frameR = (circles_right[0], circles_right[1])
            centerL_frameL, centerR_frameL = (circles_left[0], circles_left[1])

            # Estimacion de la profundidad para los dos marcadores en cada imagen estereo
            depthL = tri.find_depth(centerL_frameL, centerL_frameR, frame_right, frame_left, B, f, alpha)
            depthR = tri.find_depth(centerR_frameL, centerR_frameR, frame_right, frame_left, B, f, alpha)

            # Se muestran en pantalla la distancia a la que se encuentran los marcadores de la estereocamara
            cv2.putText(frame_right, "Distance 1: " + str(depthL) + " Distance 2:" + str(depthR), (200, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124, 252, 0), 2)


            # Calculo del marcador mas cercano al robot para realizar estimacion de ancho de paso
            if depthL < depthR:
                depthRelative = depthL 
                
                # Calculo de la distancia en pixeles entre los centroides de los marcadores
                distanceX_pixel = centerR_frameL[0] - centerL_frameL[0] 

            else:
                depthRelative = depthR

                # Calculo de la distancia en pixeles entre los centroides de los marcadores
                distanceX_pixel = centerR_frameR[0] - centerL_frameR[0]

            # Calculo de la distancia real en cm del ancho de paso
            distanceX_relative = (0.0447 * (depthRelative**2)) - (9.9119 * depthRelative) + 707.96
            distanceX_cm = (distanceX_pixel * 20)/distanceX_relative
            distanceX_cm = round(distanceX_cm, 3)

            # Calculo del largo de paso en cm
            stepLgt = depthR - depthL
            stepLgt = abs(round(stepLgt, 2))

            # Almacenamiento de datos en variables temporales 
            stepLgt_temp = stepLgt_temp + [stepLgt]
            distanceX_cm_temp = distanceX_cm_temp + [distanceX_cm]
            
            # Se muestra en pantalla los valores de largo y ancho de paso calculados
            cv2.putText(frame_left, "Lenght: " + str(stepLgt) + "  Width: " + str(distanceX_cm), (200, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124, 252, 0), 2)

            # Cada medio ciclo de paso se almacenan las variables de ancho y largo de paso obetnidas
            # en un arreglo
            if 0 <= stepLgt <= 6:
                
                stepLgt_total = sorted(stepLgt_temp, reverse=True) 
                distanceX_cm_total = sorted(distanceX_cm_temp, reverse=True)
                stepLgt_temp = []
                distanceX_cm_temp = []


                if stepLgt_total[0] > 14:

                    # Se toma el mayor valor de cada parametro para almacenar
                    array = [(stepLgt_total[0], distanceX_cm_total[0])]
                    step_wid_Lgt = step_wid_Lgt + array


        # Se crean cuatro ventanas que permiten visualizar los datos obtenidos 
        # y los videos cargados al algoritmo
        cv2.imshow("frame right", frame_right)
        cv2.imshow("frame left", frame_left)
        cv2.imshow("mask right", mask_right)
        cv2.imshow("mask left", mask_left)


        # Presionar q para terminar el algoritmo
        if cv2.waitKey(1) & 0xFF == ord('q'):
            dataxde = set(stepLgt)
            df = pd.DataFrame(data=dataxde)
            df.to_excel("data1.xlsx")

            break

# Si hay algo almacenado en el arreglo de datos se guarda como documento excel
if step_wid_Lgt:
    df = pd.DataFrame(data=step_wid_Lgt)
    df.to_excel("stepLgt.xlsx")

# Limpieza del programa
cap_right.release()
cap_left.release()

# Cierre de ventanas creadas 
cv2.destroyAllWindows()