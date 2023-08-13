python -m venv "env_lkh"
cd env_lkh/Scripts
activate.bat
python -m pip install --upgrade pip
cd ../..
pip install -r requirements.txt

pip install mecab_python-0.996_ko_0.9.2_msvc-cp39-cp39-win_amd64.whl
