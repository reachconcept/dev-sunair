#!/usr/bin/env bash

# Variables
POSTGRES_CONTAINER_NAME="karnmeets-db"    # Name of your Postgres container
SUPERUSER="odoo"                          # Superuser (the one you can use to create/drop DB)
DB_USER="odoo"                            # DB user (Odoo user)
 
read -p "Enter the database name to restore into: " DB_NAME
read -p "Enter the path/filename of the backup dump file: " BACKUP_FILE

echo "You chose to restore '${BACKUP_FILE}' into the database '${DB_NAME}'."
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Drop and recreate the database using a known existing database (postgres) and superuser
docker exec -i "${POSTGRES_CONTAINER_NAME}" psql -U "${SUPERUSER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"
docker exec -i "${POSTGRES_CONTAINER_NAME}" psql -U "${SUPERUSER}" -d postgres -c "CREATE DATABASE ${DB_NAME};"

# Grant privileges on the newly created DB if necessary
docker exec -i "${POSTGRES_CONTAINER_NAME}" psql -U "${SUPERUSER}" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"

# Restore the database using psql since it's a text file
cat "${BACKUP_FILE}" | docker exec -i "${POSTGRES_CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}"

echo "Database '${DB_NAME}' restored successfully from '${BACKUP_FILE}'."