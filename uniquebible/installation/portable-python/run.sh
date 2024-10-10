if [[ $# == 0 ]]
then
  echo "Need to specify portable python directory (3.10.8_m1 or 3.10.8_x86)"
  exit
fi

if [[ ! -d "../$1" ]]
then
  echo "$1 does not exist"
  exit
fi

../$1/bin/python uba.py
echo "Starting UBA..."
