import cv2                  # Importar librerías de OpenCV
import numpy as np          # Importar libreriás numpy para vectores y matrices
global flag                 # Variable global para interrumpir ciclo 

#============== Definición de función para calibración de cámara de seguimiento ===============#

def generate_frames_main(get_frame):
    
    global flag
    flag = get_frame

    # Usar comando: <v4l2-ctl --list-devices> en sistemas linux listará los dispositivos con su respectivo slot
    camera = cv2.VideoCapture(0)   # Inicializar cámara para seguimiento

    # Construcción de arrays para la máscara de color HSV color rojo
    redbot0 = np.array([0, 100, 20], np.uint8)
    redtop0 = np.array([8, 255, 255], np.uint8)
    redbot1 = np.array([170, 100, 20], np.uint8)
    redtop1 = np.array([179, 255, 255], np.uint8)

#======================= Inicio de ciclo de captura y análizis de los frames de video =====================#

    while flag:  # Sólo funciona estando en la pestaña Calibrar

        # Captura de frames de la cámara
        ret, frame = camera.read()


        if camera.isOpened(): # Procede solo si la cámara está reproduciendo
            
            # Operaciones morfológicas sobre la imágen para corregir ruido
            blur = cv2.GaussianBlur(frame,(5,5),0)            # Suavizado de imágen
            framehsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)  # Transformación RGB a HSV

            # Aplicación de máscaras de color rojo en los rangos inferiores y superiores del espectro HSV
            maskred1 = cv2.inRange(framehsv, redbot0, redtop0)
            maskred2 = cv2.inRange(framehsv, redbot1, redtop1)
            maskred0 = cv2.add(maskred1, maskred2)             # Adición de las dos máscaras

            # Operaciones morfológicas sobre la imágen para corregir ruido
            maskred = cv2.erode(maskred0, None, iterations=2)
            maskred = cv2.dilate(maskred, None, iterations=2)

            # Busqueda contornos en los frames con la máscara HSV aplicada    
            contours, _ = cv2.findContours(maskred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:            # Proceder si se encuentran contornos

                for c in contours:  # Para cada contorno encontrado se ejecuta el siguiente bloque
                    
                    # Cálculo del área del contorno
                    area = cv2.contourArea(c)   

                    if 8000 > area > 1000:

                        # Cáculo de momentos del contorno
                        m = cv2.moments(c)      

                        # Reasignación para evitar división por cero
                        if m["m00"] == 0:       
                            m["m00"] = 1

                        # Cálculo de coorneadas X e Y del centroide del contorno
                        x = int(m["m10"] / m["m00"])
                        y = int(m['m01'] / m['m00'])

                        # Dibujado de punto verde sobre centroide del contorno
                        cv2.circle(frame, (x, y), 7, (0, 255, 0), -1)

                        # Definición del borde exterior del contorno
                        new_contour = cv2.convexHull(c)

                        # Cáculo de la distancia entre el marcador y el robot
                        distance  = -2.8030e-04*area + 2.1205

                        # Coloreado del borde exterior del contorno según la distancia a 
                        # la que se encuentre el marcador (metros)
                        if 1.05 >= area >= 0.95:
                            cv2.drawContours(frame, [new_contour], 0, (0, 255, 0), 3)
                        if area > 1.05:
                            cv2.drawContours(frame, [new_contour], 0, (154, 0, 255), 3)
                        if area < 0.95:
                            cv2.drawContours(frame, [new_contour], 0, (0, 0, 255), 3)

            # Redimensionamiento de los frames para facilitar transmisión entre dispositivos
            w = int(frame.shape[1] * 0.4)
            h = int(frame.shape[0] * 0.4)
            dim = (w, h)
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            ret, buffer = cv2.imencode('.jpg', frame)   # Codificación de la imágen
            frame = buffer.tobytes()                    # Conversión de los frames a bytes

        else:  # Si no se detecta cámara se detiene la función
            break

        # Retorna cada frame según se genera en formato avif para navegador web
        yield (b' --frame\r\n' b'Content-Type: image/avif\r\n\r\n' + frame + b'\r\n')


#============== Definición de función para calibración de stereocámara ===============#

def generate_frames_capture(get_frame):

    global flag
    flag = get_frame

    # Usar comando: <v4l2-ctl --list-devices> en sistemas linux listará los dispositivos con su respectivo slot
    camera = cv2.VideoCapture(1)
    camera.set(7, 5)
    redbot0 = np.array([0, 100, 20], np.uint8)
    redtop0 = np.array([8, 255, 255], np.uint8)
    redbot1 = np.array([170, 100, 20], np.uint8)
    redtop1 = np.array([179, 255, 255], np.uint8)

    while flag:

        ret, frame = camera.read()

        if ret:
            
            blur = cv2.GaussianBlur(frame,(5,5),0)
            framehsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

            maskred1 = cv2.inRange(framehsv, redbot0, redtop0)
            maskred2 = cv2.inRange(framehsv, redbot1, redtop1)
            maskred0 = cv2.add(maskred1, maskred2)

            maskred = cv2.erode(maskred0, None, iterations=2)
            maskred = cv2.dilate(maskred, None, iterations=2)
    
            contours, _ = cv2.findContours(maskred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:

                for c in contours:

                    area = cv2.contourArea(c)

                    if 6500 > area > 1500:

                        m = cv2.moments(c)

                        if m["m00"] == 0:
                            m["m00"] = 1

                        x = int(m["m10"] / m["m00"])
                        y = int(m['m01'] / m['m00'])
                        cv2.circle(frame, (x, y), 7, (0, 255, 0), -1)
                        new_contour = cv2.convexHull(c)
                        print(area)

                        if 120 > area > 360:
                            cv2.drawContours(frame, [new_contour], 0, (0, 255, 0), 3)

            w = int(frame.shape[1] * 0.4)
            h = int(frame.shape[0] * 0.4)
            dim = (w, h)
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        else:
            break

        yield (b' --frame\r\n' b'Content-Type: image/avif\r\n\r\n' + frame + b'\r\n')