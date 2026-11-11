# so101: el brazo robótico SO-101

Programas y registro del brazo SO-101 de Pablo. Qué es, cómo se conecta y qué se aprendió:
[README.md](README.md), que también leen sus colegas. Lo pendiente: [ABIERTO.md](ABIERTO.md).

## Reglas de este proyecto

- **Leer no necesita permiso; mover, sí.** `so101_leer.py` y `so101_recorrido.py` se corren
  cuando haga falta. Todo lo que activa el torque o escribe en la memoria de un motor se hace con
  la orden de Pablo en esa sesión, porque hay personas al lado del brazo.
- **Nunca se suelta el torque con el brazo en alto.** Un programa nuevo que mueva hombro o codo
  pliega el brazo antes de soltar, también cuando falla.
- **Antes de concluir que un motor falla, se leen sus límites grabados** (direcciones 9 y 11) y
  se prueba dejándolo terminar el movimiento con el cable de la pinza desenchufado. El 10-11-2026
  se dio dos veces por dañado un motor que estaba sano.
- **Un valor grabado en un motor se anota antes de cambiarlo**, con el valor anterior, en el
  README.
- **El panel y los programas de Python no usan el puerto a la vez.**
- El README es para personas que no estuvieron: cada término se define, y lo que no se comprobó
  se dice ahí mismo.
