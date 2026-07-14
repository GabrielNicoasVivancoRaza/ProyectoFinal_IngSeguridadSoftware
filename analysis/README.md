# Análisis estadístico

Evaluación experimental de los módulos criptográficos de la plataforma.

## Ejecución

```bash
pip install -r requirements.txt

python benchmark.py   # ejecuta las mediciones -> results/*.csv
python analyze.py     # estadísticos + gráficos -> results/*.png
```

`benchmark.py` importa los módulos **reales** del backend (`app.crypto.*`), por lo que
las métricas corresponden al código de producción, no a una simulación.

## Experimentos realizados

| Experimento | Repeticiones |
|---|---|
| Hash SHA-256 (10 KB, 100 KB, 1 MB) | 30 por tamaño |
| Cifrado / descifrado AES-256-GCM | 10 por tamaño |
| Firma / verificación RSA-PSS | 10 por tamaño |
| Generación de claves RSA-2048 | 5 |
| Emisión de certificado X.509 | 5 |
| Validación de certificado | 20 |
| Hash / verificación de contraseña (bcrypt) | 10 |
| Detección de alteraciones (hash, firma, AES-GCM) | 50 cada uno |
| Autenticación (correcta / incorrecta) | 15 cada una |

## Salidas

| Archivo | Contenido |
|---|---|
| `results/timings.csv` | Cada medición individual (ms) |
| `results/rates.csv` | Tasas de detección y autenticación |
| `results/summary_timings.csv` | Media, desviación estándar, mínimo y máximo |
| `results/fig_operaciones.png` | Tiempo promedio por operación |
| `results/fig_por_tamano.png` | Rendimiento según el tamaño del archivo |
| `results/fig_tasas.png` | Detección de alteraciones y autenticación |

## Hallazgos principales

- **Detección de alteraciones: 100 %** en los tres mecanismos (hash SHA-256, firma
  digital RSA-PSS y tag de AES-GCM) sobre 50 intentos cada uno.
- **Autenticación: 100 %** de aciertos con credenciales correctas y **100 %** de
  rechazos con credenciales incorrectas.
- Las operaciones más costosas son las de **derivación deliberadamente lenta**
  (bcrypt ≈ 560 ms, PBKDF2 dentro de AES) y la **generación de claves RSA** (≈ 400 ms).
  Este coste es intencional: encarece los ataques de fuerza bruta.
- El **hash SHA-256 es el más rápido** (≈ 0,007 ms en 10 KB) y escala linealmente
  con el tamaño, lo que lo hace ideal para verificar integridad.
- La **verificación de firma es mucho más rápida que firmar** (1,5 ms vs 224 ms en
  1 MB), comportamiento esperado en RSA (el exponente público es pequeño).
