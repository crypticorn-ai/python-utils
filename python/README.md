This module serves as a central place for providing utilities for our python backends.

- **Auth**: Authentication and authorization for APIs with API key and JWT bearer token support
- **Decorators**: Utility decorators for model manipulation, including `partial_model` for optional fields
- **Enums**: Common enumerations for type safety and consistency
- **Errors**: Comprehensive error handling system with HTTP exceptions and error content structures
- **Exceptions**: Custom exception classes and error handling utilities
- **Logging**: Logging configuration and utilities for consistent formatting
- **Middleware**: API middleware components for request/response processing
- **Pagination**: Utilities for paginated API responses and cursor-based pagination
- **Utils**: General utility functions and helper methods

# Changelog

<!-- changelog-insertion -->

## v1.0.0-rc.1 (2025-07-17)

### Build System

- Deployment config for v1 branches
  ([`b94d9e7`](https://github.com/crypticorn-ai/util-libraries/commit/b94d9e72616e398760993f6ebb1a6fd876a95802))

BREAKING CHANGE: - removed: mixins, openapi and both router modules; CLI; Scope Enum class;
  `throw_if_none` and `throw_if_falsy`; all deprecation warnings - reworked: exceptions and error
  modules

- Mark packaage as typed
  ([`69544a8`](https://github.com/crypticorn-ai/util-libraries/commit/69544a8709f4d55850e107031b82d91c28334b3c))

- Remove support for python versions 3.9 and 3.10
  ([`80b8543`](https://github.com/crypticorn-ai/util-libraries/commit/80b8543ed5559a0de421aef4e2382193e930751a))


## v0.1.0-rc.1 (2025-06-23)

### Documentation

- Add changelog
  ([`788f1f6`](https://github.com/crypticorn-ai/util-libraries/commit/788f1f670a8a50251401ebd1fc9ab7d2ca855a8d))

- Update Readme
  ([`d2b52cf`](https://github.com/crypticorn-ai/util-libraries/commit/d2b52cfe48de7a8b248ceefbc3bc7007ad21ea72))

### Features

- Initial release
  ([`4da5fe3`](https://github.com/crypticorn-ai/util-libraries/commit/4da5fe3d33abd31b3b35462e93052db0cde077c2))


## Unreleased

### Documentation

- Add changelog
  ([`788f1f6`](https://github.com/crypticorn-ai/util-libraries/commit/788f1f670a8a50251401ebd1fc9ab7d2ca855a8d))

- Update Readme
  ([`d2b52cf`](https://github.com/crypticorn-ai/util-libraries/commit/d2b52cfe48de7a8b248ceefbc3bc7007ad21ea72))
