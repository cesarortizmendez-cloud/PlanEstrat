#!/bin/bash
# Build de estáticos para Vercel (@vercel/static-build).
# Recolecta en staticfiles_build/static (mismo patrón que IO-Lab / Pronostat).
pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
