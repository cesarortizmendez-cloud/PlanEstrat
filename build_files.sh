#!/bin/bash
# Build alternativo/manual: recolecta los estáticos de Django para servirlos con
# WhiteNoise. En Vercel esto ya lo hace `buildCommand` en vercel.json; este script
# sirve para builds locales o en otras plataformas.
pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
