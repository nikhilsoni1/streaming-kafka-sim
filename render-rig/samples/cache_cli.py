import click
from render_rig2.utils.cache import cache


@click.group()
def cli():
    """CLI to interact with the cache."""
    pass


@cli.command("list-keys")
def list_keys():
    """List all keys currently in cache."""
    click.echo("📦 Cached keys:")
    for key in cache.iterkeys():
        click.echo(f"- {key}")


@cli.command("clear")
def clear_cache():
    """Clear all keys in cache."""
    cache.clear()
    click.echo("✅ Cache cleared.")


if __name__ == "__main__":
    cli()
