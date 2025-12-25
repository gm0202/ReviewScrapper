import uvicorn
import sys
import os
import traceback

# Add current directory to path to mimic running from inside backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Attempting to import main app...")
    from main import app
    print("Import successful.")
    
    print("Starting Uvicorn server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

except Exception as e:
    error_msg = f"CRITICAL STARTUP ERROR:\n{str(e)}\n\n{traceback.format_exc()}"
    print(error_msg)
    with open("backend_startup_error.log", "w") as f:
        f.write(error_msg)
    sys.exit(1)
