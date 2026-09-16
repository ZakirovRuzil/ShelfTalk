# Changelog

All notable changes to this project will be documented in this file. The format follows
Keep a Changelog, and the project uses Semantic Versioning.

## [Unreleased]

### Changed

- Format Python, Vue, TypeScript, CSS, and documentation for readability.
- Use four-space indentation and template-first Vue single-file components.
- Simplify registration serializers and authentication wrappers.
- Shorten the README to setup and everyday commands.

### Added

- Ruff, ESLint, and Prettier configuration with repeatable lint and format commands.

## [1.0.0] - 2026-09-14

### Added

- Custom email-based users and JWT registration, login, refresh, and current-user API.
- Public book catalog with computed ratings and review counts.
- User reviews with ownership checks and database constraints.
- Django Admin and a repeatable command to seed eight books.
- Vue 3 and TypeScript frontend with search, authentication, and review management.
- PostgreSQL and environment configuration.
- 24 backend tests for authentication, permissions, validation, and database behavior.
- Setup instructions and API documentation.
