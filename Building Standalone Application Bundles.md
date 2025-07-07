\# Building Standalone Application Bundles

This document provides instructions on how to create standalone executable bundles of the Darkroom Enlarger Application for Windows, macOS, and Linux using PyInstaller.

\#\# Prerequisites

Before you begin, ensure you have the following installed on your machine:

\-   **\*\*Python 3.x\*\***: It is recommended to use the same Python version across all platforms for consistency.  
\-   **\*\*Git\*\***: For cloning the repository.  
\-   **\*\*PyInstaller\*\***: This tool will be used to create the standalone executables.

\#\# General Steps (for all platforms)

1\.  **\*\*Clone the repository:\*\***  
    If you haven't already, clone the application's GitHub repository to your local machine:  
    \`\`\`bash  
    git clone https://github.com/dpattinson/digital\_enlarger\_app.git  
    cd digital\_enlarger\_app  
    \`\`\`

2\.  **\*\*Create and activate a virtual environment:\*\***  
    It's good practice to use a virtual environment to manage project dependencies.  
    \`\`\`bash  
    python3 \-m venv .venv  
    \# On Linux/macOS:  
    source .venv/bin/activate  
    \# On Windows (Command Prompt):  
    .venv\\Scripts\\activate.bat  
    \# On Windows (PowerShell):  
    .venv\\Scripts\\Activate.ps1  
    \`\`\`

3\.  **\*\*Install dependencies:\*\***  
    Install all required Python packages, including PyInstaller.  
    \`\`\`bash  
    pip install PyQt6 numpy imageio tifffile pyinstaller  
    \`\`\`

\#\# Building for Windows

**\*\*Note:\*\*** You must perform these steps on a Windows machine.

1\.  **\*\*Open Command Prompt or PowerShell\*\*** and navigate to the \`digital\_enlarger\_app\` directory.

2\.  **\*\*Activate your virtual environment\*\*** (as shown in General Steps).

3\.  **\*\*Run PyInstaller:\*\***  
    Use the following command to create a single executable file. The \`--windowed\` flag prevents a console window from appearing, and \`--icon\` can be used to specify an application icon (you'll need to provide a \`.ico\` file).  
    \`\`\`bash  
    pyinstaller \--noconfirm \--onefile \--windowed \--name "DarkroomEnlarger" main.py  
    \`\`\`  
    \-   \`--noconfirm\`: Overwrite existing \`dist\` and \`build\` directories without asking.  
    \-   \`--onefile\`: Package the application into a single executable file.  
    \-   \`--windowed\` or \`--noconsole\`: Prevents a console window from opening when the application runs.  
    \-   \`--name 

"DarkroomEnlarger"\`: Specifies the name of the executable.  
    \-   \`main.py\`: The main script file of your application.

4\.  **\*\*Find the executable:\*\***  
    The executable will be located in the \`dist/\` directory (e.g., \`dist/DarkroomEnlarger.exe\`).

\#\# Building for macOS

**\*\*Note:\*\*** You must perform these steps on a macOS machine.

1\.  **\*\*Open Terminal\*\*** and navigate to the \`digital\_enlarger\_app\` directory.

2\.  **\*\*Activate your virtual environment\*\*** (as shown in General Steps).

3\.  **\*\*Run PyInstaller:\*\***  
    Similar to Windows, use \`--windowed\` for a GUI application. For macOS, \`--onefile\` is generally recommended for simpler distribution.  
    \`\`\`bash  
    pyinstaller \--noconfirm \--onefile \--windowed \--name "DarkroomEnlarger" main.py  
    \`\`\`

4\.  **\*\*Find the executable:\*\***  
    The executable will be located in the \`dist/\` directory (e.g., \`dist/DarkroomEnlarger\`). On macOS, this will be a Unix executable, but it will launch the GUI application.

\#\# Building for Linux

**\*\*Note:\*\*** You must perform these steps on a Linux machine.

1\.  **\*\*Open Terminal\*\*** and navigate to the \`digital\_enlarger\_app\` directory.

2\.  **\*\*Activate your virtual environment\*\*** (as shown in General Steps).

3\.  **\*\*Run PyInstaller:\*\***  
    For Linux, \`--onefile\` is also commonly used. You might need to install additional system dependencies if they are not present on the target Linux distribution.  
    \`\`\`bash  
    pyinstaller \--noconfirm \--onefile \--windowed \--name "DarkroomEnlarger" main.py  
    \`\`\`

4\.  **\*\*Find the executable:\*\***  
    The executable will be located in the \`dist/\` directory (e.g., \`dist/DarkroomEnlarger\`).

\#\# Important Considerations

\-   **\*\*Dependencies:\*\*** PyInstaller attempts to bundle all necessary dependencies. However, some system-level libraries (like Qt platform plugins on Linux) might still be required on the target machine. If you encounter errors, check the PyInstaller documentation and your system's dependencies.  
\-   **\*\*Icons:\*\*** To add a custom icon to your application, use the \`--icon\` flag with the path to your icon file (e.g., \`--icon=path/to/your/icon.ico\` for Windows, \`.icns\` for macOS, or \`.png\` for Linux).  
\-   **\*\*Hidden Imports:\*\*** If PyInstaller fails to find certain modules, you might need to add \`--hidden-import \<module\_name\>\` to your PyInstaller command.  
\-   **\*\*Testing:\*\*** Always test the generated executable on a clean machine (without the development environment) to ensure all dependencies are correctly bundled.

