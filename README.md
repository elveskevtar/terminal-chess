# terminal-chess
A python based terminal chess application. Uses ANSI escape sequences to print board squares and clear the screen – for reprinting. Visual UI likely to vary based on terminal and terminal settings/preferences.

![A screenshot of the starting game board](https://github.com/elveskevtar/terminal-chess/blob/mainline/game.png "Starting Game Board")
*Initial game board, waiting for first player's input*

Input to this application is standard [algebraic notation](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)). Long/fully-expanded algebraic notation, ICCF numeric notation, PGN, minimal/abbreviated algebraic notation are not supported yet, but may be in the future.

## Bug/Issue Reporting
Submit these to Github [issues](https://github.com/elveskevtar/terminal-chess).

Some things to keep in mind:
1. Prevent duplicates - search existing open and even closed issues before submitting
2. Rule out local issues - could this be an issue with your terminal/settings/preferences?
3. Provide steps to reproduce - e.g. if this is a bug in chess logic, provide the input that produces the bug
4. Provide environment details - if applicable, provide information like OS, terminal emulator, python version, terminal settings/preferences
5. Be respectful - this is a place for fun and collaboration :) keep it clean and respectful

Failure to follow these may result in your issue/bug report being immediately closed or ignored until the relevant details are provided.

## Feature Requests
Submit these to Github [issues](https://github.com/elveskevtar/terminal-chess). Please consider that this project is being worked on in the maintainer's free time so you are much more likely to have your feature if you make it yourself! See [Development](#development). Please cross-reference your feature request with items [In Development](#in-development) which have already been considered and likely to be picked up at some point.

## In Development
These are some of the items that have been thought of as potential next features/improvements to the current implementation. This list does not necessarily guarantee that the feature will ever be implemented but they have been considered.

1. General refactoring of the logic, initial implementation was done as a quick MVP focusing on correctness and not maintainability or future development. This is a high priority item.
2. Better UI/UX: this includes listing the moves already played, ~~the pieces captured per player~~, an option to flip the board display each turn, better help messages, etc.
3. Serialization and ability to save/continue a game
4. Draws/surrenders
5. Turn/game clock and different game modes like bullet, etc.
6. A hardy test suite
7. Allow other input notations and support formats like PGN
8. A simple AI

Writing a network module is something that I want to do but will take significant effort. It's on the long-term roadmap though.

## Development
Submit pull requests to Github. This project utilizes `pipenv` for development. Run `pipenv shell` to create and activate the virtual environment and use `pipenv install --dev` to install the necessary development dependencies.

* Start python virtual environment
```bash
/project-root> pipenv shell
```

* Install development dependencies
```bash
/project-root> pipenv install --dev
```

Please use flake8 to handle linting issues before submitting PRs. This includes linting for test files.

* Run linter
```bash
/project-root> flake8
```

Please run tests to ensure nothing was broken. Also, write tests for your changes if applicable.

* Run tests
```bash
/project-root> pytest
```

If you want to install the package to validate the script.

* Install terminal-chess package
```bash
/project-root> pip install .
```

* Run game from script after install
```bash
/project-root> pychess
``` 

## Tenets
A list of tenets that this project goes by:
1. Avoid unnecessary dependencies - this is a relatively minimal implementation of chess for the terminal
2. Maintainable and expandable - changes over time should promote and make future development easier & reduce tech debt; this includes linting, sufficient testing, and using proper design patterns
3. Avoid boilerplate/setup hell - avoid any changes that complicate future development or further restrict useable environments to run/develop on
4. Open source - engage the community and promote collaboration on this project

## License
`terminal-chess` is published under the MIT license; see [LICENSE](LICENSE).
