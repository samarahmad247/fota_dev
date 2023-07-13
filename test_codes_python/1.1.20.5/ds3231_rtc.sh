#!/bin/bash


# Script to set and read date-time setting for ds3231.
#
# Usage -->  ./ds3231_rtc.sh <read/write> [option]{<day> <month> <date> <hour> <minute> <second> <year>}
#
#          <read> = 0, <write> = 1
#          <day> = Sun/Mon/Tue/Wed/Thu/Fri/Sat
#          <month> = Jan/Feb/Mar/Apr/May/Jun/Jul/Aug/Sept/Oct/Nov/Dec
#
#      For setting time: 
#                       Example: time to set is -- Tue Apr 18 21:02:48 2023
#                                run the script by using following arguments
#                                --> bash /etc/scripts/ds3231_rtc.sh 1 Tue Apr 18 21 02 48 2023
#      For reading set time:
#                           run the script with the following arguments
#                           --> bash /etc/scripts/ds3231_rtc.sh 0          

IFS='x'
r_w_bit=$1

day_var=$2
month_var=$3
date_var=$4
hour_var=$5
min_var=$6
sec_var=$7
year_var=$8
act_year=$(echo "${year_var} - 1970"|bc)

declare -A day_map_write=( ["Sun"]="0x01" ["Mon"]="0x02" ["Tue"]="0x03" ["Wed"]="0x04" ["Thu"]="0x05" ["Fri"]="0x06" ["Sat"]="0x07" )
declare -A day_map_read=( ["0x01"]="Sun" ["0x02"]="Mon" ["0x03"]="Tue" ["0x04"]="Wed" ["0x05"]="Thu" ["0x06"]="Fri" ["0x07"]="Sat" )
declare -A month_map_read=( ["0x01"]="Jan" ["0x02"]="Feb" ["0x03"]="Mar" ["0x04"]="Apr" ["0x05"]="May" ["0x06"]="Jun" ["0x07"]="Jul" ["0x08"]="Aug" ["0x09"]="Sept" ["0x10"]="Oct" ["0x11"]="Nov" ["0x12"]="Dec" )
declare -A month_map_write=( ["Jan"]="0x01" ["Feb"]="0x02" ["Mar"]="0x03" ["Apr"]="0x04" ["May"]="0x05" ["Jun"]="0x06" ["Jul"]="0x07" ["Aug"]="0x08" ["Sept"]="0x09" ["Oct"]="0x10" ["Nov"]="0x11" ["Dec"]="0x12" )

if [ $r_w_bit -eq 1 ]
then 
        #year
        temp=$(i2cset -f -y 0 0x68 0x06 0x"$act_year")
        #month
        temp=$(i2cset -f -y 0 0x68 0x05 "${month_map_write[$month_var]}")
        #date
        temp=$(i2cset -f -y 0 0x68 0x04 0x"$date_var")
        #day
        temp=$(i2cset -f -y 0 0x68 0x03 "${day_map_write[$day_var]}")
        #hour
        temp=$(i2cset -f -y 0 0x68 0x02 0x"$hour_var")
        #minute
        temp=$(i2cset -f -y 0 0x68 0x01 0x"$min_var")
        #second
        temp=$(i2cset -f -y 0 0x68 0x00 0x"$sec_var")
        echo "Date time set to $day_var $month_var $date_var $hour_var:$min_var:$sec_var $year_var"
fi

if [ $r_w_bit -eq 0 ]
then
        #year
        get=$(i2cget -f -y 0 0x68 0x06); set -- "$get"; declare -a get_year=($*)   
        #month
        get_month=$(i2cget -f -y 0 0x68 0x05)
        #date
        get=$(i2cget -f -y 0 0x68 0x04); set -- "$get"; declare -a get_date=($*)
        #day
        get_day=$(i2cget -f -y 0 0x68 0x03)
        #hour
        get=$(i2cget -f -y 0 0x68 0x02); set -- "$get"; declare -a get_hour=($*)
        #minute
        get=$(i2cget -f -y 0 0x68 0x01); set -- "$get"; declare -a get_min=($*)
        #second
        get=$(i2cget -f -y 0 0x68 0x00); set -- "$get"; declare -a get_sec=($*)

        echo -n "${day_map_read[$get_day]} "; echo -n "${month_map_read[$get_month]} " ; echo -n "${get_date[1]} " ;echo -n "${get_hour[1]}:"; echo -n "${get_min[1]}:"; echo -n "${get_sec[1]} "; echo "${get_year[1]}+1970"|bc
fi
