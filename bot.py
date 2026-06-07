# نسخه جدید دیباگ : 6
# تغییرات: کسر ساعتی انقضا و رفع باگ دکمه برگشت
# صفر تا صد توسط @Camaeal دیباگ شده 
# اگه ننت خراب نیست اسکی میری منبع بزن

#تنها نسخه سالم و دیباگ در حال حاضر همین نسخه فقط اگه لازم داشتید خودتون api اضافه کنید برای هوش مصنوعی و ...
from colorama import Fore
from pyrogram import Client, filters, idle, errors
from pyrogram.types import *
from functools import wraps
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import subprocess
import html
import zipfile
import pymysql
import shutil
import signal
import re
import os

#==================== Config =====================#
Admin = 7074367029  # عددی مالک
Token = "8482217758:AAEpQgyu0TopXAIqHUaa7b825WO8JxbKL70"  # توکن تبچی ساز
API_ID = 26154106  # ایپی ایدی اکانت مالک
API_HASH = "86490b8b2b82b69a2eb012b9b20e4788"  # ایپی هش اکانت مالک
Channel_ID = "jiroft_moon"  # ایدی چنل بدون @
Helper_ID = "helbabarselfBot"  # ایدی ربات هلپر بدون 
DBName = "xxxxxxxx_tabchiland"  # اسم دیتابیس اصلی
DBUser = "xxxxxxxx_tabchiland"  # یوزرنیم دیتابیس اصلی
DBPass = "xxxxxxxx_tabchiland"  # پسورد دیتابیس اصلی
HelperDBName = "xxxxxxxx_landhelp"  # اسم دیتابیس هلپر
HelperDBUser = "xxxxxxxx_landhelp"  # یوزرنیم دیتابیس هلپر
HelperDBPass = "xxxxxxxx_landhelp"  # پسورد دیتابیس هلپر
CardNumber = "6219861865739832"  # شماره کارت برای فروش
CardName = "محسن پدیدار"  # اسم دارنده کارت

#==================== Create =====================#
if not os.path.isdir("sessions"):
    os.mkdir("sessions")
if not os.path.isdir("selfs"):
    os.mkdir("selfs")

#===================== App =======================#
app = Client("Bot", api_id=API_ID, api_hash=API_HASH, bot_token=Token)
scheduler = AsyncIOScheduler()
scheduler.start()
def safe_config_check():
    missing = []
    if not Token: missing.append("Token")
    if not API_ID: missing.append("API_ID")
    if not API_HASH: missing.append("API_HASH")
    if missing:
        raise RuntimeError(f"Missing required config values: {', '.join(missing)}")
    if not all([DBName, DBUser, DBPass]):
        print("[WARN] Database credentials are empty; DB operations will fail until configured.")

safe_config_check()
temp_Client = {}
lock = asyncio.Lock()

def get_data(query, params=None):
    try:
        connection = pymysql.connect(
            host="localhost",
            database=DBName,
            user=DBUser,
            password=DBPass,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10,
        )
        db = connection.cursor()
        if params is None:
            m = re.match(r"^\s*SELECT\s+\*\s+FROM\s+(\w+)\s+WHERE\s+id\s*=\s*'?([0-9]+)'?\s*(LIMIT\s+1)?\s*$", query, re.IGNORECASE)
            if m:
                table, _id, _ = m.groups()
                query = f"SELECT * FROM {table} WHERE id = %s LIMIT 1"
                params = (_id,)
        db.execute(query, params or ())
        return db.fetchone()
    except Exception as e:
        print(f"[DB][get_data] Error: {type(e).__name__}: {e}")
        return None
    finally:
        try:
            connection.close()
        except Exception:
            pass


def get_datas(query):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        result = db.fetchall()
        return result

def update_data(query):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        connect.commit()

def helper_getdata(query):
    with pymysql.connect(host="localhost", database=HelperDBName, user=HelperDBUser, password=HelperDBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        result = db.fetchone()
        return result

def helper_updata(query):
    with pymysql.connect(host="localhost", database=HelperDBName, user=HelperDBUser, password=HelperDBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        connect.commit()

update_data("""
CREATE TABLE IF NOT EXISTS bot(
status varchar(10) DEFAULT 'ON'
) default charset=utf8mb4;
""")
update_data("""
CREATE TABLE IF NOT EXISTS user(
id bigint PRIMARY KEY,
step varchar(150) DEFAULT 'none',
phone varchar(150) DEFAULT NULL,
amount bigint DEFAULT '0',
expir bigint DEFAULT '0',
account varchar(50) DEFAULT 'verified',
self varchar(50) DEFAULT 'inactive',
pid bigint DEFAULT NULL
) default charset=utf8mb4;
""")
update_data("""
CREATE TABLE IF NOT EXISTS block(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")
helper_updata("""
CREATE TABLE IF NOT EXISTS ownerlist(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")
helper_updata("""
CREATE TABLE IF NOT EXISTS adminlist(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")

bot = get_data("SELECT * FROM bot")
if bot is None:
    update_data("INSERT INTO bot() VALUES()")

OwnerUser = helper_getdata(f"SELECT * FROM ownerlist WHERE id = '{Admin}' LIMIT 1")
if OwnerUser is None:
    helper_updata(f"INSERT INTO ownerlist(id) VALUES({Admin})")

AdminUser = helper_getdata(f"SELECT * FROM adminlist WHERE id = '{Admin}' LIMIT 1")
if AdminUser is None:
    helper_updata(f"INSERT INTO adminlist(id) VALUES({Admin})")

def add_admin(user_id):
    if helper_getdata(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is None:
        helper_updata(f"INSERT INTO adminlist(id) VALUES({user_id})")

def delete_admin(user_id):
    if helper_getdata(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is not None:
        helper_updata(f"DELETE FROM adminlist WHERE id = '{user_id}' LIMIT 1")

def checker(func):
    @wraps(func)
    async def wrapper(c, m, *args, **kwargs):
        chat_id = m.chat.id if hasattr(m, "chat") else m.from_user.id
        bot = get_data("SELECT * FROM bot")
        block = get_data(f"SELECT * FROM block WHERE id = '{chat_id}' LIMIT 1")

        if block is not None and chat_id != Admin:
            return

        try:
            await app.get_chat_member(Channel_ID, chat_id)
        except errors.UserNotParticipant:
            await app.send_message(chat_id, """**• برای استفاده از خدمات ما باید ابتدا در کانال ما عضو باشید ، بعد از اینکه عضو شدید ربات را مجدد استارت کنید.
/start**""", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="عضویت در چنل", url=f"https://t.me/{Channel_ID}")
                    ]
                ]
            ))
            return
        except errors.ChatAdminRequired:
            if chat_id == Admin:
                await app.send_message(Admin, "ربات برای فعال شدن جوین اجباری در کانال مورد نظر ادمین نمی باشد!\nلطفا ربات را با دستوری های لازم در کانال مورد نظر ادمین کنید")
            return

        if bot["status"] == "OFF" and chat_id != Admin:
            await app.send_message(chat_id, "**ربات خاموش میباشد!**")
            return

        return await func(c, m, *args, **kwargs)
    return wrapper

# تابع کسر ساعتی انقضا - هر 1 ساعت یکبار اجرا می شود
async def expirdec(user_id):
    user = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
    user_expir = user["expir"]
    if user_expir > 0:
        user_upexpir = user_expir - 1
        update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
    else:
        job = scheduler.get_job(str(user_id))
        if job:
            scheduler.remove_job(str(user_id))
        if user_id != Admin:
            delete_admin(user_id)
        if os.path.isdir(f"selfs/self-{user_id}"):
            pid = user["pid"]
            try:
                if pid:
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                    await asyncio.sleep(2)
            except:
                pass
            shutil.rmtree(f"selfs/self-{user_id}")
        if os.path.isfile(f"sessions/{user_id}.session"):
            async with Client(f"sessions/{user_id}") as user_client:
                await user_client.log_out()
            if os.path.isfile(f"sessions/{user_id}.session"):
                os.remove(f"sessions/{user_id}.session")
        if os.path.isfile(f"sessions/{user_id}.session-journal"):
            os.remove(f"sessions/{user_id}.session-journal")
        await app.send_message(user_id, "کاربر گرامی اشتراک تبچی شما به پایان رسید. برای خرید مجدد اشتراک به قسمت خرید اشتراک مراجعه کنید")
        update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{user_id}' LIMIT 1")
        update_data(f"UPDATE user SET pid = NULL WHERE id = '{user_id}' LIMIT 1")

async def setscheduler(user_id):
    job = scheduler.get_job(str(user_id))
    if not job:
        scheduler.add_job(expirdec, "interval", hours=1, args=[user_id], id=str(user_id))

Main = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="🤔 تبچی چیست؟", callback_data="WhatSelf")
        ],
        [
            InlineKeyboardButton(text="💲 بها", callback_data="Price"),
            InlineKeyboardButton(text="➕ افزایش موجودی", callback_data="BuyAmount")
        ],
        [
            InlineKeyboardButton(text="🛒 خرید اشتراک", callback_data="BuySub")
        ],
        [
            InlineKeyboardButton(text="🤖 تبچی های من", callback_data="Subinfo"),
            InlineKeyboardButton(text="👤 حساب کاربری", callback_data="MyAccount")
        ],
        [
            InlineKeyboardButton(text="👨‍💻 پشتیبانی", callback_data="Support")
        ]
    ]
)

@app.on_message(filters.private, group=-1)
async def update(c, m):
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    if user is None:
        update_data(f"INSERT INTO user(id) VALUES({m.chat.id})")

@app.on_message(filters.private&filters.command("start"))
@checker
async def update(c, m):
    await app.send_message(m.chat.id, f"""**🫡 سلام {html.escape(m.chat.first_name)} عزیز

• به ربات خرید , پشتیبانی و مدیریت تبچی لند خوش آمدید

• این ربات جهت اتوماتیک بودن خرید , تمدید و مدیریت تبچی شما کاربران عزیز طراحی شده است

• جهت ادامه کار یکی از گزینه های زیر را انتخاب کنید :**""", reply_markup=Main)
    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
    async with lock:
        if m.chat.id in temp_Client:
            del temp_Client[m.chat.id]
    if os.path.isfile(f"sessions/{m.chat.id}.session") and not os.path.isfile(f"sessions/{m.chat.id}.session-journal"):
        os.remove(f"sessions/{m.chat.id}.session")

@app.on_callback_query()
@checker
async def call(c, call):
    global temp_Client
    user = get_data(f"SELECT * FROM user WHERE id = '{call.from_user.id}' LIMIT 1")
    phone_number = user["phone"]
    expir = user["expir"]
    amount = user["amount"]
    chat_id = call.from_user.id
    m_id = call.message.id
    data = call.data
    username = f"@{call.from_user.username}" if call.from_user.username else "وجود ندارد"

    if data == "MyAccount":
        await app.edit_message_text(chat_id, m_id, "**اطلاعات حساب کاربری شما در Tabchi Land به شرح زیر می باشد:**", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="نام شما", callback_data="text"),
                    InlineKeyboardButton(text=f"{call.from_user.first_name}", callback_data="text")
                ],
                [
                    InlineKeyboardButton(text="آیدی شما", callback_data="text"),
                    InlineKeyboardButton(text=f"{call.from_user.id}", callback_data="text")
                ],
                [
                    InlineKeyboardButton(text="یوزرنیم شما", callback_data="text"),
                    InlineKeyboardButton(text=f"{username}", callback_data="text")
                ],
                [
                    InlineKeyboardButton(text="موجودی شما", callback_data="text"),
                    InlineKeyboardButton(text=f"{amount} تومان", callback_data="text")
                ],
                [
                    InlineKeyboardButton(text="----------------", callback_data="text")
                ],
                [
                    InlineKeyboardButton(text=f"انقضای شما ({expir} ساعت)", callback_data="text")
                ],
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "BuySub" or data == "Back2":
        if user["phone"] is None:
            await app.delete_messages(chat_id, m_id)
            await app.send_message(chat_id, "**لطفا با استفاده از دکمه زیر شماره خود را به اشتراک بگذارید**", reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(text="اشتراک گذاری شماره", request_contact=True)
                    ]
                ], resize_keyboard=True
            ))
            update_data(f"UPDATE user SET step = 'contact' WHERE id = '{call.from_user.id}' LIMIT 1")
        else:
            if not os.path.isfile(f"sessions/{chat_id}.session-journal"):
                await app.edit_message_text(chat_id, m_id, "مدت زمان اشتراک را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="یک ماهه • 70 تومان", callback_data="Login-720-70000")
                        ],
                        [
                            InlineKeyboardButton(text="دو ماه • 140 تومان", callback_data="Login-1440-140000")
                        ],
                        [
                            InlineKeyboardButton(text="سه ماهه • 210 تومان", callback_data="Login-2160-210000")
                        ],
                        [
                            InlineKeyboardButton(text="چهار ماهه • 280 تومان", callback_data="Login-2880-280000")
                        ],
                        [
                            InlineKeyboardButton(text="پنج ماهه • 350 تومان", callback_data="Login-3600-350000")
                        ],
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
                async with lock:
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session") and not os.path.isfile(f"sessions/{chat_id}.session-journal"):
                    os.remove(f"sessions/{chat_id}.session")
            else:
                await app.answer_callback_query(call.id, text="اشتراک تبچی برای شما فعال است!", show_alert=True)

    elif data.split("-")[0] == "Login":
        expir_count = data.split("-")[1]
        cost = data.split("-")[2]
        if int(amount) >= int(cost):
            mess = await app.edit_message_text(chat_id, m_id, "در حال پردازش...")
            async with lock:
                if chat_id not in temp_Client:
                    temp_Client[chat_id] = {}
                temp_Client[chat_id]["client"] = Client(f"sessions/{chat_id}", api_id=API_ID, api_hash=API_HASH, device_model="Tabchi-Land", system_version="Linux")
                temp_Client[chat_id]["number"] = phone_number
                await temp_Client[chat_id]["client"].connect()
            try:
                await app.edit_message_text(chat_id, mess.id, "کد تایید 5 رقمی را با فرمت زیر ارسال کنید:\n1.2.3.4.5", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                async with lock:
                    temp_Client[chat_id]["response"] = await temp_Client[chat_id]["client"].send_code(temp_Client[chat_id]["number"])
                update_data(f"UPDATE user SET step = 'login1-{expir_count}-{cost}' WHERE id = '{call.from_user.id}' LIMIT 1")

            except errors.BadRequest:
                await app.edit_message_text(chat_id, mess.id, "اتصال ناموفق بود! لطفا دوباره تلاش کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")

            except errors.PhoneNumberInvalid:
                await app.edit_message_text(chat_id, mess.id, "این شماره نامعتبر است!", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")

            except errors.PhoneNumberBanned:
                await app.edit_message_text(chat_id, mess.id, "این اکانت محدود است!", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")

            except Exception:
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")
        else:
            await app.edit_message_text(chat_id, m_id, "موجودی حساب شما برای خرید این اشتراک کافی نیست", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="افزایش موجودی", callback_data="Wallet")
                    ],
                    [
                        InlineKeyboardButton(text="برگشت", callback_data="Back2")
                    ]
                ]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "Price":
        await app.edit_message_text(chat_id, m_id, """**
⤸ بَهاء تبچی عبارت است از : 

↤ 1 ماهه: `70` هزار تومان
↤ 2 ماهه: `140` هزار تومان
↤ 3 ماهه: `210` هزار تومان
↤ 4 ماهه: `280` هزار تومان
↤ 5 ماهه: `350` هزار تومان
**""", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "Wallet" or data == "Back3":
        await app.edit_message_text(chat_id, m_id, f"موجودی شما: {amount} تومان\nیکی از گزینه های زیر را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="خرید موجودی", callback_data="BuyAmount"),
                    InlineKeyboardButton(text="انتقال موجودی", callback_data="TransferAmount")
                ],
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "BuyAmount":
        await app.edit_message_text(chat_id, m_id, "میزان موجودی مورد نظر خود را برای شارژ حساب وارد کنید:\nحداقل موجودی قابل خرید 10000 تومان است!", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back3")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'buyamount1' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data.split("-")[0] == "AcceptAmount":
        user_id = int(data.split("-")[1])
        count = int(data.split("-")[2])
        user_amount = get_data(f"SELECT amount FROM user WHERE id = '{user_id}' LIMIT 1")
        user_upamount = int(user_amount["amount"]) + int(count)
        update_data(f"UPDATE user SET amount = '{user_upamount}' WHERE id = '{user_id}' LIMIT 1")
        await app.edit_message_text(Admin, m_id, f"تایید انجام شد\nمبلغ {count} تومان به حساب کاربر [ {user_id} ] انتقال یافت\nموجودی جدید کاربر: {user_upamount} تومان")
        await app.send_message(user_id, f"شد🎉 پرداخت شما تایید شد!\nمقدار {count} تومان به حسابت اضافه شد.")

    elif data.split("-")[0] == "RejectAmount":
        user_id = int(data.split("-")[1])
        await app.edit_message_text(Admin, m_id, "درخواست کاربر مورد نظر برای افزایش موجودی رد شد")
        await app.send_message(user_id, "درخواست شما برای افزایش موجودی رد شد")

    elif data == "TransferAmount":
        await app.edit_message_text(chat_id, m_id, "آیدی عددی کاربری که قصد انتقال موجودی به او را دارید ارسال کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back3")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'transferam1' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data.split("-")[0] == "AcceptExpir":
        user_id = int(data.split("-")[1])
        count = int(data.split("-")[2])
        user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
        user_upexpir = int(user_expir["expir"]) + int(count)
        update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
        await app.edit_message_text(Admin, m_id, f"تایید انجام شد\n{count} ساعت به انقضای کاربر [ {user_id} ] افزوده شد\nانقضای جدید کاربر: {user_upexpir} ساعت")
        await app.send_message(user_id, f"درخواست شما برای افزایش انقضا تایید شد\n{count} ساعت به انقضای شما افزوده شد\nانقضای جدید شما: {user_upexpir} ساعت")

    elif data.split("-")[0] == "RejectExpir":
        user_id = int(data.split("-")[1])
        await app.edit_message_text(Admin, m_id, "درخواست کاربر مورد نظر برای افزایش انقضا رد شد")
        await app.send_message(user_id, "درخواست شما برای افزایش انقضا رد شد")

    elif data == "Subinfo" or data == "Back4":
        if os.path.isfile(f"sessions/{chat_id}.session-journal"):
            substatus = "فعال" if user["self"] == "active" else "غیرفعال"
            await app.edit_message_text(chat_id, m_id, f"وضعیت اشتراک: {substatus}\nشماره اکانت: {phone_number}\nانقضا: {expir} ساعت", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="خرید انقضا", callback_data="BuyExpir"),
                        InlineKeyboardButton(text="انتقال انقضا", callback_data="TransferExpir")
                    ],
                    [
                        InlineKeyboardButton(text="برگشت", callback_data="Back")
                    ]
                ]
            ))
        else:
            await app.answer_callback_query(call.id, text="شما اشتراک فعالی ندارید!", show_alert=True)

    elif data == "BuyExpir":
        await app.edit_message_text(chat_id, m_id, "میزان انقضای مورد نظر خود را برای افزایش وارد کنید (ساعت):\nهزینه هر 24 ساعت انقضا 1000 تومان است", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back4")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'buyexpir1' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "TransferExpir":
        await app.edit_message_text(chat_id, m_id, "آیدی عددی کاربری که قصد انتقال انقضا به او را دارید ارسال کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back4")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'transferex1' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "WhatSelf":
        await app.edit_message_text(chat_id, m_id, """**
🔴 تبچی چیست؟

تبچی یک اکانت هوشمند تلگرام است که برای ارسال خودکار پیام، تبلیغات هدفمند و مدیریت هم‌زمان چندین گروه و پیوی استفاده می‌شود.

این سیستم با شبیه‌سازی رفتار یک کاربر واقعی، پیام‌ها را به‌صورت زمان‌بندی‌شده و کنترل‌شده ارسال می‌کند تا از فلود، فریز و بن شدن جلوگیری شود.

تبچی معمولاً برای:
• تبلیغات گسترده و هوشمند  
• ارسال پیام به گروه‌ها و پیوی‌ها  
• مدیریت کمپین‌های تلگرامی  
• افزایش بازدهی با حداقل ریسک  

مورد استفاده قرار می‌گیرد.

⚠️ توجه: استفاده نادرست از تبچی (سرعت بالا، پیام تکراری، اکانت خام) می‌تواند باعث محدودیت یا مسدود شدن اکانت شود. به همین دلیل رعایت تنظیمات اصولی و نکات ایمنی الزامی است.

اگر حرفه‌ای تنظیم شود، تبچی یک ابزار قدرتمند است؛  
اگر اشتباه استفاده شود، سریع حذف می‌شود.
**""", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "Support":
        await app.edit_message_text(chat_id, m_id, "پیام خود را ارسال کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="برگشت", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'support' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data.split("-")[0] == "Reply":
        exit = data.split("-")[1]
        getuser = await app.get_users(exit)
        await app.send_message(Admin, f"پیام خود را برای کاربر [ {html.escape(getuser.first_name)} ] ارسال کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="صفحه اصلی", callback_data="Back"),
                    InlineKeyboardButton(text="پنل مدیریت", callback_data="Panel")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'ureply-{exit}' WHERE id = '{Admin}' LIMIT 1")

    elif data.split("-")[0] == "Block":
        exit = data.split("-")[1]
        getuser = await app.get_users(exit)
        block = get_data(f"SELECT * FROM block WHERE id = '{exit}' LIMIT 1")
        if block is None:
            await app.send_message(exit, "کاربر محترم شما به دلیل نقض قوانین از ربات مسدود شدید")
            await app.send_message(Admin, f"کاربر [ {html.escape(getuser.first_name)} ] از ربات بلاک شد")
            update_data(f"INSERT INTO block(id) VALUES({exit})")
        else:
            await app.send_message(Admin, f"کاربر [ {html.escape(getuser.first_name)} ] از قبل بلاک است")

    elif data == "Back":
        try:
            await app.edit_message_text(
                chat_id,
                m_id,
                f"""**🫡 سلام {html.escape(call.from_user.first_name)} عزیز

• به ربات خرید , پشتیبانی و مدیریت تبچی لند خوش آمدید

• این ربات جهت اتوماتیک بودن خرید , تمدید و مدیریت تبچی شما کاربران عزیز طراحی شده است

• جهت ادامه کار یکی از گزینه های زیر را انتخاب کنید :**""",
                reply_markup=Main
            )
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
            async with lock:
                if chat_id in temp_Client:
                    del temp_Client[chat_id]
        except errors.MessageNotModified:
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
            async with lock:
                if chat_id in temp_Client:
                    del temp_Client[chat_id]
            await app.answer_callback_query(call.id, text="به منوی اصلی بازگشتید!", show_alert=True)
        except Exception as e:
            await app.answer_callback_query(call.id, text="خطایی رخ داد! لطفاً دوباره تلاش کنید.", show_alert=True)

    elif data == "text":
        await app.answer_callback_query(call.id, text="این دکمه نمایشی است", show_alert=True)

@app.on_message(filters.contact)
@checker
async def update(c, m):
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    if user["step"] == "contact":
        phone_number = str(m.contact.phone_number)
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
        contact_id = m.contact.user_id
        if m.contact and m.chat.id == contact_id:
            mess = await app.send_message(m.chat.id, "شماره شما تایید شد", reply_markup=ReplyKeyboardRemove())
            update_data(f"UPDATE user SET phone = '{phone_number}' WHERE id = '{m.chat.id}' LIMIT 1")
            await asyncio.sleep(1)
            await app.delete_messages(m.chat.id, mess.id)
            await app.send_message(m.chat.id, f"""**🫡 سلام {html.escape(m.chat.first_name)} عزیز

• به ربات خرید , پشتیبانی و مدیریت تبچی لند خوش آمدید

• این ربات جهت اتوماتیک بودن خرید , تمدید و مدیریت تبچی شما کاربران عزیز طراحی شده است

• جهت ادامه کار یکی از گزینه های زیر را انتخاب کنید :**""", reply_markup=Main)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(m.chat.id, "لطفا از دکمه اشتراک گذاری شماره استفاده کنید!")

@app.on_message(filters.private)
@checker
async def update(c, m):
    global temp_Client
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    username = f"@{m.from_user.username}" if m.from_user.username else "وجود ندارد"
    phone_number = user["phone"]
    expir = user["expir"]
    amount = user["amount"]
    chat_id = m.chat.id
    text = m.text
    m_id = m.id

    if user["step"].split("-")[0] == "login1":
        if re.match(r'^\d\.\d\.\d\.\d\.\d$', text):
            code = ''.join(re.findall(r'\d', text))
            expir_count = user["step"].split("-")[1]
            cost = user["step"].split("-")[2]
            mess = await app.send_message(chat_id, "در حال پردازش...")
            try:
                async with lock:
                    await temp_Client[chat_id]["client"].sign_in(temp_Client[chat_id]["number"], temp_Client[chat_id]["response"].phone_code_hash, code)
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                mess = await app.edit_message_text(chat_id, mess.id, "لاگین با موفقیت انجام شد")
                mess = await app.edit_message_text(chat_id, mess.id, "در حال فعالسازی تبچی...\n(ممکن است چند لحظه طول بکشد)")
                if not os.path.isdir(f"selfs/self-{m.chat.id}"):
                    os.mkdir(f"selfs/self-{m.chat.id}")
                    with zipfile.ZipFile("source/Self.zip", "r") as extract:
                        extract.extractall(f"selfs/self-{m.chat.id}")
                
                process = subprocess.Popen(
                    ["python3", "self.py", str(m.chat.id), str(API_ID), API_HASH, Helper_ID],
                    cwd=f"selfs/self-{m.chat.id}",
                    preexec_fn=os.setsid
                )
                
                await asyncio.sleep(10)
                if process.poll() is None:
                    await app.edit_message_text(chat_id, mess.id, f"تبچی با موفقیت برای اکانت شما فعال شد\nمدت زمان اشتراک: {expir_count} ساعت", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text="برگشت", callback_data="Back")
                            ]
                        ]
                    ))
                    upamount = int(amount) - int(cost)
                    update_data(f"UPDATE user SET amount = '{upamount}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET expir = '{expir_count}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET self = 'active' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                    add_admin(m.chat.id)
                    await setscheduler(m.chat.id)
                    await app.send_message(Admin, f"#گزارش_خرید_اشتراک\n\nآیدی کاربر: `{m.chat.id}`\nشماره کاربر: {phone_number}\nقیمت اشتراک: {cost} تومان\nمدت زمان اشتراک: {expir_count} ساعت")
                else:
                    await app.edit_message_text(chat_id, mess.id, "در فعالسازی تبچی برای اکانت شما مشکلی رخ داد! هیچ مبلغی از حساب شما کسر نشد\nلطفا دوباره امتحان کنید و در صورتی که مشکل ادامه داشت با پشتیبانی تماس بگیرید", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text="برگشت", callback_data="Back")
                            ]
                        ]
                    ))
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                    if os.path.isfile(f"sessions/{chat_id}.session"):
                        os.remove(f"sessions/{chat_id}.session")
            except errors.SessionPasswordNeeded:
                await app.edit_message_text(chat_id, mess.id, "رمز تایید دو مرحله ای برای اکانت شما فعال است\nرمز را وارد کنید:", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'login2-{expir_count}-{cost}' WHERE id = '{m.chat.id}' LIMIT 1")
            except errors.BadRequest:
                await app.edit_message_text(chat_id, mess.id, "کد نامعتبر است!")
            except errors.PhoneCodeInvalid:
                await app.edit_message_text(chat_id, mess.id, "کد نامعتبر است!")
            except errors.PhoneCodeExpired:
                await app.edit_message_text(chat_id, mess.id, "کد منقضی شده است! لطفا عملیات ورود را دوباره تکرار کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back2")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")
            except Exception:
                async with lock:
                    await temp_Client[chat_id]["client"].disconnect()
                    if chat_id in temp_Client:
                        del temp_Client[chat_id]
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")
        else:
            await app.send_message(chat_id, "فرمت نامعتبر است! لطفا کد را با فرمت ذکر شده وارد کنید:")

    elif user["step"].split("-")[0] == "login2":
        password = text.strip()
        expir_count = user["step"].split("-")[1]
        cost = user["step"].split("-")[2]
        mess = await app.send_message(chat_id, "در حال پردازش...")
        try:
            async with lock:
                await temp_Client[chat_id]["client"].check_password(password)
                await temp_Client[chat_id]["client"].disconnect()
                if chat_id in temp_Client:
                    del temp_Client[chat_id]
            mess = await app.edit_message_text(chat_id, mess.id, "لاگین با موفقیت انجام شد")
            mess = await app.edit_message_text(chat_id, mess.id, "در حال فعالسازی تبچی...\n(ممکن است چند لحظه طول بکشد)")
            if not os.path.isdir(f"selfs/self-{m.chat.id}"):
                os.mkdir(f"selfs/self-{m.chat.id}")
                with zipfile.ZipFile("source/Self.zip", "r") as extract:
                    extract.extractall(f"selfs/self-{m.chat.id}")
            
            process = subprocess.Popen(
                ["python3", "self.py", str(m.chat.id), str(API_ID), API_HASH, Helper_ID],
                cwd=f"selfs/self-{m.chat.id}",
                preexec_fn=os.setsid
            )
            
            await asyncio.sleep(10)
            if process.poll() is None:
                await app.edit_message_text(chat_id, mess.id, f"تبچی با موفقیت برای اکانت شما فعال شد\nمدت زمان اشتراک: {expir_count} ساعت", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back")
                        ]
                    ]
                ))
                upamount = int(amount) - int(cost)
                update_data(f"UPDATE user SET amount = '{upamount}' WHERE id = '{m.chat.id}' LIMIT 1")
                update_data(f"UPDATE user SET expir = '{expir_count}' WHERE id = '{m.chat.id}' LIMIT 1")
                update_data(f"UPDATE user SET self = 'active' WHERE id = '{m.chat.id}' LIMIT 1")
                update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{m.chat.id}' LIMIT 1")
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                add_admin(m.chat.id)
                await setscheduler(m.chat.id)
                await app.send_message(Admin, f"#گزارش_خرید_اشتراک\n\nآیدی کاربر: `{m.chat.id}`\nشماره کاربر: {phone_number}\nقیمت اشتراک: {cost} تومان\nمدت زمان اشتراک: {expir_count} ساعت")
            else:
                await app.edit_message_text(chat_id, mess.id, "در فعالسازی تبچی برای اکانت شما مشکلی رخ داد! هیچ مبلغی از حساب شما کسر نشد\nلطفا دوباره امتحان کنید و در صورتی که مشکل ادامه داشت با پشتیبانی تماس بگیرید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                if os.path.isfile(f"sessions/{chat_id}.session"):
                    os.remove(f"sessions/{chat_id}.session")
        except errors.BadRequest:
            await app.edit_message_text(chat_id, mess.id, "رمز نادرست است!\nرمز را وارد کنید:", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="برگشت", callback_data="Back2")
                    ]
                ]
            ))
        except Exception:
            async with lock:
                await temp_Client[chat_id]["client"].disconnect()
                if chat_id in temp_Client:
                    del temp_Client[chat_id]
            if os.path.isfile(f"sessions/{chat_id}.session"):
                os.remove(f"sessions/{chat_id}.session")

    elif user["step"] == "buyamount1":
        if text.isdigit():
            count = text.strip()
            if int(count) >= 10000:
                await app.send_message(chat_id, f"فاکتور افزایش موجودی به مبلغ {count} تومان ایجاد شد\n\nشماره کارت: `{CardNumber}`\nبه نام {CardName}\nمبلغ قابل پرداخت: {count} تومان\n\nبعد از پرداخت رسید تراکنش را در همین قسمت ارسال کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back3")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'buyamount2-{count}' WHERE id = '{m.chat.id}' LIMIT 1")
            else:
                await app.send_message(chat_id, "حداقل موجودی قابل خرید 10000 تومان است!")
        else:
            await app.send_message(chat_id, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "buyamount2":
        if m.photo:
            count = int(user["step"].split("-")[1])
            mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
            await app.send_message(Admin, f"""
مدیر گرامی درخواست افزایش موجودی جدید دارید

نام کاربر: {html.escape(m.chat.first_name)}
آیدی کاربر: `{m.chat.id}`
یوزرنیم کاربر: {username}
مبلغ درخواستی کاربر: {count} تومان
""", reply_to_message_id=mess.id, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("تایید", callback_data=f"AcceptAmount-{chat_id}-{count}"),
                        InlineKeyboardButton("رد کردن", callback_data=f"RejectAmount-{chat_id}")
                    ]
                ]
            ))
            await app.send_message(chat_id, "✅ فیش دریافت شد. پس از بررسی نتیجه اعلام می‌شود.", reply_to_message_id=m_id)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "ورودی نامعتبر! فقط ارسال عکس مجاز است")

    elif user["step"] == "transferam1":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if user_id != m.chat.id:
                    await app.send_message(chat_id, "میزان موجودی مورد نظر خود را برای انتقال وارد کنید:\nحداقل موجودی قابل ارسال 10000 تومان است")
                    update_data(f"UPDATE user SET step = 'transferam2-{user_id}' WHERE id = '{m.chat.id}' LIMIT 1")
                else:
                    await app.send_message(chat_id, "شما نمی توانید به خودتان موجودی انتقال دهید!")
            else:
                await app.send_message(chat_id, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(chat_id, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "transferam2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = text.strip()
            if int(amount) >= int(count):
                if int(count) >= 10000:
                    user_amount = get_data(f"SELECT amount FROM user WHERE id = '{user_id}' LIMIT 1")
                    upamount = int(amount) - int(count)
                    user_upamount = int(user_amount["amount"]) + int(count)
                    update_data(f"UPDATE user SET amount = '{upamount}' WHERE id = '{m.chat.id}' LIMIT 1")
                    update_data(f"UPDATE user SET amount = '{user_upamount}' WHERE id = '{user_id}' LIMIT 1")
                    await app.send_message(chat_id, f"مبلغ {count} تومان از حساب شما کسر شد و به حساب کاربر [ {user_id} ] انتقال یافت\nموجودی جدید شما: {upamount} تومان", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text="برگشت", callback_data="Back3")
                            ]
                        ]
                    ))
                    await app.send_message(user_id, f"مبلغ {count} تومان از حساب کاربر [ {m.chat.id} ] به حساب شما انتقال یافت\nموجودی جدید شما: {user_upamount} تومان")
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                else:
                    await app.send_message(chat_id, "حداقل موجودی قابل ارسال 10000 تومان است!")
            else:
                await app.send_message(chat_id, "موجودی شما کافی نیست!")
        else:
            await app.send_message(chat_id, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"] == "buyexpir1":
        if text.isdigit():
            count = int(text.strip())
            if int(count) > 0:
                cost_per_day = 1000
                total_cost = (count // 24) * cost_per_day if count >= 24 else cost_per_day
                await app.send_message(chat_id, f"فاکتور افزایش انقضا به مدت {count} ساعت ایجاد شد\n\nشماره کارت: `{CardNumber}`\nبه نام {CardName}\nمبلغ قابل پرداخت: {total_cost} تومان\n\nبعد از پرداخت رسید تراکنش را در همین قسمت ارسال کنید", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="برگشت", callback_data="Back4")
                        ]
                    ]
                ))
                update_data(f"UPDATE user SET step = 'buyexpir2-{count}' WHERE id = '{m.chat.id}' LIMIT 1")
            else:
                await app.send_message(chat_id, "حداقل انقضای قابل خرید 1 ساعت است!")
        else:
            await app.send_message(chat_id, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "buyexpir2":
        if m.photo:
            count = int(user["step"].split("-")[1])
            mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
            await app.send_message(Admin, f"""
مدیر گرامی درخواست افزایش انقضای جدید دارید

نام کاربر: {html.escape(m.chat.first_name)}
آیدی کاربر: `{m.chat.id}`
یوزرنیم کاربر: {username}
تعداد ساعت های درخواستی کاربر: {count} ساعت
""", reply_to_message_id=mess.id, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("تایید", callback_data=f"AcceptExpir-{chat_id}-{count}"),
                        InlineKeyboardButton("رد کردن", callback_data=f"RejectExpir-{chat_id}")
                    ]
                ]
            ))
            await app.send_message(chat_id, "رسید تراکنش شما ارسال شد. لطفا منتظر تایید توسط مدیر باشید", reply_to_message_id=m_id)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "ورودی نامعتبر! فقط ارسال عکس مجاز است")

    elif user["step"] == "transferex1":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                if user_id != m.chat.id:
                    if os.path.isfile(f"sessions/{user_id}.session-journal"):
                        await app.send_message(chat_id, "میزان انقضای مورد نظر خود را برای انتقال وارد کنید (ساعت):\nحداقل باید 10 ساعت انقضا برای شما باقی بماند!")
                        update_data(f"UPDATE user SET step = 'transferex2-{user_id}' WHERE id = '{m.chat.id}' LIMIT 1")
                    else:
                        await app.send_message(chat_id, "اشتراک تبچی برای این کاربر فعال نیست!")
                else:
                    await app.send_message(chat_id, "شما نمی توانید به خودتان انقضا انتقال دهید!")
            else:
                await app.send_message(chat_id, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(chat_id, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "transferex2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = text.strip()
            user_hours = expir
            if int(user_hours) >= int(count):
                if int(user_hours) - int(count) >= 10:
                    user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
                    user_expir_hours = int(user_expir["expir"])
                    
                    sender_new_hours = user_hours - int(count)
                    update_data(f"UPDATE user SET expir = '{sender_new_hours}' WHERE id = '{m.chat.id}' LIMIT 1")
                    
                    receiver_new_hours = user_expir_hours + int(count)
                    update_data(f"UPDATE user SET expir = '{receiver_new_hours}' WHERE id = '{user_id}' LIMIT 1")
                    
                    sender_user = await app.get_users(m.chat.id)
                    receiver_user = await app.get_users(user_id)
                    
                    sender_name = html.escape(sender_user.first_name) if sender_user.first_name else "کاربر"
                    receiver_name = html.escape(receiver_user.first_name) if receiver_user.first_name else "کاربر"
                    
                    receiver_msg = await app.send_message(user_id, f"""👤 کاربر {receiver_name} عزیز

**✅ از سمت [{sender_name}](tg://user?id={m.chat.id}) مقدار {count} ساعت انقضا برای شما ارسال شد**

**⏰ انقضای جدید شما: {receiver_new_hours} ساعت**""", 
                        reply_to_message_id=m.reply_to_message_id if m.reply_to_message_id else None,
                        disable_web_page_preview=True
                    )
                    
                    await app.send_message(chat_id, f"{count} ساعت از انقضای شما کسر شد و به کاربر [{receiver_name}](tg://user?id={user_id}) انتقال یافت\nانقضای جدید شما: {sender_new_hours} ساعت", 
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(text="برگشت", callback_data="Back4")
                                ]
                            ]
                        ),
                        disable_web_page_preview=True
                    )
                    
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
                else:
                    await app.send_message(chat_id, "حداقل باید 10 ساعت انقضا برای شما باقی بماند!")
            else:
                await app.send_message(chat_id, "انقضای شما کافی نیست!")
        else:
            await app.send_message(chat_id, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"] == "support":
        mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
        await app.send_message(Admin, f"""
مدیر گرامی پیام ارسال شده جدید دارید

نام کاربر: {html.escape(m.chat.first_name)}
آیدی کاربر: `{m.chat.id}`
یوزرنیم کاربر: {username}
""", reply_to_message_id=mess.id, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("پاسخ", callback_data=f"Reply-{chat_id}"),
                    InlineKeyboardButton("بلاک", callback_data=f"Block-{chat_id}")
                ]
            ]
        ))
        await app.send_message(chat_id, "پیام شما ارسال شد و در اسرع وقت به آن پاسخ داده خواهد شد", reply_to_message_id=m_id)

    elif user["step"].split("-")[0] == "ureply":
        exit = user["step"].split("-")[1]
        mess = await app.copy_message(from_chat_id=Admin, chat_id=exit, message_id=m_id)
        await app.send_message(exit, "کاربر گرامی پیام ارسال شده جدید از پشتیبانی دارید", reply_to_message_id=mess.id)
        await app.send_message(Admin, "پیام شما ارسال شد پیام دیگری ارسال یا روی یکی از گزینه های زیر کلیک کنید:", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="صفحه اصلی", callback_data="Back"),
                    InlineKeyboardButton(text="پنل مدیریت", callback_data="Panel")
                ]
            ]
        ))

    elif text and (text.startswith("انتقال انقضا") or text.startswith("انتقال ساعت")):
        try:
            parts = text.split()
            if len(parts) >= 3:
                hours = int(parts[2])
                receiver = None
                
                if len(parts) >= 4:
                    username_input = parts[3].replace("@", "")
                    try:
                        receiver_user = await app.get_users(username_input)
                        receiver = receiver_user.id
                    except:
                        pass
                
                if not receiver and len(parts) >= 4 and parts[3].isdigit():
                    receiver = int(parts[3])
                
                if not receiver and m.reply_to_message:
                    receiver = m.reply_to_message.from_user.id
                
                if receiver:
                    user_hours = expir
                    if user_hours >= hours:
                        if user_hours - hours >= 10:
                            user_expir = get_data(f"SELECT expir FROM user WHERE id = '{receiver}' LIMIT 1")
                            if user_expir:
                                user_expir_hours = int(user_expir["expir"])
                                
                                sender_new_hours = user_hours - hours
                                update_data(f"UPDATE user SET expir = '{sender_new_hours}' WHERE id = '{m.chat.id}' LIMIT 1")
                                
                                receiver_new_hours = user_expir_hours + hours
                                update_data(f"UPDATE user SET expir = '{receiver_new_hours}' WHERE id = '{receiver}' LIMIT 1")
                                
                                sender_user = await app.get_users(m.chat.id)
                                receiver_user = await app.get_users(receiver)
                                
                                sender_name = html.escape(sender_user.first_name) if sender_user.first_name else "کاربر"
                                receiver_name = html.escape(receiver_user.first_name) if receiver_user.first_name else "کاربر"
                                
                                receiver_msg = await app.send_message(receiver, f"""👤 کاربر {receiver_name} عزیز

**✅ از سمت [{sender_name}](tg://user?id={m.chat.id}) مقدار {hours} ساعت انقضا برای شما ارسال شد**

**⏰ انقضای جدید شما: {receiver_new_hours} ساعت**""", 
                                    reply_to_message_id=m.reply_to_message_id if m.reply_to_message_id else None,
                                    disable_web_page_preview=True
                                )
                                
                                await app.send_message(chat_id, f"{hours} ساعت از انقضای شما کسر شد و به کاربر [{receiver_name}](tg://user?id={receiver}) انتقال یافت\nانقضای جدید شما: {sender_new_hours} ساعت", 
                                    disable_web_page_preview=True
                                )
                            else:
                                await app.send_message(chat_id, "کاربر گیرنده در ربات یافت نشد!")
                        else:
                            await app.send_message(chat_id, "حداقل باید 10 ساعت انقضا برای شما باقی بماند!")
                    else:
                        await app.send_message(chat_id, "انقضای شما کافی نیست!")
                else:
                    await app.send_message(chat_id, "لطفاً کاربر گیرنده را مشخص کنید:\n- با یوزرنیم: @username\n- با آیدی عددی: 123456789\n- با ریپلای روی پیام کاربر")
            else:
                await app.send_message(chat_id, "فرمت صحیح:\n`انتقال انقضا [مقدار ساعت] [یوزرنیم/آیدی/ریپلای]`")
        except ValueError:
            await app.send_message(chat_id, "مقدار ساعت باید عدد باشد!")
        except Exception as e:
            await app.send_message(chat_id, f"خطا: {str(e)}")

    elif chat_id == Admin and text and (text.startswith("افزایش") or text.startswith("کسر")):
        try:
            parts = text.split()
            if len(parts) >= 3:
                action = parts[0]
                hours = int(parts[1])
                target = None
                
                if len(parts) >= 3:
                    username_input = parts[2].replace("@", "")
                    try:
                        target_user = await app.get_users(username_input)
                        target = target_user.id
                    except:
                        pass
                
                if not target and len(parts) >= 3 and parts[2].isdigit():
                    target = int(parts[2])
                
                if not target and m.reply_to_message:
                    target = m.reply_to_message.from_user.id
                
                if target:
                    user_expir = get_data(f"SELECT expir FROM user WHERE id = '{target}' LIMIT 1")
                    if user_expir:
                        user_hours = int(user_expir["expir"])
                        
                        if action == "افزایش":
                            new_hours = user_hours + hours
                            update_data(f"UPDATE user SET expir = '{new_hours}' WHERE id = '{target}' LIMIT 1")
                            
                            target_user = await app.get_users(target)
                            target_name = html.escape(target_user.first_name) if target_user.first_name else "کاربر"
                            
                            await app.send_message(chat_id, f"✅ با موفقیت {hours} ساعت انقضا به کاربر {target_name} افزوده شد ✓", 
                                disable_web_page_preview=True)
                            
                            if target != Admin:
                                await app.send_message(target, f"مدیر گرامی {hours} ساعت به انقضای شما افزود.\nانقضای جدید شما: {new_hours} ساعت")
                            
                        elif action == "کسر":
                            if user_hours >= hours:
                                if user_hours - hours >= 1:
                                    new_hours = user_hours - hours
                                    update_data(f"UPDATE user SET expir = '{new_hours}' WHERE id = '{target}' LIMIT 1")
                                    
                                    target_user = await app.get_users(target)
                                    target_name = html.escape(target_user.first_name) if target_user.first_name else "کاربر"
                                    
                                    await app.send_message(chat_id, f"✅ با موفقیت {hours} ساعت انقضا از کاربر {target_name} کسر شد ✓", 
                                        disable_web_page_preview=True)
                                    
                                    if target != Admin:
                                        await app.send_message(target, f"مدیر گرامی {hours} ساعت از انقضای شما کسر کرد.\nانقضای جدید شما: {new_hours} ساعت")
                                else:
                                    await app.send_message(chat_id, "❌ حداقل باید 1 ساعت انقضا برای کاربر باقی بماند!")
                            else:
                                await app.send_message(chat_id, "❌ انقضای کاربر کافی نیست!")
                        
                        await setscheduler(target)
                    else:
                        await app.send_message(chat_id, "❌ کاربر مورد نظر در ربات یافت نشد!")
                else:
                    await app.send_message(chat_id, "❌ لطفاً کاربر مورد نظر را مشخص کنید:\n- با یوزرنیم: @username\n- با آیدی عددی: 123456789\n- با ریپلای روی پیام کاربر")
            else:
                await app.send_message(chat_id, "فرمت صحیح:\n`افزایش [مقدار ساعت] [یوزرنیم/آیدی/ریپلای]`\n`کسر [مقدار ساعت] [یوزرنیم/آیدی/ریپلای]`")
        except ValueError:
            await app.send_message(chat_id, "❌ مقدار ساعت باید عدد باشد!")
        except Exception as e:
            await app.send_message(chat_id, f"❌ خطا: {str(e)}")

#===================== Panel ======================#
Panel = ReplyKeyboardMarkup(
    [
        [
            ("آمار 📊")
        ],
        [
            ("ارسال همگانی ✉️"),
            ("فوروارد همگانی ✉️")
        ],
        [
            ("بلاک کاربر 🚫"),
            ("آنبلاک کاربر ✅️")
        ],
        [
            ("افزودن موجودی ➕"),
            ("کسر موجودی ➖")
        ],
        [
            ("افزودن زمان اشتراک ➕"),
            ("کسر زمان اشتراک ➖")
        ],
        [
            ("فعال کردن تبچی 🔵"),
            ("غیرفعال کردن تبچی 🔴")
        ],
        [
            ("روشن کردن ربات 🔵"),
            ("خاموش کردن ربات 🔴")
        ],
        [
            ("صفحه اصلی 🏠")
        ]
    ], resize_keyboard=True
)

AdminBack = ReplyKeyboardMarkup(
    [
        [
            ("برگشت")
        ]
    ], resize_keyboard=True
)

@app.on_message(filters.private&filters.user(Admin)&filters.command("panel"), group=1)
async def update(c, m):
    await app.send_message(Admin, "مدیر گرامی به پنل مدیریت Tabchi Land خوش آمدید!", reply_markup=Panel)
    update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
    async with lock:
        if Admin in temp_Client:
            del temp_Client[Admin]

@app.on_callback_query(filters.user(Admin), group=-1)
async def call(c, call):
    data = call.data
    m_id = call.message.id
    if data == "Panel":
        await app.send_message(Admin, "مدیر گرامی به پنل مدیریت Tabchi Land خوش آمدید!", reply_markup=Panel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]
    
    elif data.split("-")[0] == "DeleteSub":
        user_id = int(data.split("-")[1])
        await app.edit_message_text(Admin, m_id, "**هشدار! با این کار اشتراک کاربر مورد نظر به طور کامل حذف می شود و امکان فعالسازی دوباره از پنل مدیریت وجود ندارد\n\nاگر از این کار اطمینان دارید روی گزینه تایید و در غیر این صورت روی گزینه برگشت کلیک کنید**", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="تایید", callback_data=f"AcceptDelSub-{user_id}")
                ],
                [
                    InlineKeyboardButton(text="برگشت", callback_data="AdminBack")
                ]
            ]
        ))
    
    elif data.split("-")[0] == "AcceptDelSub":
        await app.edit_message_text(Admin, m_id, "اشتراک تبچی کاربر مورد نظر به طور کامل حذف شد", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="برگشت", callback_data="AdminBack")
                ]
            ]
        ))
        user_id = int(data.split("-")[1])
        if os.path.isdir(f"selfs/self-{user_id}"):
            shutil.rmtree(f"selfs/self-{user_id}")
        if os.path.isfile(f"sessions/{user_id}.session"):
            async with Client(f"sessions/{user_id}") as user_client:
                await user_client.log_out()
            if os.path.isfile(f"sessions/{user_id}.session"):
                os.remove(f"sessions/{user_id}.session")
        if os.path.isfile(f"sessions/{user_id}.session-journal"):
            os.remove(f"sessions/{user_id}.session-journal")
        update_data(f"UPDATE user SET expir = '0' WHERE id = '{user_id}' LIMIT 1")
        update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{user_id}' LIMIT 1")
        update_data(f"UPDATE user SET pid = NULL WHERE id = '{user_id}' LIMIT 1")
        await app.send_message(user_id, "کاربر گرامی اشتراک تبچی شما توسط مدیر حذف شد\nبرای کسب اطلاعات بیشتر و دلیل حذف اشتراک به پشتیبانی مراجعه کنید")
    
    elif data == "AdminBack":
        await app.delete_messages(Admin, m_id)
        await app.send_message(Admin, "مدیر گرامی به پنل مدیریت Tabchi Land خوش آمدید!", reply_markup=Panel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]

@app.on_message(filters.private&filters.user(Admin), group=1)
async def update(c, m):
    bot = get_data("SELECT * FROM bot")
    user = get_data(f"SELECT * FROM user WHERE id = '{Admin}' LIMIT 1")
    text = m.text
    m_id = m.id

    if text == "برگشت":
        await app.send_message(Admin, "مدیر گرامی به پنل مدیریت Tabchi Land خوش آمدید!", reply_markup=Panel)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]

    elif text == "آمار 📊":
        mess = await app.send_message(Admin, "در حال دریافت اطلاعات...")
        botinfo = await app.get_me()
        allusers = get_datas("SELECT COUNT(id) FROM user")[0][0]
        allblocks = get_datas("SELECT COUNT(id) FROM block")[0][0]
        await app.edit_message_text(Admin, mess.id, f"""
تعداد کاربران ربات: {allusers}
تعداد کاربران بلاک شده: {allblocks}
--------------------------
نام ربات: {botinfo.first_name}
آیدی ربات: `{botinfo.id}`
یوزرنیم ربات: @{botinfo.username}
""")
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")

    elif text == "ارسال همگانی ✉️":
        await app.send_message(Admin, "پیام خود را ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'sendall' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "sendall":
        mess = await app.send_message(Admin, "در حال ارسال به همه کاربران...")
        users = get_datas(f"SELECT id FROM user")
        for user in users:
            await app.copy_message(from_chat_id=Admin, chat_id=user[0], message_id=m_id)
            await asyncio.sleep(0.1)
        await app.edit_message_text(Admin, mess.id, "پیام شما برای همه کاربران ارسال شد")

    elif text == "فوروارد همگانی ✉️":
        await app.send_message(Admin, "پیام خود را ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'forall' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "forall":
        mess = await app.send_message(Admin, "در حال فوروارد به همه کاربران...")
        users = get_datas(f"SELECT id FROM user")
        for user in users:
            await app.forward_messages(from_chat_id=Admin, chat_id=user[0], message_ids=m_id)
            await asyncio.sleep(0.1)
        await app.edit_message_text(Admin, mess.id, "پیام شما برای همه کاربران فوروارد شد")

    elif text == "بلاک کاربر 🚫":
        await app.send_message(Admin, "آیدی عددی کاربری را که می خواهید بلاک کنید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'userblock' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "userblock":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                block = get_data(f"SELECT * FROM block WHERE id = '{user_id}' LIMIT 1")
                if block is None:
                    await app.send_message(user_id, "کاربر محترم شما به دلیل نقض قوانین از ربات مسدود شدید")
                    await app.send_message(Admin, f"کاربر [ {user_id} ] از ربات بلاک شد")
                    update_data(f"INSERT INTO block(id) VALUES({user_id})")
                else:
                    await app.send_message(Admin, "این کاربر از قبل بلاک است")
            else:
                await app.send_message(Admin, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif text == "آنبلاک کاربر ✅️":
        await app.send_message(Admin, "آیدی عددی کاربری را که می خواهید آنبلاک کنید ارسال کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'userunblock' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "userunblock":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                block = get_data(f"SELECT * FROM block WHERE id = '{user_id}' LIMIT 1")
                if block is not None:
                    await app.send_message(user_id, "کاربر عزیز شما آنبلاک شدید و اکنون می توانید از ربات استفاده کنید")
                    await app.send_message(Admin, f"کاربر [ {user_id} ] از ربات آنبلاک شد")
                    update_data(f"DELETE FROM block WHERE id = '{user_id}' LIMIT 1")
                else:
                    await app.send_message(Admin, "این کاربر از ربات بلاک نیست!")
            else:
                await app.send_message(Admin, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif text == "افزودن موجودی ➕":
        await app.send_message(Admin, "آیدی عددی کاربری که می خواهید موجودی او را افزایش دهید وارد کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'amountinc' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "amountinc":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                await app.send_message(Admin, "میزان موجودی مورد نظر خود را برای افزایش وارد کنید:")
                update_data(f"UPDATE user SET step = 'amountinc2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
            else:
                await app.send_message(Admin, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "amountinc2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = int(text.strip())
            user_amount = get_data(f"SELECT amount FROM user WHERE id = '{user_id}' LIMIT 1")
            user_upamount = int(user_amount["amount"]) + int(count)
            update_data(f"UPDATE user SET amount = '{user_upamount}' WHERE id = '{user_id}' LIMIT 1")
            await app.send_message(Admin, f"مبلغ {count} تومان به حساب کاربر [ {user_id} ] افزوده شد\nموجودی جدید کاربر: {user_upamount} تومان")
            await app.send_message(user_id, f"مبلغ {count} تومان از طرف مدیر به حساب شما افزوده شد\nموجودی جدید شما: {user_upamount} تومان")
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif text == "کسر موجودی ➖":
        await app.send_message(Admin, "آیدی عددی کاربری که می خواهید موجودی او را کسر کنید وارد کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'amountdec' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "amountdec":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                await app.send_message(Admin, "میزان موجودی مورد نظر خود را برای کسر وارد کنید:")
                update_data(f"UPDATE user SET step = 'amountdec2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
            else:
                await app.send_message(Admin, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "amountdec2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = int(text.strip())
            user_amount = get_data(f"SELECT amount FROM user WHERE id = '{user_id}' LIMIT 1")
            if int(user_amount["amount"]) >= int(count):
                user_upamount = int(user_amount["amount"]) - int(count)
                update_data(f"UPDATE user SET amount = '{user_upamount}' WHERE id = '{user_id}' LIMIT 1")
                await app.send_message(Admin, f"مبلغ {count} تومان از حساب کاربر [ {user_id} ] کسر شد\nموجودی جدید کاربر: {user_upamount} تومان")
                await app.send_message(user_id, f"مبلغ {count} تومان از طرف مدیر از حساب شما کسر شد\nموجودی جدید شما: {user_upamount} تومان")
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
            else:
                await app.send_message(Admin, "موجودی کاربر کافی نیست!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif text == "افزودن زمان اشتراک ➕":
        await app.send_message(Admin, "آیدی عددی کاربری که می خواهید زمان اشتراک او را افزایش دهید وارد کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'expirinc' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "expirinc":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                await app.send_message(Admin, "میزان زمان اشتراک مورد نظر خود را برای افزایش وارد کنید (ساعت):")
                update_data(f"UPDATE user SET step = 'expirinc2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
            else:
                await app.send_message(Admin, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "expirinc2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = int(text.strip())
            user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
            user_expir_hours = int(user_expir["expir"])
            user_expir_hours += count
            update_data(f"UPDATE user SET expir = '{user_expir_hours}' WHERE id = '{user_id}' LIMIT 1")
            await app.send_message(Admin, f"{count} ساعت به انقضای کاربر [ {user_id} ] افزوده شد\nانقضای جدید کاربر: {user_expir_hours} ساعت")
            await app.send_message(user_id, f"{count} ساعت از طرف مدیر به انقضای شما افزوده شد\nانقضای جدید شما: {user_expir_hours} ساعت")
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
            await setscheduler(user_id)
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif text == "کسر زمان اشتراک ➖":
        await app.send_message(Admin, "آیدی عددی کاربری که می خواهید زمان اشتراک او را کسر کنید وارد کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'expirdec' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "expirdec":
        if text.isdigit():
            user_id = int(text.strip())
            if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                await app.send_message(Admin, "میزان زمان اشتراک مورد نظر خود را برای کسر وارد کنید (ساعت):")
                update_data(f"UPDATE user SET step = 'expirdec2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
            else:
                await app.send_message(Admin, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "expirdec2":
        if text.isdigit():
            user_id = int(user["step"].split("-")[1])
            count = int(text.strip())
            user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
            user_expir_hours = int(user_expir["expir"])
            if user_expir_hours >= count:
                user_expir_hours -= count
                update_data(f"UPDATE user SET expir = '{user_expir_hours}' WHERE id = '{user_id}' LIMIT 1")
                await app.send_message(Admin, f"{count} ساعت از انقضای کاربر [ {user_id} ] کسر شد\nانقضای جدید کاربر: {user_expir_hours} ساعت")
                await app.send_message(user_id, f"{count} ساعت از طرف مدیر از انقضای شما کسر شد\nانقضای جدید شما: {user_expir_hours} ساعت")
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
                await setscheduler(user_id)
            else:
                await app.send_message(Admin, "انقضای کاربر کافی نیست!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif text == "فعال کردن تبچی 🔵":
        await app.send_message(Admin, "آیدی عددی کاربری که می خواهید تبچی او را فعال کنید وارد کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'selfon' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "selfon":
        if text.isdigit():
            user_id = int(text.strip())
            user_info = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
            if user_info is not None:
                if user_info["self"] == "inactive":
                    if user_info["phone"] is not None:
                        if not os.path.isfile(f"sessions/{user_id}.session-journal"):
                            async with lock:
                                temp_Client[user_id] = {}
                                temp_Client[user_id]["client"] = Client(f"sessions/{user_id}", api_id=API_ID, api_hash=API_HASH, device_model="Tabchi-Land", system_version="Linux")
                                temp_Client[user_id]["number"] = user_info["phone"]
                                await temp_Client[user_id]["client"].connect()
                            try:
                                await app.send_message(Admin, "در حال پردازش...")
                                async with lock:
                                    temp_Client[user_id]["response"] = await temp_Client[user_id]["client"].send_code(temp_Client[user_id]["number"])
                                await app.send_message(Admin, "کد تایید 5 رقمی را با فرمت زیر ارسال کنید:\n1.2.3.4.5")
                                update_data(f"UPDATE user SET step = 'selfon2-{user_id}' WHERE id = '{Admin}' LIMIT 1")
                            except errors.BadRequest:
                                await app.send_message(Admin, "اتصال ناموفق بود! لطفا دوباره تلاش کنید")
                                async with lock:
                                    await temp_Client[user_id]["client"].disconnect()
                                    if user_id in temp_Client:
                                        del temp_Client[user_id]
                                if os.path.isfile(f"sessions/{user_id}.session"):
                                    os.remove(f"sessions/{user_id}.session")
                            except errors.PhoneNumberInvalid:
                                await app.send_message(Admin, "این شماره نامعتبر است!")
                                async with lock:
                                    await temp_Client[user_id]["client"].disconnect()
                                    if user_id in temp_Client:
                                        del temp_Client[user_id]
                                if os.path.isfile(f"sessions/{user_id}.session"):
                                    os.remove(f"sessions/{user_id}.session")
                            except errors.PhoneNumberBanned:
                                await app.send_message(Admin, "این اکانت محدود است!")
                                async with lock:
                                    await temp_Client[user_id]["client"].disconnect()
                                    if user_id in temp_Client:
                                        del temp_Client[user_id]
                                if os.path.isfile(f"sessions/{user_id}.session"):
                                    os.remove(f"sessions/{user_id}.session")
                            except Exception:
                                async with lock:
                                    await temp_Client[user_id]["client"].disconnect()
                                    if user_id in temp_Client:
                                        del temp_Client[user_id]
                                if os.path.isfile(f"sessions/{user_id}.session"):
                                    os.remove(f"sessions/{user_id}.session")
                        else:
                            await app.send_message(Admin, "اشتراک تبچی برای این کاربر از قبل فعال است!")
                    else:
                        await app.send_message(Admin, "این کاربر شماره تلفن ثبت شده ندارد!")
                else:
                    await app.send_message(Admin, "تبچی این کاربر از قبل فعال است!")
            else:
                await app.send_message(Admin, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif user["step"].split("-")[0] == "selfon2":
        if re.match(r'^\d\.\d\.\d\.\d\.\d$', text):
            user_id = int(user["step"].split("-")[1])
            code = ''.join(re.findall(r'\d', text))
            mess = await app.send_message(Admin, "در حال پردازش...")
            try:
                async with lock:
                    await temp_Client[user_id]["client"].sign_in(temp_Client[user_id]["number"], temp_Client[user_id]["response"].phone_code_hash, code)
                    await temp_Client[user_id]["client"].disconnect()
                    if user_id in temp_Client:
                        del temp_Client[user_id]
                mess = await app.edit_message_text(Admin, mess.id, "لاگین با موفقیت انجام شد")
                mess = await app.edit_message_text(Admin, mess.id, "در حال فعالسازی تبچی...\n(ممکن است چند لحظه طول بکشد)")
                if not os.path.isdir(f"selfs/self-{user_id}"):
                    os.mkdir(f"selfs/self-{user_id}")
                    with zipfile.ZipFile("source/Self.zip", "r") as extract:
                        extract.extractall(f"selfs/self-{user_id}")
                
                process = subprocess.Popen(
                    ["python3", "self.py", str(user_id), str(API_ID), API_HASH, Helper_ID],
                    cwd=f"selfs/self-{user_id}",
                    preexec_fn=os.setsid
                )
                
                await asyncio.sleep(10)
                if process.poll() is None:
                    await app.edit_message_text(Admin, mess.id, f"تبچی با موفقیت برای کاربر [ {user_id} ] فعال شد")
                    await app.send_message(user_id, "اشتراک تبچی شما توسط مدیر فعال شد")
                    update_data(f"UPDATE user SET self = 'active' WHERE id = '{user_id}' LIMIT 1")
                    update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{user_id}' LIMIT 1")
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
                    add_admin(user_id)
                    await setscheduler(user_id)
                else:
                    await app.edit_message_text(Admin, mess.id, "در فعالسازی تبچی برای کاربر مشکلی رخ داد! لطفا دوباره امتحان کنید")
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
                    if os.path.isfile(f"sessions/{user_id}.session"):
                        os.remove(f"sessions/{user_id}.session")
            except errors.SessionPasswordNeeded:
                await app.edit_message_text(Admin, mess.id, "رمز تایید دو مرحله ای برای اکانت این کاربر فعال است\nرمز را وارد کنید:")
                update_data(f"UPDATE user SET step = 'selfon3-{user_id}' WHERE id = '{Admin}' LIMIT 1")
            except errors.BadRequest:
                await app.edit_message_text(Admin, mess.id, "کد نامعتبر است!")
            except errors.PhoneCodeInvalid:
                await app.edit_message_text(Admin, mess.id, "کد نامعتبر است!")
            except errors.PhoneCodeExpired:
                await app.edit_message_text(Admin, mess.id, "کد منقضی شده است! لطفا عملیات ورود را دوباره تکرار کنید")
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
                async with lock:
                    await temp_Client[user_id]["client"].disconnect()
                    if user_id in temp_Client:
                        del temp_Client[user_id]
                if os.path.isfile(f"sessions/{user_id}.session"):
                    os.remove(f"sessions/{user_id}.session")
            except Exception:
                async with lock:
                    await temp_Client[user_id]["client"].disconnect()
                    if user_id in temp_Client:
                        del temp_Client[user_id]
                if os.path.isfile(f"sessions/{user_id}.session"):
                    os.remove(f"sessions/{user_id}.session")
        else:
            await app.send_message(Admin, "فرمت نامعتبر است! لطفا کد را با فرمت ذکر شده وارد کنید:")

    elif user["step"].split("-")[0] == "selfon3":
        user_id = int(user["step"].split("-")[1])
        password = text.strip()
        mess = await app.send_message(Admin, "در حال پردازش...")
        try:
            async with lock:
                await temp_Client[user_id]["client"].check_password(password)
                await temp_Client[user_id]["client"].disconnect()
                if user_id in temp_Client:
                    del temp_Client[user_id]
            mess = await app.edit_message_text(Admin, mess.id, "لاگین با موفقیت انجام شد")
            mess = await app.edit_message_text(Admin, mess.id, "در حال فعالسازی تبچی...\n(ممکن است چند لحظه طول بکشد)")
            if not os.path.isdir(f"selfs/self-{user_id}"):
                os.mkdir(f"selfs/self-{user_id}")
                with zipfile.ZipFile("source/Self.zip", "r") as extract:
                    extract.extractall(f"selfs/self-{user_id}")
            
            process = subprocess.Popen(
                ["python3", "self.py", str(user_id), str(API_ID), API_HASH, Helper_ID],
                cwd=f"selfs/self-{user_id}",
                preexec_fn=os.setsid
            )
            
            await asyncio.sleep(10)
            if process.poll() is None:
                await app.edit_message_text(Admin, mess.id, f"تبچی با موفقیت برای کاربر [ {user_id} ] فعال شد")
                await app.send_message(user_id, "اشتراک تبچی شما توسط مدیر فعال شد")
                update_data(f"UPDATE user SET self = 'active' WHERE id = '{user_id}' LIMIT 1")
                update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{user_id}' LIMIT 1")
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
                add_admin(user_id)
                await setscheduler(user_id)
            else:
                await app.edit_message_text(Admin, mess.id, "در فعالسازی تبچی برای کاربر مشکلی رخ داد! لطفا دوباره امتحان کنید")
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
                if os.path.isfile(f"sessions/{user_id}.session"):
                    os.remove(f"sessions/{user_id}.session")
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        except errors.BadRequest:
            await app.edit_message_text(Admin, mess.id, "رمز نادرست است!\nرمز را وارد کنید:")
        except Exception:
            async with lock:
                await temp_Client[user_id]["client"].disconnect()
                if user_id in temp_Client:
                    del temp_Client[user_id]
            if os.path.isfile(f"sessions/{user_id}.session"):
                os.remove(f"sessions/{user_id}.session")

    elif text == "غیرفعال کردن تبچی 🔴":
        await app.send_message(Admin, "آیدی عددی کاربری که می خواهید تبچی او را غیرفعال کنید وارد کنید:", reply_markup=AdminBack)
        update_data(f"UPDATE user SET step = 'selfoff' WHERE id = '{Admin}' LIMIT 1")

    elif user["step"] == "selfoff":
        if text.isdigit():
            user_id = int(text.strip())
            user_info = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
            if user_info is not None:
                if user_info["self"] == "active":
                    await app.send_message(Admin, "**هشدار! با این کار اشتراک کاربر مورد نظر به طور کامل حذف می شود و امکان فعالسازی دوباره از پنل مدیریت وجود ندارد\n\nاگر از این کار اطمینان دارید روی گزینه تایید و در غیر این صورت روی گزینه برگشت کلیک کنید**", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text="تایید", callback_data=f"AcceptDelSub-{user_id}")
                            ],
                            [
                                InlineKeyboardButton(text="برگشت", callback_data="AdminBack")
                            ]
                        ]
                    ))
                    update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
                else:
                    await app.send_message(Admin, "اشتراک تبچی برای این کاربر غیرفعال است!")
            else:
                await app.send_message(Admin, "چنین کاربری در ربات یافت نشد!")
        else:
            await app.send_message(Admin, "ورودی نامعتبر! فقط ارسال عدد مجاز است")

    elif text == "روشن کردن ربات 🔵":
        if bot["status"] == "OFF":
            update_data("UPDATE bot SET status = 'ON'")
            await app.send_message(Admin, "ربات روشن شد")
        else:
            await app.send_message(Admin, "ربات از قبل روشن است!")

    elif text == "خاموش کردن ربات 🔴":
        if bot["status"] == "ON":
            update_data("UPDATE bot SET status = 'OFF'")
            await app.send_message(Admin, "ربات خاموش شد")
        else:
            await app.send_message(Admin, "ربات از قبل خاموش است!")

    elif text == "صفحه اصلی 🏠":
        await app.send_message(Admin, f"""**🫡 سلام {html.escape(m.chat.first_name)} عزیز

• به ربات خرید , پشتیبانی و مدیریت تبچی لند خوش آمدید

• این ربات جهت اتوماتیک بودن خرید , تمدید و مدیریت تبچی شما کاربران عزیز طراحی شده است

• جهت ادامه کار یکی از گزینه های زیر را انتخاب کنید :**""", reply_markup=Main)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
        async with lock:
            if Admin in temp_Client:
                del temp_Client[Admin]

#===================== Start ======================#
print(Fore.GREEN + "Bot is running...")
app.run()