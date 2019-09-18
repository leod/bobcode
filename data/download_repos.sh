# Clone a list of repos

dir=$1

sep='___'

while read repo branch; do
  # Strip "^git@github.com:" and ".git$"
  owner_name=$(echo $repo | cut -d':' -f2 | sed -e 's/.git$//')
  owner=$(echo $owner_name | cut -d'/' -f1)
  name=$(echo $owner_name | cut -d'/' -f2)

  target="$dir/$(echo $owner_name | sed -e "s#/#$sep#").zip"

  if [ ! -e $target ]; then
    url="https://github.com/$owner/$name/archive/$branch.zip"
    echo "Downloading $target from $url"
    wget -O $target $url
  fi
done
