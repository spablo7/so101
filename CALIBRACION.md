# Registro de lo grabado en los motores

Cada valor que se cambia en la memoria permanente de un motor se anota aquí con el valor que
tenía antes, para poder volver atrás. Las posiciones van en pasos (4096 por vuelta).

## 10-11-2026: límites y centro de la muñeca

Los límites se midieron con la mano dos veces. Cada uno es el tope más corto de las dos
mediciones, menos 20 pasos de margen.

| Motor | Articulación | Límites que traía | Límites grabados | Corrección de cero |
|---|---|---|---|---|
| 1 | Giro de la base | 1448 a 3071 | 704 a 3339 | −2012 (sin cambio) |
| 2 | Hombro | 902 a 3207 | 864 a 3197 | 1930 (sin cambio) |
| 3 | Codo | 904 a 3107 | 899 a 3087 | −2008 (sin cambio) |
| 4 | Muñeca, flexión | 812 a 3152 | 899 a 3191 | 1769 (sin cambio) |
| 5 | Muñeca, giro | 0 a 4095 | 341 a 3755 | −1270 (traía −180) |
| 6 | Pinza | 1337 a 2826 | 2046 a 3500 | 1699 (sin cambio) |

- **La corrección de cero** es un número que el motor resta a su posición real antes de
  informarla: posición informada = posición real − corrección. Está en la dirección 31 de la
  memoria, con el signo en el bit 11.
- **El giro de muñeca (motor 5)** se dejó con su centro en 2048, que es la posición con la pinza
  derecha y el cable relajado, y con 150° de límite a cada lado. Durante la jornada pasó por una
  corrección intermedia de −1312 y volvió por un rato a la original.
- **Lo grabado sobrevive a apagar y encender la fuente** (comprobado el 10-11-2026).

## Las dos mediciones con la mano

| Motor | Primera medición | Segunda medición |
|---|---|---|
| 1 | 665 a 3359 | 684 a 3400 |
| 2 | 818 a 3257 | 844 a 3217 |
| 3 | 875 a 3123 | 879 a 3107 |
| 4 | 864 a 3241 | 879 a 3211 |
| 6 | 2011 a 3542 | 2026 a 3520 |

El motor 5 no tiene topes que medir.

## Otros ajustes que traían los motores

Iguales en los seis, salvo donde se indica, y no se cambiaron: modo de posición (dirección 33 en
0), fase 12 (dirección 18), ajustes de control 16, 32 y 0 (direcciones 21, 22 y 23), y tope de
fuerza 1000 (dirección 16), con 500 en la pinza. Versión del programa interno: 3.10.
