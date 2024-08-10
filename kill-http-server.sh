ps -ef | grep http-server |  grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep http-server 
