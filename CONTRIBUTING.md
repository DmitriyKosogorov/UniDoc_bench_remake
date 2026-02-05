# Contributing Guide For UNIDOC-BENCH

This page lists the operational governance model of this project, as well as the recommendations and requirements for how to best contribute to UNIDOC-BENCH. We strive to obey these as best as possible. As always, thanks for contributing – we hope these guidelines make it easier and shed some light on our approach and processes.

# Governance Model

## Salesforce Sponsored

The intent and goal of open sourcing this project is to increase the contributor and user base. However, only Salesforce employees will be given `admin` rights and will be the final arbiters of what contributions are accepted or not. This ensures consistency with the research goals and maintains quality standards for the benchmark.

# Getting started

Please join the community by opening an issue on GitHub for discussions. Also please make sure to take a look at the project structure and understand the four main components:

1. **Document Tagging** (`src/vllm_tagging.py`) - Document classification and metadata extraction
2. **Dataset Synthesis** (`src/qa_synthesize/`) - QA pair generation pipeline
3. **Baseline Implementations** (`src/baselines/`) - RAG system implementations
4. **Evaluation Framework** (`src/evaluation/`) - Benchmark evaluation tools

# Issues, requests & ideas

Use GitHub Issues page to submit issues, enhancement requests and discuss ideas.

### Bug Reports and Fixes
-  If you find a bug, please search for it in the [Issues](https://github.com/salesforce/unidoc-bench/issues), and if it isn't already tracked,
   [create a new issue](https://github.com/salesforce/unidoc-bench/issues/new). Fill out the "Bug Report" section of the issue template. Even if an Issue is closed, feel free to comment and add details, it will still
   be reviewed.
-  Issues that have already been identified as a bug (note: able to reproduce) will be labelled `bug`.
-  If you'd like to submit a fix for a bug, [send a Pull Request](#creating_a_pull_request) and mention the Issue number.
  -  Include tests that isolate the bug and verifies that it was fixed.

### New Features
-  If you'd like to add new functionality to this project, describe the problem you want to solve in a [new Issue](https://github.com/salesforce/unidoc-bench/issues/new).
-  Issues that have been identified as a feature request will be labelled `enhancement`.
-  If you'd like to implement the new feature, please wait for feedback from the project
   maintainers before spending too much time writing the code. In some cases, `enhancement`s may
   not align well with the project objectives at the time.

### Domain-Specific Contributions
-  **New Domain Support**: Adding support for new document domains (e.g., scientific papers, technical manuals)
-  **Baseline Improvements**: New RAG implementations or improvements to existing baselines
-  **Evaluation Metrics**: Additional evaluation metrics or analysis tools
-  **Document Processing**: Improvements to document parsing, tagging, or preprocessing

### Tests, Documentation, Miscellaneous
-  If you'd like to improve the tests, you want to make the documentation clearer, you have an
   alternative implementation of something that may have advantages over the way its currently
   done, or you have any other change, we would be happy to hear about it!
  -  If its a trivial change, go ahead and [send a Pull Request](#creating_a_pull_request) with the changes you have in mind.
  -  If not, [open an Issue](https://github.com/salesforce/unidoc-bench/issues/new) to discuss the idea first.

If you're new to our project and looking for some way to make your first contribution, look for
Issues labelled `good first contribution`.

# Contribution Checklist

- [x] Clean, simple, well styled code
- [x] Commits should be atomic and messages must be descriptive. Related issues should be mentioned by Issue number.
- [x] Comments
  - Module-level & function-level comments.
  - Comments on complex blocks of code or algorithms (include references to sources).
  - Document any domain-specific logic or evaluation metrics.
- [x] Tests
  - The test suite, if provided, must be complete and pass
  - Increase code coverage, not versa.
  - For new baselines, include evaluation results on a subset of the benchmark
  - For new evaluation metrics, include validation against known ground truth
- [x] Dependencies
  - Minimize number of dependencies.
  - Prefer Apache 2.0, BSD3, MIT, ISC and MPL licenses.
  - Document any new dependencies and their purpose
- [x] Documentation
  - Update README.md if adding new features or changing existing functionality
  - Document any new command-line arguments or configuration options
  - Include usage examples for new features
- [x] Reviews
  - Changes must be approved via peer code review

# Creating a Pull Request

1. **Ensure the bug/feature was not already reported** by searching on GitHub under Issues.  If none exists, create a new issue so that other contributors can keep track of what you are trying to add/fix and offer suggestions (or let you know if there is already an effort in progress).
2. **Fork** the repository on GitHub
3. **Clone** the forked repo to your machine.
4. **Create** a new branch to contain your work (e.g. `git checkout -b feature/new-baseline`)
5. **Commit** changes to your own branch with descriptive commit messages.
6. **Test** your changes thoroughly, especially if adding new baselines or evaluation metrics.
7. **Push** your work back up to your fork. (e.g. `git push origin feature/new-baseline`)
8. **Submit** a Pull Request against the `main` branch and refer to the issue(s) you are fixing. Try not to pollute your pull request with unintended changes. Keep it simple and small.
9. **Sign** the Salesforce CLA (you will be prompted to do so when submitting the Pull Request)

> **NOTE**: Be sure to [sync your fork](https://help.github.com/articles/syncing-a-fork/) before making a pull request.

## Pull Request Guidelines

### For New Baselines
- Include evaluation results on at least one domain from the benchmark
- Document any new dependencies or requirements
- Provide clear usage instructions in the README or script comments

### For New Evaluation Metrics
- Validate the metric against known ground truth or existing benchmarks
- Include examples of the metric output
- Document the interpretation of the metric values

### For Dataset Contributions
- Ensure data quality and proper formatting
- Include domain information and metadata
- Follow the existing data structure conventions

# Contributor License Agreement ("CLA")
In order to accept your pull request, we need you to submit a CLA. You only need
to do this once to work on any of Salesforce's open source projects.

Complete your CLA here: <https://cla.salesforce.com/sign-cla>

# Development Environment Setup

## Prerequisites
- Python 3.9+
- Conda or virtual environment
- Git

## Setup Steps
1. Fork and clone the repository
2. Create a conda environment: `conda create -n unidoc-bench python=3.9`
3. Activate environment: `conda activate unidoc-bench`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up API keys for OpenAI, Google, and other services as needed

## Testing Your Changes
- Run existing tests: `python -m pytest tests/`
- Test new baselines on a small subset of data
- Validate evaluation metrics against known results

# Issues
We use GitHub issues to track public bugs, feature requests, and enhancement proposals. Please ensure your description is clear and has sufficient instructions to be able to reproduce the issue.

# Code of Conduct
Please follow our [Code of Conduct](CODE_OF_CONDUCT.md).

# License
By contributing your code, you agree to license your contribution under the terms of our project [LICENSE](LICENSE.txt) and to sign the [Salesforce CLA](https://cla.salesforce.com/sign-cla)
