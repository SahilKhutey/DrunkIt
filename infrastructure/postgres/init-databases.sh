#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create one database per microservice
    CREATE DATABASE faccp_identity;
    CREATE DATABASE faccp_consumer;
    CREATE DATABASE faccp_retailer;
    CREATE DATABASE faccp_catalog;
    CREATE DATABASE faccp_inventory;
    CREATE DATABASE faccp_order;
    CREATE DATABASE faccp_compliance;
    CREATE DATABASE faccp_audit;
    CREATE DATABASE faccp_risk;
    CREATE DATABASE faccp_verification;
    CREATE DATABASE faccp_delivery;
    CREATE DATABASE faccp_notification;
    CREATE DATABASE faccp_payment;
    CREATE DATABASE faccp_pricing;
    CREATE DATABASE faccp_analytics;
    CREATE DATABASE faccp_realtime;
    CREATE DATABASE faccp_whitelabel;
    CREATE DATABASE faccp_reporting;
    CREATE DATABASE faccp_support;
    CREATE DATABASE faccp_portal;
    CREATE DATABASE faccp_sustainability;
    CREATE DATABASE faccp_cdp;
    CREATE DATABASE faccp_marketing;
    CREATE DATABASE faccp_listing;
    
    -- Enable required extensions in each
    \c faccp_identity
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "citext";
    
    \c faccp_consumer
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "citext";
    
    \c faccp_retailer
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "citext";
    CREATE EXTENSION IF NOT EXISTS "postgis";
    
    \c faccp_catalog
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "citext";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    \c faccp_inventory
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_order
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "citext";
    
    \c faccp_compliance
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_audit
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_risk
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_verification
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_delivery
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "postgis";
    
    \c faccp_notification
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_payment
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_pricing
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_analytics
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_realtime
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    \c faccp_listing
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "postgis";
EOSQL

echo "All FACCP databases created successfully."
