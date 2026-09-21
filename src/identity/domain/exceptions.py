"""Domain exceptions for Identity & Access Management (IAM)."""


class IdentityDomainError(Exception):
    """Base exception for all IAM domain invariant violations."""


class InvalidUserIdError(IdentityDomainError):
    """Raised when a UserId fails validation invariants."""


class InvalidEmailError(IdentityDomainError):
    """Raised when an Email address fails RFC 5322 structure rules."""


class WeakPasswordError(IdentityDomainError):
    """Raised when a plain password fails security strength criteria."""


class InactiveUserError(IdentityDomainError):
    """Raised when attempting operations on a deactivated user account."""


class InvalidTokenError(IdentityDomainError):
    """Raised when a token or PAT is corrupted, malformed, or invalid."""


class InvalidCredentialsError(IdentityDomainError):
    """Raised when authentication credentials fail verification."""


class UserAlreadyExistsError(IdentityDomainError):
    """Raised when registering a user with an already registered email."""
