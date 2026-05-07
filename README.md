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

# Project Structure

```
enterprise_qa_platform_py/
├── artifacts/                    # Test artifacts and reports
├── ci/                          # CI/CD pipeline configuration files
├── configs/                     # Configuration files
│   ├── default.yaml             # Default configuration
│   └── dev.yaml                 # Development configuration
├── src/                         # Framework source code
│   └── framework/
│       ├── adapters/            # External integrations
│       │   └── playwright_factory.py
│       ├── core/                # Core framework functionality
│       │   ├── config/
│       │   │   └── models.py     # Configuration data models
│       │   ├── exceptions/
│       │   │   └── exceptions.py # Custom exception definitions
│       │   ├── governance/
│       │   │   └── yaml_schema.py # YAML schema validation
│       │   ├── observability/   # Logging and reporting
│       │   │   ├── logger_config/
│       │   │   │   ├── log_setup.py
│       │   │   │   ├── logger_v1.py
│       │   │   │   └── logger_v2.py
│       │   │   └── reporting/
│       │   └── quality/         # QA assertions and heuristics
│       │       ├── assertions/
│       │       │   ├── assert_api.py      # API assertions
│       │       │   ├── assert_desktop.py  # Desktop app assertions
│       │       │   ├── assert_evidence.py # Evidence-based assertions
│       │       │   └── assert_web.py      # Web assertions
│       │       └── heuristics/
│       │           └── flaky_detection.py # Flaky test detection
│       ├── utils/               # Utility functions
│       │   ├── utils_date.py
│       │   ├── utils_file.py
│       │   ├── utils_generic.py
│       │   ├── utils_loader.py
│       │   ├── utils_path.py
│       │   ├── utils_string.py
│       │   └── utils_yaml_generator.py
│       ├── domains/             # Domain-specific implementations
│       │   ├── api/             # API testing domain
│       │   └── web/             # Web testing domain
│       │       ├── base_page.py
│       │       ├── locators/     # Locator management
│       │       │   ├── locator_actions.py
│       │       │   └── locator_resolver.py
│       │       ├── locators_repository/
│       │       │   └── loginpage.yaml
│       │       └── pages/        # Page object models
│       │           └── login.py
│       └── services/            # Business services
├── tests/                       # Test files
│   ├── conftest.py             # Pytest configuration
│   ├── api/                    # API tests
│   ├── desktop/                # Desktop application tests
│   ├── poc/                    # Proof of concept tests
│   │   ├── test_hello.py
│   │   └── test_web.py
│   └── web/                    # Web tests
├── pyproject.toml              # Poetry dependencies and project metadata
├── README.md                   # Project documentation
└── LearningAndFixing_Issues.md # Learning notes and issues log
```

## Key Components

### Framework (`src/framework/`)
- **Adapters**: External integrations (Playwright, etc.)
- **Core**: Central framework logic including config, exceptions, and observability
- **Utils**: Reusable utility functions for common operations
- **Domains**: Domain-specific implementations (API, Web, Desktop)
- **Services**: Business service layers

### Configuration (`configs/`)
- Environment-specific YAML configurations
- Default and development settings

### Tests (`tests/`)
- API tests
- Web tests (Selenium/Playwright)
- Desktop application tests
- Proof of concepts

### CI/CD (`ci/`)
- Pipeline configuration files

# Commands :








 # Ref Url's:
 ## https://yrkan.com/blog/pytest-advanced-techniques/
 ## https://pytest-with-eric.com/hooks/pytest-hooks/ Git Repo: [text][def]

[def]: https://github.com/pytest-with-Eric/pytest-hooks-example.git