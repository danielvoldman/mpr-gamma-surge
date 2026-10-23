# MS9 9i: G3 facts table (class counts; facts only, no verdict)

Source: stored records and class tables, no simulation (DL-258 to DL-260). The G3 rule (plan, Table 11.2 and section 4.3): add M3a/M3b only if every onset is S-sus or D-sus and termination by J -> 0 is rejected. This table gives the class counts only; it does not test whether termination by J -> 0 is rejected (the plan gives no operational test; asked in the 9i report).

| group | mode | runs | D-tr | D-sus | D-none | failed | S+ | S-rel | S-abs | S-sus | NS | other | surge class | sus class | quiet class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S5 P1 | D | 52 | 0 | 15 | 37 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 15 | 37 |
| S5 P2 | D | 27 | 26 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 26 | 0 | 1 |
| S5 P2 | N | 130 | 0 | 0 | 0 | 0 | 42 | 32 | 5 | 44 | 7 | 0 | 79 | 44 | 7 |
| S5 P5 | D | 26 | 26 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 26 | 0 | 0 |
| S6 pre-registered (20) | D | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 |
| S6 supplementary P2 references (2) | D | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| map 1 (900 cells) | D | 900 | 760 | 0 | 140 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 760 | 0 | 140 |
| map 2 (325 cells) | D | 325 | 296 | 0 | 29 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 296 | 0 | 29 |
| subgrid runs (225 cells x 10 seeds) | N | 2250 | 0 | 0 | 0 | 0 | 475 | 378 | 507 | 829 | 61 | 0 | 1360 | 829 | 61 |
| subgrid cells, deterministic class (225) | D | 225 | 188 | 0 | 37 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 188 | 0 | 37 |

Surge class = D-tr (mode D) or S+, S-rel, S-abs (mode N), Table 2.1. Sus class = D-sus or S-sus. Quiet class = D-none or NS.
