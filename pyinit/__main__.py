import os
import argparse
import sys


def create_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Python project structure"
    )
    parser.add_argument("name", help="Name of the Python script to create")
    args = parser.parse_args()

    name = args.name
    
    # Validate that the name doesn't contain hyphens
    if "-" in name:
        suggested_name = name.replace("-", "_")
        print("Error: Hyphens ('-') are not allowed in Python package names.", file=sys.stderr)
        print("This causes issues with mypy and other tools that expect import names to match package names.", file=sys.stderr)
        print("Please use underscores ('_') instead.", file=sys.stderr)
        print(f"Suggestion: Use '{suggested_name}' instead of '{name}'", file=sys.stderr)
        sys.exit(1)

    os.mkdir(name)
    os.chdir(name)

    os.mkdir(name)

    create_file(f"{name}/__init__.py", "")

    create_file(
        f"{name}/__main__.py",
        f"""import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description='{name}')

    args = parser.parse_args()

    print("Hello, world!")


if __name__ == "__main__":
    main()
""",
    )

    create_file(
        ".gitignore",
        """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/latest/usage/project/#working-with-version-control
.pdm.toml
.pdm-python
.pdm-build/

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/

# nix
result
""",
    )

    create_file(
        "flake.nix",
        f"""{{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  outputs =
    {{
      self,
      nixpkgs,
      poetry2nix,
    }}:
    let
      supportedSystems = [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${{system}});
    in
    {{
      packages = forAllSystems (
        system:
        let
          inherit (poetry2nix.lib.mkPoetry2Nix {{ pkgs = pkgs.${{system}}; }}) mkPoetryApplication;
        in
        {{
          default = mkPoetryApplication {{ 
            projectDir = self;
            # Set checkGroups to an empty list to disable the inclusion of dev dependencies
            # https://github.com/nix-community/poetry2nix/issues/1335
            checkGroups = [ ];
          }};
        }}
      );

      devShells = forAllSystems (
        system:
        let
          inherit (poetry2nix.lib.mkPoetry2Nix {{ pkgs = pkgs.${{system}}; }}) mkPoetryEnv;
        in
        {{
          default = pkgs.${{system}}.mkShellNoCC {{
            packages = with pkgs.${{system}}; [
              (mkPoetryEnv {{ projectDir = self; }})
              poetry
            ];
          }};
        }}
      );
    }};
}}
""",
    )

    #     create_file('mypy.ini', '''[mypy]
    # strict = True
    # ''')

    create_file(
        "pyproject.toml",
        f"""[tool.poetry]
name = "{name}"
version = "0.1.0"
description = ""
authors = ["Author Name <author@example.com>"]
readme = "README.md"
packages = [
  {{ include = "{name}" }}
]

[tool.poetry.dependencies]
python = "^3.10"

[tool.poetry.group.dev.dependencies]
black = "^23.3.0"
mypy = "^1.11.0"

[tool.poetry.scripts]
{name} = "{name}.__main__:main"

[tool.black]

[tool.mypy]
strict = true

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""",
    )

    create_file(
        "README.md",
        f"""# {name}

To get started, run the following:

```
poetry install
poetry run {name}
```

# Formating & type checking
```
poetry run black {name}
poetry run mypy {name}
```

# Nix Support
This project comes with nix support. You can enter the nix shell by running `nix develop`.

## Building
Building can help troubleshoot packaging issues. Run `nix build` and then `results/bin/{name}`.
""",
    )

    try:
        os.system("git rev-parse --is-inside-work-tree")
    except:
        # TODO: this can also happen if git isn't present, we should handle that
        os.system("git init")
        os.system("git add *")
        os.system('git commit -m "Initial commit"')

    # Generate poetry.lock
    os.system("poetry lock --no-update")


if __name__ == "__main__":
    main()
