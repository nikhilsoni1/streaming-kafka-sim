import click
import redis
from tabulate import tabulate

def get_redis_client(host, port, db):
    return redis.Redis(host=host, port=port, db=db)

@click.group()
@click.option('--host', default='localhost', help='Redis host')
@click.option('--port', default=6379, type=int, help='Redis port')
@click.option('--db', default=0, type=int, help='Redis DB index')
@click.pass_context
def cli(ctx, host, port, db):
    """Lightweight CLI to query Redis."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = get_redis_client(host, port, db)
    ctx.obj['db'] = db

@cli.command()
@click.pass_context
def keycount(ctx):
    """Show total number of keys in the DB."""
    client = ctx.obj['client']
    count = client.dbsize()
    click.echo(tabulate([["Total Keys", count]], headers=["Metric", "Value"], tablefmt="pretty"))

@cli.command()
@click.option('--pattern', default='*', help='Key pattern to match')
@click.pass_context
def allkeys(ctx, pattern):
    """List all keys matching a pattern."""
    client = ctx.obj['client']
    keys = client.keys(pattern)
    table = [[i + 1, k.decode('utf-8')] for i, k in enumerate(keys)]
    click.echo(tabulate(table, headers=["#", "Key"], tablefmt="pretty"))

@cli.command()
@click.pass_context
def info(ctx):
    """Show key distribution across DBs."""
    client = ctx.obj['client']
    info = client.info()
    db_keys = [(db, info[db].get("keys", 0)) for db in info if db.startswith("db")]
    click.echo(tabulate(db_keys, headers=["DB", "Key Count"], tablefmt="pretty"))

@cli.command()
@click.option('--all', 'flush_all', is_flag=True, help='Flush all Redis databases')
@click.pass_context
def flush(ctx, flush_all):
    """Flush current Redis DB (default) or all DBs."""
    client = ctx.obj['client']
    db = ctx.obj['db']
    if flush_all:
        client.flushall()
        click.echo("✅ Flushed all Redis databases.")
    else:
        client.flushdb()
        click.echo(f"✅ Flushed Redis DB {db}.")

if __name__ == "__main__":
    cli()
