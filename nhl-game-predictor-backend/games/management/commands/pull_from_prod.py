import os
import subprocess
import re
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

class Command(BaseCommand):
  help = "Restores the production Supabase instance with your local database"

  def get_db_tables_from_inspectdb(self):
    # run command to get names of all Django related PostgreSQL tables
    project_root = Path(__file__).resolve().parents[3]
    manage_py_path = project_root / "manage.py"
    result = subprocess.run(
      ["python", manage_py_path, "inspectdb"],
      capture_output=True,
      text=True,
      check=True
    )

    # use regex for finding table names from above command
    inspectdb_output = result.stdout
    table_names = []
    for line in inspectdb_output.splitlines():
      match = re.search(r"db_table = ['\"]([\w_]+)['\"]", line)
      if match:
        table_names.append(match.group(1))

    return table_names

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

    if not all([local_db_name, local_db_user, local_db_password, local_db_host, local_db_port]):
      raise CommandError("Missing production DB credentials. Check your env vars.")

    if not all([prod_db_name, prod_db_user, prod_db_password, prod_db_host, prod_db_port]):
      raise CommandError("Missing production DB credentials. Check your env vars.")
    
    confirm = input(
        "\033[93mWARNING: This will overwrite the LOCAL database. Are you sure? [yes/no]: \033[0m"
    )
    if confirm.lower() != "yes":
      self.stdout.write("Aborting.")
      return

    # construct the file path for the local dump
    now = timezone.now().strftime("%Y%m%d_%H%M%S")
    command_dir = os.path.dirname(os.path.abspath(__file__))
    dump_dir = os.path.join(command_dir, "prod_db_dumps")
    dump_file_path = f"{dump_dir}/prod_dump_{now}.dump"
    os.makedirs(dump_dir, exist_ok=True)

    # dump local DB
    self.stdout.write("Dumping prod DB...")
    subprocess.run([
      "pg_dump",
      "-Fc",
      "-h", prod_db_host,
      "-p", prod_db_port,
      "-U", prod_db_user,
      "-d", prod_db_name,
      "-f", dump_file_path
    ], check=True, env={"PGPASSWORD": prod_db_password})

    self.stdout.write(f"Dumped prod DB into `{dump_file_path}`.")