#!/bin/bash
#basepath=$(cd `dirname $0`; pwd)

if [ -f ~/.bash_profile ];
then
  . ~/.bash_profile
fi

cd $(dirname "$0")
pwd
python unicom.py
