#!/usr/bin/env python3
"""
Installe automatiquement les hooks Git locaux.
"""

import os
import shutil

HOOKS = ["pre-commit", "pre-push"]

def main() -> None:
    git_hooks_dir = os.path.join(".git", "hooks")
    local_hooks_dir = ".git/hooks"

    for hook in HOOKS:
        src = os.path.join(local_hooks_dir, hook)
        dst = os.path.join(git_hooks_dir, hook)
        shutil.copy(src, dst)
        os.chmod(dst, 0o775)
        print(f"✅ Hook {hook} installé dans {git_hooks_dir}")

if __name__ == "__main__":
    main()
