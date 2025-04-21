$env.config.show_banner = false

if not (".venv" | path exists) {
    uv venv --no-python-downloads
}
