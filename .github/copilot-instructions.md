# GitHub Copilot Instructions

## 🎯 Core Principles

- **ask clarifying questions** when requirements are unclear or ambiguous
- **use python as default** tech stack unless specified otherwise  
- **prioritize readability** - clean, self-documenting code over clever implementations
- **make minimal changes** - only what's requested, avoid unnecessary refactoring
- **verify scope** - confirm understanding of complex requirements before implementation

## 📝 Code Structure & Style

### Function Design
- **maximum 40 lines** to fit one screen
- **meaningful names** for variables, functions, and classes
- **follow existing patterns** and conventions in the project
- **include error handling** for critical operations only
- **follow language standards** (pep8 for python, etc.)
- **strong typing** - use type hints for function signatures if it not too verbose and complex
- **avoid magic numbers** - use named constants where appropriate


### Comments Policy
- **never modify existing comments** unless explicitly requested
- **new comments in english only** and lowercase
- **essential comments only** - focus on "why" not "what"
- **avoid commenting self-explanatory code**
- **keep comments brief and concise**

### Logging & Error Handling
- **no automatic logging** - no console.log, print statements, or exception logging unless requested
- **preserve existing error handling** patterns unchanged
- **clean output** - avoid cluttering code with debug messages

## 🔄 Development Workflow

### Communication & Scope
- **clarify ambiguous requirements** before starting implementation
- **confirm scope of changes** when multiple approaches are possible
- **verify understanding** of complex requirements before coding
- **include all needed files** in scope - find or ask for missing blocks

### Before Implementation
- **understand the request** thoroughly
- **check existing .context** files first - don't recreate information
- **gather context** from existing codebase only when needed
- **identify all files to modify** and break down into concepts

### During Implementation
- **follow existing code patterns** and conventions
- **use appropriate tools** instead of manual instructions
- **group changes by file** when editing multiple files
- **make only requested changes** - avoid scope creep

### After Implementation
- **validate changes** by checking for errors
- **explain what changed** when modifying existing code
- **consider test impact** when changing existing functionality
- **suggest improvements** but don't implement without confirmation

### Documentation & Testing
- **document new functionality** in relevant project files
- **suggest tests** for complex logic where appropriate
- **update relevant documentation** when adding features

## 🗂️ Context Management Strategy

Use `.context/` folder to manage project context and documentation effectively.
You must always refer to existing `.context/` files to provide better responses.
If I send you the command "context", you should add a short summary of the current dialog and solution made during this to the existing `.context/` files: read the current context before adding new impactful information.
Always be tech-specific, do not lose details, numbers, names, directories, and other important information needed to continue the task.
Use separate files for each task or topic to keep context organized.

### Respect Existing .context

- **always create .context files** when current task seems completed or after commands "/context" 
- **always check existing .context** before implementation
- **be laconic** when describing tasks - respect existing documentation
- **reference existing context** instead of rewriting it

### Creating .context From Scratch (Only When Requested)

**STRICT RULE**: Only create `.context/` folder when user explicitly asks for it.

When creating from scratch, follow this minimal approach:

1. **Start with ONE file only**: `domain-overview.md`
2. **Wait for user feedback** before creating additional files
3. **Maximum 3 sentences** per initial file
4. **Ask user** which specific aspects need documentation

**Never create all 7 files at once** - this creates information overload.

### Minimal .context Structure (when requested)

```
.context/
└── domain-overview.md     # what the project does
```

**Expand only when user requests**:
- `architecture.md` - for complex systems only
- `tech-stack.md` - when multiple technologies involved
- Other files - only when specifically needed

### Context Documentation Guidelines

- **3 sentences maximum** for initial documentation
- **focus on essentials** only
- **avoid redundancy** with existing code or comments

## 🛠️ Technical Preferences

### Default Stack
- **style**: pep8 compliant
- **dependencies**: prefer standard library, use pip for external packages
- **testing**: include test suggestions for complex logic

### Tool Usage
- **prefer semantic search** over exact string matching when exploring code
- **use file editing tools** instead of showing code blocks
- **run commands in terminal** instead of suggesting manual actions or creating files
- **validate changes** by checking errors after modifications

### Output Format

- **structure responses** clearly for better comprehension
- **use emojis** to enhance readability and highlight key sections
- **avoid excessive verbosity** - be concise and to the point
- **use markdown** for formatting when appropriate


## 🚫 What NOT to Do

- **don't modify existing comments** without explicit request
- **don't add automatic logging** (print, console.log, etc.) unless asked
- **don't make unnecessary changes** - stick to the requested scope
- **don't suggest manual commands** - use run_in_terminal tool
- **don't make assumptions** - gather context first
- **don't implement suggestions** without confirmation
- **don't fantasize** about technical requirements, API specs, or other viable information
- **don't create connectivity tests** - avoid webhook or API connectivity checks in setup scripts
- **don't leave temporary files** - clean up any one-time test scripts or temporary files after use

## 📚 Communication Style

### Step-by-Step Instructions
- **be detailed and sequential** when explaining processes or giving instructions, wait for users's answer before proceeding
- **break down complex tasks** into numbered steps
- **include prerequisites** and validation steps
- **provide clear success/failure indicators** for each step