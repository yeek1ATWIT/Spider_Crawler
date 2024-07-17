
#PACKAGE_INSTALL_______________________________________________________________
# List of packages to check
packages = [
    'pysqlite3',
    'PyQt5',
    'requests',
    'beautifulsoup4',
    'selenium',
    'futures',
    'urllib3',
    'httpx',
    'scrapy',
    'regex',
    'os_sys',  # Note: Corrected to 'os_sys' as 'os-sys' is not a valid package name
    'playwright'
]

# Function to check if a package is installed
def check_package(package_name):
    try:
        importlib.import_module(package_name)
        print(f"{package_name} is installed.")
    except ImportError:
        print(f"{package_name} is not installed. Attempting to install...")
        install_package(package_name)

# Function to install a package using pip
def install_package(package_name):
    try:
        subprocess.run(["pip", "install", package_name], check=True)
        print(f"{package_name} installed successfully.")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}. Please install it manually.")

# Loop through the list of packages and check/install each one
for package in packages:
    check_package(package)

# Additional check for playwright installation
try:
    import playwright
    print("playwright is installed.")
except ImportError:
    print("playwright is not installed. Please check installation manually.")

check_package()
#END OF INSTALL_______________________________________________________________