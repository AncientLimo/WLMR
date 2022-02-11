from flask import Flask, render_template, Response  # Se importan librerias de Flask
import calibrate                                    # Se importa algoritmo de calibracion
#import following_red                                # Se importa algoritmo de control
                                          


app = Flask(__name__)
message = '  '

# Banderas para controlar recoleccion de imagenes

get_frame = False
camera_num = False


# ===== Definicion de las rutas en el servidor =======#


# Pagina de inicio
@app.route('/')
def index():
    global get_frame 
    global camera_num 
    camera_num = False  # Desactiva transmision fuera de pagina de calibracion
    get_frame = False   # Desactiva transmision fuera de pagina de calibracion
    return render_template('page1.html')  # Cargar pagina de inicio

# Pagina de instrucciones
@app.route('/Instrucciones')
def page2():
    global get_frame
    global camera_num
    camera_num = False
    get_frame = False
    return render_template('page2.html')  # Cargar pagina de instrucciones

# Pagina de control de robot
@app.route('/Empezar')
def page3():
    global get_frame
    global camera_num
    camera_num = False
    get_frame = False
    global message
    return render_template('page3.html', message=message)  # Cargar pagina de control

# Pagina para calibrar camaras
@app.route('/Calibrar')
def page4():
    global get_frame
    global camera_num
    camera_num = False
    get_frame = False
    return render_template('page4.html')                    # Cargar pagina de calibracion

# Inicializar transmision de camara uno en pagina de calibracion
@app.route('/main_camera')
def main_camera():
    global camera_num
    global get_frame
    camera_num = int(0)
    get_frame = True
    return render_template('page4.html')

# Inicializar transmision de camara dos en pagina de calibracion
@app.route('/stereo_camera')
def stereo_camera():
    global camera_num
    global get_frame
    camera_num = int(1)
    get_frame = True
    return render_template('page4.html')

# Tranmision de imagenes de las camaras en pagina de calibracion
@app.route('/video')
def video():
    global get_frame
    global camera_num
    if camera_num == 0: # Indicador para iniciar transmision de camara uno
        return Response(calibrate.generate_frames_main(get_frame), 
        mimetype='multipart/x-mixed-replace; boundary=frame')
    if camera_num == 1: # Indicador para iniciar transmision de camara dos
        return Response(calibrate.generate_frames_capture(get_frame), 
        mimetype='multipart/x-mixed-replace; boundary=frame')


# Iniciar algortimos de seguimiento y recoleccion de imagenes con boton Inicar en pagina de control
@app.route('/start')
def start():
    global message
    message = 'Aplicacion iniciada...'   
    #following_red.move(1)
    return render_template('page3.html', message=message)  # Mostrar mensaje

# Detener algortimos de seguimiento y recoleccion de imagenes con boton Detener en pagina de control
@app.route('/stop')
def stop():
    global message
    #following_red.move(0)
    message = 'Aplicacion detenida...'
    return render_template('page3.html', message=message)  # Mostrar mensaje

# ======== Inicializar servidor en la IP del host y puerto 8080 =======#
if __name__ == '__main__':
    app.debug = False
    app.run(host="0.0.0.0", port=8080)
