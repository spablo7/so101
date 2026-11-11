# Brazo robótico SO-101 manejado desde un Mac, sin drivers ni librerías

Este repositorio tiene los programas con que se puso en marcha un brazo robótico SO-101 el
10-11-2026, en una tarde, y el registro de lo que se aprendió en el camino. El SO-101 es un brazo
de seis motores, de diseño abierto e impreso en 3D, pensado para aprender robótica.

Hay dos cosas adentro:

- **Cuatro programas de Python** que leen el brazo, miden su recorrido, mueven un motor y corren
  una demostración de 25 segundos. Usan solo lo que Python trae de fábrica.
- **Un panel que se abre en Google Chrome** para mover cada articulación, guardar posturas y armar
  secuencias de movimiento.

**En qué estado está.** Los seis motores quedaron calibrados. La demostración corrió completa dos
veces, pero la versión que está aquí tiene una corrección posterior que no se ha corrido. El panel
conectó con el brazo real y activó la fuerza de los motores; no quedó registrado cómo respondieron
sus controles. Al final de la jornada el brazo se cayó mientras se manejaba con el panel, y lo
apagamos sin revisarlo. Lo pendiente está en [ABIERTO.md](ABIERTO.md).

## Las palabras que se usan

- **Motor o servo:** cada articulación tiene un motor Feetech STS3215, que además mide su propia
  posición, voltaje y temperatura. Están numerados del 1 al 6, desde la base hasta la pinza.
- **Paso:** la unidad en que el motor mide su posición. Una vuelta completa son 4096 pasos, así
  que 11 pasos son cerca de 1°.
- **Torque:** la fuerza con que el motor sostiene su posición. Con el torque suelto, el brazo se
  mueve con la mano; con el torque activado, obedece a las órdenes y se resiste a la mano.
- **Límite:** la posición mínima y máxima que un motor acepta como orden. Queda grabada dentro
  del motor.

## Qué se necesita

| Pieza | La que se usó |
|---|---|
| Brazo | SO-101 «seguidor» (el que tiene pinza), con seis motores Feetech STS3215 de 7,4 V |
| Placa | Feetech URT-2, que une el USB del computador con el cable de datos de los motores |
| Fuente | De laboratorio. Se partió en 5,0 V y se terminó en 6,1 V |
| Computador | Mac con Python 3 y Google Chrome. No se instaló ningún driver ni librería |

Sobre el voltaje: 7,4 V es el máximo de estos motores, no el voltaje al que hay que ponerlos.
Con 5,0 V responden y se mueven; con más voltaje tienen más fuerza. Sobre 7,4 V se dañan.

Los programas de Python abren el puerto con funciones propias de macOS. En Linux o Windows hay
que cambiar esa parte; no se probó. El panel de Chrome no depende del sistema.

## Cómo se conecta

1. **La fuente a la placa.** El negativo va al borne marcado **G** y el positivo al borne **V1**,
   con los cables atornillados directo. Los otros dos bornes (G y V2) son de otra salida y quedan
   vacíos.
2. **El brazo a la placa**, con su cable de tres hilos, en el enchufe marcado «S V1 G».
3. **La placa al computador**, por USB. El USB alimenta solo la placa: sin la fuente, los motores
   no responden.

Con todo bien, la fuente marca cerca de 0,13 A con el brazo quieto y el torque suelto.

En el Mac la placa aparece como un puerto de nombre `/dev/cu.usbmodem…`. El nombre completo se
obtiene con el comando `ls /dev/cu.usbmodem*`.

## Los programas

En todos, `PUERTO` es el nombre que entregó `ls /dev/cu.usbmodem*`.

| Programa | Qué hace | ¿Mueve el brazo? |
|---|---|---|
| `python3 so101_leer.py PUERTO` | Dice qué motores responden y lee de cada uno posición, voltaje, temperatura y torque | No |
| `python3 so101_recorrido.py PUERTO SEGUNDOS SALIDA.csv` | Registra la posición de los seis mientras se mueven con la mano y entrega el mínimo y el máximo de cada uno | No |
| `python3 so101_mover_uno.py PUERTO MOTOR DESTINO MIN MAX` | Lleva un motor a la posición `DESTINO` y lo devuelve, lento y con la fuerza al 30 %. `MIN` y `MAX` son los topes de ese motor medidos con la mano: el programa se niega a correr si el destino queda a menos de 100 pasos de alguno. Corta solo si el motor se aleja de la meta o pierde el torque | Sí |
| `python3 so101_demo.py PUERTO` | La demostración: el brazo se endereza, mira a los lados, asiente, saluda y se guarda. Con `--ensayo` al final muestra los pasos sin mover nada | Sí |
| `so101_panel.html` | El panel de Chrome, descrito abajo | Sí |

Para partir, lo seguro es `so101_leer.py`: no mueve nada y confirma que el cableado está bien.

**Sobre la demostración.** En su segunda corrida el saludo salió más corto de lo diseñado. Se
corrigió un número, la aceleración de la muñeca, y esa versión es la que está aquí: no se ha
corrido. Quien la corra primero la está probando.

**No hay un programa que grabe los límites.** Se grabaron con órdenes escritas en el momento,
siguiendo el procedimiento de la sección de calibración. Falta empaquetarlo.

## El panel de Chrome

Se abre el archivo `so101_panel.html` en Google Chrome y se pulsa «Conectar el brazo». Chrome
muestra una lista de puertos; se elige el de la placa. La página habla con los motores por Web
Serial, la función de Chrome que permite a una página usar un puerto USB con permiso de la persona.

**Qué está comprobado y qué no.** Con seis motores simulados se probó el recorrido completo. Con
el brazo real se comprobó que conecta, lee los seis motores y activa el torque. Lo demás de esta
lista describe cómo está construido, no algo visto con el brazo real:

- **Un control por articulación**, que llega solo hasta los límites grabados en cada motor.
- **Enseñar con la mano:** con el torque suelto, se mueve el brazo y los controles lo siguen.
- **Posturas guardadas**, con nombre.
- **Secuencia:** una lista de pasos, cada uno con una postura, un tiempo y una pausa. Las seis
  articulaciones llegan juntas a cada postura.
- **Reposo:** la postura en que está el brazo la primera vez que se activa el torque, que debe ser
  plegado y apoyado. «Volver a Reposo y soltar» lo lleva ahí antes de cortar la fuerza.
- **«Soltar ahora»** corta la fuerza de inmediato. Es la salida de emergencia: si el brazo está
  en alto, cae.

Solo un programa puede usar el puerto a la vez: con el panel conectado, los programas de Python
no pueden abrirlo.

## La calibración de este brazo

Calibrar fue medir con la mano, dos veces, hasta dónde llega cada articulación, y grabar esos
límites en cada motor con 20 pasos de margen (cerca de 2°), para que el motor no quede empujando
contra el plástico. El giro de muñeca es la excepción: no tiene topes que medir, así que se le
fijó un centro, que es la postura con la pinza derecha y el cable relajado, y un límite de 150° a
cada lado de ese centro.

| Motor | Articulación | Límites grabados (pasos) | Recorrido |
|---|---|---|---|
| 1 | Giro de la base | 704 a 3339 | 232° |
| 2 | Hombro | 864 a 3197 | 205° |
| 3 | Codo | 899 a 3087 | 192° |
| 4 | Muñeca, flexión | 899 a 3191 | 201° |
| 5 | Muñeca, giro | 341 a 3755 | 300° |
| 6 | Pinza | 2046 a 3500 | 128° |

**Estos números son de este brazo.** Otro SO-101 tendrá los suyos, porque dependen de cómo quedó
montado cada motor. La demostración usa varias posiciones fijas tomadas de esta calibración, así
que en otro brazo hay que calibrar primero y revisar esas posiciones con `--ensayo`.

Cómo se graba un límite: con el torque suelto, se escribe 0 en la dirección 55 de la memoria del
motor (abre el candado), el mínimo en la dirección 9 y el máximo en la 11 (2 bytes cada uno), y
1 en la 55 (cierra el candado). Los valores anteriores y las mediciones están en
[CALIBRACION.md](CALIBRACION.md).

## Lo que se aprendió por las malas

1. **La polaridad invertida se nota en la fuente.** Con los cables al revés, la fuente saltó a
   su tope de 5 A con el voltaje caído a 1,4 V, y ningún motor respondía. Si al encender la fuente
   pasa a corriente constante (luz «C.C.»), hay que apagarla de inmediato.
2. **Un motor ignora una meta fuera de sus límites: va hasta el límite y se queda ahí.** La
   primera vez pareció una falla del motor. Antes de concluir que un motor falla, se leen sus
   límites grabados.
3. **El brazo puede traer una calibración anterior que no le corresponde.** Este traía límites
   grabados que no calzaban con su montaje: los de la pinza estaban corridos unos 60°.
4. **El giro de la muñeca no tiene tope mecánico.** Lo único que lo limita es el cable de la
   pinza, que se enrolla. Su límite no se puede medir: hay que decidirlo y grabarlo.
5. **El motor del giro de muñeca dejó de obedecer, y no estaba dañado.** Giraba siempre hacia el
   mismo lado sin detenerse en la meta, aunque su configuración era igual a la de los demás. Con
   el cable de la pinza desenchufado se lo dejó girar libre: dio 4 vueltas y se detuvo solo, justo
   en la meta. Desde entonces llega a la meta y se detiene. La explicación que calza es que el
   motor lleva una cuenta interna de vueltas y que estaba desfasada; es una inferencia a partir de
   esa sola observación. Tampoco se comprobó qué la desfasa: se supone que es girar la muñeca con
   la mano hasta cruzar el final de su escala.
6. **El motor 5 entregó lecturas falsas de temperatura.** Informó 38 °C y 54 °C, y segundos
   después 27 °C. Por eso los programas confirman una temperatura alta con dos lecturas más antes
   de cortar.
7. **En uso normal no se suelta el torque con el brazo en alto.** La demostración y «Volver a
   Reposo y soltar» pliegan el brazo antes de soltar, y la demostración lo intenta también cuando
   algo falla a mitad de camino. Las dos salidas de emergencia sí lo dejan caer: «Soltar ahora» y
   apagar la fuente.

## Antes de mover el brazo

- **Primero, revisarlo después de la caída:** piezas impresas, conectores y una lectura con
  `so101_leer.py`. Está en [ABIERTO.md](ABIERTO.md).
- La base va fija a la mesa, con 40 cm despejados alrededor. Cómo se fijó ese día no quedó
  registrado, y una de las dos causas posibles de la caída es que se haya soltado.
- Manos lejos mientras se mueve. Si algo se ve mal, se apaga la fuente: el brazo cae, pero se
  detiene.
- Por precaución, la muñeca no se gira con la mano más de media vuelta desde su centro.

## Otros proyectos para este brazo

Salen de una búsqueda del 10-11-2026 y de lo que el buscador resumió de cada uno: ninguna página
se abrió en primera mano y nada se instaló. No apareció una colección de movimientos ya hechos
para reproducir.

| Proyecto | Para qué sirve, según el buscador |
|---|---|
| [LeRobot](https://huggingface.co/docs/lerobot), de Hugging Face | Calibra el brazo, lo maneja con un segundo brazo, teclado o control de juegos, y graba y reproduce movimientos |
| [SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100), de The Robot Studio | El repositorio del diseño del brazo, con su modelo con medidas |
| robokin (`legalaspro/robokin` en GitHub) | Calcula qué ángulo poner en cada articulación para llevar la pinza a un punto |
| [phosphobot](https://github.com/phospho-app/phosphobot) | Maneja el brazo con teclado, control de juegos o visor de realidad virtual |
| [LeRobot.js](https://huggingface.co/blog/NERDDISCO/lerobotjs) y bambot (`timqian/bambot` en GitHub) | Hablan con los motores desde Chrome, como el panel de este repositorio |
