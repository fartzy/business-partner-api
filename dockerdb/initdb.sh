#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	GRANT ALL PRIVILEGES ON DATABASE brazilian_business_partner_db TO braz_bp_user;
    CREATE SCHEMA IF NOT EXISTS stage;
    CREATE SCHEMA IF NOT EXISTS transformed;
    CREATE TABLE IF NOT EXISTS stage.company (
            "nr_cnpj" VARCHAR(1000), 
            "nm_fantasia" VARCHAR(1000), 
            "sg_uf" VARCHAR(1000), 
            "in_cpf_cnpj" VARCHAR(1000), 
            "nr_cpf_cnpj_socio" VARCHAR(1000), 
            "cd_qualificacao_socio" VARCHAR(1000), 
            "ds_qualificacao_socio" VARCHAR(1000), 
            "nm_socio" VARCHAR(1000), 
            "created_datetime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOSQL