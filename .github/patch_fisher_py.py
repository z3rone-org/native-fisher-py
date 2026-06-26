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
            
        # Add import sys if needed
        if "import sys" not in content:
            content = "import sys\n" + content
            
        # Ensure sys.path.append(dll_path) is added
        if "sys.path.append(os.path.realpath(dll_path))" not in content:
            content = content.replace("clr.AddReference('mscorlib')", "clr.AddReference('mscorlib')\nsys.path.append(os.path.realpath(dll_path))")

        # Replace clr.AddReference(os.path.join(dll_path, 'AssemblyName.dll'))
        # with clr.AddReference('AssemblyName')
        content = re.sub(
            r"clr\.AddReference\((?:os\.path\.join\()?dll_path,\s*'([^']+)\.dll'(?:\))?\)",
            r"clr.AddReference('\1')",
            content
        )
        # Also clean up any lingering Assembly.LoadFrom from previous patches just in case
        content = re.sub(
            r"Assembly\.LoadFrom\(os\.path\.realpath\(os\.path\.join\(dll_path,\s*'([^']+)\.dll'\)\)\)",
            r"clr.AddReference('\1')",
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
