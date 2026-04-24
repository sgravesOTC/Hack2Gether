# OTCPulse

A campus community platform for Ozarks Technical Community College.

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/sgravesOTC/Hack2Gether.git
cd Hack2Gether
```

**2. Create and activate a virtual environment**

macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (Command Prompt)
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

Windows (PowerShell)
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

> If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` first.

**3. Install dependencies**
```bash
pip install -r otc_engage/requirements.txt
```

**4. Apply migrations**
```bash
cd otc_engage
python3 manage.py migrate
```

**5. Create a superuser**
```bash
python3 manage.py createsuperuser
```

**6. Run the development server**
```bash
python3 manage.py runserver
```

The app will be available at `http://127.0.0.1:8000`
