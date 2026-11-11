# Lo que queda abierto en el brazo SO-101

Estado al 10-11-2026, cuando apagamos el brazo.

## Antes de volver a darle fuerza

- **Revisar el brazo después de la caída.** Se cayó mientras se manejaba con el panel, y lo
  apagamos sin revisarlo. No se sabe si se desplomó por perder el torque o si se soltó la base.
  Hay que mirar las piezas impresas y los conectores, y correr `so101_leer.py` para ver que
  responden los seis motores, su posición y su temperatura. Ese programa no muestra las fallas ni
  los límites grabados: se leen de la memoria de cada motor (dirección 65 para las fallas, 9 y 11
  para los límites) y se comparan con [CALIBRACION.md](CALIBRACION.md).

## Sin comprobar

- **El panel con el brazo real.** Conectó, leyó los seis motores y activó el torque. No quedó
  registrado cómo respondieron los controles ni si se reprodujo una secuencia.
- **La demostración con el saludo corregido.** En la segunda corrida la mano se meció unos 13°
  por lado en vez de los 33° pedidos; esa cifra se calculó desde las lecturas de los motores, no
  se midió sobre el brazo. Se subió la aceleración de la flexión de muñeca de 40 a 150 (en
  unidades de 100 pasos por segundo al cuadrado). Esa versión es la que está en el repositorio y
  no se ha corrido.
- **Los programas de Python fuera de macOS.**

## Sin explicación

- **Lecturas de voltaje que saltan en los motores 4, 5 y 6.** Con la fuente en 6,1 V y el brazo
  quieto, los motores 1 a 3 no bajan de 6,0 V; el 4 marca hasta 5,6 V, el 5 hasta 4,9 V y el 6
  hasta 4,6 V, en menos del 1 % de las lecturas. Reasentar los conectores no lo cambió. No se sabe
  si el voltaje cae de verdad o si salta la medición. En las pruebas ningún motor se reinició.
- **El giro de muñeca se movió al doble de la velocidad pedida** (unos 580 pasos por segundo con
  un tope de 300) después de grabarle su centro y sus límites. Llega a la meta y se detiene bien.
- **Qué desfasa la cuenta de vueltas del giro de muñeca**, si es que esa es la explicación. Se
  supone que es girarla con la mano hasta cruzar el final de su escala; no se comprobó. El
  problema siguió igual después de apagar y encender la fuente.

## Por hacer

- **Un programa que grabe los límites.** Hoy se hace con órdenes escritas en el momento.
- **Rediseñar el panel como un controlador de arcade.** Hay un esquema propuesto: dos palancas
  (base y hombro en una, giro de muñeca y codo en la otra), seis botones que reproducen
  movimientos, y lo que el panel ya tiene, plegado abajo. Falta decidir si se construye así.
- **Que una palanca mueva la mano en línea recta** en vez de una articulación. Necesita las
  medidas del brazo; según el buscador están en el repositorio SO-ARM100, y no se abrió.
- **Correr la demostración desde una ESP32**, un microcontrolador con wifi, para que el brazo no
  dependa de un computador. La placa URT-2 tiene una fila de cinco pines que podría servir para
  conectarla; no se revisó.
