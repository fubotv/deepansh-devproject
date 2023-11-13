#!/bin/bash

function branchPrefix() {
  #echo "branchPrefix ${ENV} $1"
  vname=${ENV}_$1
  #echo ""$ENV $vname""
  x=${!vname}
  echo ${x}
}

function getProjectId() {
  if [[ $1 == *"master"* ]]; then
    echo "model-gearing-425"
  elif [[ $1 == *"feature/DE-backfill-name"* ]]; then
    echo "model-gearing-425"
  elif [[ $1 == *"release"* ]]; then
    echo "fubotv-prod"
  else
    echo "fubotv-dev"
  fi
}

function getBranchEnv() {
  if [[ $1 == *"master"* ]]; then
    echo "QA"
  elif [[ $1 == *"feature/DE-backfill-name"* ]]; then
    echo "QA"
  elif
    [[ $1 == *"release"* ]]
  then
    echo "PROD"
  else
    echo "DEV"
  fi
}

function caps() {
  echo "${1}" | tr '[:lower:]' '[:upper:]'
}

function capsPipe() {
  while read -r x; do echo "${x}" | tr '[:lower:]' '[:upper:]'; done
}
