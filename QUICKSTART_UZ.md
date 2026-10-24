# Unector — tez boshlash (Windows)

1. Python 3.12 o‘rnating.
2. Command Prompt’da Unector papkasiga kiring.
3. `py -3.12 -m venv .venv`
4. `.venv\\Scripts\\activate`
5. `pip install -e ".[dev]"`
6. `copy .env.example .env` va token/ID’larni kiriting.
7. `python -m unector`
8. Test: `ruff check .` va `pytest`

To‘liq ko‘rsatmalar: `Unector_Discord_Bot_Guide_UZ.docx` fayli alohida berilgan.


## Sayt orqali boshqa kanallarga post yuborish
1. `.env` ichida `WEB_PANEL_ENABLED=1` qiling.
2. `WEB_PANEL_USER=publisher` va kamida 16 belgili kuchli `WEB_PANEL_PASSWORD` kiriting.
3. Botni qayta ishga tushiring.
4. Shu kompyuterda `http://127.0.0.1:8787` ni oching va login/parol kiriting.
5. Kanalni tanlab, sarlavha, matn, rasm URL yoki video havolasini kiriting va yuboring.
6. Panelni internetga ochiq qilmang; masofadan kirish kerak bo‘lsa VPN ishlating.
