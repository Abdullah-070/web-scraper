# Contributing to Sanestix Web Scraper

Thank you for contributing to this project.

This repository is owned and maintained by Sanestix Labs. To ensure code quality, maintainability, and smooth collaboration among team members and interns, please follow the guidelines below.

---

## Development Workflow

All development must follow the Git workflow below:

```text
main
│
└── develop
    ├── feature/your-feature-name
    ├── feature/another-feature
    └── bugfix/issue-name
```

### Rules

- Never commit directly to `main`.
- Never commit directly to `develop`.
- Create a feature branch for every task.
- Submit a Pull Request (PR) for review before merging.

---

## Branch Naming Convention

### Feature

```text
feature/add-login-system
feature/create-parser
feature/dashboard-ui
```

### Bug Fix

```text
bugfix/fix-duplicate-records
bugfix/resolve-api-timeout
```

### Documentation

```text
docs/update-readme
docs/api-documentation
```

---

## Getting Started

### Clone Repository

```bash
git clone https://github.com/SanestixLabs/sanestix-web-scraper.git
cd sanestix-web-scraper
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Project Structure

```text
sanestix-web-scraper/
│
├── scraper/
├── parsers/
├── api/
├── database/
├── config/
├── scripts/
├── tests/
├── docs/
│
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
└── .env.example
```

---

## Coding Standards

### General

- Write clean and readable code.
- Keep functions small and focused.
- Use meaningful variable names.
- Avoid duplicated code.
- Add comments only when necessary.

### Naming Conventions

#### Variables

```python
user_name
product_url
scrape_result
```

#### Functions

```python
fetch_products()
parse_html()
save_to_database()
```

#### Classes

```python
ProductParser
DatabaseManager
ScraperEngine
```

---

## Commit Message Convention

Use the following format:

### Feature

```text
feat: add product parser
```

### Bug Fix

```text
fix: resolve duplicate scraping issue
```

### Documentation

```text
docs: update installation instructions
```

### Refactoring

```text
refactor: simplify parser architecture
```

### Testing

```text
test: add parser unit tests
```

### Maintenance

```text
chore: update dependencies
```

---

## Pull Request Guidelines

Before creating a Pull Request:

### Checklist

- [ ] Code compiles successfully
- [ ] No unnecessary files included
- [ ] Tests pass successfully
- [ ] Documentation updated if required
- [ ] Branch is up to date with develop
- [ ] Code follows project standards

### Pull Request Title Examples

```text
feat: implement Amazon product scraper

fix: resolve database connection issue

docs: update API documentation
```

---

## Issue Assignment Process

1. Issue is created.
2. Issue is assigned to a contributor.
3. Contributor creates a feature branch.
4. Development is completed.
5. Pull Request is submitted.
6. Maintainer reviews code.
7. Changes are requested if needed.
8. Approved code is merged into `develop`.

---

## Testing

All new features should include appropriate tests whenever possible.

Run tests:

```bash
pytest
```

Contributors are encouraged to verify that all tests pass before submitting a Pull Request.

---

## Security Policy

Never commit:

```text
.env
API Keys
Passwords
Tokens
Database Credentials
SSH Keys
```

Only commit:

```text
.env.example
```

Example:

```env
DATABASE_URL=
OPENAI_API_KEY=
SCRAPER_API_KEY=
```

---

## Code Review Policy

Every Pull Request must be reviewed before merging.

Reviewers will check:

- Code quality
- Security concerns
- Project architecture
- Performance impact
- Documentation updates

---

## Communication

If you are stuck on a task:

1. Create a comment on the assigned Issue.
2. Explain the problem clearly.
3. Include screenshots or error logs when relevant.
4. Do not leave tasks inactive without updates.

---

## Ownership

This repository is the intellectual property of Sanestix Labs.

All contributions made within this repository become part of the company's codebase and may be modified, redistributed, or used by Sanestix Labs as required.
