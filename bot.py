import os
import asyncio
import sqlite3
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-2.0-flash")

# ─── Database ───────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("andozalar.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS andozalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matn TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def andoza_qosh(matn: str):
    conn = sqlite3.connect("andozalar.db")
    c = conn.cursor()
    c.execute("INSERT INTO andozalar (matn) VALUES (?)", (matn,))
    conn.commit()
    conn.close()

def andozalar_olish():
    conn = sqlite3.connect("andozalar.db")
    c = conn.cursor()
    c.execute("SELECT id, matn, created_at FROM andozalar ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def andoza_ochir(andoza_id: int):
    conn = sqlite3.connect("andozalar.db")
    c = conn.cursor()
    c.execute("DELETE FROM andozalar WHERE id = ?", (andoza_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def hammani_ochir():
    conn = sqlite3.connect("andozalar.db")
    c = conn.cursor()
    c.execute("DELETE FROM andozalar")
    conn.commit()
    conn.close()

# ─── States ──────────────────────────────────────────────────────────────────
class BotState(StatesGroup):
    andoza_kutish = State()
    stil_kutish = State()
    mavzu_kutish = State()
    ochirish_kutish = State()

# ─── Keyboard ────────────────────────────────────────────────────────────────
def asosiy_klaviatura():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✍️ Kopirayt yozish"), KeyboardButton(text="➕ Andoza qo'shish")],
            [KeyboardButton(text="📋 Andozalarni ko'rish"), KeyboardButton(text="🗑 Andoza o'chirish")],
            [KeyboardButton(text="🧹 Hammasini tozalash")],
        ],
        resize_keyboard=True
    )

# ─── Access check ────────────────────────────────────────────────────────────
def ruxsat_bormi(user_id: int) -> bool:
    if ALLOWED_USER_ID == 0:
        return True
    return user_id == ALLOWED_USER_ID

# ─── /start ──────────────────────────────────────────────────────────────────
@dp.message(Command("start"))
async def start(message: types.Message):
    if not ruxsat_bormi(message.from_user.id):
        await message.answer("❌ Sizga ruxsat yo'q.")
        return
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "🤖 Bu bot sizga Telegram kanal uchun zo'r <b>kopiraytlar</b> yozishda yordam beradi.\n\n"
        "📌 Andozalar qo'shing — bot o'sha uslubda yozishni o'rganadi!\n\n"
        "Quyidagi tugmalardan birini tanlang 👇",
        reply_markup=asosiy_klaviatura(),
        parse_mode="HTML"
    )

# ─── Andoza qo'shish ─────────────────────────────────────────────────────────
@dp.message(F.text == "➕ Andoza qo'shish")
async def andoza_qoshish_boshlash(message: types.Message, state: FSMContext):
    if not ruxsat_bormi(message.from_user.id):
        return
    await state.set_state(BotState.andoza_kutish)
    await message.answer(
        "📝 Andozani yuboring:\n\n"
        "Bu sizning kanalda ishlatgan <b>tayyor kopiraytingiz</b> bo'lishi kerak.\n"
        "Bot o'sha uslubni eslab qoladi va keyingi safar o'shanga o'xshab yozadi.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

@dp.message(BotState.andoza_kutish)
async def andoza_saqlash(message: types.Message, state: FSMContext):
    if not ruxsat_bormi(message.from_user.id):
        return
    matn = message.text.strip()
    if len(matn) < 10:
        await message.answer("❗ Andoza juda qisqa. Kamida 10 ta belgi bo'lsin.")
        return
    andoza_qosh(matn)
    await state.clear()
    await message.answer(
        "✅ Andoza saqlandi! Bot endi shu uslubni eslab qoldi.\n\n"
        "Qancha ko'p andoza qo'shsangiz — natija shuncha yaxshi bo'ladi! 💪",
        reply_markup=asosiy_klaviatura()
    )

# ─── Andozalarni ko'rish ─────────────────────────────────────────────────────
@dp.message(F.text == "📋 Andozalarni ko'rish")
async def andozalar_korish(message: types.Message):
    if not ruxsat_bormi(message.from_user.id):
        return
    andozalar = andozalar_olish()
    if not andozalar:
        await message.answer("📭 Hali hech qanday andoza yo'q.\n\n'➕ Andoza qo'shish' tugmasini bosing!")
        return
    javob = f"📋 <b>Saqlangan andozalar ({len(andozalar)} ta):</b>\n\n"
    for row in andozalar:
        aid, matn, sana = row
        qisqa = matn[:80] + "..." if len(matn) > 80 else matn
        javob += f"🔹 <b>#{aid}</b> | {sana[:10]}\n{qisqa}\n\n"
    await message.answer(javob, parse_mode="HTML")

# ─── Andoza o'chirish ─────────────────────────────────────────────────────────
@dp.message(F.text == "🗑 Andoza o'chirish")
async def andoza_ochirish_boshlash(message: types.Message, state: FSMContext):
    if not ruxsat_bormi(message.from_user.id):
        return
    andozalar = andozalar_olish()
    if not andozalar:
        await message.answer("📭 O'chirish uchun andoza yo'q.")
        return
    await state.set_state(BotState.ochirish_kutish)
    javob = "🗑 Qaysi andozani o'chirmoqchisiz?\n\nID raqamini yuboring:\n\n"
    for row in andozalar:
        aid, matn, sana = row
        qisqa = matn[:60] + "..." if len(matn) > 60 else matn
        javob += f"<b>#{aid}</b> — {qisqa}\n\n"
    await message.answer(javob, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())

@dp.message(BotState.ochirish_kutish)
async def andoza_ochirish(message: types.Message, state: FSMContext):
    if not ruxsat_bormi(message.from_user.id):
        return
    try:
        aid = int(message.text.strip().replace("#", ""))
        if andoza_ochir(aid):
            await message.answer(f"✅ #{aid} andoza o'chirildi!", reply_markup=asosiy_klaviatura())
        else:
            await message.answer(f"❌ #{aid} topilmadi. ID ni tekshiring.")
    except ValueError:
        await message.answer("❗ Faqat raqam yuboring. Masalan: 3")
    await state.clear()

# ─── Hammasini tozalash ───────────────────────────────────────────────────────
@dp.message(F.text == "🧹 Hammasini tozalash")
async def hammani_tozalash(message: types.Message):
    if not ruxsat_bormi(message.from_user.id):
        return
    hammani_ochir()
    await message.answer("🧹 Barcha andozalar o'chirildi.", reply_markup=asosiy_klaviatura())

# ─── Kopirayt yozish ──────────────────────────────────────────────────────────
@dp.message(F.text == "✍️ Kopirayt yozish")
async def kopirayt_boshlash(message: types.Message, state: FSMContext):
    if not ruxsat_bormi(message.from_user.id):
        return
    andozalar = andozalar_olish()
    if not andozalar:
        await message.answer(
            "⚠️ Hali andoza yo'q!\n\n"
            "Avval '➕ Andoza qo'shish' tugmasi orqali kamida 1 ta andoza qo'shing."
        )
        return
    await state.set_state(BotState.stil_kutish)
    await message.answer(
        "🎨 <b>Stil va yo'riqnoma yuboring:</b>\n\n"
        "Masalan:\n"
        "• <i>Qisqa, emotsional, emoji bilan</i>\n"
        "• <i>Rasmiy, professional, uzun</i>\n"
        "• <i>Yoshlarga mo'ljallangan, zamonaviy</i>\n"
        "• <i>Savdo uchun, qoʻngʻiroqqa chaqiruvchi</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(BotState.stil_kutish)
async def stil_qabul(message: types.Message, state: FSMContext):
    if not ruxsat_bormi(message.from_user.id):
        return
    await state.update_data(stil=message.text.strip())
    await state.set_state(BotState.mavzu_kutish)
    await message.answer(
        "📌 <b>Endi mavzuni yuboring:</b>\n\n"
        "Masalan:\n"
        "• <i>Yangi mahsulot — qishki jaket</i>\n"
        "• <i>Chegirma — 30% off</i>\n"
        "• <i>Xizmat taqdimoti — veb-dizayn</i>",
        parse_mode="HTML"
    )

@dp.message(BotState.mavzu_kutish)
async def mavzu_qabul_va_yoz(message: types.Message, state: FSMContext):
    if not ruxsat_bormi(message.from_user.id):
        return
    data = await state.get_data()
    stil = data.get("stil", "")
    mavzu = message.text.strip()
    await state.clear()

    yuklanmoqda = await message.answer("⏳ Yozilmoqda...")

    andozalar = andozalar_olish()
    andoza_matni = "\n\n---\n\n".join([row[1] for row in andozalar])

    prompt = f"""Sen O'zbek tilida Telegram kanal uchun professional kopirayt yozuvchisisiz.

Quyida foydalanuvchining o'zi yozgan ANDOZALAR (namunalar) berilgan. 
Bu andozalarning USLUBI, TONI, TUZILISHI va YOZISH MANNERINI diqqat bilan o'rgan.
Yangi kopirayt HAR DOIM o'sha uslubda bo'lishi shart.

═══════════════════════════════
ANDOZALAR (foydalanuvchi uslubi):
═══════════════════════════════
{andoza_matni}

═══════════════════════════════
YANGI KOPIRAYT UCHUN MA'LUMOT:
═══════════════════════════════
Mavzu: {mavzu}
Stil/Yo'riqnoma: {stil}

═══════════════════════════════
QOIDALAR:
═══════════════════════════════
1. Faqat O'zbek tilida yoz
2. Andozalar uslubiga to'liq mos kel
3. Kreativ va original bo'l — copy-paste qilma
4. Tayyor kopiraytni yoz, tushuntirma bema
5. Kanal uchun mos, jozibali va samarali bo'lsin"""

    try:
        response = gemini.generate_content(prompt)
        natija = response.text
        await yuklanmoqda.delete()
        await message.answer(
            f"✨ <b>Tayyor kopirayt:</b>\n\n{natija}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 Boshqa variant kerakmi? Yana mavzu yuboring!",
            parse_mode="HTML",
            reply_markup=asosiy_klaviatura()
        )
    except Exception as e:
        await yuklanmoqda.delete()
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}", reply_markup=asosiy_klaviatura())

# ─── Main ─────────────────────────────────────────────────────────────────────
async def main():
    init_db()
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
