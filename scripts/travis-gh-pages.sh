#!/usr/bin/env bash
set -e # Exit with nonzero exit code if anything fails

# Save some useful information
REPO=`git config remote.origin.url`
SHA=`git rev-parse --verify HEAD`
DOC="project-gh-pages"

# Get the deploy key by using Travis's stored variables to decrypt deploy_key.enc
ENCRYPTED_KEY_VAR="encrypted_${ENCRYPTION_LABEL}_key"
ENCRYPTED_IV_VAR="encrypted_${ENCRYPTION_LABEL}_iv"
ENCRYPTED_KEY=${!ENCRYPTED_KEY_VAR}
ENCRYPTED_IV=${!ENCRYPTED_IV_VAR}
OUT_KEY="github-id_rsa"
openssl aes-256-cbc -K $ENCRYPTED_KEY -iv $ENCRYPTED_IV -in github-id_rsa.enc -out $OUT_KEY -d
chmod 600 $OUT_KEY
eval `ssh-agent -s`
ssh-add $OUT_KEY

# Clone/checkout the gh-pages branch from Github alongside the master branch working copy directory :
rm -rf ../${DOC}
git -C .. clone -b gh-pages ${REPO} ${DOC}
GIT="git -C ../${DOC}"

# Build in-project documents: docs/html
cd sphinx
make html

# Deploy
$GIT rm \*.\*
cp -r _build/html/* ../../${DOC}
echo "nanohttp.org" > ../../${DOC}/CNAME
$GIT add .


# Commit & push
${GIT} config user.name "Travis CI"
${GIT} config user.email "$COMMIT_AUTHOR_EMAIL"
${GIT} commit -am "Deploy to GitHub Pages: ${SHA}"
${GIT} push origin gh-pages
