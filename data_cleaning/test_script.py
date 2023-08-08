from PIL import Image
import subprocess

p = subprocess.Popen(["display", "pandas.png"])
print("\nA black and white Panda bear")
response = input("Is this caption acceptable? (Y/N)")
p.kill()

print("Thank you")
