# RPS Design V2 (Epitrocoidal)

    pip install -r requirements.txt
    python main.py

Copiar los 5 módulos de Qt Designer (sin cambios) a la raíz o a `ui/designer/`:
`Seleccion_de_sistema.py, EpitrocoidalV2.py, ToothProfile_Window.py, Graficas_Window.py,
Perfildevelocidad_simulador_Window.py`. Seleccion_de_sistema necesita la carpeta `Recursos/`.
Tests: `python -m pytest tests`

## Motor real
Archivo → Ajustes → Motor: puerto, relación, rpm máx., ACEL; "Conectar"; marcar "Ejecutar en el motor al
dar Play". Sin hardware: "Motor simulado". Protocolo: `MOVE <revs> <rpm>` (bloqueante) y `S`.
