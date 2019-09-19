dir=$1
name=$2

if [ ! -f $dir ]; then
  repos=$(ls $dir | wc -l)
  files=$(find $dir -type f -name $name | wc -l)
  read lines words chars \
    < \
    <(find $dir -type f -name $name -print0 \
      | xargs -0 cat \
      | wc)
else
  repos=$(wc -l < $dir)
  files=$(find $(< $dir) -type f -name $name | wc -l)
  read lines words chars \
    < \
    <(find $(< $dir) -type f -name $name -print0 \
      | xargs -0 cat \
      | wc)
fi

echo -e "number of repos\t$repos
number of files\t$files
number of lines\t$lines
number of words\t$words
number of chars\t$chars
files/repo\t$(bc -l <<< $files/$repos)
lines/repo\t$(bc -l <<< $lines/$repos)
lines/file\t$(bc -l <<< $lines/$files)
words/line\t$(bc -l <<< $words/$lines)"
