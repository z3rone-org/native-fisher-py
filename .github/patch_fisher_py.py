import os
import re
import site
import sys

def get_fisher_py_path():
    for site_pkg in site.getsitepackages() + [site.getusersitepackages()]:
        path = os.path.join(site_pkg, 'fisher_py')
        if os.path.exists(path):
            return path
            
    # Also check virtual environments where site.getsitepackages() might be missing
    for p in sys.path:
        path = os.path.join(p, 'fisher_py')
        if os.path.exists(path):
            return path
            
    raise RuntimeError("fisher_py not found in sys.path or site-packages")

def patch_fisher_py():
    try:
        fisher_py_path = get_fisher_py_path()
        init_file = os.path.join(fisher_py_path, 'net_wrapping', '__init__.py')
        
        with open(init_file, 'r') as f:
            content = f.read()
            
        # Add import System.Reflection if needed
        if "from System.Reflection import Assembly" not in content:
            content = content.replace("from System import Environment", "from System import Environment\nfrom System.Reflection import Assembly")
            
        # Replace clr.AddReference(os.path.join(dll_path, '...')) 
        # with Assembly.LoadFrom(os.path.realpath(os.path.join(dll_path, '...')))
        content = re.sub(
            r"clr\.AddReference\((os\.path\.join\(dll_path, '[^']+'\))\)",
            r"Assembly.LoadFrom(os.path.realpath(\1))",
            content
        )
        
        with open(init_file, 'w') as f:
            f.write(content)
            
        print(f"Successfully patched {init_file}")
    except Exception as e:
        print(f"Failed to patch fisher_py: {e}")
        sys.exit(1)

if __name__ == '__main__':
    patch_fisher_py()
