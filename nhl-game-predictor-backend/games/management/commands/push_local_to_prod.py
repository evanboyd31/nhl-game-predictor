import os
import subprocess
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
  help = "Restores the production Supabase instance with your local database"

  def handle(self, *args, **options):
    # credentials needed to access local database
    local_db_name = os.getenv("DATABASE_NAME")
    local_db_user = os.getenv("DATABASE_USER")
    local_db_password = os.getenv("DATABASE_PASSWORD")
    local_db_host = os.getenv("DATABASE_HOST")
    local_db_port = os.getenv("DATABASE_PORT")

    # credentials needed to access production supabase-hosted database
    prod_db_name = os.getenv("PROD_DATABASE_NAME")
    prod_db_user = os.getenv("PROD_DATABASE_USER")
    prod_db_password = os.getenv("PROD_DATABASE_PASSWORD")
    prod_db_host = os.getenv("PROD_DATABASE_HOST")
    prod_db_port = os.getenv("PROD_DATABASE_PORT")
