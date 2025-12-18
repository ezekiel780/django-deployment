"""React command for Django project."""
import time

try:
    # prefer psycopg (psycopg3) when available
    import psycopg as _psycopg
    Psycopg2OpError = _psycopg.OperationalError
except Exception:
    # fallback to psycopg2 if present
    try:
        import psycopg2 as _psycopg2
        Psycopg2OpError = _psycopg2.OperationalError
    except Exception:
        Psycopg2OpError = Exception
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command to wait for the database."""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))

        