#!/bin/bash
# Recolecta los estáticos de Django (WhiteNoise los sirve en runtime).
pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
