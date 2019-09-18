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

  echo "Got list of java repos with $(wc -l <$WORK/repos.txt) entries"
fi

if [ ! -e $WORK/downloads ]; then
  echo "2] Downloading repos"

  mkdir -p $WORK/downloads
  $(dirname $0)/download_repos.sh $WORK/downloads < $WORK/repos.txt
fi

echo "3] Unzipping downloads"
mkdir -p $WORK/repos

for file in $(find $WORK/downloads -name '*.zip'); do
  target="$WORK/repos/$(basename $file .zip)"

  if [ ! -e $target ]; then
    echo "Unzipping '$file' to '$target'"
    unzip -q -d $target $file '*.java'
  fi
done
