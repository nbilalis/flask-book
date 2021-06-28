Remove-Item .venv -Recurse -Force -Confirm:$false

python -m venv .venv
.\.venv\Scripts\activate

pip install -r .\requirements.txt
python -m pip install --upgrade pip
