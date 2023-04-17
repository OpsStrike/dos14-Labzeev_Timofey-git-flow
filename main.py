#!/home/tima/.pyenv/shims/python

import os

shell = os.environ.get("SHELL")
if shell == "/bin/bash":
    print("Greetings bash")
else:
    print(f"Hello {shell}")
