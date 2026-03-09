This guide covers the essential commands for managing [Homebrew](https://brew.sh/), the primary package manager for macOS. [1, 2]
1. Basic Management

* brew install <formula>: Installs a command-line tool (formula).
* brew install --cask <app>: Installs a GUI application (cask) like Chrome or Slack.
* brew uninstall <formula>: Removes an installed package.
* brew list: Displays all currently installed packages. [1, 3, 4, 5, 6]
* brew list --installed-on-request: List all packages manually installed

2. Maintenance & Updates

* brew update: Updates the Homebrew database of available packages.
* brew upgrade: Upgrades all installed packages to their latest versions.
* brew outdated: Lists all installed packages that have a newer version available.
* brew cleanup: Deletes old versions of installed formulae and clears the download cache.
* brew doctor: Diagnoses your system for potential issues or configuration errors. [1, 4, 7, 8, 9, 10]

3. Discovery & Information

* brew search <text>: Searches for available formulae or casks matching the text.
* brew info <formula>: Displays detailed metadata, including version, dependencies, and caveats.
* brew deps <formula>: Shows the other packages required for a specific formula to run. [1, 3, 4, 11]

4. Advanced Commands

* brew tap <user/repo>: Adds a third-party repository (tap) to expand available packages.
* brew pin <formula>: Locks a package at its current version so it won't be updated by brew upgrade.
* brew unpin <formula>: Allows a previously locked package to be updated again.
* brew services: Manages background services (e.g., starting or stopping a database like PostgreSQL). [1, 7, 12, 13]

------------------------------
🚀 Quick-Start Cheatsheet [14]

| Action [1, 15] | Command |
|---|---|
| New Install | brew install <package> |
| Update All | brew update && brew upgrade |
| Check Health | brew doctor |
| Find App | brew search <name> |
| View Installed | brew list |
| Free Up Space | brew cleanup |

Do you want to see how to back up all your currently installed apps into a single file for easy migration to a new Mac?

[1] [https://bold-brew.com](https://bold-brew.com/blog/essential-homebrew-commands.html)
[2] [https://www.scribd.com](https://www.scribd.com/document/412085891/Cheatsheet-Homebrew)
[3] [https://www.scribd.com](https://www.scribd.com/document/488478899/cheatsheet-homebrew)
[4] [https://www.ubuntumint.com](https://www.ubuntumint.com/homebrew-commands-cheat-sheet-linux/)
[5] [https://www.scribd.com](https://www.scribd.com/document/488478899/cheatsheet-homebrew)
[6] [https://cheatsheets.zip](https://cheatsheets.zip/homebrew#:~:text=Table_title:%20Commands%20Table_content:%20row:%20%7C%20brew%20uninstall,List%20the%20installed%20versions%20of%20package%20%7C)
[7] [https://medium.com](https://medium.com/@richyvk/basic-homebrew-commands-f99c704e564f)
[8] [https://infoheap.com](https://infoheap.com/mac-home-brew-beginner-guide/)
[9] [https://www.educative.io](https://www.educative.io/answers/what-is-brew-cleanup#:~:text=brew%20cleanup%20%5B%2D%2Dprune=days%5D%20%5B%2D%2Ddry%2Drun%5D%20%5B%2Ds%5D%20%5Bformulae%5D:%20For,remove%20all%20cache%20files%20older%20than%20days.)
[10] [https://onecompiler.com](https://onecompiler.com/cheatsheets/homebrew#:~:text=Table_title:%20Other%20useful%20commands%20Table_content:%20header:%20%7C,sooftware%20%7C%20Example:%20brew%20upgrade%20mongodb%20%7C)
[11] [https://gist.github.com](https://gist.github.com/9661ea5de9f460fb5e8b)
[12] [https://www.scribd.com](https://www.scribd.com/document/488478899/cheatsheet-homebrew)
[13] [https://dev.to](https://dev.to/andremare/homebrew---basics--cheatsheet-3a3n#:~:text=%23%20List%20all%20the%20current%20tapped%20repositories,tap%20from%20the%20repository%20$%20brew%20untap)
[14] [https://marslo.github.io](https://marslo.github.io/ibook/osx/apps/brew.html)
[15] [https://gist.github.com](https://gist.github.com/9661ea5de9f460fb5e8b)
