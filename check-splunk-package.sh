#!/bin/bash
rm -f TA-prisma-cloud-audit-logs-collector_0_0_1_export.tgz
tar -czvf TA-prisma-cloud-audit-logs-collector_0_0_1_export.tgz TA-prisma-cloud-audit-logs-collector/*
git add . && \ 
    git add -u && \
    git commit -m "Automatic push: $1" && \
    git push --force

splunk-appinspect inspect TA-prisma-cloud-audit-logs-collector_0_0_1_export.tgz