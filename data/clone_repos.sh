# Clone a list of repos

while read repo; do
  # Strip "^git@github.com:" and ".git$"
  owner_name=$(echo $repo | cut -d':' -f2 | sed -e 's/.git$//')
  owner=$(echo $owner_name | cut -d'/' -f1)
  name=$(echo $owner_name | cut -d'/' -f2)

  if [ ! -e $owner_name ]; then
    echo "Cloning $owner_name"
    mkdir -p $owner_name

    git clone "https://github.com/$owner/${name}.git" $owner/$name
  fi
done
