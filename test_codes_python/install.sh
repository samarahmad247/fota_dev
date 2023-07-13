#!/bin/bash

#Noccarc Robotics Pvt. Ltd. OS update script
VERSION="1.1.20.5"
K_LIST="1.1.20.1,1.1.20.2,1.1.20.4"
E_LIST="1.1.20.3"
LOG_SUFFIX="_install_log"
TIME=$(date)

handle_error() {

    echo "--??An error occurred while installing $FILE." >>"$VERSION""$LOG_SUFFIX"
    STATE=0
}

handle_error1() {

    echo "--??An error occurred while installing $FILE." >>"$VERSION""$LOG_SUFFIX"
    STATE=0
}
# Set the error handler function to be invoked when an error occurs
trap 'handle_error' ERR

#INCLUSION 
echo "-------------------Starting Installation of packages for version 1.1.20.5. ("$TIME")------------------" 
echo "-------------------Starting Installation of packages for version 1.1.20.5. ("$TIME")------------------" >> "$VERSION""$LOG_SUFFIX" 
FILE="rtc.sh"
LOCATION="/etc/scripts/"
STATE=1

echo "Installing $FILE.."
echo "Installing $FILE.." >> "$VERSION""$LOG_SUFFIX" 

echo -ne "Completed 0 of 2 steps\033[0k\r"

install -m 755 ./"$VERSION"/"$FILE" "$LOCATION" >> "$VERSION""$LOG_SUFFIX" 2>&1
test $STATE -eq 1 && echo -ne "Completed 1 of 2 steps\033[0k\r"
sleep 1

test $STATE -eq 1 && sed -i -e '$a\added this line in the end' /"$LOCATION"/"$FILE" >> "$VERSION""$LOG_SUFFIX" 2>&1
test $STATE -eq 1 && echo -e "Completed 2 of 2 steps      DONE!\033[0k\r" && echo "-->Installed $FILE." >> "$VERSION""$LOG_SUFFIX"  || echo -e "\n--??An error occurred while installing $FILE." 
sleep 1

FILE="ds3231_rtc.sh"
LOCATION="/etc/scripts/"
STATE=1

echo "Installing $FILE.."
echo "Installing $FILE.." >> "$VERSION""$LOG_SUFFIX" 

echo -ne "Completed 0 of 2 steps\033[0k\r"

install -m 755 ./"$VERSION"/"$FILE" "$LOCATION" >> "$VERSION""$LOG_SUFFIX" 2>&1
test $STATE -eq 1 && echo -ne "Completed 1 of 2 steps\033[0k\r" 
sleep 1

test $STATE -eq 1 && chmod 777 /"$LOCATION"/"$FILE" >> "$VERSION""$LOG_SUFFIX" 2>&1
test $STATE -eq 1 && echo -e "Completed 2 of 2 steps      DONE!\033[0k\r" && echo "-->Installed $FILE." >> "$VERSION""$LOG_SUFFIX"  || echo -e "\n--??An error occurred while installing $FILE." 
sleep 1

trap 'handle_error1' ERR

FILE="Router_Noccarc"
LOCATION="/usr/local"
STATE=1

echo "Installing $FILE.."
echo "Installing $FILE.." >> "$VERSION""$LOG_SUFFIX" 

echo -ne "Completed 0 of 2 steps\033[0k\r"

cp -r ./"$VERSION"/"$FILE" "$LOCATION" >> "$VERSION""$LOG_SUFFIX" 2>&1
test $STATE -eq 1 && echo -ne "Completed 1 of 2 steps\033[0k\r"
sleep 1

test $STATE -eq 1 && chmod -R 755 /"$LOCATION"/"$FILE" >> "$VERSION""$LOG_SUFFIX" 2>&1
test $STATE -eq 1 && echo -e "Completed 2 of 2 steps      DONE!\033[0k\r" && echo "-->Installed $FILE." >> "$VERSION""$LOG_SUFFIX"  || echo -e "\n--??An error occurred while installing $FILE." 

FILE="test/test.service"
LOCATION="/lib/systemd/system/"
STATE=1

echo "Installing $FILE.."
echo "Installing $FILE.." >> "$VERSION""$LOG_SUFFIX" 

echo -ne "Completed 0 of 2 steps\033[0k\r"

install -m 600 ./"$VERSION"/"$FILE" "$LOCATION" >> "$VERSION""$LOG_SUFFIX" 2>&1
test $STATE -eq 1 && echo -ne "Completed 1 of 2 steps\033[0k\r"
sleep 1

test $STATE -eq 1 && systemctl enable test.service >> "$VERSION""$LOG_SUFFIX" 2>&1
test $STATE -eq 1 && echo -e "Completed 2 of 2 steps      DONE!\033[0k\r" && echo "-->Installed $FILE." >> "$VERSION""$LOG_SUFFIX"  || echo -e "\n--??An error occurred while installing $FILE." 
#EXCLUSION 

