#!/usr/bin/env bash
set -euo pipefail
INPUT="${1:?input json required}"

python3 - "$INPUT" <<'PY'
import json, sys
p=sys.argv[1]
d=json.load(open(p,encoding="utf-8"))
nodes=[n["id"] for n in d["evidence_graph"]["nodes"]]
if len(nodes) != len(set(nodes)):
    raise SystemExit("duplicate graph node id")
node_set=set(nodes)
adj={n:[] for n in nodes}
for e in d["evidence_graph"]["edges"]:
    if e["from"] not in node_set or e["to"] not in node_set:
        raise SystemExit("edge references unknown node")
    adj[e["from"]].append(e["to"])
state={}
def visit(n):
    s=state.get(n,0)
    if s==1: raise SystemExit("evidence graph is cyclic")
    if s==2: return
    state[n]=1
    for x in adj[n]: visit(x)
    state[n]=2
for n in nodes: visit(n)
if "decision" not in node_set:
    raise SystemExit("decision node missing")
print("DAG_VALID")
PY
