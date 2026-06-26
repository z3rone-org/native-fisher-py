import os
import site
import sys

def get_fisher_py_path():
    for site_pkg in site.getsitepackages() + [site.getusersitepackages()]:
        path = os.path.join(site_pkg, 'fisher_py')
        if os.path.exists(path):
            return path
    for p in sys.path:
        path = os.path.join(p, 'fisher_py')
        if os.path.exists(path):
            return path
    raise RuntimeError("fisher_py not found")

def patch_fisher_py():
    try:
        fisher_py_path = get_fisher_py_path()
        init_file = os.path.join(fisher_py_path, 'net_wrapping', '__init__.py')
        
        with open(init_file, 'r') as f:
            content = f.read()
            
        if "from System.Reflection import Assembly" not in content:
            content = content.replace("from System import Environment", "from System import Environment\nfrom System.Reflection import Assembly")

        import re
        
        # Add helper function at the top of the file after imports
        helper = """
def _safe_load_assembly(path):
    try:
        Assembly.LoadFrom(path)
    except Exception:
        pass
"""
        if "_safe_load_assembly" not in content:
            content = content.replace("import os", "import os\n" + helper, 1)

        def replacer(match):
            original = match.group(1)
            return f"_safe_load_assembly(os.path.realpath({original}))"

        content = re.sub(
            r"clr\.AddReference\((os\.path\.join\(dll_path,\s*'[^']+'\))\)",
            replacer,
            content
        )

        with open(init_file, 'w') as f:
            f.write(content)
            
        print(f"Successfully patched {init_file}")
    except Exception as e:
        print(f"Failed to patch: {e}")
        sys.exit(1)

if __name__ == '__main__':
    patch_fisher_py()
