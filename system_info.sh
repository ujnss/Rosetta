#!/usr/bin/env bash

########################################
# CPU & Memory Info
# name/logical/physical/cores
cpu_n=$(cat /proc/cpuinfo | grep "model name" | head -n 1 | awk -F":" '{print $2}')
cpu_l=$(cat /proc/cpuinfo | grep "processor" | wc -l)
cpu_p=$(cat /proc/cpuinfo | grep "physical id" | sort | uniq | wc -l)

echo -e "\n>>>>>>>>>>> CPU Info <<<<<<<<<<<"
echo " Model Name:$cpu_n"
echo "Physical(s): $cpu_p"
echo " Logical(s): $cpu_l"

echo -e "\n>>>>>>>>>>> MEM Info <<<<<<<<<<<"
mem_info=($(awk '/MemTotal/{memtotal=$2}/MemAvailable/{memavailable=$2}END{printf "%.3f %.3f %.2f",memtotal/1024/1024," "(memtotal-memavailable)/1024/1024," "(memtotal-memavailable)/memtotal*100}' /proc/meminfo))
echo total:${mem_info[0]}G used:${mem_info[1]}G Usage:${mem_info[2]}%
echo ""
########################################
