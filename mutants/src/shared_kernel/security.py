"""Shared security contracts consumed across Bounded Contexts (Cresmo, IAM, etc.)."""

from dataclasses import dataclass, field


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁAuthenticatedUserǁhas_role__mutmut: MutantDict = {}  # type: ignore
mutants_xǁAuthenticatedUserǁhas_scope__mutmut: MutantDict = {}  # type: ignore


@dataclass(frozen=True)
class AuthenticatedUser:
    """Immutable security principal contract for cross-context authorization.

    Shields domain cores (such as Cresmo) from depending on IAM persistence
    or password hashing models.
    """

    user_id: str
    tenant_id: str = "default"
    email: str = ""
    roles: frozenset[str] = field(default_factory=frozenset)
    scopes: frozenset[str] = field(default_factory=frozenset)

    @_mutmut_mutated(mutants_xǁAuthenticatedUserǁhas_role__mutmut)
    def has_role(self, role: str) -> bool:
        """Verifies if the principal possesses a given role or is an administrator."""
        return role in self.roles or "admin" in self.roles

    def xǁAuthenticatedUserǁhas_role__mutmut_orig(self, role: str) -> bool:
        """Verifies if the principal possesses a given role or is an administrator."""
        return role in self.roles or "admin" in self.roles

    def xǁAuthenticatedUserǁhas_role__mutmut_1(self, role: str) -> bool:
        """Verifies if the principal possesses a given role or is an administrator."""
        return role in self.roles and "admin" in self.roles

    def xǁAuthenticatedUserǁhas_role__mutmut_2(self, role: str) -> bool:
        """Verifies if the principal possesses a given role or is an administrator."""
        return role not in self.roles or "admin" in self.roles

    def xǁAuthenticatedUserǁhas_role__mutmut_3(self, role: str) -> bool:
        """Verifies if the principal possesses a given role or is an administrator."""
        return role in self.roles or "XXadminXX" in self.roles

    def xǁAuthenticatedUserǁhas_role__mutmut_4(self, role: str) -> bool:
        """Verifies if the principal possesses a given role or is an administrator."""
        return role in self.roles or "ADMIN" in self.roles

    def xǁAuthenticatedUserǁhas_role__mutmut_5(self, role: str) -> bool:
        """Verifies if the principal possesses a given role or is an administrator."""
        return role in self.roles or "admin" not in self.roles

    @_mutmut_mutated(mutants_xǁAuthenticatedUserǁhas_scope__mutmut)
    def has_scope(self, scope: str) -> bool:
        """Verifies if the principal possesses a specific permission scope or admin role."""
        return scope in self.scopes or "admin" in self.roles

    def xǁAuthenticatedUserǁhas_scope__mutmut_orig(self, scope: str) -> bool:
        """Verifies if the principal possesses a specific permission scope or admin role."""
        return scope in self.scopes or "admin" in self.roles

    def xǁAuthenticatedUserǁhas_scope__mutmut_1(self, scope: str) -> bool:
        """Verifies if the principal possesses a specific permission scope or admin role."""
        return scope in self.scopes and "admin" in self.roles

    def xǁAuthenticatedUserǁhas_scope__mutmut_2(self, scope: str) -> bool:
        """Verifies if the principal possesses a specific permission scope or admin role."""
        return scope not in self.scopes or "admin" in self.roles

    def xǁAuthenticatedUserǁhas_scope__mutmut_3(self, scope: str) -> bool:
        """Verifies if the principal possesses a specific permission scope or admin role."""
        return scope in self.scopes or "XXadminXX" in self.roles

    def xǁAuthenticatedUserǁhas_scope__mutmut_4(self, scope: str) -> bool:
        """Verifies if the principal possesses a specific permission scope or admin role."""
        return scope in self.scopes or "ADMIN" in self.roles

    def xǁAuthenticatedUserǁhas_scope__mutmut_5(self, scope: str) -> bool:
        """Verifies if the principal possesses a specific permission scope or admin role."""
        return scope in self.scopes or "admin" not in self.roles

mutants_xǁAuthenticatedUserǁhas_role__mutmut['_mutmut_orig'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_role__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_role__mutmut['xǁAuthenticatedUserǁhas_role__mutmut_1'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_role__mutmut_1 # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_role__mutmut['xǁAuthenticatedUserǁhas_role__mutmut_2'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_role__mutmut_2 # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_role__mutmut['xǁAuthenticatedUserǁhas_role__mutmut_3'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_role__mutmut_3 # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_role__mutmut['xǁAuthenticatedUserǁhas_role__mutmut_4'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_role__mutmut_4 # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_role__mutmut['xǁAuthenticatedUserǁhas_role__mutmut_5'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_role__mutmut_5 # type: ignore # mutmut generated

mutants_xǁAuthenticatedUserǁhas_scope__mutmut['_mutmut_orig'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_scope__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_scope__mutmut['xǁAuthenticatedUserǁhas_scope__mutmut_1'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_scope__mutmut_1 # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_scope__mutmut['xǁAuthenticatedUserǁhas_scope__mutmut_2'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_scope__mutmut_2 # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_scope__mutmut['xǁAuthenticatedUserǁhas_scope__mutmut_3'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_scope__mutmut_3 # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_scope__mutmut['xǁAuthenticatedUserǁhas_scope__mutmut_4'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_scope__mutmut_4 # type: ignore # mutmut generated
mutants_xǁAuthenticatedUserǁhas_scope__mutmut['xǁAuthenticatedUserǁhas_scope__mutmut_5'] = AuthenticatedUser.xǁAuthenticatedUserǁhas_scope__mutmut_5 # type: ignore # mutmut generated
