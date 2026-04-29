import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT_DIR / "bench" / "results"
PLOTS_DIR = RESULTS_DIR / "plots"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gera graficos PNG a partir do CSV de benchmark do MongoDB."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Caminho do CSV gerado pelo mongodb_benchmark.py",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Diretorio de saida para os graficos. Padrao: bench/results/plots/",
    )
    return parser.parse_args()


def read_rows(csv_path: Path):
    with csv_path.open("r", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


def aggregate(rows):
    by_operation = defaultdict(lambda: defaultdict(lambda: {"tempo": [], "throughput": [], "cpu": [], "mem": []}))
    resource_by_volume = defaultdict(lambda: {"cpu": [], "mem": []})

    for row in rows:
        operation = row["operacao"]
        volume = int(row["volume_registros"])
        by_operation[operation][volume]["tempo"].append(float(row["tempo_ms"]))
        by_operation[operation][volume]["throughput"].append(float(row["throughput_ops_s"]))
        if row["cpu_percent"]:
            by_operation[operation][volume]["cpu"].append(float(row["cpu_percent"]))
            resource_by_volume[volume]["cpu"].append(float(row["cpu_percent"]))
        if row["memoria_mb"]:
            by_operation[operation][volume]["mem"].append(float(row["memoria_mb"]))
            resource_by_volume[volume]["mem"].append(float(row["memoria_mb"]))

    return by_operation, resource_by_volume


def average(values):
    return sum(values) / len(values) if values else 0.0


def plot_line(by_operation, metric_key, ylabel, output_path):
    plt.figure(figsize=(10, 6))
    ordered_operations = sorted(by_operation.keys())
    for operation in ordered_operations:
        volumes = sorted(by_operation[operation].keys())
        values = [average(by_operation[operation][volume][metric_key]) for volume in volumes]
        plt.plot(volumes, values, marker="o", linewidth=2, label=operation)
    plt.xlabel("Volume de registros")
    plt.ylabel(ylabel)
    plt.title(f"MongoDB - {ylabel}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_resources(resource_by_volume, output_path):
    volumes = sorted(resource_by_volume.keys())
    cpu_values = [average(resource_by_volume[volume]["cpu"]) for volume in volumes]
    mem_values = [average(resource_by_volume[volume]["mem"]) for volume in volumes]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(volumes, cpu_values, marker="o", color="#1f77b4", label="CPU %")
    ax1.set_xlabel("Volume de registros")
    ax1.set_ylabel("CPU %", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(volumes, mem_values, marker="s", color="#d62728", label="Memoria MB")
    ax2.set_ylabel("Memoria MB", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")

    plt.title("MongoDB - Consumo medio de recursos")
    fig.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def main():
    args = parse_args()
    csv_path = Path(args.input)
    output_dir = Path(args.output_dir) if args.output_dir else PLOTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_rows(csv_path)
    by_operation, resource_by_volume = aggregate(rows)

    plot_line(
        by_operation,
        "tempo",
        "Tempo medio (ms)",
        output_dir / "mongodb_tempo_medio.png",
    )
    plot_line(
        by_operation,
        "throughput",
        "Throughput medio (ops/s)",
        output_dir / "mongodb_throughput_medio.png",
    )
    if resource_by_volume:
        plot_resources(
            resource_by_volume,
            output_dir / "mongodb_recursos_medios.png",
        )

    print(f"Graficos gerados em: {output_dir}")


if __name__ == "__main__":
    main()
