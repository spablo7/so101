"""Mueve UN servo Feetech STS3215 a una posición y lo devuelve, con fuerza limitada.
Escribe solo registros de memoria temporal (se pierden al apagar) y los deja como estaban.
Uso: python3 so101_mover_uno.py PUERTO ID DESTINO MIN MAX
  MIN y MAX son los topes medidos a mano; el destino tiene que quedar dentro, con margen.
"""
import array, fcntl, os, select, sys, termios, time

PUERTO = sys.argv[1]
SID, DESTINO, MIN, MAX = (int(x) for x in sys.argv[2:6])
MARGEN = 100            # pasos de distancia mínima a cada tope medido
TORQUE = 300            # 30 % (escala 0 a 1000)
VELOCIDAD = 300         # pasos por segundo (26° por segundo)
ACELERACION = 10        # x100 pasos/s²
TEMP_MAX = 50           # °C: sobre esto se suelta el torque

# Direcciones del STS3215
MODO, TORQUE_ON, ACEL, META, VEL, LIM_TORQUE = 33, 40, 41, 42, 46, 48
POS, CARGA, VOLT, TEMP, ESTADO, CORRIENTE = 56, 60, 62, 63, 65, 69

fd = os.open(PUERTO, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = 0; a[1] = 0; a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL; a[3] = 0
a[6][termios.VMIN] = 0; a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
fcntl.ioctl(fd, 0x80045402, array.array("i", [1_000_000]), 1)
termios.tcflush(fd, termios.TCIOFLUSH)


def tx(instr, params, ndatos):
    c = bytes([SID, len(params) + 2, instr]) + params
    p = b"\xff\xff" + c + bytes([(~sum(c)) & 0xFF])
    for _ in range(3):                                  # hasta 3 intentos
        termios.tcflush(fd, termios.TCIFLUSH)
        os.write(fd, p)
        buf = b""
        fin = time.time() + 0.03
        while time.time() < fin and len(buf) < 6 + ndatos:
            r, _, _ = select.select([fd], [], [], 0.002)
            if r:
                buf += os.read(fd, 64)
        if (len(buf) == 6 + ndatos and buf[:3] == b"\xff\xff" + bytes([SID])
                and (~sum(buf[2:-1])) & 0xFF == buf[-1]):
            return buf[4], buf[5:-1]
    raise RuntimeError(f"el servo {SID} no respondió a la instrucción {instr} {params.hex()}")


def leer(d, n):
    return int.from_bytes(tx(0x02, bytes([d, n]), n)[1], "little")


def escribir(d, valor, n):
    err, _ = tx(0x03, bytes([d]) + valor.to_bytes(n, "little"), 0)
    return err


def con_signo(v, bit=15):
    return -(v & ((1 << bit) - 1)) if v & (1 << bit) else v


def ir_a(meta, etiqueta):
    escribir(META, meta, 2)
    t0 = time.time()
    max_i = max_c = 0
    min_v = 99.0
    llegada = None
    traza = []
    sig = 0.0
    dist0 = abs(leer(POS, 2) - meta)
    ventana = dist0 / VELOCIDAD + 3                     # el viaje más 3 s: se sigue mirando después de llegar
    reposo = []                                         # (posición, carga, corriente) del último medio segundo
    while time.time() - t0 < ventana:
        t = time.time() - t0
        p = leer(POS, 2)
        i = abs(con_signo(leer(CORRIENTE, 2))) * 6.5
        c = abs(con_signo(leer(CARGA, 2), 10)) / 10
        v = leer(VOLT, 1) / 10
        temp = leer(TEMP, 1)
        est = leer(ESTADO, 1)
        tq = leer(TORQUE_ON, 1)
        max_i, max_c, min_v = max(max_i, i), max(max_c, c), min(min_v, v)
        if t >= sig:
            traza.append(f"{t:.1f}s:{p}")
            sig += 0.25
        if temp > TEMP_MAX:                             # una lectura suelta puede ser falsa: se confirma
            temp = min(temp, leer(TEMP, 1), leer(TEMP, 1))
        if temp > TEMP_MAX or est != 0:
            raise RuntimeError(f"corte de seguridad: {temp} °C, registro de fallas {est}")
        if tq != 1:
            raise RuntimeError(f"el servo perdió el torque solo a los {t:.2f} s (posición {p}, {v} V): se reinició")
        if abs(p - meta) > dist0 + 300:
            raise RuntimeError(f"se aleja de la meta en vez de acercarse (posición {p}): corte")
        if llegada is None and abs(p - meta) <= 15:
            llegada = t
        if t > ventana - 0.5:
            reposo.append((p, c, i))
        time.sleep(0.01)
    n = max(1, len(reposo))
    print(f"{etiqueta}: meta {meta}, primera llegada a los {llegada if llegada is None else round(llegada, 2)} s, "
          f"posición final {leer(POS, 2)}, corriente máx {max_i:.0f} mA, carga máx {max_c:.0f} %, "
          f"voltaje mín {min_v:.1f} V")
    print(f"   en reposo sobre la meta: carga media {sum(r[1] for r in reposo) / n:.0f} %, "
          f"corriente media {sum(r[2] for r in reposo) / n:.0f} mA")
    print("   traza " + " ".join(traza[::2]))


assert MIN + MARGEN <= DESTINO <= MAX - MARGEN, "el destino queda fuera del recorrido medido"
modo = leer(MODO, 1)
assert modo == 0, f"el servo no está en modo posición (modo {modo}); no se mueve"
inicio = leer(POS, 2)
previos = {"torque": leer(LIM_TORQUE, 2), "vel": leer(VEL, 2), "acel": leer(ACEL, 1)}
print(f"Servo {SID}: posición {inicio}, {leer(VOLT, 1) / 10:.1f} V, {leer(TEMP, 1)} °C, "
      f"límite de torque {previos['torque']}, velocidad {previos['vel']}, aceleración {previos['acel']}")

try:
    escribir(LIM_TORQUE, TORQUE, 2)
    escribir(ACEL, ACELERACION, 1)
    escribir(VEL, VELOCIDAD, 2)
    escribir(META, inicio, 2)                          # la meta es donde ya está: no salta al activar
    escribir(TORQUE_ON, 1, 1)
    time.sleep(0.3)
    ir_a(DESTINO, "Ida")
    ir_a(inicio, "Vuelta")
finally:
    escribir(TORQUE_ON, 0, 1)                          # pase lo que pase, se suelta el torque
    escribir(LIM_TORQUE, previos["torque"], 2)
    escribir(VEL, previos["vel"], 2)
    escribir(ACEL, previos["acel"], 1)
    print(f"Final: torque {'activo' if leer(TORQUE_ON, 1) else 'suelto'}, posición {leer(POS, 2)}, "
          f"{leer(TEMP, 1)} °C, registro de fallas {leer(ESTADO, 1)}, "
          f"límite de torque {leer(LIM_TORQUE, 2)}, velocidad {leer(VEL, 2)}, aceleración {leer(ACEL, 1)}")
    os.close(fd)
