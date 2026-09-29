# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and architecture
- Backend: FastAPI with SQLAlchemy 2.x, Alembic migrations
- Backend: Engine abstraction (VAD, ASR, Summarizer protocols)
- Backend: Provider selection (QNN → CUDA → DML → CPU)
- Backend: Mock engines for development (flagged `simulated: true`)
- Backend: Session CRUD API
- Backend: WebSocket for live captions
- Backend: Summary generation API
- Backend: Benchmark API
- Backend: System capabilities endpoint
- Frontend: React 18 + TypeScript + Vite + Tailwind
- Frontend: Live captions page with microphone capture
- Frontend: Sessions list and detail pages
- Frontend: NPU Advantage Dashboard with charts
- Frontend: Settings page
- Frontend: React Query for data fetching
- Frontend: Accessibility (WCAG AA) compliance
- Docker: Multi-stage builds for backend and frontend
- CI: GitHub Actions workflow
- Documentation: Architecture, API, Snapdragon setup guides

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2026-09-30

### Added
- Baseline demo-ready system
- Live captions with voice activity detection
- Session persistence with transcripts
- Extractive summarization
- NPU Advantage Dashboard with real benchmark measurements
- Honest simulated mode with visible badges
- Comprehensive documentation