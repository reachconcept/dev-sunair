#!/bin/bash
# How to use this script
# Save this script as run_tests.sh and give it execute permissions:
# chmod +x run_tests.sh
#
# Examples:
# Run tests for a specific class:
# ./run_tests.sh -c <test_class> -d <db_name>
#
# Run tests with a specific tag:
# ./run_tests.sh -t <tag> -d <db_name>
#
# Run all tests:
# ./run_tests.sh -a -d <db_name>
# sh dev/scripts/run_tests.sh -t sale_custom -d adam

# Function to display usage
usage() {
    echo "Usage: $0 [-c <test_class>] [-t <tag>] [-a] [-d <db_name>]"
    echo "  -c <test_class>  Run tests for the specified test class"
    echo "  -t <tag>         Run tests with the specified tag"
    echo "  -a               Run all tests"
    echo "  -d <db_name>     Specify the database name"
    exit 1
}

# Parse command line arguments
while getopts ":c:t:ad:" opt; do
    case ${opt} in
        c )
            TEST_CLASS=$OPTARG
            ;;
        t )
            TAG=$OPTARG
            ;;
        a )
            RUN_ALL=true
            ;;
        d )
            DB_NAME=$OPTARG
            ;;
        \? )
            usage
            ;;
    esac
done

# Check if at least one option is provided
if [ -z "$TEST_CLASS" ] && [ -z "$TAG" ] && [ -z "$RUN_ALL" ]; then
    usage
fi

# Find the Docker container running Odoo
ODOO_CONTAINER=$(docker ps --filter "name=potomac-odoo" --format "{{.ID}}")

if [ -z "$ODOO_CONTAINER" ]; then
    echo "No running Odoo container found."
    read -p "Do you want to start the Odoo container and its database? (yes/no): " response
    if [[ "$response" == "yes" ]]; then
        COMPOSE_FILE="$(dirname "$0")/../../docker-compose.yml"
        docker-compose -f $COMPOSE_FILE up -d
        ODOO_CONTAINER=$(docker ps --filter "name=potomac-odoo" --format "{{.ID}}")
        if [ -z "$ODOO_CONTAINER" ]; then
            echo "Failed to start the Odoo container."
            exit 1
        fi
    else
        echo "Exiting."
        exit 1
    fi
fi

debugger = "-m debugpy --listen 0.0.0.0:8889"

# Run tests based on the provided options
if [ ! -z "$TEST_CLASS" ]; then
    echo "Running tests for class: $TEST_CLASS on container $ODOO_CONTAINER"
    docker exec -it $ODOO_CONTAINER odoo -c /etc/odoo/odoo.conf --log-level=test --test-enable --stop-after-init -p 9999 --test-tags $TEST_CLASS -d $DB_NAME
elif [ ! -z "$TAG" ]; then
    echo "Running tests with tag: $TAG on container $ODOO_CONTAINER"
    docker exec -it $ODOO_CONTAINER $debugger odoo -c /etc/odoo/odoo.conf --log-level=test --test-enable --stop-after-init -p 9999 --test-tags $TAG -d $DB_NAME
elif [ ! -z "$RUN_ALL" ]; then
    echo "Running all tests on container $ODOO_CONTAINER"
    docker exec -it $ODOO_CONTAINER odoo -c /etc/odoo/odoo.conf --log-level=test --test-enable --stop-after-init -p 9999 -d $DB_NAME
fi