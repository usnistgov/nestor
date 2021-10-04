#!/bin/bash
# https://gitlab.nist.gov/gitlab/eldst/eerc/-/blob/master/publish-on-nist-pages
TEMP_BRANCH=temp-split
PAGES_BRANCH=nist-pages
MASTER_REMOTE=nist-origin
PAGES_REMOTE=nist-origin
BUILD_DIR="$MKDOCS_SITE_DIR"
opt_force=""

if [ "$1" = "-f" ]; then
  opt_force="-f"
fi

die() {
  echo "$@" >> /dev/stderr
  exit 1
}

cleanup() {
  git branch -D "$TEMP_BRANCH" >/dev/null 2>&1  # Ignore errors; branch probably doesn't exist anyway
  git branch -D "$PAGES_BRANCH" >/dev/null 2>&1  # Ignore errors; branch probably doesn't exist anyway
  rm -rf build
}

if [ ! -d .git ]; then
  die "You must run this from the root of the master repo"
fi

cleanup

status=$(git status --porcelain -b)
echo $status | egrep -q '^##\smaster\.\.\.' || die "Must be run while master is checked out"
changes=$(echo "$status" | egrep -v '^(##|\?\?)' | wc -l)
if [ "$changes" -ne 0 -a -z "$opt_force" ]; then
  die "You have uncommited changes - run with '-f' to force but CAUTION: CHANGES WILL BE LOST!"
fi
# npm run build || die "'npm run build' failed"
poetry run task deploy
git checkout $opt_force -b $TEMP_BRANCH || die "Could not create branch $TEMP_BRANCH" # should bring over build directory
git add -f $BUILD_DIR || die "Could not add $BUILD_DIR to $TEMP_BRANCH"
git commit -m "irrelevant commit for $PAGES_BRANCH generation" || die "Could not commit to $TEMP_BRANCH"
git subtree split --prefix build -b "$PAGES_BRANCH" || die "'git subtree split' failed"
git checkout master || die "'git checkout master' failed"
git push -f "${PAGES_REMOTE}" "${PAGES_BRANCH}:${PAGES_BRANCH}" || die "'git push' failed"

cleanup

exit 0
