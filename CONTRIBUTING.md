# Contributing to Sahayak

Thank you for your interest in contributing to Sahayak! This document provides guidelines for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/Hexacode.git`
3. Create a branch: `git checkout -b feat/your-feature-name`
4. Make your changes
5. Run tests and linters: `make test && make lint`
6. Commit your changes using Conventional Commits
7. Push to your fork and create a Pull Request

## Development Setup

See the [README](README.md#quick-start) for development setup instructions.

## Coding Standards

### Backend (Python)
- Python 3.11+
- Type hints required for all public functions
- Follow PEP 8 (enforced by Ruff)
- MyPy strict mode compliance
- Docstrings for all public modules, classes, and functions
- Maximum line length: 100 characters

### Frontend (TypeScript/React)
- TypeScript strict mode
- ESLint + Prettier compliance
- Functional components with hooks
- No business logic in components (use hooks and services)
- Accessibility (WCAG AA) compliance

### General
- Conventional Commits for commit messages
- Small, focused PRs
- No dead code or commented-out code
- No magic numbers (use named constants)
- Comments explain WHY, not WHAT

## Architecture Guidelines

### Backend Layer Separation
```
api/ (routers) → services/ → repositories/ → db/ (models)
```
- No business logic in routers
- Services contain business logic
- Repositories handle data access
- Models are pure SQLAlchemy definitions

### Engine Abstraction
- All ML engines implement protocols (`VoiceActivityDetector`, `SpeechRecognizer`, `Summarizer`)
- Provider selection is centralized in `ProviderSelector`
- Real implementations use ONNX Runtime
- Mock implementations flagged with `simulated: true`

### Database
- Use repository pattern for all data access
- All write paths are transactional
- Use Alembic for migrations
- Index foreign keys and time columns

## Testing

### Backend
- Unit tests for services and engine selection
- API tests with test database
- WebSocket tests
- Target: ≥80% coverage on services

### Frontend
- Component tests for main flows
- E2E smoke tests
- Testing Library for React components

## Pull Request Process

1. Ensure all CI checks pass
2. Update documentation if needed
3. Add tests for new functionality
4. Request review from maintainers
5. Address review comments
6. Squash and merge (maintainers will handle)

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding missing tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add session summary endpoint
fix(ws): handle audio chunk parsing error
docs(readme): update quick start instructions
```

## Release Process

Releases are managed by maintainers. Version numbers follow [Semantic Versioning](https://semver.org/).

## Security

See [SECURITY.md](SECURITY.md) for security vulnerability reporting.

## Questions?

Open a [discussion](https://github.com/your-org/Hexacode/discussions) or ask in the PR.