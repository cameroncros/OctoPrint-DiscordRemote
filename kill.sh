kill -9 `ps -e | grep octoprint | awk '{print $1;}'`
