#!/bin/bash

command_data=`ps aux | grep uwsgi | head -1`
uwsgi_ID=`echo $command_data | awk '{ print $2; }'`
execute_command=`echo $command_data | awk '{for(i=11;i<=NF;++i)print $i}'`

kill $uwsgi_ID
echo "Restarting uwsgi."
$execute_command
