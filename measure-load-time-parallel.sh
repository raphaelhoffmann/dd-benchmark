psql -p 6432 bench -c "TRUNCATE TABLE sentences_escort"

date
psql -p 6432 bench -c "EXECUTE DIRECT ON (data1) 'COPY sentences_escort FROM ''/data/bench/xaa'''" &
PID1=$!
psql -p 6432 bench -c "EXECUTE DIRECT ON (data2) 'COPY sentences_escort FROM ''/data/bench/xab'''" &
PID2=$!
psql -p 6432 bench -c "EXECUTE DIRECT ON (data3) 'COPY sentences_escort FROM ''/data/bench/xac'''" &
PID3=$!
psql -p 6432 bench -c "EXECUTE DIRECT ON (data4) 'COPY sentences_escort FROM ''/data/bench/xad'''" &
PID4=$!
psql -p 6432 bench -c "EXECUTE DIRECT ON (data5) 'COPY sentences_escort FROM ''/data/bench/xae'''" &
PID5=$!
psql -p 6432 bench -c "EXECUTE DIRECT ON (data6) 'COPY sentences_escort FROM ''/data/bench/xaf'''" &
PID6=$!
psql -p 6432 bench -c "EXECUTE DIRECT ON (data7) 'COPY sentences_escort FROM ''/data/bench/xag'''" &
PID7=$!
psql -p 6432 bench -c "EXECUTE DIRECT ON (data8) 'COPY sentences_escort FROM ''/data/bench/xah'''" &
PID8=$!

wait $PID1
wait $PID2
wait $PID3
wait $PID4
wait $PID5
wait $PID6
wait $PID7
wait $PID8

date

