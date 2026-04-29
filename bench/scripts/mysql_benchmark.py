import argparse
import csv
import json
import random
import re
import statistics
import string
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import mysql.connector
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Dependencia ausente: mysql-connector-python. "
        "Instale com: pip install -r bench/requirements.txt"
    ) from exc


DEFAULT_VOLUMES = [100, 1000, 10000]
DEFAULT_REPEAT = 5
ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / "bench" / "results"


def random_text(prefix: str, size: int = 8) -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=size))
    return f"{prefix}_{suffix}"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_connection(args):
    return mysql.connector.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        autocommit=False,
    )


def docker_stats(container_name: str):
    command = [
        "docker",
        "stats",
        container_name,
        "--no-stream",
        "--format",
        "{{json .}}",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    data = json.loads(completed.stdout.strip())
    cpu = parse_percent(data["CPUPerc"])
    mem_mb = parse_memory_mb(data["MemUsage"].split("/")[0].strip())
    return cpu, mem_mb


def safe_docker_stats(container_name: str):
    try:
        return docker_stats(container_name)
    except Exception:
        return None, None


def parse_percent(value: str) -> float:
    return float(value.replace("%", "").replace(",", ".").strip())


def parse_memory_mb(value: str) -> float:
    match = re.match(r"^\s*([0-9]+(?:[.,][0-9]+)?)\s*([A-Za-z]+)\s*$", value)
    if not match:
        raise ValueError(f"Formato de memoria nao suportado: {value}")
    raw, unit = match.groups()
    amount = float(raw.replace(",", "."))
    unit = unit.upper()
    if unit.startswith("GIB"):
        return amount * 1024
    if unit.startswith("MIB"):
        return amount
    if unit.startswith("KIB"):
        return amount / 1024
    if unit.startswith("B"):
        return amount / (1024 * 1024)
    raise ValueError(f"Unidade de memoria nao suportada: {value}")


def reset_tables(cursor):
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE access_logs")
    cursor.execute("TRUNCATE TABLE products")
    cursor.execute("TRUNCATE TABLE users")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def seed_base_data(cursor):
    users = [
        ("admin", "admin@tcc.local", "hash_admin_demo", "admin"),
        ("ana", "ana@tcc.local", "hash_ana_demo", "user"),
        ("bruno", "bruno@tcc.local", "hash_bruno_demo", "user"),
    ]
    cursor.executemany(
        """
        INSERT INTO users (username, email, password_hash, role_name)
        VALUES (%s, %s, %s, %s)
        """,
        users,
    )


def generate_products(volume: int, marker: str):
    rows = []
    categories = ["eletronicos", "livros", "moveis", "papelaria"]
    for index in range(volume):
        rows.append(
            (
                f"{marker}_produto_{index}",
                categories[index % len(categories)],
                round(random.uniform(10, 5000), 2),
                random.randint(1, 200),
            )
        )
    return rows


def bulk_insert_products(cursor, rows):
    cursor.executemany(
        """
        INSERT INTO products (name, category, price, stock)
        VALUES (%s, %s, %s, %s)
        """,
        rows,
    )


def preload_products(connection, volume: int):
    marker = random_text("preload")
    rows = generate_products(volume, marker)
    cursor = connection.cursor()
    try:
        reset_tables(cursor)
        seed_base_data(cursor)
        bulk_insert_products(cursor, rows)
        connection.commit()
        ids = list(range(1, volume + 1))
        return ids
    finally:
        cursor.close()


def measure_insert(connection, volume: int):
    marker = random_text("insert")
    rows = generate_products(volume, marker)
    cursor = connection.cursor()
    try:
        reset_tables(cursor)
        seed_base_data(cursor)
        start = time.perf_counter()
        bulk_insert_products(cursor, rows)
        connection.commit()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms
    finally:
        cursor.close()


def measure_select_by_id(connection, volume: int):
    ids = preload_products(connection, volume)
    cursor = connection.cursor(dictionary=True)
    try:
        sample_size = min(100, len(ids))
        selected_ids = random.sample(ids, sample_size)
        start = time.perf_counter()
        for product_id in selected_ids:
            cursor.execute(
                "SELECT id, name, category, price, stock FROM products WHERE id = %s",
                (product_id,),
            )
            cursor.fetchone()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms
    finally:
        cursor.close()


def measure_select_filter(connection, volume: int):
    preload_products(connection, volume)
    cursor = connection.cursor(dictionary=True)
    try:
        start = time.perf_counter()
        for _ in range(25):
            cursor.execute(
                """
                SELECT id, name, category, price, stock
                FROM products
                WHERE category = %s AND price BETWEEN %s AND %s
                ORDER BY price DESC
                LIMIT 20
                """,
                ("eletronicos", 50, 2500),
            )
            cursor.fetchall()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms
    finally:
        cursor.close()


def measure_update(connection, volume: int):
    ids = preload_products(connection, volume)
    cursor = connection.cursor()
    try:
        sample_size = min(100, len(ids))
        selected_ids = random.sample(ids, sample_size)
        start = time.perf_counter()
        for product_id in selected_ids:
            cursor.execute(
                "UPDATE products SET stock = stock + 1 WHERE id = %s",
                (product_id,),
            )
        connection.commit()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms
    finally:
        cursor.close()


def throughput(volume: int, elapsed_ms: float, logical_operations: int) -> float:
    seconds = elapsed_ms / 1000
    if seconds == 0:
        return 0.0
    return logical_operations / seconds


def benchmark_operation(connection, operation: str, volume: int):
    if operation == "insert":
        elapsed_ms = measure_insert(connection, volume)
        ops = volume
    elif operation == "select_id":
        elapsed_ms = measure_select_by_id(connection, volume)
        ops = min(100, volume)
    elif operation == "select_filtro":
        elapsed_ms = measure_select_filter(connection, volume)
        ops = 25
    elif operation == "update":
        elapsed_ms = measure_update(connection, volume)
        ops = min(100, volume)
    else:
        raise ValueError(f"Operacao invalida: {operation}")
    return elapsed_ms, throughput(volume, elapsed_ms, ops)


def write_csv(rows, output_file: Path):
    fieldnames = [
        "timestamp",
        "teste",
        "banco",
        "volume_registros",
        "operacao",
        "execucao",
        "tempo_ms",
        "throughput_ops_s",
        "cpu_percent",
        "memoria_mb",
        "observacoes",
    ]
    with output_file.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows):
    print("\nResumo consolidado:")
    grouped = {}
    for row in rows:
        key = (row["operacao"], row["volume_registros"])
        grouped.setdefault(key, []).append(float(row["tempo_ms"]))
    for (operation, volume), samples in sorted(grouped.items(), key=lambda item: (item[0][1], item[0][0])):
        avg = statistics.mean(samples)
        print(f"- {operation} | volume={volume}: media={avg:.2f} ms")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark de desempenho para MySQL voltado ao TCC."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3307)
    parser.add_argument("--user", default="tcc_user")
    parser.add_argument("--password", default="tcc_pass")
    parser.add_argument("--database", default="tcc_security")
    parser.add_argument("--container", default="tcc-mysql")
    parser.add_argument(
        "--volumes",
        nargs="+",
        type=int,
        default=DEFAULT_VOLUMES,
        help="Lista de volumes para teste, por exemplo: 100 1000 10000",
    )
    parser.add_argument("--repeat", type=int, default=DEFAULT_REPEAT)
    parser.add_argument(
        "--output",
        default=None,
        help="Caminho do CSV de saida. Se omitido, usa bench/results/",
    )
    parser.add_argument(
        "--test-name",
        default="mysql_base",
        help="Nome logico do teste para aparecer no CSV.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_output_dir()
    output_file = (
        Path(args.output)
        if args.output
        else OUTPUT_DIR / f"mysql_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    operations = ["insert", "select_id", "select_filtro", "update"]
    rows = []

    try:
        connection = get_connection(args)
    except mysql.connector.Error as exc:
        raise SystemExit(f"Falha ao conectar no MySQL: {exc}") from exc

    try:
        for volume in args.volumes:
            for operation in operations:
                for execution in range(1, args.repeat + 1):
                    elapsed_ms, ops_s = benchmark_operation(connection, operation, volume)
                    cpu_percent, mem_mb = safe_docker_stats(args.container)
                    row = {
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "teste": args.test_name,
                        "banco": "MySQL",
                        "volume_registros": volume,
                        "operacao": operation,
                        "execucao": execution,
                        "tempo_ms": f"{elapsed_ms:.4f}",
                        "throughput_ops_s": f"{ops_s:.4f}",
                        "cpu_percent": "" if cpu_percent is None else f"{cpu_percent:.2f}",
                        "memoria_mb": "" if mem_mb is None else f"{mem_mb:.2f}",
                        "observacoes": "" if cpu_percent is not None else "docker_stats_indisponivel",
                    }
                    rows.append(row)
                    print(
                        f"[ok] volume={volume} operacao={operation} execucao={execution} "
                        f"tempo_ms={elapsed_ms:.2f} throughput={ops_s:.2f}"
                    )
    finally:
        connection.close()

    write_csv(rows, output_file)
    print_summary(rows)
    print(f"\nCSV salvo em: {output_file}")


if __name__ == "__main__":
    random.seed(42)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nExecucao interrompida pelo usuario.")
