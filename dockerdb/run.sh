#!/bin/bash
docker build -t brazilian-biz-part-db .
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=braz_bp_user! -e POSTGRES_USER=braz_bp_user -e POSTGRES_DB=brazilian_business_partner_db --name brazilian-biz-part-db  brazilian-biz-part-db -c 'config_file=/etc/postgresql/postgresql.conf'
cd .. 