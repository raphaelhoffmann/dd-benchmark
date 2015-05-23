source env_local.sh

psql -p $PGPORT postgres -c "DROP DATABASE IF EXISTS $DBNAME"
psql -p $PGPORT postgres -c "CREATE DATABASE $DBNAME"

find schemas -type f -name '*.sql' -print | xargs -L 1 bash -c 'psql -p $PGPORT $DBNAME < "$0"'

psql -p $PGPORT $DBNAME -c "copy sentences_escort FROM '/data/bench/sentences_escort.tsv'"

