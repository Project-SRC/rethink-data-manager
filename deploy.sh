#!/bin/bash
#
# Purpose: Continuous deploy on production environment
#
# Author: João Pedro Sconetto <sconetto.joao@gmail.com>

docker build -t rethink-data-manager:latest .

docker tag rethink-data-manager:latest radop/rethink-data-manager:latest

docker push radop/rethink-data-manager:latest