#!/bin/bash
# adapted from https://stackoverflow.com/a/40178818 (Thanks @Matt Zeunert)

STATUS="$(git status)"

if [[ $STATUS == *"nothing to commit, working tree clean"* ]]
then
    # sed -i "" '/public/' ./.gitignore
    mv public nist-pages
    git add .
    git commit -m "Edit .gitignore to publish"
    git push nist-origin `git subtree split --prefix nist-pages master`:nist-pages --force
    git reset HEAD~
    git checkout .gitignore
else
    echo "Need clean working directory to publish"
fi
