.. This document is in reStructuredText format

.. Files:
.. - git-docu.uml
..   UML diagrams visualizing git concepts. Format is ArgoUML (http://argouml.tigris.org/)
.. - gitconnector_tutorial.txt
..   Tutorial on git & gitconnector. It's HTML output is used by gitconnector as help page.
.. - *.py
..   Python source code of gitconnector. 
.. - pre-commit, commit-msg, ... (git hook names)
..   Well, nataurally the git hook scripts.

gitconnector
======================================================================


Responsibilities / Goals
--------------------------------------------------
Ordered after prio:

- Central repo adheres to dragon guidelines.

- Simple and easy standart use cases

  - refine local state so it is 'nice' and thus pushable to central repo

  - push to central repo

  - pull from central repo

  - all that for 'main' branch

- Local repo can be anything. The point of DVCS is to locally do whatever you like.

  - However git dragon is only required to be able to work with a set of predefined states 

  - Engineers should be allowed any git tool/frontend they like

- Must remain minimalistic, simple. We cannot afford to build yet another cool
  git front end. Git offers loads of features, gitconnector can't even cover a
  small subset of them. We should define a standart front end like tortoise or
  smart-git, which then also appears in our own howtos. Some of the not anymore
  very basic workflows, but still standard/common workflows, like
  creating/switching multiple lokal branches, using the index, using the stash,
  should not be done with gitconnector.

- We don't have the (HW) infrastructure to do expensive compile test on the
  central server side. Thus the compile test must remain, as with
  vssconnector, on the client side.

- Does not undertake countermeassures against 'malicous' co-workers - we don't
  have them. If somebody really want's to circumvent the checks he can do it
  anyway.

Beside the 'ensure guidelines' thing, vssconnector was needed because vss is so
bad. gitconnector is needed because git offers so many workflows, the average
user might be overhelmed at the beginning - gitconnector shall give an easy to
use minimalistic abstraction of git's huge feature set.


.sln Problematic
--------------------------------------------------

.sln files are logically not needed. However final builder seems to need them.
Furthermore, MS Studio seems to always change some funny 'hash' values within
this file, altough no change to the solution was made. Thus: Because of final
builder, .sln files need to be in the git repo. Because of MS Studio's changes
to the .sln, we will always have merge conflicts if the .sln are in the repo.
Possible solutions

1) Put the .sln in a say ``./guesel/myproject.sln``. Nobody except final builer
   uses that file. A new build step in final builder would copy the file from
   ``./guesel/`` to ``./`` prior to actually building the solution.

2) git commit hook could always undo the changes MS Visual studio does. The
   characteristics of MS Studios automatic changes are known, so we can
   distinguis them from intended changes by the user. However maybe that will
   crash MS Studio because it doesn't like if one changes it's files behind it's
   back.


gitconnector commands
--------------------------------------------------

The basic commandos are release, commit, pull, make-nice.

release does almost everything together:

- commit any local changes

- pull

  - fetch all remote refs

  - merge remote tracking branch into free branch

  - rebase nice branch onto remote tracking branch

- make nice = merge-squash free into/onto nice

- push nice branch

.. Always on top level: commit


todo / ideas
--------------------------------------------------

- gitconnector can run in different modes: a) dummy/verbose and b)
  expert/normal. In dummy mode much more info is shown, more is asked etc.

- status windows clearly visibel shows when repo is in merge/rebase conflict. 
  - most commands cannot even be started. Precondition check fails.	

- when free is tracking remote, the '# of commits ahead' count is not what I
  expect.

- make use of branches dir for a per branch refspec	

- Proposed info text: A gitconnector release/... was interrupted / not finished.
  However that does not mean anything special. You can continue to work however
  you want. Most likely you want restart the release/pull/... gitconnector's
  commands can work with (almost) any state of you're repo; they get their job
  done, no mather with what repo state they have to start with.

- The idea is to never be stuck / limited to a given dialog. WHEN you have any
  controll, you have FULL controll. So you always can use whatever tools you
  would like. It also fits into how git usualy works, there are none (?)
  interactive commands which keep on working with you while they are running.
  interactive in git also always mean, you have full controll.

- Gitconnector can work with almost any state anyway. That must be, because on
  your local repo you can do whatever you want, and use whichever tool you want.

- disabled buttons/menus: tooltip tells why it is disabled

- Copy Paste must be possible everywhere. 

- No label/text/info is ever truncated

1) I want to see what is going on basically. --> I want to see the major steps
   and their major result.

2) If something fails, I want to know the major cause, and a tip what I should do now.

3) I dont want to remember that info --> log which can be opened again upon
   request --> current state warning info if current state is not normal

4) If I know git well, or if i am gitconnector developper, I want to find the
   root of a trouble myself, I want to see more indepth info.



