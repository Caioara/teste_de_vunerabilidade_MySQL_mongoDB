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
    from pymongo import MongoClient, UpdateOne
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Dependencia ausente: pymongo. "
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


def get_database(args):
    uri = (
        f"mongodb://{args.user}:{args.password}@{args.host}:{args.port}/"
        f"?authSource={args.auth_database}"
    )
    client = MongoClient(uri)
    return client, client[args.database]


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


def reset_collections(db):
    db.users.delete_many({})
    db.products.delete_many({})
    db.access_logs.delete_many({})


def ensure_indexes(db):
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    db.products.create_index("product_id", unique=True)
    db.products.create_index("category")
    db.access_logs.create_index("user_id")
    db.access_logs.create_index("created_at")


def seed_base_data(db):
    db.users.insert_many(
        [
            {
                "user_id": 1,
                "username": "admin",
                "email": "admin@tcc.local",
                "password_hash": "hash_admin_demo",
                "role_name": "admin",
                "created_at": datetime.utcnow(),
            },
            {
                "user_id": 2,
                "username": "ana",
                "email": "ana@tcc.local",
                "password_hash": "hash_ana_demo",
                "role_name": "user",
                "created_at": datetime.utcnow(),
            },
            {
                "user_id": 3,
                "username": "bruno",
                "email": "bruno@tcc.local",
                "password_hash": "hash_bruno_demo",
                "role_name": "user",
                "created_at": datetime.utcnow(),
            },
        ]
    )


def generate_products(volume: int, marker: str):
    rows = []
    categories = ["eletronicos", "livros", "moveis", "papelaria"]
    for index in range(volume):
        rows.append(
            {
                "product_id": index + 1,
                "name": f"{marker}_produto_{index}",
                "category": categories[index % len(categories)],
                "price": round(random.uniform(10, 5000), 2),
                "stock": random.randint(1, 200),
                "created_at": datetime.utcnow(),
            }
        )
    return rows


def preload_products(db, volume: int):
    marker = random_text("preload")
    reset_collections(db)
    ensure_indexes(db)
    seed_base_data(db)
    rows = generate_products(volume, marker)
    db.products.insert_many(rows, ordered=False)
    return [item["product_id"] for item in rows]


def measure_insert(db, volume: int):
    marker = random_text("insert")
    rows = generate_products(volume, marker)
    reset_collections(db)
    ensure_indexes(db)
    seed_base_data(db)
    start = time.perf_counter()
    db.products.insert_many(rows, ordered=False)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms


def measure_select_by_id(db, volume: int):
    ids = preload_products(db, volume)
    sample_size = min(100, len(ids))
    selected_ids = random.sample(ids, sample_size)
    start = time.perf_counter()
    for product_id in selected_ids:
        db.products.find_one({"product_id": product_id}, {"_id": 0})
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms


def measure_select_filter(db, volume: int):
    preload_products(db, volume)
    start = time.perf_counter()
    for _ in range(25):
        list(
            db.products.find(
                {"category": "eletronicos", "price": {"$gte": 50, "$lte": 2500}},
                {"_id": 0},
            ).sort("price", -1).limit(20)
        )
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms


def measure_update(db, volume: int):
    ids = preload_products(db, volume)
    sample_size = min(100, len(ids))
    selected_ids = random.sample(ids, sample_size)
    operations = [
        UpdateOne({"product_id": product_id}, {"$inc": {"stock": 1}})
        for product_id in selected_ids
    ]
    start = time.perf_counter()
    db.products.bulk_write(operations, ordered=False)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms


def throughput(elapsed_ms: float, logical_operations: int) -> float:
    seconds = elapsed_ms / 1000
    if seconds == 0:
        return 0.0
    return logical_operations / seconds


def benchmark_operation(db, operation: str, volume: int):
    if operation == "insert":
        elapsed_ms = measure_insert(db, volume)
        ops = volume
    elif operation == "select_id":
        elapsed_ms = measure_select_by_id(db, volume)
        ops = min(100, volume)
    elif operation == "select_filtro":
        elapsed_ms = measure_select_filter(db, volume)
        ops = 25
    elif operation == "update":
        elapsed_ms = measure_update(db, volume)
        ops = min(100, volume)
    else:
        raise ValueError(f"Operacao invalida: {operation}")
    return elapsed_ms, throughput(elapsed_ms, ops)


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
        description="Benchmark de desempenho para MongoDB voltado ao TCC."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=27018)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="root123")
    parser.add_argument("--database", default="tcc_security")
    parser.add_argument("--auth-database", default="admin")
    parser.add_argument("--container", default="tcc-mongodb")
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
        default="mongodb_base",
        help="Nome logico do teste para aparecer no CSV.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_output_dir()
    output_file = (
        Path(args.output)
        if args.output
        else OUTPUT_DIR / f"mongodb_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    operations = ["insert", "select_id", "select_filtro", "update"]
    rows = []

    try:
        client, db = get_database(args)
        client.admin.command("ping")
    except Exception as exc:
        raise SystemExit(f"Falha ao conectar no MongoDB: {exc}") from exc

    try:
        for volume in args.volumes:
            for operation in operations:
                for execution in range(1, args.repeat + 1):
                    elapsed_ms, ops_s = benchmark_operation(db, operation, volume)
                    cpu_percent, mem_mb = safe_docker_stats(args.container)
                    row = {
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "teste": args.test_name,
                        "banco": "MongoDB",
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
        client.close()

    write_csv(rows, output_file)
    print_summary(rows)
    print(f"\nCSV salvo em: {output_file}")


if __name__ == "__main__":
    random.seed(42)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nExecucao interrompida pelo usuario.")
