# ---------- Build base ----------
FROM python:3.13-slim AS base


WORKDIR /app

# ---------- Runtime ----------
FROM base AS runtime

# (Opción A) Usando requirements.txt :
# COPY requirements*.txt /app/
# RUN pip install --upgrade pip \
#  && pip install -r requirements.txt -r requirements-dev.txt

# (Opción B):
COPY requirements.txt /app/
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copiamos solo el código de la app
COPY src /app/src

EXPOSE 8000

CMD ["python3", "src/main.py"]