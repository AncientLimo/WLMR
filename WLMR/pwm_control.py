import RPi.GPIO as GPIO # Importar librerías para uso de pines en Raspberry PI

# Declaración de pines a utilizar

ena = 13
in1 = 27
in2 = 22

enb = 12
in3 = 23
in4 = 24

# Definición de los pines a utilizar como salidas
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(ena, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)

# Declaración de pines para control PWM
pwm_a = GPIO.PWM(ena, 255)
pwm_b = GPIO.PWM(enb, 255)

# Inicialización de pines PWM
pwm_a.start(0)
pwm_b.start(0)

#==================== Definición de funcion para movimiento de motores ==================#

def move(pwm_r, pwm_l):
    

    # Corrección de valores PWM    
    pwm_r = max(0, pwm_r)
    pwm_r = min(pwm_r, 100)

    pwm_l = max(0, pwm_l)
    pwm_l = max(pwm_l, 100)

    # Definición de pines para mover robot hacia adelante
    GPIO.output(in1, False)
    GPIO.output(in2, True)
    GPIO.output(in3, False)
    GPIO.output(in4, True)

    # Control de velocidad de motores
    pwm_a.ChangeDutyCycle(int(pwm_r))
    pwm_b.ChangeDutyCycle(int(pwm_l))
    return;

#======================= Definición de función para detener motores ===============#
def stop():

    pwm_a.ChangeDutyCycle(int(0))
    pwm_b.ChangeDutyCycle(int(0))
    return;
        



