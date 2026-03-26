#!/bin/bash
# docker exec -it velikocak-odoo-1 odoo -c /etc/odoo/odoo.conf -u sale_custom --stop-after-init -d adam

# Check if DB_NAME is provided as a parameter
if [ -z "$1" ]; then
    echo "Usage: $0 <DB_NAME>"
    exit 1
fi

DB_NAME=$1

# Find the Docker container running Odoo
ODOO_CONTAINER=$(docker ps --filter "name=potomac-odoo" --format "{{.ID}}")

if [ -z "$ODOO_CONTAINER" ]; then
    echo "No running Odoo container found."
    read -p "Do you want to start the Odoo container and its database? (yes/no): " response
    if [[ "$response" == "yes" ]]; then
        COMPOSE_FILE="$(dirname "$0")/../../docker-compose.yml"
        docker-compose -f $COMPOSE_FILE up -d
        ODOO_CONTAINER=$(docker ps --filter "name=odoo-1" --format "{{.ID}}")
        if [ -z "$ODOO_CONTAINER" ]; then
            echo "Failed to start the Odoo container."
            exit 1
        fi
    else
        echo "Exiting."
        exit 1
    fi
fi

echo "Stopping the Odoo container $ODOO_CONTAINER"
docker stop $ODOO_CONTAINER

echo "Updating the sale_custom module"
docker exec -it $ODOO_CONTAINER odoo -c /etc/odoo/odoo.conf -u sale_custom --stop-after-init -d $DB_NAME