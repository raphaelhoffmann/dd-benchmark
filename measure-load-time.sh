psql -p 6432 bench -c "TRUNCATE TABLE sentences_escort"
date
psql -p 6432 bench -c "COPY sentences_escort FROM '/data/bench/sentences_escort.tsv'"
date
