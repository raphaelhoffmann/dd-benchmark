cd `echo $0 | sed "s:[^/]*$:../:"`
source env_local.sh

# THIS IS TOO SLOW
#echo "TRUNCATE sentences_escort;" | psql -h $PGHOST -p $PGPORT -U $PGUSER $DBNAME
#find /lfs/local/0/raphaelh/shipment3/split/done -name '*.parsed' 2>/dev/null -print0 | xargs -0 -L 1 -P 1 bash -c 'echo "COPY sentences_escort FROM '\''"$0"'\'' CSV DELIMITER E'\''\t'\'' QUOTE E'\''\1'\'';" | psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" $DBNAME'

# THIS WORKS: STILL NEED TO TURN THIS INTO A SCRIPT
#/lfs/local/0/raphaelh/software/greenplum-loaders$ gpfdist -d /lfs/local/0/raphaelh/shipment3/ -V -m 256000000
#create external table xyz2 (like sentences_escort) location ('gpfdist://localhost:8080/split/done/split_*.parsed') format 'csv' (DELIMITER AS E'\t' QUOTE AS E'\1') log errors into err SEGMENT REJECT LIMIT 1 PERCENT;
#insert into sentences_escort_large select * from xyz2;

