# enterprise_qa_platform_py

# Setup from Scratch
## Create a directory and open the folder from VS Code (VSC)

## Open terminal window
### Run command "python -m venv .venv" or "Ctrl + Shift + P"->"Python:Create Environment"
### Run command "poetry init --no-interaction" Comments: if poetry file "pyproject.toml" do not exists it will be initialized.

## Add packages:
### Run command "poetry add --group required pydantic pytest pytest-xdist pytest-timeout pytest-rerunfailures pytest-html allure-pytest pytest-playwright playwright requests pywinauto structlog pyyaml python-dotenv" comment: single command to add all dependencies in group and install

# Create directory structure
    mkdir config                :> YAML config files, YAML locator files
    mkdir src                   :> Framework files
    mkdir tests                 :> Test files
    mkdir ci                    :> YAML CI/CD pipeline files

# Commands :








 # Ref Url's:
 ## https://pytest-with-eric.com/hooks/pytest-hooks/ Git Repo: [text][def]

[def]: https://github.com/pytest-with-Eric/pytest-hooks-example.git