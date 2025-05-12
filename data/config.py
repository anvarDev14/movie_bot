from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan ma'lumotlarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot token
ADMINS = env.list("ADMINS", subcast=int)  # Adminlar ro'yxati (int ga aylantiramiz)
IP = env.str("ip")  # Xosting IP manzili

# Ma'lumotlarni konsolda chiqarish (tekshirish uchun)
print(f"BOT_TOKEN: {BOT_TOKEN}")
print(f"ADMINS: {ADMINS}")
print(f"IP: {IP}")
