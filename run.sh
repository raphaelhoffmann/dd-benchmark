#!/bin/bash

DIRNAME=`dirname $0`

. "${DIRNAME}/env_local.sh"

if [ "$USING_EC2" = true ] ; then
    echo 'Copying python libs and dicts to scratch space for Greenplum'
    script/copy-pylibs-to-greenplum.sh && script/copy-dicts-to-greenplum.sh
fi

cd $DEEPDIVE_HOME
export PYTHONPATH=$DEEPDIVE_HOME/ddlib:$PYTHONPATH

### Compile and run:
sbt/sbt "run -c $APP_HOME/${APP_CONF:-application.conf} -o ${TMP_DIR}"
