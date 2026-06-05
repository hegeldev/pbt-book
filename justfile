set ignore-comments := true

# List available recipes
default:
    @just --list

# Install the preprocessors this book depends on
setup:
    cargo install mdbook-tabs

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

# Run the runnable language examples and regenerate their captured output.
# This actually compiles and runs each example under examples/ (they're the
# real, tested versions of the code shown in the book), so it needs the Rust,
# Go, C++ and Node toolchains. Pass a language name to run just one, e.g.
# `just examples rust`.
examples *langs:
    python3 examples/run.py {{langs}}
