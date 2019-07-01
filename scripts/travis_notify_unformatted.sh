#!/bin/bash
# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

COMMENT=$(sed ':a;N;$!ba;s/\n/\\\\n/g' <<EOF
Your branch contains non-formatted code.

Please reformat your code by running `black .` at the root of the project.
You may consider automating this process by installing default git hooks:

```bash
pip install -r requirements-dev.txt
pre-commit install
```
EOF
)

if [ "$TRAVIS_PULL_REQUEST" != "false" ] ; then
    curl -H "Authorization: token $GITHUB_TOKEN" \
         -X POST \
         -d "{\"body\": \"$COMMENT\"}" \
         "https://api.github.com/repos/${TRAVIS_REPO_SLUG}/issues/${TRAVIS_PULL_REQUEST}/comments"
fi
