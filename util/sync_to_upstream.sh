#!/bin/bash

## source: http://gitready.com/intermediate/2009/02/12/easily-fetching-upstream-changes.html
## This only need once
# git remote add upstream git@github.com:ymei/TMSPlane.git

git fetch origin -v; git fetch upstream -v; git merge upstream/master
