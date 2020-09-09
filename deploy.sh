#!/bin/bash
#
# Purpose: Continuous deploy on production environment
#
# Author: João Pedro Sconetto <sconetto.joao@gmail.com>

docker build -t rethink-data-manager:latest .

docker tag rethink-data-manager:latest sconetto/rethink-data-manager:latest

docker push sconetto/rethink-data-manager:latest