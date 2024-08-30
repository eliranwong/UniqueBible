ps -ef | grep api-server |  grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep api-server 
