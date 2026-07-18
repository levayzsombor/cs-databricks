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
4. Node
5. Shellcheck
6. shfmt
7. actionlint
8. uv
9. yamlfmt
