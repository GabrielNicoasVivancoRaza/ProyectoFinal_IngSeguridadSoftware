"""Analisis estadistico de las metricas del benchmark criptografico.

Lee results/timings.csv y results/rates.csv, calcula estadisticos descriptivos
y genera los graficos para el articulo tecnico.

Uso:  python analyze.py   (requiere haber ejecutado antes benchmark.py)
"""
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # backend sin ventana (permite generar PNG en servidor)
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"

# --- Paleta y estilo (sistema de diseno validado) ---
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SERIES = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948"]
STATUS_GOOD = "#0ca30c"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.edgecolor": BASELINE,
    }
)


def estilo_ejes(ax, eje_x_grid=True):
    """Aplica cuadricula recesiva y elimina bordes innecesarios."""
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_color(BASELINE)
    ax.spines["bottom"].set_color(BASELINE)
    ax.grid(axis="x" if eje_x_grid else "y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def resumen_estadistico(timings: pd.DataFrame) -> pd.DataFrame:
    """Estadisticos descriptivos por operacion y tamano."""
    resumen = (
        timings.groupby(["operation", "size_label"])["duration_ms"]
        .agg(n="count", media="mean", desv_std="std", minimo="min", maximo="max")
        .round(3)
        .reset_index()
    )
    resumen.to_csv(RESULTS / "summary_timings.csv", index=False)
    return resumen


def grafico_operaciones(timings: pd.DataFrame):
    """Tiempo promedio por operacion (barras horizontales, serie unica)."""
    medias = (
        timings.groupby("operation")["duration_ms"].mean().sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.barh(
        medias.index, medias.values, color=SERIES[0], height=0.6, zorder=2
    )
    # Extremo redondeado en el borde de dato.
    for barra in barras:
        barra.set_joinstyle("round")

    # Etiquetas directas (serie unica -> sin leyenda).
    for barra, valor in zip(barras, medias.values, strict=True):
        ax.text(
            barra.get_width() * 1.02,
            barra.get_y() + barra.get_height() / 2,
            f"{valor:.2f} ms",
            va="center",
            fontsize=9,
            color=INK,
        )

    ax.set_xscale("log")  # los tiempos abarcan varios ordenes de magnitud
    ax.set_xlabel("Tiempo promedio (ms, escala logaritmica)")
    ax.set_title("Tiempo promedio por operacion criptografica", color=INK, pad=14)
    ax.set_xlim(right=medias.max() * 3)
    estilo_ejes(ax)

    fig.tight_layout()
    fig.savefig(RESULTS / "fig_operaciones.png", dpi=150)
    plt.close(fig)


def grafico_por_tamano(timings: pd.DataFrame):
    """Tiempo promedio segun el tamano del archivo (varias series -> leyenda)."""
    por_tamano = timings[timings["size_label"] != "n/a"]
    orden = ["10 KB", "100 KB", "1 MB"]
    tabla = (
        por_tamano.pivot_table(
            index="size_label", columns="operation", values="duration_ms", aggfunc="mean"
        )
        .reindex(orden)
    )

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for i, operacion in enumerate(tabla.columns):
        ax.plot(
            tabla.index,
            tabla[operacion],
            marker="o",
            markersize=8,
            linewidth=2,
            color=SERIES[i % len(SERIES)],
            label=operacion,
            zorder=2,
        )

    # Con 5 series los valores de los extremos se solapan: la identidad la lleva
    # la leyenda (fuera del area de datos), no una etiqueta por punto.
    ax.set_yscale("log")
    ax.set_ylabel("Tiempo promedio (ms, escala logaritmica)")
    ax.set_xlabel("Tamano del archivo")
    ax.set_title("Rendimiento segun el tamano del archivo", color=INK, pad=14)
    ax.legend(
        frameon=False,
        fontsize=9,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.13),
        ncol=3,
    )
    ax.margins(x=0.08)
    estilo_ejes(ax, eje_x_grid=False)

    fig.tight_layout()
    fig.savefig(RESULTS / "fig_por_tamano.png", dpi=150)
    plt.close(fig)


def grafico_tasas(rates: pd.DataFrame):
    """Tasas de deteccion de alteraciones y de autenticacion."""
    rates = rates.sort_values("rate_pct")

    fig, ax = plt.subplots(figsize=(9, 4))
    barras = ax.barh(
        rates["metric"], rates["rate_pct"], color=STATUS_GOOD, height=0.6, zorder=2
    )

    for barra, fila in zip(barras, rates.itertuples(), strict=True):
        ax.text(
            barra.get_width() + 1.5,
            barra.get_y() + barra.get_height() / 2,
            f"{fila.rate_pct:.0f}%  ({fila.successes}/{fila.total})",
            va="center",
            fontsize=9,
            color=INK,
        )

    ax.set_xlim(0, 118)
    ax.set_xlabel("Porcentaje de exito (%)")
    ax.set_title(
        "Deteccion de alteraciones y tasa de autenticacion", color=INK, pad=14
    )
    estilo_ejes(ax)

    fig.tight_layout()
    fig.savefig(RESULTS / "fig_tasas.png", dpi=150)
    plt.close(fig)


def main():
    # keep_default_na=False: si no, pandas convierte la etiqueta "n/a" en NaN y
    # descarta las operaciones de tamano fijo (claves RSA, certificados, bcrypt).
    timings = pd.read_csv(RESULTS / "timings.csv", keep_default_na=False)
    timings["duration_ms"] = pd.to_numeric(timings["duration_ms"])
    rates = pd.read_csv(RESULTS / "rates.csv")

    resumen = resumen_estadistico(timings)
    grafico_operaciones(timings)
    grafico_por_tamano(timings)
    grafico_tasas(rates)

    print("\n=== RESUMEN ESTADISTICO (tiempos en ms) ===")
    print(resumen.to_string(index=False))

    print("\n=== TASAS ===")
    print(rates.to_string(index=False))

    print(f"\nGraficos y resumen guardados en: {RESULTS}")


if __name__ == "__main__":
    main()
