#!/bin/bash

#------------Function-help---------------#
Help()
{
   # Display Help
   echo
   echo "Program to Read, Set and Test I2C Based RTC"
   echo
   echo "Syntax: rtc {i2c_bus_num=0} {dev_name=0} [-r|h|o|s]"
   echo "options:"
   echo "-s    Set Date Time to RTC , uses '-s \"Wed May 3 10:12:13 IST 2023\"' "
   echo "-r    Get Date Time from RTC "
   echo "-o    Enable Clockout, uses '-o frequency'"
   echo "-h , --help    For Printing Help "
   echo
   echo "Device Name" 
   echo "0 - PCF8523"
   echo "1 - RX8111"
   echo "2 - RV-3028"
}

#------------Function-PCF8523---------------#
# call : PFC8523_Init bus_num
PCF8523_Init()
{
	i2cset -f -y $1 0x68 0x00 0x80
	i2cset -f -y $1 0x68 0x01 0x00
	i2cset -f -y $1 0x68 0x02 0x00   # Battery switchover in standard mode
}

#------------Function-PCF8523---------------#
# call : PFC8523_Clockout bus_num frequency 
PCF8523_Clockout()
{
	freq=$2
	reg=0x00
	if [ $freq -eq 32768 ]
	then
		reg=0x00
	elif [ $freq -eq 16384 ]
	then
		reg=0x08
	elif [ $freq -eq 8192 ]
	then
		reg=0x10
	elif [ $freq -eq 4096 ]
	then
		reg=0x18
	elif [ $freq -eq 1024 ]
	then
		reg=0x20
	elif [ $freq -eq 32 ]
	then
		reg=0x28
	elif [ $freq -eq 1 ]
	then
		reg=0x30
	elif [ $freq -eq 0 ]
	then
		reg=0x38
	fi
	#check frequency and make register value 
	i2cset -f -y $1 0x68 0x0f $reg
}

#------------Function-PCF8523---------------#
# call : PFC8523_ReadDT Read Time date
PCF8523_ReadDT()
{
	 	#year
        get=$(i2cget -f -y $1 0x68 0x09)
        year=`bcdhex2dec $get`
      #month
        get=$(i2cget -f -y $1 0x68 0x08)
        month=`bcdhex2dec $get`
      #date
        get=$(i2cget -f -y $1 0x68 0x06)
        date=`bcdhex2dec $get`
      #day
        get=$(i2cget -f -y $1 0x68 0x07)
        day=`bcdhex2dec $get`
      #hour
        get=$(i2cget -f -y $1 0x68 0x05)
        hour=`bcdhex2dec $get`
      #minute
        get=$(i2cget -f -y $1 0x68 0x04)
        minute=`bcdhex2dec $get`
      #second
        get=$(i2cget -f -y $1 0x68 0x03)
        second=$(($get & 0x7f))
        second=`bcdhex2dec $get`


        echo "`num2day 0 $day`  `num2month 1 $month` $date $hour:$minute:$second IST $(($year + 2000))"
}

#------------Function-PCF8523---------------#
# call : Set Date time 
PCF8523_SetDT()
{

	# Braking String
	day_data=$(echo $2| cut -d' ' -f 1)
	day=`day2num $day_data`
	day=`dec2bcdhex $day`
	month_data=$(echo $2| cut -d' ' -f 2)
	month=`month2num $month_data`
	month=$((`dec2bcdhex $month` + 1)) 
	date=$(echo $2| cut -d' ' -f 3)
	date=`dec2bcdhex $date`
	time=$(echo $2| cut -d' ' -f 4)
	hour=$(echo $time| cut -d':' -f 1)
	hour=`dec2bcdhex $hour`
	minute=$(echo $time| cut -d':' -f 2)
	minute=`dec2bcdhex $minute`
	second=$(echo $time| cut -d':' -f 3)
	second=`dec2bcdhex $second`
	year=$(echo $2| cut -d' ' -f 6)
	if [ $year -gt 1999 ] && [ $year -lt 2099 ]
	then
		year=`dec2bcdhex $(($year - 2000))`
	else
		echo "Date Time Format Error"
		exit
	fi

	i2cset -f -y $1 0x68 0x03 $second
	i2cset -f -y $1 0x68 0x04 $minute
	i2cset -f -y $1 0x68 0x05 $hour
	i2cset -f -y $1 0x68 0x06 $date
	i2cset -f -y $1 0x68 0x07 $day
	i2cset -f -y $1 0x68 0x08 $month
	i2cset -f -y $1 0x68 0x09 $year

	echo "Time Set to $2"
	
}


#------------Function-RX8111---------------#
# call : RX8111_Init bus_num
RX8111_Init()
{
	i2cset -f -y $1 0x32 0x32 0x04   # Battery Swithover
}

#------------Function-RX8111---------------#
# call : RX8111_Clockout bus_num frequency 
RX8111_Clockout()
{
	freq=$2
	reg=0x00
	if [ $freq -eq 32768 ]
	then
		reg=0x00
	elif [ $freq -eq 1024 ]
	then
		reg=0x40
	elif [ $freq -eq 1 ]
	then
		reg=0x80
	elif [ $freq -eq 0 ]
	then
		reg=0xC0
	fi
	#check frequency and make register value 
	i2cset -f -y $1 0x32 0x1D $reg
}

#------------Function-RX8111---------------#
# call : RX8111_ReadDT Read Time date
RX8111_ReadDT()
{
	 	#year
        get=$(i2cget -f -y $1 0x32 0x16)
        year=`bcdhex2dec $get`
      #month
        get=$(i2cget -f -y $1 0x32 0x15)
        month=`bcdhex2dec $get`
      #date
        get=$(i2cget -f -y $1 0x32 0x14)
        date=`bcdhex2dec $get`
      #day
       get=$(i2cget -f -y $1 0x32 0x13)
       data=$get
       count=1
       while [ $data != 1 ]
       do
               data=$(($data >> 1))
               count=$(($count + 1))
       done
       day=$count
      #hour
        get=$(i2cget -f -y $1 0x32 0x12)
        hour=`bcdhex2dec $get`
      #minute
        get=$(i2cget -f -y $1 0x32 0x11)
        minute=`bcdhex2dec $get`
      #second
        get=$(i2cget -f -y $1 0x32 0x10)
        second=$(($get & 0x7f))
        second=`bcdhex2dec $get`


        echo "`num2day 1 $day`  `num2month 1 $month` $date $hour:$minute:$second IST $(($year + 2000))"
}

#------------Function-RX8111---------------#
# call : Set Date time 
RX8111_SetDT()
{

	# Braking String
	day_data=$(echo $2| cut -d' ' -f 1)
	day=`day2num $day_data`
	day=$((1 << $day))
	month_data=$(echo $2| cut -d' ' -f 2)
	month=`month2num $month_data`
	month=$((`dec2bcdhex $month` + 1)) 
	date=$(echo $2| cut -d' ' -f 3)
	date=`dec2bcdhex $date`
	time=$(echo $2| cut -d' ' -f 4)
	hour=$(echo $time| cut -d':' -f 1)
	hour=`dec2bcdhex $hour`
	minute=$(echo $time| cut -d':' -f 2)
	minute=`dec2bcdhex $minute`
	second=$(echo $time| cut -d':' -f 3)
	second=`dec2bcdhex $second`
	year=$(echo $2| cut -d' ' -f 6)
	if [ $year -gt 1999 ] && [ $year -lt 2099 ]
	then
		year=`dec2bcdhex $(($year - 2000))`
	else
		echo "Date Time Format Error"
		exit
	fi

	i2cset -f -y $1 0x32 0x10 $second
	i2cset -f -y $1 0x32 0x11 $minute
	i2cset -f -y $1 0x32 0x12 $hour
	i2cset -f -y $1 0x32 0x14 $date
	i2cset -f -y $1 0x32 0x13 $day
	i2cset -f -y $1 0x32 0x15 $month
	i2cset -f -y $1 0x32 0x16 $year

	echo "Time Set to $2"
	
}


#------------Function-RV3028---------------#
# call : RV3028_Init bus_num
RV3028_Init()
{
	get=$(i2cget -f -y $1 0x52 0x37)
	get=$(($(($get & 0xf3)) + 0x0c))
	i2cset -f -y $1 0x52 0x37 $get    # Battery Swithover
	i2cset -f -y $1 0x52 0x13 0x40    # EVI Valid level
	i2cset -f -y $1 0x52 0x35 0x47    # Clockout disable
	#i2cset -f -y $1 0x52 0x27 0x11    # Save data to internal eeprom
}

#------------Function-RV3028---------------#
# call : RV3028_Clockout bus_num frequency 
RV3028_Clockout()
{
	freq=$2
	reg=0xC0
	if [ $freq -eq 32768 ]
	then
		reg=0xC0
	elif [ $freq -eq 8192 ]
	then
		reg=0xC1
	elif [ $freq -eq 1024 ]
	then
		reg=0xC2
	elif [ $freq -eq 64 ]
	then
		reg=0xC3
	elif [ $freq -eq 32 ]
	then
		reg=0xC4
	elif [ $freq -eq 1 ]
	then
		reg=0xC5
	elif [ $freq -eq 0 ]
	then
		reg=0x40
	fi
	#check frequency and make register value 
	i2cset -f -y $1 0x52 0x35 $reg
}

#------------Function-RV3028---------------#
# call : RV3028_ReadDT Read Time date
RV3028_ReadDT()
{
	 	#year
        get=$(i2cget -f -y $1 0x52 0x06)
        year=`bcdhex2dec $get`
      #month
        get=$(i2cget -f -y $1 0x52 0x05)
        month=`bcdhex2dec $get`
      #date
        get=$(i2cget -f -y $1 0x52 0x04)
        date=`bcdhex2dec $get`
      #day
        get=$(i2cget -f -y $1 0x52 0x03)
        day=`bcdhex2dec $get`
      #hour
        get=$(i2cget -f -y $1 0x52 0x02)
        hour=`bcdhex2dec $get`
      #minute
        get=$(i2cget -f -y $1 0x52 0x01)
        minute=`bcdhex2dec $get`
      #second
        get=$(i2cget -f -y $1 0x52 0x00)
        second=$(($get & 0x7f))
        second=`bcdhex2dec $get`


        echo "`num2day 0 $day`  `num2month 1 $month` $date $hour:$minute:$second IST $(($year + 2000))"
}

#------------Function-RV3028---------------#
# call : Set Date time 
RV3028_SetDT()
{

	# Braking String
	day_data=$(echo $2| cut -d' ' -f 1)
	day=`day2num $day_data`
	day=$((`dec2bcdhex $day`+ 0))
	month_data=$(echo $2| cut -d' ' -f 2)
	month=`month2num $month_data`
	month=$((`dec2bcdhex $month` + 1)) 
	date=$(echo $2| cut -d' ' -f 3)
	date=`dec2bcdhex $date`
	time=$(echo $2| cut -d' ' -f 4)
	hour=$(echo $time| cut -d':' -f 1)
	hour=`dec2bcdhex $hour`
	minute=$(echo $time| cut -d':' -f 2)
	minute=`dec2bcdhex $minute`
	second=$(echo $time| cut -d':' -f 3)
	second=`dec2bcdhex $second`
	year=$(echo $2| cut -d' ' -f 6)
	if [ $year -gt 1999 ] && [ $year -lt 2099 ]
	then
		year=`dec2bcdhex $(($year - 2000))`
	else
		echo "Date Time Format Error"
		exit
	fi

	i2cset -f -y $1 0x52 0x00 $second
	i2cset -f -y $1 0x52 0x01 $minute
	i2cset -f -y $1 0x52 0x02 $hour
	i2cset -f -y $1 0x52 0x04 $date
	i2cset -f -y $1 0x52 0x03 $day
	i2cset -f -y $1 0x52 0x05 $month
	i2cset -f -y $1 0x52 0x06 $year

	echo "Time Set to $2"
	
}

#------------Function-PCF2131---------------#
# call : PCF2131_Init bus_num
PCF2131_Init()
{
	i2cset -f -y $1 0x53 0x00 0x08
	i2cset -f -y $1 0x53 0x01 0x00
	i2cset -f -y $1 0x53 0x02 0x10
	i2cset -f -y $1 0x53 0x13 0xe7
	i2cset -f -y $1 0x53 0x07 0x00
}

#------------Function-PCF2131---------------#
# call : PCF2131_Clockout bus_num frequency 
PCF2131_Clockout()
{
	freq=$2
	reg=$(i2cget -f -y $1 0x53 0x13)
	data_to_set=$(($(($reg & 0xf8)) + 7))
	if [ $freq -eq 32768 ]
	then
		data_to_set=$(($(($reg & 0xf8)) + 0))
	elif [ $freq -eq 16384 ]
	then
		data_to_set=$(($(($reg & 0xf8)) + 1))
	elif [ $freq -eq 8192 ]
	then
		data_to_set=$(($(($reg & 0xf8)) + 2))
	elif [ $freq -eq 4096 ]
	then
		data_to_set=$(($(($reg & 0xf8)) + 3))
	elif [ $freq -eq 2048 ]
	then
		data_to_set=$(($(($reg & 0xf8)) + 4))
	elif [ $freq -eq 1024 ]
	then
		data_to_set=$(($(($reg & 0xf8)) + 5))
	elif [ $freq -eq 1 ]
	then
		data_to_set=$(($(($reg & 0xf8)) + 6))
	elif [ $freq -eq 0 ]
	then
		data_to_set=$(($(($reg & 0xf8)) + 7))
	fi
	#check frequency and make register value 
	i2cset -f -y $1 0x53 0x13 $data_to_set
}

#------------Function-PCF2131---------------#
# call : PCF2131_ReadDT Read Time date
PCF2131_ReadDT()
{
		read_data=$(i2ctransfer -f -y 1 w1@0x53 0x07 r7)

	 	#year
        get=$(echo $read_data| cut -d' ' -f 7)
        year=`bcdhex2dec $get`
      #month
        get=$(echo $read_data| cut -d' ' -f 6)
        month=`bcdhex2dec $get`
      #date
        get=$(echo $read_data| cut -d' ' -f 4)
        date=`bcdhex2dec $get`
      #day
       	get=$(echo $read_data| cut -d' ' -f 5)
        day=`bcdhex2dec $get`
      #hour
        get=$(echo $read_data| cut -d' ' -f 3)
        hour=`bcdhex2dec $get`
      #minute
        get=$(echo $read_data| cut -d' ' -f 2)
        minute=`bcdhex2dec $get`
      #second
        get=$(echo $read_data| cut -d' ' -f 1)
        second=$(($get & 0x7f))
        second=`bcdhex2dec $get`


        echo "`num2day 0 $day`  `num2month 1 $month` $date $hour:$minute:$second IST $(($year + 2000))"
}

#------------Function-PCF2131---------------#
# call : Set Date time 
PCF2131_SetDT()
{

	# Braking String
	day_data=$(echo $2| cut -d' ' -f 1)
	day=`day2num $day_data`
	day=$((`dec2bcdhex $day`+ 0))
	month_data=$(echo $2| cut -d' ' -f 2)
	month=`month2num $month_data`
	month=$((`dec2bcdhex $month` + 1)) 
	date=$(echo $2| cut -d' ' -f 3)
	date=`dec2bcdhex $date`
	time=$(echo $2| cut -d' ' -f 4)
	hour=$(echo $time| cut -d':' -f 1)
	hour=`dec2bcdhex $hour`
	minute=$(echo $time| cut -d':' -f 2)
	minute=`dec2bcdhex $minute`
	second=$(echo $time| cut -d':' -f 3)
	second=`dec2bcdhex $second`
	year=$(echo $2| cut -d' ' -f 6)
	if [ $year -gt 1999 ] && [ $year -lt 2099 ]
	then
		year=`dec2bcdhex $(($year - 2000))`
	else
		echo "Date Time Format Error"
		exit
	fi

	#stop clock and reset cpr
	i2cset -f -y $1 0x53 0x00 0x28 
	i2cset -f -y $1 0x53 0x13 0xA4

	i2cset -f -y $1 0x53 0x07 $second
	i2cset -f -y $1 0x53 0x08 $minute
	i2cset -f -y $1 0x53 0x09 $hour
	i2cset -f -y $1 0x53 0x0a $date
	i2cset -f -y $1 0x53 0x0b $day
	i2cset -f -y $1 0x53 0x0c $month
	i2cset -f -y $1 0x53 0x0d $year

	i2cset -f -y $1 0x53 0x00 0x08
	#start clock

	echo "Time Set to $2"
	
}

# Function to convert bcd coded hex to decimal
bcdhex2dec()
{
	echo $(($(($1 & 0x0f)) + $(($(($(($1 >> 4)) & 0x0f)) * 10))))
}

# Function to convert decimal to bcd coded hex
dec2bcdhex()
{
	echo $(($(($1 % 10)) + $(($(($(($1 / 10)) << 4)) & 0xf0))))
}

# Mapping of Days , pass start day(0 or 1) -- num2day 0 5
num2day()
{
	day_data=$(($2 - $1))
	if [ $day_data -eq 0 ]
	then
		echo "Sun"
	elif [ $day_data -eq 1 ]
	then
		echo "Mon" 
	elif [ $day_data -eq 2 ]
	then
		echo "Tue" 
	elif [ $day_data -eq 3 ]
	then
		echo "Wed" 
	elif [ $day_data -eq 4 ]
	then
		echo "Thu" 
	elif [ $day_data -eq 5 ]
	then
		echo "Fri" 
	elif [ $day_data -eq 6 ]
	then
		echo "Sat"
	else
		echo " "
	fi
}

# Mapping of Month

# Mapping of Month , pass start month(0 or 1) -- num2month 1 5
num2month()
{
	month_data=$(($2 - $1))
	if [ $month_data -eq 0 ]
	then
		echo "Jan"
	elif [ $month_data -eq 1 ]
	then
		echo "Feb" 
	elif [ $month_data -eq 2 ]
	then
		echo "Mar" 
	elif [ $month_data -eq 3 ]
	then
		echo "Apr" 
	elif [ $month_data -eq 4 ]
	then
		echo "May" 
	elif [ $month_data -eq 5 ]
	then
		echo "Jun" 
	elif [ $month_data -eq 6 ]
	then
		echo "Jul"
	elif [ $month_data -eq 7 ]
	then
		echo "Aug"
	elif [ $month_data -eq 8 ]
	then
		echo "Sep"
	elif [ $month_data -eq 9 ]
	then
		echo "Oct"
	elif [ $month_data -eq 10 ]
	then
		echo "Nov"
	elif [ $month_data -eq 11 ]
	then
		echo "Dec"
	else
		echo " "
	fi
}

# month to num 
month2num()
{
	month_data=$1
	if [ "$month_data" == "Jan" ]
	then
		echo 0
	elif [ "$month_data" == "Feb" ]
	then
		echo 1 
	elif [ "$month_data" == "Mar" ]
	then
		echo 2 
	elif [ "$month_data" == "Apr" ]
	then
		echo 3 
	elif [ "$month_data" == "May" ]
	then
		echo 4 
	elif [ "$month_data" == "Jun" ]
	then
		echo 5 
	elif [ "$month_data" == "Jul" ]
	then
		echo 6
	elif [ "$month_data" == "Aug" ]
	then
		echo 7
	elif [ "$month_data" == "Sep" ]
	then
		echo 8
	elif [ "$month_data" == "Oct" ]
	then
		echo 9
	elif [ "$month_data" == "Nov" ]
	then
		echo 10
	elif [ "$month_data" == "Dec" ]
	then
		echo 11
	else
		echo 0
	fi
}


# Mapping of Days , pass start day(0 or 1) -- day2num "Tue"
day2num()
{
	day_data=$1
	if [ "$day_data" == "Sun" ]
	then
		echo 0
	elif [ "$day_data" == "Mon" ]
	then
		echo 1 
	elif [ "$day_data" == "Tue" ]
	then
		echo 2 
	elif [ "$day_data" == "Wed" ]
	then
		echo 3 
	elif [ "$day_data" == "Thu" ]
	then
		echo 4 
	elif [ "$day_data" == "Fri" ]
	then
		echo 5 
	elif [ "$day_data" == "Sat" ]
	then
		echo 6
	else
		echo 0
	fi
}

#-----------------main-----------------

# Check size of input
# if 1 then check for -r , -h

# if 2 then check for -b x, -d x, -o x, -s x

# if 3 then (-b x -r), (-d x -r)

#if 4 then  (-b x -d x), (-b x -o x), (-d x -o x), (-d x -s x), (-b x -s x)

# if 5 then (-b x -d x -r)

# if 6 then (-b x -d x -o x) , (-b x -d x -s x)

bus_num=1
dev_num=3
opt="-r"
usr_dat=0

if [ $# -eq 0 ]
then
	usr_dat=0
elif [ $# -eq 1 ]
then
	if [ "$1" == "-r" ]
	then
		bus_num=0
		dev_num=0
		opt="-r"
	else
		Help
		exit
	fi

elif [ $# -eq 2 ]
then
	if [ "$1" == "-b" ]  
	then
		bus_num=$2
	elif [ "$1" == "-d" ] 
	then
		dev_num=$2
	elif [ "$1" == "-o" ] 
	then
		opt="-o"
		usr_dat=$2
	elif [ "$1" == "-s" ] 
	then
		opt="-s"
		usr_dat=$2
	else
		Help
		exit
	fi

elif [ $# -eq 3 ] && [ "$3" == "-r" ]
then
	opt="-r"
	if [ "$1" == "-b" ]
	then
		bus_num=$2
	elif [ "$1" == "-d" ]
	then
		dev_num=$2
	else
		Help
		Exit
	fi

elif [ $# -eq 4 ] && [ "$3" == "-o" ] 
then
	opt="-o"
	usr_dat=$4
	if [ "$1" == "-b" ]
	then
		bus_num=$2
	elif [ "$1" == "-d" ]
	then
		dev_num=$2
	else
		Help
		Exit
	fi
	
elif [ $# -eq 4 ] && [ "$3" == "-s" ] 
then
	opt="-s"
	usr_dat=$4
	if [ "$1" == "-b" ]
	then
		bus_num=$2
	elif [ "$1" == "-d" ]
	then
		dev_num=$2
	else
		Help
		Exit
	fi

elif [ $# -eq 4 ] && [ "$1" == "-d" ] && [ "$3" == "-b" ]
then
	opt="-r"
	bus_num=$4
	dev_num=$2

elif [ $# -eq 4 ] && [ "$1" == "-b" ] && [ "$3" == "-d" ]
then
	opt="-r"
	bus_num=$2
	dev_num=$4

elif [ $# -eq 5 ] && [ "$5" == "-r" ]
then
	opt="-r"
	if [ "$1" == "-b" ] && [ "$3" == "-d" ]
	then
		bus_num=$2
		dev_num=$4
	elif [ "$1" == "-d" ] && [ "$3" == "-b" ]
	then
		bus_num=$4
		dev_num=$2
	else
		Help
		exit
	fi

elif [ $# -eq 6 ] && [ "$5" == "-o" ]
then
	opt="-o"
	usr_dat=$6
	if [ "$1" == "-b" ] && [ "$3" == "-d" ]
	then
		bus_num=$2
		dev_num=$4
	elif [ "$1" == "-d" ] && [ "$3" == "-b" ]
	then
		bus_num=$4
		dev_num=$2
	else
		Help
		exit
	fi

elif [ $# -eq 6 ] && [ "$5" == "-s" ]
then
	opt="-s"
	usr_dat=$6
	if [ "$1" == "-b" ] && [ "$3" == "-d" ]
	then
		bus_num=$2
		dev_num=$4
	elif [ "$1" == "-d" ] && [ "$3" == "-b" ]
	then
		bus_num=$4
		dev_num=$2
	else
		Help
		exit
	fi

else
	Help
	exit
fi


if [ $dev_num -eq 0 ] && [ "$opt" == "-r" ]
then
	PCF8523_ReadDT $bus_num
elif [ $dev_num -eq 0 ] && [ "$opt" == "-s" ]
then
	PCF8523_SetDT $bus_num "$usr_dat"
	PCF8523_Init $bus_num
elif [ $dev_num -eq 0 ] && [ "$opt" == "-o" ]
then
	PCF8523_Clockout $bus_num $usr_dat

elif [ $dev_num -eq 1 ] && [ "$opt" == "-r" ]
then
	RX8111_ReadDT $bus_num
elif [ $dev_num -eq 1 ] && [ "$opt" == "-s" ]
then
	RX8111_SetDT $bus_num "$usr_dat"
	RX8111_Init $bus_num
elif [ $dev_num -eq 1 ] && [ "$opt" == "-o" ]
then
	RX8111_Clockout $bus_num $usr_dat


elif [ $dev_num -eq 2 ] && [ "$opt" == "-r" ]
then
	RV3028_ReadDT $bus_num
elif [ $dev_num -eq 2 ] && [ "$opt" == "-s" ]
then
	RV3028_SetDT $bus_num "$usr_dat"
	RV3028_Init $bus_num
elif [ $dev_num -eq 2 ] && [ "$opt" == "-o" ]
then
	RV3028_Clockout $bus_num $usr_dat


elif [ $dev_num -eq 3 ] && [ "$opt" == "-r" ]
then
	PCF2131_ReadDT $bus_num
elif [ $dev_num -eq 3 ] && [ "$opt" == "-s" ]
then
	PCF2131_SetDT $bus_num "$usr_dat"
	PCF2131_Init $bus_num
elif [ $dev_num -eq 3 ] && [ "$opt" == "-o" ]
then
	PCF2131_Clockout $bus_num $usr_dat

else
	Help
fi


#--------------------------------------------
