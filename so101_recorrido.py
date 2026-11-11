"""Solo lectura: registra la posición de los servos 1 a 6 durante N segundos y
entrega el mínimo y el máximo de cada uno. No escribe registros ni activa torque.
Uso: python3 so101_recorrido.py /dev/cu.usbmodemXXXX 120 salida.csv
"""
import array, fcntl, os, select, sys, termios, time

PUERTO, DURACION, SALIDA = sys.argv[1], float(sys.argv[2]), sys.argv[3]
IDS = [1, 2, 3, 4, 5, 6]

fd = os.open(PUERTO, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = 0; a[1] = 0; a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL; a[3] = 0
a[6][termios.VMIN] = 0; a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
fcntl.ioctl(fd, 0x80045402, array.array("i", [1_000_000]), 1)
termios.tcflush(fd, termios.TCIOFLUSH)


def posicion(sid):
    c = bytes([sid, 4, 2, 56, 2])                      # LEER 2 bytes desde la dirección 56
    p = b"\xff\xff" + c + bytes([(~sum(c)) & 0xFF])
    termios.tcflush(fd, termios.TCIFLUSH)
    os.write(fd, p)
    buf = b""
    fin = time.time() + 0.02
    while time.time() < fin and len(buf) < 8:
        r, _, _ = select.select([fd], [], [], 0.002)
        if r:
            buf += os.read(fd, 64)
    if len(buf) < 8 or buf[:3] != b"\xff\xff" + bytes([sid]):
        return None
    if (~sum(buf[2:7])) & 0xFF != buf[7]:
        return None
    return int.from_bytes(buf[5:7], "little")


ini = {s: None for s in IDS}
mn = {s: 9999 for s in IDS}
mx = {s: -1 for s in IDS}
ant = {s: None for s in IDS}
primer_mov = {s: None for s in IDS}
saltos = {s: 0 for s in IDS}
fallas = {s: 0 for s in IDS}
n = 0
t0 = time.time()
with open(SALIDA, "w") as f:
    f.write("t," + ",".join(f"id{s}" for s in IDS) + "\n")
    while time.time() - t0 < DURACION:
        t = time.time() - t0
        fila = []
        for s in IDS:
            p = posicion(s)
            fila.append("" if p is None else str(p))
            if p is None:
                fallas[s] += 1
                continue
            if ini[s] is None:
                ini[s] = p
            if ant[s] is not None and abs(p - ant[s]) > 2000:
                saltos[s] += 1                          # el contador dio la vuelta (4095 <-> 0)
            ant[s] = p
            mn[s] = min(mn[s], p)
            mx[s] = max(mx[s], p)
            if primer_mov[s] is None and abs(p - ini[s]) > 80:
                primer_mov[s] = t
        f.write(f"{t:.3f}," + ",".join(fila) + "\n")
        n += 1

os.close(fd)
print(f"{n} lecturas en {DURACION:.0f} s ({n / DURACION:.0f} por segundo)")
for s in IDS:
    rec = mx[s] - mn[s]
    pm = "no se movió" if primer_mov[s] is None else f"se movió a los {primer_mov[s]:.0f} s"
    print(f"ID {s}: inicio {ini[s]}, mín {mn[s]}, máx {mx[s]}, recorrido {rec} pasos = {rec * 360 / 4096:.0f}°, "
          f"final {ant[s]}, {pm}, vueltas del contador {saltos[s]}, lecturas fallidas {fallas[s]}")
