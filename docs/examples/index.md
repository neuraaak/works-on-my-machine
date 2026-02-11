# Examples

Practical examples and common use cases for WOMM.

## Basic Usage

### Create a Simple Python Project

```bash
# Create project
womm new python hello-world

# Navigate to project
cd hello-world

# Activate virtual environment
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows

# Your project is ready!
```

### Create a JavaScript Project

```bash
# Basic Node.js project
womm new javascript my-app

# Navigate and install dependencies
cd my-app
npm install

# Start development
npm run dev
```

## Python Examples

### Django Web Application

```bash
# Create Python project
womm new python django-blog

cd django-blog
source .venv/bin/activate

# Install Django
pip install django

# Create Django project
django-admin startproject config .
python manage.py startapp blog

# Run with pre-configured linting
womm lint
```

### FastAPI REST API

```bash
# Create Python project
womm new python fastapi-api

cd fastapi-api
source .venv/bin/activate

# Install FastAPI and uvicorn
pip install fastapi uvicorn[standard]

# Create main.py
cat > src/main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
EOF

# Run server
uvicorn src.main:app --reload

# Lint code
womm lint
```

### Data Science Project

```bash
# Create Python project
womm new python data-analysis

cd data-analysis
source .venv/bin/activate

# Install data science libraries
pip install pandas numpy matplotlib jupyter

# Create Jupyter notebook
jupyter notebook

# Lint Python files
womm lint src/
```

## JavaScript Examples

### React Application

```bash
# Create React project
womm new javascript my-react-app --type react

cd my-react-app

# Install dependencies
npm install

# Start development server
npm start

# Run linting
womm lint
```

### Vue Application

```bash
# Create Vue project
womm new javascript my-vue-app --type vue

cd my-vue-app
npm install

# Start dev server
npm run dev

# Lint code
womm lint
```

### Express REST API

```bash
# Create JavaScript project
womm new javascript express-api

cd express-api

# Install Express
npm install express cors dotenv

# Create server.js
cat > src/server.js << 'EOF'
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello World!' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
EOF

# Run server
node src/server.js

# Lint code
womm lint
```

## Complete Workflows

### Full Python Development Workflow

```bash
# 1. Create project
womm new python my-package

# 2. Navigate and activate
cd my-package
source .venv/bin/activate

# 3. Install dependencies
pip install requests pydantic

# 4. Write code
cat > src/main.py << 'EOF'
from typing import List
import requests

def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    data = fetch_data("https://api.github.com")
    print(data)
EOF

# 5. Write tests
cat > tests/test_main.py << 'EOF'
from src.main import fetch_data

def test_fetch_data():
    data = fetch_data("https://api.github.com")
    assert isinstance(data, dict)
EOF

# 6. Run linting
womm lint

# 7. Check spelling
womm spell

# 8. Run tests
pytest

# 9. Format code
black src/ tests/

# 10. Type check
mypy src/
```

### Template Creation and Reuse

```bash
# 1. Create and configure a project
womm new python my-template-project
cd my-template-project

# 2. Add custom configurations
# ... configure tools, add files ...

# 3. Create template from project
womm templates create my-company-template

# 4. List templates to verify
womm templates list

# 5. Use template for new project
cd ..
womm templates use my-company-template new-project

# New project has all configurations!
cd new-project
ls -la
```

### Multi-Project Setup

```bash
# Setup multiple projects in a workspace
mkdir workspace
cd workspace

# Create backend API
womm new python api-backend
cd api-backend
pip install fastapi uvicorn
cd ..

# Create frontend
womm new javascript app-frontend --type react
cd app-frontend
npm install
cd ..

# Create shared library
womm new python shared-lib
cd shared-lib
pip install -e .
cd ..

# Lint all projects
for dir in api-backend app-frontend shared-lib; do
  echo "Linting $dir..."
  cd $dir
  womm lint
  cd ..
done
```

## Advanced Configuration

### Custom Python Configuration

```bash
# Create project
womm new python advanced-project
cd advanced-project

# Edit pyproject.toml for custom Black config
cat >> pyproject.toml << 'EOF'

[tool.black]
line-length = 100
target-version = ['py310', 'py311']
include = '\.pyi?$'

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
EOF

# Run with custom config
womm lint
pytest
```

### Custom JavaScript Configuration

```bash
# Create project
womm new javascript advanced-js
cd advanced-js

# Customize ESLint
cat > .eslintrc.js << 'EOF'
module.exports = {
  extends: ['eslint:recommended'],
  env: {
    node: true,
    es2021: true,
  },
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    'no-console': 'warn',
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
  },
};
EOF

# Lint with custom rules
womm lint
```

## Error Handling

### Handling Project Creation Errors

```bash
# Try to create project in existing directory
womm new python existing-dir
# Error: Directory already exists

# Force creation (overwrites)
womm new python existing-dir --force

# Or use interactive mode
womm new --interactive
# Will prompt for action
```

### Handling Setup Errors

```bash
# Setup without detecting project type
womm setup detect
# Error: Could not detect project type

# Manually specify type
womm setup python

# Or use interactive mode
womm setup --interactive
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install WOMM
        run: pip install works-on-my-machine
      - name: Run linting
        run: womm lint
```

### GitLab CI

```yaml
# .gitlab-ci.yml
lint:
  image: python:3.10
  script:
    - pip install works-on-my-machine
    - womm lint
  only:
    - merge_requests
    - main
```

## Docker Integration

### Dockerfile for Python Project

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install WOMM
RUN pip install works-on-my-machine

# Copy project
COPY . .

# Setup project
RUN womm setup python

# Install dependencies
RUN pip install -r requirements.txt

CMD ["python", "src/main.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  app:
    build: .
    volumes:
      - .:/app
    command: |
      sh -c "
        pip install works-on-my-machine &&
        womm setup python &&
        pip install -r requirements.txt &&
        python src/main.py
      "
```

## Best Practices

### Project Structure

```bash
# Good: Organized structure
my-project/
├── src/           # Source code
├── tests/         # Tests
├── docs/          # Documentation
├── .venv/         # Virtual environment
└── README.md

# Bad: Messy structure
my-project/
├── file1.py
├── file2.py
├── test1.py
└── random_stuff/
```

### Dependency Management

```bash
# Good: Separate dev dependencies
pip install -r requirements.txt      # Production
pip install -r requirements-dev.txt  # Development

# Good: Lock versions
pip freeze > requirements.txt

# Good: Use virtual environments
source .venv/bin/activate
```

### Code Quality

```bash
# Regular linting
womm lint

# Spell checking
womm spell

# Type checking
mypy src/

# Testing
pytest --cov=src

# Formatting
black src/ tests/
```

## See Also

- [Getting Started](../getting-started.md) - Installation and first steps
- [CLI Reference](../cli/index.md) - Complete command documentation
- [Configuration Guide](../guides/configuration.md) - Advanced configuration
- [API Reference](../api/index.md) - Technical documentation

---

Ready to build professional projects with WOMM? Try these examples and customize them for your needs! 🚀
