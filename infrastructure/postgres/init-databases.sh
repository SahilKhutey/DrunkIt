#!/usr/bin/env bash
set -e

# Multi-database initialization script for FACCP PostgreSQL container
DATABASES=(
    "faccp_identity"
    "faccp_consumer"
    "faccp_retailer"
    "faccp_catalog"
    "faccp_inventory"
    "faccp_order"
    "faccp_compliance"
    "faccp_audit"
    "faccp_risk"
    "faccp_verification"
    "faccp_delivery"
    "faccp_notification"
    "faccp_payment"
    "faccp_pricing"
    "faccp_analytics"
    "faccp_realtime"
    "faccp_recommendation"
)

echo "Initializing multi-database PostgreSQL setup for FACCP..."

for db in "${DATABASES[@]}"; do
    echo "Creating database: ${db}"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        SELECT 'CREATE DATABASE ${db}'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${db}')\gexec
        GRANT ALL PRIVILEGES ON DATABASE ${db} TO ${POSTGRES_USER};
EOSQL

    echo "Enabling extensions in: ${db}"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${db}" <<-EOSQL
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE EXTENSION IF NOT EXISTS "pgcrypto";
EOSQL
done

echo "All FACCP databases initialized successfully."
