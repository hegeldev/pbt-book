set ignore-comments := true

# List available recipes
default:
    @just --list

# Build the book into ./book
build:
    mdbook build

# Serve the book locally with live reload
alias dev: serve
serve:
    mdbook serve --open

# Remove build artifacts
clean:
    mdbook clean

# Run mdbook's tests (e.g. checks on code blocks)
test:
    mdbook test
