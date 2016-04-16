#!/bin/bash

script_path="/etc/init.d/IPdisplay"
script_name=$(basename $script_path)

if [[ ! -f $script_path ]]; then
  cat > $script_path <<EOF
#!/bin/sh
# $script_path

### BEGIN INIT INFO
# Provides: $script_name
# Required-Start: \$remote_fs \$syslog
# Required-Stop: \$remote_fs \$syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Start IP address display
# Description: Start IP address display
### END INIT INFO

PATH=/sbin:/usr/sbin:/bin:/usr/bin
. /lib/lsb/init-functions

DAEMON_PATH="/home/pi/NokiaLCD/python"
DAEMON=./showIP.py
DAEMONOPTS=""

NAME=$script_name
PIDFILE=/var/run/\$NAME.pid
SCRIPTNAME=$script_path

start() {
  log_action_msg "Starting IP address display"
  cd \$DAEMON_PATH
  PID=\$(\$DAEMON \$DAEMONOPTS > /dev/null 2>&1 & echo \$!)
  if [ -z \$PID ]; then
    return 1
  else
    echo \$PID > \$PIDFILE
    return 0
  fi
}

stop() {
  log_action_msg "Stopping IP address display"
  PID=\$(cat \$PIDFILE)
  cd \$DAEMON_PATH
  if [ -f \$PIDFILE ]; then
    kill -HUP \$PID
    rm -f \$PIDFILE
    return 0
  else
    log_warning_msg "Could not find pid file"
    return 1
  fi
}

case "\$1" in
 start)
  start
  ;;

 stop)
  stop
  ;;

 restart)
  stop
  start
  ;;

 *)
  log_success_msg "Usage: \$SCRIPTNAME {start|stop|restart}"
  return 1
  ;;
esac

exit 0
EOF
  if [[ $? != 0 ]]; then
    echo "ERROR: could not create $script_path"
    exit 1
  fi

  chmod 755 $script_path
  update-rc.d $script_name defaults 
fi
