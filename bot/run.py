import uvicorn
import os

if __name__=='__main__':
  os.system(f"start http://127.0.0.1:{8080}")
  uvicorn.run("app:app", host="0.0.0.0", port=8080, debug=True, reload=True)
