##### Setup

```shell
python -m venv .venv
.venv/bin/pip install -U pip setuptools
.venv/bin/pip install poetry
.venv/bin/poetry install
```

##### Docs

- https://ai.google.dev/gemini-api/docs/models
- https://google.github.io/adk-docs/

openssl req -x509 -newkey rsa:4096 -nodes -out local.cer -keyout local.key -days 365

https://animista.net/

```shell
/Users/anthony/Developer/dfs.recipes/.venv/bin/python -m poetry run uvicorn dfs_recipes.main:app --host 0.0.0.0 --port 8000 --reload --ssl-keyfile local.key --ssl-certfile local.cer
```

```shell
/Users/anthony/Developer/dfs.recipes/.venv/bin/python /Users/anthony/Developer/dfs.recipes/src/dfs_recipes/main.py
```

https://github.com/ecomfe/echarts-gl/blob/master/test/bar3D-music.html

https://css-tricks.com/meta-theme-color-and-trickery/

https://grid.malven.co/

```shell
npm webpack serve --server-type https --server-options-key ../../../local.key --server-options-cert ../../../local.cer
```

https://scroll-driven-animations.style/
https://www.patterns.dev/vanilla/observer-pattern/


prompts

stacked bar chart showing the relationship between field goals made and field goal attempts

stacked bar chart showing the points, rebounds, and assists for each game

line chart showing points scored over time

chart showing the relationship between points scored at home vs points scored away

stacked radial chart showing the average points scored against each team

stacked radial chart showing the average points scored against each team, include a tooltip and legend

calendar heatmap showing points scored

Write code to sandbox directory
- perform AST and static checking ensuring code is safe to execute
- Wrap the function in a web worker and perform a try / catch on the function, post message to return the outcome of the function
- Create web worker using BLOB
- Get result
