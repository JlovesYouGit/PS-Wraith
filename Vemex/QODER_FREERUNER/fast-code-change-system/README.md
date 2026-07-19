# Fast Code Change Application System

A high-performance code modification engine that enables Qoder to efficiently apply multiple changes across a codebase.

## Features

- **Intelligent Parsing**: Parse change requests into structured edit operations
- **IDE Integration**: Leverage IDE tools for navigation, validation, and editing
- **Precise Positioning**: Lock onto exact line and character positions
- **Rapid Navigation**: Optimized scrolling between change locations
- **Conflict Handling**: Detect and resolve content mismatches
- **Progress Tracking**: Monitor batch modifications with detailed reporting

## Project Structure

```
fast-code-change-system/
├── src/
│   ├── types/           # TypeScript type definitions
│   ├── parser/          # Change request parsing
│   ├── navigator/       # IDE navigation
│   ├── lock/            # Position locking
│   ├── scroll/          # Scroll speed logic
│   ├── applicator/      # Change application orchestration
│   └── index.ts         # Main entry point
├── tests/               # Test files
├── package.json
├── tsconfig.json
└── vitest.config.ts
```

## Installation

```bash
npm install
```

## Development

```bash
# Build the project
npm run build

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## Testing

The project uses:
- **Vitest** for unit testing
- **fast-check** for property-based testing (minimum 100 iterations per property)

Each property-based test is tagged with: `Feature: fast-code-change-system, Property {number}: {property_text}`

## Requirements

See `.kiro/specs/fast-code-change-system/requirements.md` for detailed requirements.

## Design

See `.kiro/specs/fast-code-change-system/design.md` for architecture and design decisions.

## License

MIT
