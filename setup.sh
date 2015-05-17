dropdb bench
createdb bench

psql -d $DBNAME < $APP_HOME/schema.sql
psql -d $DBNAME -c "copy articles from STDIN CSV;" < $APP_HOME/data/articles_dump.csv
psql -d $DBNAME -c "copy sentences from STDIN CSV;" < $APP_HOME/data/sentences_dump.csv
