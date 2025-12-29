"""Final verification of price calculation using check_miraflores.py output"""
import subprocess
import sys

print("\n=== Running check_miraflores.py to verify price calculations ===\n")
result = subprocess.run(
    [sys.executable, "check_miraflores.py"],
    capture_output=True,
    text=True,
    cwd="."
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n=== Now run the application with: uv run python run.py ===")
print("=== Then load the file and check the pricing calculations ===")
