# MS15a push record (sub-step 21, part A)

Pasted by the user in chat on 2026-11-10 at 20:43 local time (America/Toronto). The user ran the push commands himself because the permission check denied them to Claude Code. The user confirms in the chat that he will check on GitHub that the repository is private (not yet confirmed in the chat): UNVERIFIED.

This file is the user's output word for word (the block below is unchanged; the characters are as pasted). It is the user's output, not a check made by Claude Code. Claude Code ran no network command. `scripts/ms15a_check_push_record.py` compares the `git ls-remote` lines below with the local repository (no network); its comparison table is printed by the script and recorded in the decision log (the results entry of step 21).

```text
(.venv) (base) PS C:\dev\mpr-gamma-surge> git push -u origin master
Enumerating objects: 5417, done.
Counting objects: 100% (5417/5417), done.
Delta compression using up to 12 threads
Compressing objects: 100% (5102/5102), done.
Writing objects: 100% (5417/5417), 6.60 MiB | 2.91 MiB/s, done.
Total 5417 (delta 3756), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (3756/3756), done.
To https://github.com/danielvoldman/mpr-gamma-surge
 * [new branch]      master -> master
branch 'master' set up to track 'origin/master'.
(.venv) (base) PS C:\dev\mpr-gamma-surge> git push origin fig-F1-v2 fig-F2-v2 fig-F3-v2 fig-F4a-v2 fig-F4b-v2 fig-F5-v2 fig-F5c-v2 fig-F6-v2 fig-FS1-v2 fig-FS2-v2 fig-FS3-v2 fig-FS4-v2 fig-FS5-v2 release-v1.0 criteria-frozen env-v1 replication-pass tolerances-frozen
Enumerating objects: 17, done.
Counting objects: 100% (17/17), done.
Delta compression using up to 12 threads
Compressing objects: 100% (17/17), done.
Writing objects: 100% (17/17), 10.20 KiB | 1.28 MiB/s, done.
Total 17 (delta 12), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (12/12), done.
To https://github.com/danielvoldman/mpr-gamma-surge
 * [new tag]         fig-F1-v2 -> fig-F1-v2
 * [new tag]         fig-F2-v2 -> fig-F2-v2
 * [new tag]         fig-F3-v2 -> fig-F3-v2
 * [new tag]         fig-F4a-v2 -> fig-F4a-v2
 * [new tag]         fig-F4b-v2 -> fig-F4b-v2
 * [new tag]         fig-F5-v2 -> fig-F5-v2
 * [new tag]         fig-F5c-v2 -> fig-F5c-v2
 * [new tag]         fig-F6-v2 -> fig-F6-v2
 * [new tag]         fig-FS1-v2 -> fig-FS1-v2
 * [new tag]         fig-FS2-v2 -> fig-FS2-v2
 * [new tag]         fig-FS3-v2 -> fig-FS3-v2
 * [new tag]         fig-FS4-v2 -> fig-FS4-v2
 * [new tag]         fig-FS5-v2 -> fig-FS5-v2
 * [new tag]         release-v1.0 -> release-v1.0
 * [new tag]         criteria-frozen -> criteria-frozen
 * [new tag]         env-v1 -> env-v1
 * [new tag]         replication-pass -> replication-pass
 * [new tag]         tolerances-frozen -> tolerances-frozen
(.venv) (base) PS C:\dev\mpr-gamma-surge> git ls-remote --heads --tags origin
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/heads/master
0ad5793c1c64b04f40efba6b121b7e41743dbe83        refs/tags/criteria-frozen
dd8330c5eaacd63d21e7b7969430988d00862769        refs/tags/criteria-frozen^{}
bfb8ce3ad34407a7849524263d6d8f639279bfc6        refs/tags/env-v1
034a565828191dc730f5cd4ecd4169da7b84181a        refs/tags/env-v1^{}
9cee72f4655191c79b680d706fd5692b597ae3bf        refs/tags/fig-F1-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-F1-v2^{}
daee39a24b4471567d97b835ad526bbc6a5a87da        refs/tags/fig-F2-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-F2-v2^{}
92b9250345f348a74fa84bdaa0796c6b6e78d215        refs/tags/fig-F3-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-F3-v2^{}
44c28ad060fc3c61c63c390112180e94344d5736        refs/tags/fig-F4a-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-F4a-v2^{}
2bff282f8c57286f6e03476356ff86ba47f5efd9        refs/tags/fig-F4b-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-F4b-v2^{}
f16ba9c340156ca2397c9440651d5a4611d8fb2d        refs/tags/fig-F5-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-F5-v2^{}
bc647be2bdf3d1a37155e3f213c250ffb9b5b472        refs/tags/fig-F5c-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-F5c-v2^{}
86ab10e2b7fce482711cdc89516119902433ca06        refs/tags/fig-F6-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-F6-v2^{}
3fd53166881348643f63f04c7ec611557dea5b96        refs/tags/fig-FS1-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-FS1-v2^{}
b48b47445c7b325e4e6be826cd106a0397220b37        refs/tags/fig-FS2-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-FS2-v2^{}
1223847d322bdd486e2668918ce455e32df01db6        refs/tags/fig-FS3-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-FS3-v2^{}
28d3afdcb5ef54bc81535c284aa61d1e6108d346        refs/tags/fig-FS4-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-FS4-v2^{}
f5458cf0044190da3ff93597febbca7f3fb9d5b6        refs/tags/fig-FS5-v2
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/fig-FS5-v2^{}
bc63713066d35ce884c913cc23dbab1798163225        refs/tags/release-v1.0
33b7575721184b90571c2bbaffc4a9a0b1607a77        refs/tags/release-v1.0^{}
3d02526c605cdb46e2f723344ae2ac5d86eaef5e        refs/tags/replication-pass
9c7fee3c94cc5579d59b3889eca1c43a0f24c9d6        refs/tags/tolerances-frozen
bd301ce9fd3ca05d67020cb575c055148b3bdabc        refs/tags/tolerances-frozen^{}
```

Visibility of the repository (private or public): NOT verified by Claude Code (UNVERIFIED); the user is to confirm it on GitHub.
