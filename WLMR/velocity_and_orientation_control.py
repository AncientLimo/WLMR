def velocity_control(pixel):

    # Conversión de pixeles a distancia
    distance  = -2.8030e-04*pixel + 2.1205
  
    # Error de la distancia [m]
    error     = 1 - distance
  
    # Control proporcional
    velocity  = -4 * error

    # Corregir valores negativos
    velocity  = max(0,velocity)    
    return velocity

def orientation_control(xcenter):   

    # Error respecto al centro
    error     = 320 - xcenter
  
    # Control proporcional 
    diffvel   = 0.003 * error
    return diffvel
 

def get_pwm_motors(vel_linear, diff_velocity):

    # Velocidad para los motores de derecha e izquierda
    vel_right = vel_linear - diff_velocity/2
    vel_left  = vel_linear + diff_velocity/2
    
    # Velocidad a PWM   
    pwm_right = 107.4766*vel_right -53.0374
    pwm_left  = 107.4766*vel_left -53.0374
  
    # corregir PWM en el rango [0,255]
    pwm_right = int(max(0,min(100,pwm_right)))
    pwm_left  = int(max(0,min(100,pwm_left)))
    return pwm_right, pwm_left
    
def control(pixel, xcenter):

    # PWM[1] para el motor derecho
    # PWM[2] para el motor izquierdo
    
    # Verifica si el área obtenida se encuentra dentro de un rango esperado
    if 4900 > pixel > 2000:
        vel_linear      = velocity_control(pixel)
        diff_velocity   = orientation_control(xcenter)
        pwm             = get_pwm_motors(vel_linear, diff_velocity)
        return pwm

    #Si el área está fuera de rango detiene el robot
    else: 
        pwm = [0,0]
        return pwm
        
