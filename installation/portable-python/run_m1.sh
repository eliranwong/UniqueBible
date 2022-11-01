INSTALLDIR='/Volumes/UBA_USB'

DIR=`pwd`
if [[ "$DIR" == "$HOME" ]]
then
  DIR=$INSTALLDIR
fi

if [[ -d $DIR/UniqueBible ]]
then
  cd $DIR/UniqueBible
fi

if [[ -f run.sh ]]
then
  ./run.sh 3.10.8_m1
else
  echo "run.sh not found"
fi