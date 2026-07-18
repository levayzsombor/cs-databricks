# Country Stats

This is a showcase project that gives statistics about countries  through Azure Databricks and Power Bi with basic open source apis.

The aim of this project is to show what improvements can be made on other projects.

## Table of content:

## Dev container for VS Code

With developer container the users can have an exact setup that is ready after they opened the repository / workspace. Devcontainers can be used with other IDEs, this one is made for VS Code in mind. It downloads the programs neccessary to work (such as python, git graph etc…), runs a post script to install everything needed such as python requirements and node modules, Downloads the VS Code extensions and configures them. 

This will make sure that everyone works from the same setup if they chose to do so. You can still use your own other Extensions ( such as Material Icon Theme). With the.devcontainer.json other IDEs can also be added to work with. Developers can opt-out from using this and disable it, then they have to make sure their own local environment works with the repository as intended.

### Install guide:

1. download  and install Git: [https://git-scm.com/install/](https://git-scm.com/install/)
2. download and install VS Code: [https://code.visualstudio.com/download](https://code.visualstudio.com/download)
3. download and install Docker Desktop (or just simple docker CLI) : [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
4. If Windows is used install WSL powershell:  `wsl --install`
5. open VS Code
6. Download this repository: [https://github.com/levayzsombor/cs-databricks](https://github.com/levayzsombor/cs-databricks)
7. Add the Dev Containers extension to VS Code: ms-vscode-remote.remote-containers
8. Either click on the pop-up to start the container or ctrl + shift + P -> Dev containers: Rebuild and Reload container

### Installed programs:

1. Git
2. Azure-CLI
3. Copilot-CLI
4. Node : for Eslint and Prettier
5. Shellcheck : for shell linting
6. shfmt: for shell formatting
7. actionlint: for github actions linting
8. yamlfmt: for yaml formatting

### Installed extensions:

1. Git graph: a visual helper for git branches
2. Git blame: can see inline the last change
3. Git History: an easy visual way to check file and commit history
4. YAML: yaml language support
5. Ruff: Python linter and formatter while coding
6. TY: Python type checker while coding
7. Jupyter: for notebooks
8. EchoAPI: Postman like Rest API program
9. Databricks: Connect to a databricks environment
10. GitHub Actions: see the GHA running on the repo
11. GitHub Pull Request: create and handle pull requests in VS Code
12. GitHub repositories: Browse GitHub repos without checkout
13. GitHub Copilot: enable copilot inside the container
14. GitHub Copilot chat: chat window for Copilot
15. GitHub Actions (YAML): YAML schema validation
16. Prettier: default formatter (python, and shell not included)
17. Bash IDE: shell script linting and formatting while coding
18. Code Spell Checker: Spell checking for for .MD files and strings
19. Markdown Editor: Helps editing .MD files in a Preview format (Right-click edit with markdown editor)

## Git Branching strategy and deployment

Git branching strategies combining Git Rules ( for branches and tags ), GitHub Actions and Permissions help create an orderly merge for code making sure the protected branched have their intended version of the code.
With the same GitHub Actions the Deployment and updates of the Azure applications can be started to make it automatic.

### Git Branches:

1. PR branch:
   - Any branch can be merged into it.
   - Can only merge to the 'main' protected branch
   - Needs a pull request
