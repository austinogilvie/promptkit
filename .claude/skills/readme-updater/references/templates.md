# README Templates

## Table of Contents
- [Full Project Templates](#full-project-templates)
  - [Node.js Project](#nodejs-project)
  - [Python Project](#python-project)
  - [CLI Tool](#cli-tool)
  - [Library/Package](#librarypackage)
- [Section Templates](#section-templates)
  - [Badges](#badges-section)
  - [Prerequisites](#prerequisites-section)
  - [Environment Variables](#environment-variables-section)
  - [Development](#development-section)
  - [Testing](#testing-section)
  - [Contributing](#contributing-section)
  - [Deployment](#deployment-section)
  - [Troubleshooting](#troubleshooting-section)

---

## Full Project Templates

### Node.js Project

```markdown
# Project Name

Brief description of what this project does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Prerequisites

- Node.js 18.x or higher
- npm or yarn

## Installation

```bash
git clone https://github.com/username/project.git
cd project
npm install
```

## Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your values:

```bash
# Required
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=your_api_key

# Optional
DEBUG=false
PORT=3000
```

## Usage

```bash
# Development
npm run dev

# Production
npm run build
npm start
```

## Testing

```bash
npm test
npm run test:coverage
```

## License

MIT
```

### Python Project

```markdown
# Project Name

Brief description of what this project does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Prerequisites

- Python 3.10 or higher
- pip or poetry

## Installation

```bash
git clone https://github.com/username/project.git
cd project

# Using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Using poetry
poetry install
```

## Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `API_KEY` | External API key | Yes |
| `DEBUG` | Enable debug mode | No |

## Usage

```bash
# Run the application
python main.py

# Or with poetry
poetry run python main.py
```

## Testing

```bash
pytest
pytest --cov=src
```

## License

MIT
```

### CLI Tool

```markdown
# tool-name

Brief description of what this CLI tool does.

## Installation

```bash
# Using npm
npm install -g tool-name

# Using pip
pip install tool-name

# From source
git clone https://github.com/username/tool-name.git
cd tool-name
make install
```

## Usage

```bash
tool-name [options] <command>
```

### Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize a new project |
| `build` | Build the project |
| `deploy` | Deploy to production |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-c, --config` | Path to config file | `./config.json` |
| `-v, --verbose` | Enable verbose output | `false` |
| `-h, --help` | Show help | |

### Examples

```bash
# Initialize a new project
tool-name init my-project

# Build with custom config
tool-name build -c custom.json

# Deploy with verbose output
tool-name deploy -v
```

## Configuration

Create a `config.json` file:

```json
{
  "option1": "value1",
  "option2": true
}
```

## License

MIT
```

### Library/Package

```markdown
# library-name

Brief description of what this library provides.

[![npm version](https://badge.fury.io/js/library-name.svg)](https://badge.fury.io/js/library-name)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
npm install library-name
# or
yarn add library-name
```

## Quick Start

```javascript
import { feature } from 'library-name';

const result = feature.doSomething();
console.log(result);
```

## API Reference

### `feature.doSomething(options)`

Does something useful.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `options.input` | `string` | Yes | The input value |
| `options.format` | `string` | No | Output format (`json` \| `text`) |

**Returns:** `Promise<Result>`

**Example:**

```javascript
const result = await feature.doSomething({
  input: 'hello',
  format: 'json'
});
```

### `feature.configure(config)`

Configure global settings.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `config.debug` | `boolean` | No | Enable debug mode |

## TypeScript

This library includes TypeScript definitions.

```typescript
import { Feature, Config } from 'library-name';

const config: Config = { debug: true };
```

## License

MIT
```

---

## Section Templates

### Badges Section

```markdown
[![Build Status](https://github.com/username/repo/workflows/CI/badge.svg)](https://github.com/username/repo/actions)
[![Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
[![npm version](https://badge.fury.io/js/package-name.svg)](https://badge.fury.io/js/package-name)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### Prerequisites Section

```markdown
## Prerequisites

Before you begin, ensure you have the following installed:

- [Node.js](https://nodejs.org/) (v18.0.0 or higher)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- [Docker](https://www.docker.com/) (optional, for containerized development)
- [PostgreSQL](https://www.postgresql.org/) 14+
```

### Environment Variables Section

```markdown
## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `API_KEY` | External service API key | Yes | - |
| `PORT` | Server port | No | `3000` |
| `NODE_ENV` | Environment mode | No | `development` |
| `LOG_LEVEL` | Logging verbosity | No | `info` |

Create a `.env` file from the example:

```bash
cp .env.example .env
```
```

### Development Section

```markdown
## Development

### Setup

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Run database migrations
npm run db:migrate

# Start development server
npm run dev
```

### Code Style

This project uses ESLint and Prettier. Run linting with:

```bash
npm run lint
npm run lint:fix
```

### Git Hooks

Pre-commit hooks run automatically via Husky:
- Lint staged files
- Run type checking
- Run affected tests
```

### Testing Section

```markdown
## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- path/to/test.spec.ts
```

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── e2e/           # End-to-end tests
```
```

### Contributing Section

```markdown
## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.
```

### Deployment Section

```markdown
## Deployment

### Docker

```bash
# Build image
docker build -t app-name .

# Run container
docker run -p 3000:3000 --env-file .env app-name
```

### Manual Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Environment-Specific Configs

| Environment | Config File | Notes |
|-------------|-------------|-------|
| Development | `.env.development` | Local development |
| Staging | `.env.staging` | Pre-production testing |
| Production | `.env.production` | Live environment |
```

### Troubleshooting Section

```markdown
## Troubleshooting

### Common Issues

#### Port already in use

```bash
# Find process using port 3000
lsof -i :3000
# Kill the process
kill -9 <PID>
```

#### Database connection failed

1. Ensure PostgreSQL is running
2. Verify `DATABASE_URL` in `.env`
3. Check database exists: `psql -l`

#### Module not found errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```
```
