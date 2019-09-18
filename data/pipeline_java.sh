WORK=work/java

echo "Working in '$WORK'"

mkdir -p $WORK

if [ ! -e $WORK/repos.txt ]; then
  echo "1] Downloading list of repos"

  # 30 entries per page => 300 repositories
  $(dirname $0)/list_github_repos.py \
    --min_stars 500 \
    --language java \
    --pages 10 \
  > $WORK/repos.txt \
  2> $WORK/repos.log

  echo "Got list of java repos with $(wc -l <$WORK/repos.txt) entries"
fi

if [ ! -d $WORK/downloads ]; then
  echo "2] Downloading repos"

  mkdir -p $WORK/downloads
  $(dirname $0)/download_repos.sh $WORK/downloads < $WORK/repos.txt
fi
