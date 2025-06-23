# Common Module

This module serves as a central place for storing variables, functions, code snippets, templates, etc.
We then use these centralized objects by installing them from our pip package.

## Auth
Handles authentication and authorization for the API, supporting both API key and JWT bearer token authentication. Includes middleware for verifying API requests, validating scopes, and handling authentication-related exceptions.

## Ansi Colors
Provides a collection of ANSI color codes for terminal text formatting, including regular, bright, and bold text colors. Useful for creating colorful and readable console output.

## Decorators
Contains utility decorators for model manipulation, including the `partial_model` decorator that converts Pydantic models to have all optional fields, useful for update operations.

## Enums
Defines common enumerations used throughout the codebase for type safety and consistency.

## Errors
Comprehensive error handling system defining various API error types, HTTP exceptions, and error content structures.

## Exceptions
Custom exception classes and error handling utilities for the API client.

## Logging
Logging configuration and utilities for consistent log formatting and handling across the application.

## Middleware
API middleware components for request/response processing and common functionality.

## Mixins
Reusable functionality components that can be mixed into other classes.

## Pagination
Utilities for handling paginated API responses and cursor-based pagination.

## Router
API routing utilities and components.

## Scopes
Authorization scope definitions and management for API access control.

## Urls
URL management utilities including base URLs, service endpoints, and API versioning.

## Utils
General utility functions and helper methods used across the codebase.

## Warnings
Warning handling and custom warning types for the application.

## Metrics
Shared metrics we collect from our APIs and expose for visualization.

## Changelog

<!-- changelog-insertion -->

## Unreleased
