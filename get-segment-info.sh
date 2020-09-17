#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

cd $CURRENT_DIR/segment-metrics

# install package and dependencies if not done already
pip3 show segment-metrics 1>/dev/null
if [ $? != 0 ]; then
    python3 setup.py develop
fi
SOLR=""
if [ "$1" ]; then
  SOLR="--solr=$1"
fi

CLUSTER=""
if [ "$2" ]; then
  CLUSTER="--cluster=$2"
fi

# run script
python3 -m segment-metrics.segment-metrics $SOLR $CLUSTER