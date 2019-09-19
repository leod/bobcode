WORK=work/java

echo "Working in '$WORK'"

mkdir -p $WORK

if [ ! -e $WORK/repos.txt ]; then
  echo "1] Downloading list of repos"

  # 30 entries per page => 1500 repositories
  $(dirname $0)/list_github_repos.py \
    --min_stars 500 \
    --language java \
    --pages 50 \
  > $WORK/repos.txt \
  2> $WORK/repos.log

  echo "Got list of java repos with $(wc -l < $WORK/repos.txt) entries"
fi

echo "2] Downloading repos"
mkdir -p $WORK/downloads

$(dirname $0)/download_repos.sh $WORK/downloads < $WORK/repos.txt

echo "3] Unzipping downloads"
mkdir -p $WORK/repos

for file in $(find $WORK/downloads -name '*.zip'); do
  target="$WORK/repos/$(basename $file .zip)"

  if [ ! -e $target ]; then
    echo "Unzipping '$file' to '$target'"
    unzip -q -d $target $file '*.java'
  fi
done

if [ ! -e $WORK/stats.repos.txt ]; then
  echo "4] Calculating statistics"
  $(dirname $0)/repos_stats.sh $WORK/repos '*.java' \
    | tee $WORK/stats.repos.txt
fi

echo "5] Preprocessing"
find $WORK/repos -name '*.java' | while IFS='\n' read file; do
  if [ ! -e "$file.pp" ]; then
    PYTHONPATH=$(dirname $0)/javalang $(dirname $0)/java_tokenize.py \
      <(sed -e 's/\t/    /g' "$file") \
      > "$file.pp"
  fi
done

if [ ! -e $WORK/stats.repos.pp.txt ]; then
  echo "6] Calculating statistics"
  $(dirname $0)/repos_stats.sh $WORK/repos '*.pp' \
    | tee $WORK/stats.repos.pp.txt
fi
