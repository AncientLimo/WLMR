import cv2                               # Importar librerias de OpenCV
import numpy as np                       # Importar librerias numpy para vectores y matrices
import pwm_control                       # Importar algoritmo de control de motores
import velocity_and_orientation_control  # Importar algoritmo de control proporcional para seguimiento
import datetime                          # Importar librerias para fecha del sistema

global flag                              # Variable global para interrumpir ciclo 



def move(value):    # Definicion de funcion de seguimiento y recoleccion de imagenes

    global flag 
    flag = value

#============= Configuracion de dispositivos de video ============#

    # Usar comando: <v4l2-ctl --list-devices> en sistemas linux listara los dispositivos con su respectivo slot
    cap = cv2.VideoCapture(2)       # Inicializar camara para seguimiento
    stereo1 = cv2.VideoCapture(0)   # Inicializar stereocamara uno
    stereo2 = cv2.VideoCapture(1)   # Inicializar stereocamara dos

    d = datetime.datetime.now()

    # Definicion de formato para nombres de archivos de salida
    filename1 = 'videoSalida1_date_{0}_time_{1}.avi'.format(d.strftime("%y-%m-%d"), d.strftime("%H-%M-%S"))
    filename2 = 'videoSalida2_date_{0}_time_{1}.avi'.format(d.strftime("%y-%m-%d"), d.strftime("%H-%M-%S"))

    # Declaracion de formato para archivos de video de salida
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')  # Definicion del codec de video
    if flag:
        out1 = cv2.VideoWriter('stereoVideo/{}'.format(filename1), fourcc, 20, (640, 480)) 
        out2 = cv2.VideoWriter('stereoVideo/{}'.format(filename2), fourcc, 20, (640, 480))

    # Construccion de arrays para la mascara de color HSV color rojo
    redbot0 = np.array([0, 100, 20], np.uint8)      
    redtop0 = np.array([8, 255, 255], np.uint8)
    redbot1 = np.array([170, 100, 20], np.uint8)
    redtop1 = np.array([179, 255, 255], np.uint8)

#== Inicio de ciclo de captura y analizis de los frames de video ==#

    while flag:  # Si se pulsa el boton Parar desde la aplicacion se termina el ciclo

        # Captura de frames para camara de seguimiento
        ret, frame = cap.read()      

#============ Recoleccion de imagenes estereoscopicas =============#   

        ret1, frame1 = stereo1.read()
        ret2, frame2 = stereo2.read()

        # Escritura de videos de salida con cada frame recibido de la estereocamara
        if ret1 and ret2:
           out1.write(frame1)
           out2.write(frame2)

#== Bloque de analisis de imagenes para seguimiento de objetivo ==#

        if ret:  # Procede solo si la camara esta reproduciendo

            # Operaciones morfologicas sobre la imagen para corregir ruido
            blur = cv2.GaussianBlur(frame,(5,5),0)   # Suavizado de imagen
            framehsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)  # Transformacion RGB a HSV

            # Aplicacion de mascaras de color rojo en los rangos inferiores y superiores del espectro HSV
            maskred1 = cv2.inRange(framehsv, redbot0, redtop0) 
            maskred2 = cv2.inRange(framehsv, redbot1, redtop1)
            maskred0 = cv2.add(maskred1, maskred2)   # Adicion de las dos mascaras

            # Operaciones morfologicas sobre la imagen para corregir ruido
            maskred = cv2.erode(maskred0, None, iterations=2)   
            maskred = cv2.dilate(maskred, None, iterations=2)

            # Busqueda de contornos en los frames con la mascara HSV aplicada
            contours, _ = cv2.findContours(maskred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:  # Proceder si se encuentran contornos
                
                for c in contours:  # Para cada contorno encontrado se ejecuta el siguiente bloque
                   
                    # Calculo del area del contorno
                    area = cv2.contourArea(c) 

                    if 7000 > area > 1000:    
                        
                        # Caculo de momentos del contorno
                        m = cv2.moments(c) 

                        # Reasignacion para evitar division por cero
                        if m["m00"] == 0:  
                            m["m00"] = 1

                        # Calculo de coorneadas X e Y del centroide del contorno
                        x = int(m["m10"] / m["m00"]) 
                        y = int(m['m01'] / m['m00'])

                        # Algoritmo basado en control proporcional para calcular velocidad de motores (PWM)
                        [pwm_right, pwm_left] = velocity_and_orientation_control.control(area, x)

                        # Control de motores utilizando pulsos PWM
                        pwm_control.move(pwm_right,pwm_left)
                    
            else: # Si no se detectan contornos se detienen los motores
                
                pwm_control.stop()
 
            if cv2.waitKey(25) & 0xFF == ord('q'):
                pwm_control.stop()
                cap.release()
                break


#====== Limpieza del algoritmo =======#

    # Dejar de leer imagenes de las camaras
    cap.release()
    stereo1.release()
    stereo2.release()
    # Se cierra cualquier ventana generada por el algoritmo
    cv2.destroyAllWindows()
