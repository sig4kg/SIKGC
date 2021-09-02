#!/usr/bin/env bash

bin="isql-vt"
host="store"
port=$STORE_ISQL_PORT
user="dba"

run_virtuoso_cmd () {
 VIRT_OUTPUT=`echo "$1" | "$bin" -H "$host" -S "$port" -U "$user" -P dba 2>&1`
 VIRT_RETCODE=$?
 if [[ $VIRT_RETCODE -eq 0 ]]; then
   echo "$VIRT_OUTPUT" | tail -n+5 | perl -pe 's|^SQL> ||g'
   return 0
 else
   echo -e "[ERROR] running the these commands in virtuoso:\n$1\nerror code: $VIRT_RETCODE\noutput:"
   echo "$VIRT_OUTPUT"
   let 'ret = VIRT_RETCODE + 128'
   return $ret
 fi
}


test_connection () {
   if [[ -z $1 ]]; then
       echo "[ERROR] missing argument: retry attempts"
       exit 1
   fi

   t=$1

   run_virtuoso_cmd 'status();'
   while [[ $? -ne 0 ]] ;
   do
       echo -n "."
       sleep 1
       echo $t
       let "t=$t-1"
       if [ $t -eq 0 ]
       then
           echo "timeout"
           return 2
       fi
       run_virtuoso_cmd 'status();'
   done
}


echo "will use ISQL port $STORE_ISQL_PORT to connect"
echo "[INFO] Waiting for store to come online (${STORE_CONNECTION_TIMEOUT}s)"
: ${STORE_CONNECTION_TIMEOUT:=60}
test_connection "${STORE_CONNECTION_TIMEOUT}"
if [ $? -eq 2 ]; then
   echo "[ERROR] store not reachable"
   exit 1
fi

#ensure that all supported formats get into the load list
#(since we have to excluse graph-files *.* won't do the trick
echo "[INFO] registring RDF documents for import"
for ext in nt nq owl rdf trig ttl xml gz bz2; do
 run_virtuoso_cmd "ld_dir ('${STORE_DATA_DIR}', '*.${ext}', 'http://treat.test');"
done

echo "[INFO] deactivating auto-indexing"
run_virtuoso_cmd "DB.DBA.VT_BATCH_UPDATE ('DB.DBA.RDF_OBJ', 'ON', NULL);"

echo '[INFO] Starting load process...';

load_cmds=`cat <<EOF
log_enable(2);
checkpoint_interval(-1);
set isolation = 'uncommitted';
rdf_loader_run();
log_enable(1);
checkpoint_interval(60);
EOF`
run_virtuoso_cmd "$load_cmds";
echo "[INFO] making checkpoint..."
run_virtuoso_cmd 'checkpoint;'
echo "[INFO] re-activating auto-indexing"
run_virtuoso_cmd "DB.DBA.RDF_OBJ_FT_RULE_ADD (null, null, 'All');"
run_virtuoso_cmd 'DB.DBA.VT_INC_INDEX_DB_DBA_RDF_OBJ ();'
echo "[INFO] making checkpoint..."
run_virtuoso_cmd 'checkpoint;'
#echo "[INFO] update/filling of geo index"
#run_virtuoso_cmd 'rdf_geo_fill();'
#echo "[INFO] making checkpoint..."
#run_virtuoso_cmd 'checkpoint;'
echo "[INFO] bulk load done; terminating loader"
