"""Solo lectura: pregunta a cada servo Feetech del bus si está y lee su estado.
No escribe ningún registro ni activa el torque. Uso: python3 so101_leer.py /dev/cu.usbmodemXXXX
"""
import array, fcntl, os, select, sys, termios, time

PUERTO = sys.argv[1]
BAUD = 1_000_000          # velocidad de fábrica de los STS3215
IOSSIOSPEED = 0x80045402  # ioctl de macOS para velocidades no estándar


def abrir():
    fd = os.open(PUERTO, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = 0                                   # iflag
    a[1] = 0                                   # oflag
    a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    a[3] = 0                                   # lflag
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    fcntl.ioctl(fd, IOSSIOSPEED, array.array("i", [BAUD]), 1)
    termios.tcflush(fd, termios.TCIOFLUSH)
    return fd


def chk(cuerpo):
    return (~sum(cuerpo)) & 0xFF


def pedir(fd, sid, instr, params=b"", espera=0.03):
    cuerpo = bytes([sid, len(params) + 2, instr]) + params
    paquete = b"\xff\xff" + cuerpo + bytes([chk(cuerpo)])
    termios.tcflush(fd, termios.TCIFLUSH)
    os.write(fd, paquete)
    buf = b""
    fin = time.time() + espera
    while time.time() < fin:
        r, _, _ = select.select([fd], [], [], 0.005)
        if r:
            buf += os.read(fd, 64)
    if buf.startswith(paquete):                # algunas placas devuelven el eco
        buf = buf[len(paquete):]
    i = buf.find(b"\xff\xff" + bytes([sid]))
    if i < 0 or len(buf) < i + 6:
        return None
    largo = buf[i + 3]
    resp = buf[i:i + 4 + largo]
    if len(resp) < 4 + largo or chk(resp[2:-1]) != resp[-1]:
        return None
    return resp[4], resp[5:-1]                 # (byte de error, datos)


def leer(fd, sid, dir_, n):
    r = pedir(fd, sid, 0x02, bytes([dir_, n]))
    if not r or len(r[1]) != n:
        return None
    return int.from_bytes(r[1], "little")


fd = abrir()
encontrados = []
for sid in range(0, 21):
    if pedir(fd, sid, 0x01) is not None:       # PING
        encontrados.append(sid)
print(f"Servos que responden (IDs 0 a 20, {BAUD} baudios): {encontrados}")
for sid in encontrados:
    modelo = leer(fd, sid, 3, 2)
    pos = leer(fd, sid, 56, 2)
    volt = leer(fd, sid, 62, 1)
    temp = leer(fd, sid, 63, 1)
    torque = leer(fd, sid, 40, 1)
    v = f"{volt / 10:.1f} V" if volt is not None else "?"
    print(f"  ID {sid}: modelo {modelo}, posición {pos}/4095, {v}, {temp} °C, torque {'activo' if torque else 'suelto'}")
os.close(fd)
