import click
import redis
from tabulate import tabulate

def get_redis_client(host, port, db):
    return redis.Redis(host=host, port=port, db=db)

@click.group()
def cli():
    """Lightweight CLI to query Redis."""
    pass

@cli.command()
@click.option('--host', default='localhost', help='Redis host')
@click.option('--port', default=6379, type=int, help='Redis port')
@click.option('--db', default=0, type=int, help='Redis DB index')
def keycount(host, port, db):
    """Show total number of keys in the DB."""
    client = get_redis_client(host, port, db)
    count = client.dbsize()
    click.echo(tabulate([["Total Keys", count]], headers=["Metric", "Value"], tablefmt="pretty"))

@cli.command()
@click.option('--pattern', default='*', help='Key pattern to match')
@click.option('--host', default='localhost', help='Redis host')
@click.option('--port', default=6379, type=int, help='Redis port')
@click.option('--db', default=0, type=int, help='Redis DB index')
def allkeys(pattern, host, port, db):
    """List all keys matching a pattern."""
    client = get_redis_client(host, port, db)
    keys = client.keys(pattern)
    table = [[i + 1, k.decode('utf-8')] for i, k in enumerate(keys)]
    click.echo(tabulate(table, headers=["#", "Key"], tablefmt="pretty"))

@cli.command()
@click.option('--host', default='localhost', help='Redis host')
@click.option('--port', default=6379, type=int, help='Redis port')
@click.option('--db', default=0, type=int, help='Redis DB index')
def info(host, port, db):
    """Show key distribution across DBs."""
    client = get_redis_client(host, port, db)
    info = client.info()
    db_keys = [(db, info[db].get("keys", 0)) for db in info if db.startswith("db")]
    click.echo(tabulate(db_keys, headers=["DB", "Key Count"], tablefmt="pretty"))

if __name__ == "__main__":
    cli()
