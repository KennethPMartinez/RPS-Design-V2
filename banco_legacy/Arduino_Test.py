import time
import serial

class Motor:
    PASOS_REV = 6400
    ACEL = 4000.0

    def __init__(self, puerto, baud=115200):
        self.ser = serial.Serial(puerto, baud, timeout=2)
        time.sleep(2)                 # la Mega se reinicia al abrir el puerto
        self.ser.reset_input_buffer()

    def mover(self, revs, rpm):
        # Estimar duración para fijar el timeout
        v = rpm * self.PASOS_REV / 60
        t_rampa = v / self.ACEL
        t_est = abs(revs) * 60 / rpm + t_rampa + 3
        self.ser.timeout = t_est

        self.ser.write(f"MOVE {revs} {rpm}\n".encode())
        resp = self.ser.readline().decode().strip()
        if resp != "OK":
            raise RuntimeError(f"Respuesta inesperada: {resp!r}")

    def parar(self):
        self.ser.write(b"S")

    def cerrar(self):
        self.ser.close()


if __name__ == "__main__":
    m = Motor("COM3")        # en Linux/Mac: "/dev/ttyACM0"
    try:
        m.mover(600, 20)     # ida
        time.sleep(1)
        #m.mover(-100, 100)    # regreso
    except KeyboardInterrupt:
        m.parar()
    finally:
        m.cerrar()