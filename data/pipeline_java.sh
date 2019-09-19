# Output directory
WORK=work/java

# Number of repos to leave for dev/test
N_REPOS_DEV=50
N_REPOS_TEST=50

# Number of files to sample from the dev/test repos
N_FILES_DEV=100
N_LINES_TEST=100

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
if [ ! -d $WORK/downloads ]; then
  mkdir -p $WORK/downloads

  $(dirname $0)/download_repos.sh $WORK/downloads < $WORK/repos.txt
fi

echo "3] Unzipping downloads"
if [ ! -d $WORK/repos ]; then
  mkdir -p $WORK/repos

  for file in $(find $WORK/downloads -name '*.zip'); do
    target="$WORK/repos/$(basename $file .zip)"

    if [ ! -e $target ]; then
      echo "Unzipping '$file' to '$target'"
      unzip -q -d $target $file '*.java'
    fi
  done
fi

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

if [ ! -e $WORK/repo-paths.dev.txt ]; then
  echo "7] Splitting repo list into train/dev/test"

  rm -f \
    $WORK/repo-paths.dev.txt \
    $WORK/repo-paths.test.txt \
    $WORK/repo-paths.train.txt

  # We have two options here:
  # 1) Sample dev/test from the list of java files across all repos
  # 2) Sample dev/test from the list of repos
  #
  # With 1), we have to assume that there is a lot of similarity within
  # individual repos. We cannot really call dev/test data unseen if code from
  # the same repo was used in training. Thus, we choose 2), sampling
  # N_DEV/N_TEST many complete repos separate from the training data, and then
  # sampling files from those repos to construct the dev/test sets.

  ls -d $WORK/repos/*/ \
    | awk \
      -v n_dev=$N_REPOS_DEV \
      -v n_test=$N_REPOS_TEST \
      -v out_dev=$WORK/repo-paths.dev.txt \
      -v out_test=$WORK/repo-paths.test.txt \
      -v out_train=$WORK/repo-paths.train.txt \
      '{
         if (NR <= n_dev)
           print $0 >> out_dev;
         else if (NR >= n_dev+1 && NR <= n_dev+n_test)
           print $0 >> out_test;
         else
           print $0 >> out_train;
       }'
fi

mkdir -p $WORK/data

if [ ! -e $WORK/data/alltrain.java.pp ]; then
  echo "8] Concatenating all training data"

  find $(< $WORK/repo-paths.train.txt) \
    -type f \
    -name '*.java.pp' \
    -print0 \
    | xargs -0 cat \
    > $WORK/data/alltrain.java.pp
  
  wc $WORK/data/alltrain.java.pp
fi

if [ ! -e $WORK/data/alltrain.5M.java.pp ]; then
  echo "9] Sampling 5M lines for training BPE"

  shuf $WORK/alltrain.java.pp \
    | head -n 5000000 \
    > $WORK/data/alltrain.5M.java.pp

  wc $WORK/data/alltrain.5M.java.pp
fi

if [ ! -e $WORK/data/bpecodes ]; then
  echo "10] Training subword units (BPE)"

  subword-nmt learn-bpe \
    --symbols 24000 \
    < $WORK/data/alltrain.5M.java.pp \
    > $WORK/data/bpecodes

  wc $WORK/bpecodes
fi
