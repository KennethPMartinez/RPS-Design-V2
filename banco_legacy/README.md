# banco_legacy

Código archivado del control del banco físico (motor paso a paso / Arduino) que salió de RPS Design V2 (decisión del 22-nov-2026): el botón «Control de banco» abrirá una aplicación independiente.
Nada de aquí se importa desde la app. `motor_plan.py` es cálculo puro (sin Qt ni serial) y su test sigue pasando: `python -m unittest banco_legacy.test_motor_plan`.
`hardware/` y `Arduino_Test.py` requieren pyserial. `epitrocoidal_window_obsoleta.py` era una copia sin uso de la ventana base.
