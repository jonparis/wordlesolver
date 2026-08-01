# wordle

A python based tool suggested words for wordle.

## Setup

`wordle.db` (the cache of solved positions) is stored with [Git LFS](https://git-lfs.com),
so you need it installed before cloning or pulling, otherwise you get a small text
pointer file instead of the real database:

```
brew install git-lfs   # or: apt install git-lfs
git lfs install
git lfs pull
```

## How to use

```
python3 run.py
```

The game has two modes.

A. Play mode. 
Allows you to play the game with suggestions as optional

B. Suggest mode. Allows you to get suggestions that you use in external games.
This allows you to share the words you got, the current matches given previous responses, 
and get the best guess to solve the game in the fewest tries.

## Note: On the suggestions
The suggested guesses have been tested solving the game in an average of 3.42592 guesses (if  starting with 'salet')

You use and share this solver with nicer user interface at [https://wordleweb.vercel.app](https://wordleweb.vercel.app/suggestions)

