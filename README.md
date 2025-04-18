# Para rodar o script execute os seguintes passos.
python -m venv venv 

## Linux
source venv/bin/activate

## Windowns
venv\scripts\activate.bat

## Para todos
pip install -r requirements.txt

python main.py

# Para gerar o executavel dele na sua plataforma windows, linux ou mac.

** pyinstaller robo.py