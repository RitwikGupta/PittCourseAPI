# Contributing Guidelines

To get started with contributing to the Pitt API, please read these guidelines in their entirety to set up your development environment and learn our tooling.

## Initial Setup

### Setting Up Your Virtual Environment

The Pitt API uses [`pipenv`](https://pipenv.pypa.io/en/latest/) to manage its dependencies. As such, you should also use `pipenv` for your own Pitt API development rather than the more traditional `pip` and `venv`.

To set up `pipenv`, first install the package using `pip`:
```sh
pip install --user pipenv
```
Now install `pipenv` to your local Pitt API git repo:
```sh
pipenv install
```
This will install all necessary dependencies listed in the [Pipfile](/Pipfile) and also set up your virtual environment.
Start the virtual environment with
```sh
pipenv shell
```
and close it down with
```sh
exit
```

### Pre-Commit

As a contributor, you should add [pre-commit](https://pre-commit.com/) to your development workflow in order to help us maintain a high-quality codebase.
We've included several pre-commit hooks in [`.pre-commit-config.yaml`](/.pre-commit-config.yaml) that we consider to be essential for our purposes.

pre-commit is installed automatically as a dependency when you set up your virtual environment with `pipenv`.
To add pre-commit to your workflow, run
```sh
pre-commit install
```
From this point on, pre-commit should run whenever you make a commit.
If it catches any errors (trailing whitespace, questionable code formatting, etc.), it'll try to fix them automatically or ask you to fix them if it can't.
Make sure to fix all pre-commit errors before you commit.

By default, pre-commit checks all modified files staged in your commit.
If you want to run pre-commit on the entire repo, including files that you haven't modified, run
```sh
pre-commit run --all-files
```

## Contributing to the API

To make a contribution to the Pitt API, simply open a PR from your local fork of the Pitt API repo.

Naturally, you should ensure that contributions work and are of high quality before you make a PR.
This includes making sure that your code compiles, passes all unit tests, and adhere to common style guidelines.

### Unit Testing

The Pitt API uses `pytest` for unit testing, and like pre-commit it's installed automatically when you set up `pipenv`.
To run all unit tests, run
```sh
pytest --cov=pittapi tests/
```

### Code Styling

To ensure consistent and readable code, we use the `black` formatter to help our code adhere to [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
`black` is also installed automatically when you set up `pipenv`, and it's also included in our pre-commit hooks.
If you have pre-commit set up correctly, pre-commit should run `black` automatically when you make a commit.

To format the whole codebase on your own, simply run
```sh
black .
```

Apart from general code styling, you should also document and comment your code based on general best practices.
This means that most if not all functions should have docstrings explaining their purpose, inputs, and outputs.
This also means that comments should primarily be written to clarify code whose function isn't immediately obvious to the average reader.
We may ask you to make changes to your documentation and comments during PR reviews.

In terms of writing style, we expect you to write in a professional manner and follow proper commenting etiquette—pretend that this is a work environment and your comments are being reviewed by your manager and coworkers.

### GitHub Workflows

Note that we use automated GitHub workflows to check incoming PRs.
For you as a contributor, this means that GitHub will run `black` and `pytest` on your PR.
Make sure your code pass all workflows before requesting a review.
