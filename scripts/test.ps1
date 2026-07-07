$ErrorActionPreference = "Stop"

$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest backend/tests -q
