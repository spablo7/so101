"""Demo del brazo SO-101: despierta, mira a los lados, asiente, saluda con la mano y se guarda.
Dura unos 25 segundos. Parte y termina en la postura en que esté el brazo al empezar (plegado y
apoyado), y solo ahí suelta el torque. Toda meta se recorta a los límites grabados en cada servo.

Uso: python3 so101_demo.py PUERTO            corre la demo
     python3 so101_demo.py PUERTO --ensayo   no mueve nada: lee el brazo y muestra los pasos
"""
import array, fcntl, os, select, sys, termios, time

PUERTO = sys.argv[1]
ENSAYO = "--ensayo" in sys.argv
BASE, HOMBRO, CODO, FLEX, GIRO, PINZA = 1, 2, 3, 4, 5, 6
NOMBRE = {1: "base", 2: "hombro", 3: "codo", 4: "flexión", 5: "giro", 6: "pinza"}
TORQUE = {BASE: 600, HOMBRO: 850, CODO: 850, FLEX: 600, GIRO: 500, PINZA: 400}   # escala 0 a 1000
# x100 pasos/s²: suave en las articulaciones que cargan peso, viva en la muñeca y la pinza
ACEL = {BASE: 20, HOMBRO: 8, CODO: 10, FLEX: 150, GIRO: 30, PINZA: 50}   # FLEX alta: con 40 el vaivén del saludo quedaba en 13° de los 33° pedidos
TEMP_MAX = 55

fd = os.open(PUERTO, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = 0; a[1] = 0; a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL; a[3] = 0
a[6][termios.VMIN] = 0; a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
fcntl.ioctl(fd, 0x80045402, array.array("i", [1_000_000]), 1)
termios.tcflush(fd, termios.TCIOFLUSH)


def tx(sid, instr, params, n):
    c = bytes([sid, len(params) + 2, instr]) + params
    p = b"\xff\xff" + c + bytes([(~sum(c)) & 0xFF])
    for _ in range(4):
        termios.tcflush(fd, termios.TCIFLUSH)
        os.write(fd, p)
        buf = b""
        fin = time.time() + 0.03
        while time.time() < fin and len(buf) < 6 + n:
            r, _, _ = select.select([fd], [], [], 0.002)
            if r:
                buf += os.read(fd, 64)
        if len(buf) == 6 + n and buf[2] == sid and (~sum(buf[2:-1])) & 0xFF == buf[-1]:
            return buf[5:-1]
    raise RuntimeError(f"el servo {sid} ({NOMBRE[sid]}) dejó de responder")


def leer(sid, d, n):
    return int.from_bytes(tx(sid, 0x02, bytes([d, n]), n), "little")


def escribir(sid, d, v, n):
    tx(sid, 0x03, bytes([d]) + v.to_bytes(n, "little"), 0)


IDS = [BASE, HOMBRO, CODO, FLEX, GIRO, PINZA]
lim = {s: (leer(s, 9, 2), leer(s, 11, 2)) for s in IDS}
reposo = {s: leer(s, 56, 2) for s in IDS}
previos = {s: (leer(s, 48, 2), leer(s, 46, 2), leer(s, 41, 1)) for s in IDS}
for s in IDS:
    assert leer(s, 33, 1) == 0, f"servo {s} fuera del modo posición"


def rec(s, v):
    return max(lim[s][0], min(lim[s][1], int(v)))


R = reposo
centro_base = rec(BASE, R[BASE])
alto = {CODO: rec(CODO, R[CODO] - 900), HOMBRO: rec(HOMBRO, R[HOMBRO] + 510), FLEX: rec(FLEX, 2000)}
mano = {CODO: rec(CODO, R[CODO] - 1400)}     # antebrazo casi vertical para saludar

# Cada paso: (qué se ve, segundos, {servo: meta})
SUBIR = [
    ("levanta el antebrazo", 2.2, {CODO: alto[CODO]}),
    ("se endereza", 2.2, {HOMBRO: alto[HOMBRO], FLEX: alto[FLEX]}),
]
NUMERO = [
    ("mira a un lado", 1.3, {BASE: centro_base + 450}),
    ("mira al otro", 2.0, {BASE: centro_base - 450}),
    ("vuelve al frente", 1.2, {BASE: centro_base}),
    ("asiente", 0.6, {FLEX: alto[FLEX] + 350}),
    ("asiente", 0.6, {FLEX: alto[FLEX]}),
    ("asiente", 0.6, {FLEX: alto[FLEX] + 350}),
    ("asiente", 0.6, {FLEX: alto[FLEX]}),
    # El saludo: levanta el antebrazo, pone la mano de canto (muñeca girada 90°) y la mueve de lado a lado
    ("levanta la mano", 1.5, {CODO: mano[CODO], FLEX: 2000, GIRO: 3072, PINZA: 3450}),
    ("saluda", 0.45, {FLEX: 2380, BASE: centro_base + 180}, True),
    ("saluda", 0.55, {FLEX: 1620, BASE: centro_base - 180}, True),
    ("saluda", 0.55, {FLEX: 2380, BASE: centro_base + 180}, True),
    ("saluda", 0.55, {FLEX: 1620, BASE: centro_base - 180}, True),
    ("saluda", 0.55, {FLEX: 2380, BASE: centro_base + 180}, True),
    ("saluda", 0.55, {FLEX: 1620, BASE: centro_base - 180}, True),
    ("saluda", 0.45, {FLEX: 2000, BASE: centro_base}, True),
    ("baja la mano", 1.4, {CODO: alto[CODO], GIRO: 2048, PINZA: 2150}),
]
GUARDAR = [
    ("se acomoda", 1.2, {BASE: R[BASE], GIRO: R[GIRO], PINZA: R[PINZA], FLEX: R[FLEX]}),
    ("baja el hombro", 2.4, {HOMBRO: R[HOMBRO]}),
    ("pliega el antebrazo", 2.4, {CODO: R[CODO]}),
]


def paso(que, seg, metas, ritmo=False):
    metas = {s: rec(s, v) for s, v in metas.items()}
    if ENSAYO:
        print(f"  {seg:>4.1f} s  {que:<26} " + ", ".join(f"{NOMBRE[s]} {leer(s, 56, 2) if s not in sim else sim[s]}→{v}" for s, v in metas.items()))
        sim.update(metas)
        return
    for s, v in metas.items():
        dist = abs(v - leer(s, 56, 2))
        escribir(s, 46, max(60, min(3000, int(dist / seg * (1.8 if ritmo else 1.25)))), 2)   # sobre la media: deja tiempo para acelerar y frenar
        escribir(s, 42, v, 2)
    t0 = time.time()
    while time.time() - t0 < (seg if ritmo else seg + 1.5):
        listo = True
        for s in IDS:
            if s in metas and abs(leer(s, 56, 2) - metas[s]) > 30:
                listo = False
            if leer(s, 40, 1) != 1:
                raise RuntimeError(f"{NOMBRE[s]} perdió el torque (se reinició)")
        if listo and not ritmo and time.time() - t0 >= seg * 0.8:
            break
    for s in IDS:
        t = leer(s, 63, 1)
        if t > TEMP_MAX:
            t = min(t, leer(s, 63, 1), leer(s, 63, 1))     # una lectura suelta puede ser falsa
        if t > TEMP_MAX or leer(s, 65, 1) != 0:
            raise RuntimeError(f"{NOMBRE[s]}: {t} °C, registro de fallas {leer(s, 65, 1)}")
    print(f"  {time.time() - t0:>4.1f} s  {que:<26} " + ", ".join(f"{NOMBRE[s]} {leer(s, 56, 2)} (meta {v})" for s, v in metas.items()))


print("Límites:", {NOMBRE[s]: lim[s] for s in IDS})
print("Postura de partida:", {NOMBRE[s]: reposo[s] for s in IDS})
if ENSAYO:
    sim = {}
    print("ENSAYO, no se mueve nada:")
    for p in SUBIR + NUMERO + GUARDAR:
        paso(*p)
    print(f"Duración prevista: {sum(p[1] for p in SUBIR + NUMERO + GUARDAR):.0f} s")
    os.close(fd)
    sys.exit(0)

arriba = False
try:
    for s in IDS:
        escribir(s, 48, TORQUE[s], 2)
        escribir(s, 41, ACEL[s], 1)
        escribir(s, 46, 200, 2)
        escribir(s, 42, reposo[s], 2)                  # la meta es donde ya está: no salta al activar
        escribir(s, 40, 1, 1)
    time.sleep(0.4)
    arriba = True
    for p in SUBIR + NUMERO:
        paso(*p)
    for p in GUARDAR:
        paso(*p)
    arriba = False
except (RuntimeError, KeyboardInterrupt) as e:
    print("CORTE:", e if str(e) else "interrumpido")
    if arriba:                                         # nunca se suelta el torque con el brazo en alto
        print("Se guarda antes de soltar:")
        for p in GUARDAR:
            try:
                paso(*p)
            except RuntimeError as e2:
                print("  no se pudo:", e2)
finally:
    time.sleep(0.4)
    for s in IDS:
        try:
            escribir(s, 40, 0, 1)
            escribir(s, 48, previos[s][0], 2); escribir(s, 46, previos[s][1], 2); escribir(s, 41, previos[s][2], 1)
        except RuntimeError as e:
            print("  al soltar:", e)
    print("Final:", ", ".join(f"{NOMBRE[s]} {leer(s, 56, 2)} {leer(s, 63, 1)}°C torque {leer(s, 40, 1)}" for s in IDS))
    os.close(fd)
