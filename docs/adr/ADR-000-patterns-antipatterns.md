Use this patterns and antipatterns* as a guide to create a better code.

### Tratamento de Exceções, Resiliência e Falhas

Anti-Swallowing & Chaining
Bulkhead Pattern
Circuit Breaker
Compensating Transaction
Correlation ID Propagation
Dead Letter Queue (DLQ)
Exception Chaining
Fail-Fast Pattern
Fallback
Graceful Degradation
Health Check Endpoints (Liveness, Readiness and Startup probes)
Idempotent Consumer (Race Conditions, Confirmation Order and TTL)
Isolated Failure Domains
Lease / Heartbeat Pattern (GC Pauses and Fencing Tokens)
Narrow Exceptions
Outbox Pattern
Process Supervisor / Restart Strategies
Rate Limiter
Retry with Exponential Backoff and Jitter
Safe Temp Paths
Timeout Pattern
Unhandled Exception Boundary
Blind Except*
Catch-All Exception Block*
Error Hiding*
Exception Swallowing*
Fail-Silent System*
Hardcoded Fallbacks*
Log and Throw*
Log-Only Suppression*
Nested Try-Except Cascades*
Optimistic Error Ignorance*
Pokemon Exception Handling*
Premature Eager Fallback Evaluation*
Resilience Starvation*
Retry Storm*
Return Codes for Exceptional Flow*
Silent Failures*
String-Based Exception Matching*
Swallowed Thread / Task Exceptions*

### Asserções, Validações e Integridade de Execução

Always-Valid Domain Model
Contract-Based Programming (Design by Contract)
Defensive Programming (Never Trust User Input, Fail-Fast, Immutability and Encapsulation, and avoid happy path; Guard Clauses, Defensive Copying, Parse, Don't Validate, Anti-Defensive Cascading)
Domain Invariant Enforcement
Fail-Safe Defaults
Guard Clauses
Input Sanitization at System Boundary
Parse, Don't Validate
Preconditions and Postconditions
Semantic Validation
Strict Dynamic Parsing (Validation via Schema)
Zero Production Asserts
Assertion Side-Effects*
Boundary Invalidation Leak*
Bypassed Invariants*
Downstream Defensive Redundancy*
Implicit Type Coercion*
Optimistic Assertions*
Production Asserts*
Validation Logic in Presentation Layer*
Validation Scattering*

### Injeção de Dependências, Configuração e Inicialização

Abstract Factory Pattern
Anti-Bifurcated Construction
Anti-Defensive Cascading
Composition Root
Config as Code
Dependency Injection (DI)
Dependency Inversion Principle (DIP)
Early Strict DI
Environment Variable Boundary Parsing
Factory Method Pattern
Immutable Settings Object
Inversion of Control (IoC)
Lazy Initialization
Pure Dependency Injection
SSOT Factory Composition
SSOT Operational Settings
Static Factory Method
Virtual Construction via Protocol
Ambient Context*
Bifurcated Construction*
Circular Dependencies*
Concrete Instantiation in Business Logic*
Config-as-Dict*
Dynamic Configuration Overriding in Runtime*
Global State Mutation*
Hardcoded Dependencies*
Hidden Dependencies*
In-Place Configuration Instantiation*
Inline Dependency Resolution Fallback*
Mutable Global Singleton*
Service Locator*
Temporal Coupling in Initialization*
Volatile Module-Level State*

### Organização de Código, Topografia e Estrutura de Arquivos

Architectural Boundaries Enforcement
Bounded Modularity (KISS)
Cyclomatic Complexity Budgeting
Explicit Public API (**all**)
High Cohesion
Low Coupling
Package by Component / Package by Feature
Package by Layer
PEP 8 Triad Layout
Primacy of Core Business Domain
Screaming Architecture
Single Responsibility Principle (SRP)
Stepdown Rule (Newspaper Metaphor)
Strict Import Topography
Top-Level Entry Points First
Vertical Slice Architecture
Barrel File Anti-Pattern*
Big Ball of Mud*
Blind Top-Level Imports Side-Effects*
Circular Imports*
Deep Inheritance Trees*
Feature Scattering*
God Class / God Module*
Hidden Cross-Domain Coupling*
Inverted Newspaper Layout*
Interleaved Code*
Kitchen Sink Module*
Monolithic File Layout*
Orphan Code / Lost Utilities*
Sprawling Modules*
Wildcard Imports (from module import *)*

### Assinaturas, Parâmetros e Interfaces

Cohesive Parameter Bundling
Data Transfer Object (DTO)
Explicit Keyword-Only Arguments
Fluent Interface
Full Subtype Interchangeability
Interface Segregation Principle (ISP)
Liskov Substitution Principle (LSP)
Narrow Interfaces
Parameter Object
Protocol-Based Duck Typing
Role Interfaces
Signature Hygiene & Dead Code
Strict Type Hints Enforcement
Typed Protocols (Structural Subtyping)
Upfront Port Typing
Value Object
Boolean Trap (Flag Arguments)*
Cargo Cult Typing (Any Overuse)*
Data Clumps*
Dead Code / Zombie Code*
Excessive Positional Arguments*
Interface Bloat*
Leaky Abstractions*
Long Parameter List*
Phantom Arguments*
Polymorphic Method Signature Distortion*
Telescoping Constructor*
Unused Parameters*
Wide Interfaces*

### Constantes, Estado e Variáveis

Canonical State Representation
Deterministic Unit Normalization
Encapsulated Mutable State
Explicit Life-Cycle State Machine
Finite State Machine (FSM)
Immutability (Frozen Models)
Single Source of Truth for Settings
Single Source of Truth (SSOT)
Strongly Typed Enums
Thread-Local Isolation
Zero Magic Literals
Anti-Shadow State Variables
Dispersed Constants*
Ghost State*
Hidden Side-Effects on State*
Implicit State Reset*
Magic Numbers*
Magic Strings*
Mutable Defaults in Functions / Classes*
Shadow State Variables*
Shared Mutable Global State*
State Aliasing*
Stringly Typed Code*
Temporal State Desynchronization*

### Fluxo de Controle, Navegação e Responsabilidade de Domínio

Active Record Pattern
Aggregate Root
Anti-Middle Man
Bounded Context
Clean Architecture
Command Handler Pattern
Command-Query Responsibility Segregation (CQRS)
Command-Query Separation (CQS)
Domain Event
Domain Service
Entity (DDD)
Event-Driven Architecture
Humble Object Pattern
Law of Demeter (Principle of Least Knowledge)
Mediator Pattern
Pipeline / Filter Architecture
Plugin Architecture
Ports and Adapters (Hexagonal Architecture)
Presentation SRP
Query Handler Pattern
Repository Pattern
Specification Pattern
Unit of Work Pattern
Zero Convenience Accessors
Anemic Domain Model*
Blind Passthrough*
Brain Method*
Chatty Interfaces*
Circular Domain Flow*
Coupled Layers*
Delegation Shims*
Divergent Change*
Fat Controller*
Fat Model*
Feature Envy*
God Controller*
Hardwired Orchestration*
Inappropriate Intimacy*
Message Chains*
Middle Man*
Premature Abstraction*
Primitive Obsession*
Shotgun Surgery*
Smart UI / Domain Logic in Presentation*
Speculative Generality*
Temporal Coupling*
Trampoline Calls*
Yo-Yo Problem*

### Compatibilidade de Sistema Operacional, I/O e Runtime

Abstracted Clock / Time Provider
Buffered Stream Processing
Cross-Platform Path Arithmetic
Deterministic Process Execution
Encoding Agnosticism (Strict UTF-8)
File System Virtualization
Isolated Temporary Filesystem
Line-Ending Agnosticism
OS-Agnostic Runtime
Path Normalization (Pathlib abstraction)
Resource Acquisition Is Initialization (RAII / Context Managers)
Safe Atomic File Writes
Case-Sensitivity Blindness*
Direct Raw Filesystem Coupling*
File Descriptor Leaking*
Hardcoded Absolute Paths*
Hardcoded Line Endings (\r\n vs \n)*
Hardcoded Path Separators (\ or /)*
Non-Deterministic Working Directory Access*
Platform Assumptions (POSIX-only / Win32-only)*
Process Signal Mishandling*
System Locale Dependence*
Unbounded File Deserialization*
Unclosed Context Resources*

### Testabilidade, Mocks e Isolamento Arquitetural

Contract Testing
Deterministic Test Data Builders
Fake Object Pattern
Hermetic Test Execution
In-Memory Repository Stub
Mock Object Pattern
Null Object Pattern
Spy Object Pattern
Subcutaneous Testing
Stub Object Pattern
Test Double
Test-Driven Development (TDD)
Brittle Tests*
Broad Network Mocking in Domain*
Excessive Mocking / Mock Hell*
Hardcoded Sleep / Non-Deterministic Testing*
Leaking Test Logic to Production*
Mocking the System Under Test*
Over-Specified Expectations*
Shared Mutable Fixtures*
Testing Internal Implementation Details*