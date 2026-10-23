\
import asyncio, os, shutil, sys, tempfile, subprocess, sqlite3
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

BASE = Path(__file__).resolve().parent
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8778611434:AAG-9JO2_LkG4BwRmSp_cua-2NtE9m519CM").strip()
ADMIN_ID = 8591405777
ADMIN, TELEGRAM = "@POLLOB_GAMER", "@pollobrayp"
REGION = os.getenv("FF_REGION", "BD").strip().upper()
sessions, pending = {}, {}
DB_PATH = BASE / "users.db"

def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            game_uid TEXT,
            first_seen TEXT NOT NULL DEFAULT (datetime('now')),
            last_seen TEXT NOT NULL DEFAULT (datetime('now')),
            start_requests INTEGER NOT NULL DEFAULT 0
        )""")

def record_user(user, game_uid=None, started=False):
    if user is None:
        return
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""INSERT INTO users (telegram_id, username, first_name, game_uid, start_requests)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
              username=excluded.username,
              first_name=excluded.first_name,
              game_uid=COALESCE(excluded.game_uid, users.game_uid),
              last_seen=datetime('now'),
              start_requests=users.start_requests + excluded.start_requests""",
            (user.id, user.username or "", user.first_name or "", game_uid, 1 if started else 0))

def keyboard(user_id=None):
    rows = [
        [InlineKeyboardButton("▶️ Start Bot", callback_data="start")],
        [InlineKeyboardButton("⏹ STOP BOT", callback_data="stop")],
        [InlineKeyboardButton("👑 Admin ID", url="https://t.me/POLLOB_GAMER"), InlineKeyboardButton("✈️ Telegram", url="https://t.me/pollobrayp")],
    ]
    if user_id == ADMIN_ID:
        rows.append([InlineKeyboardButton("📊 Admin Dashboard", callback_data="admin_stats")])
    return InlineKeyboardMarkup(rows)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    record_user(update.effective_user)
    await update.effective_message.reply_text("🎮 TCP BOT PANEL\n\nনিজের UID ও Guest Password দিয়ে Start Bot করুন।\nআপনার Telegram ID, নাম/ইউজারনেম এবং পাঠানো গেম UID এই সার্ভারের users.db ফাইলে সংরক্ষিত হবে। Password ডেটাবেসে সংরক্ষণ করা হয় না।\nADMIN : @POLLOB_GAMER\nTELEGRAM : @pollobrayp", reply_markup=keyboard(update.effective_user.id))

async def stop_user(uid):
    data=sessions.pop(uid, None)
    if not data: return "আপনার বট এখন বন্ধ আছে।"
    p=data["process"]
    if p.poll() is None:
        p.terminate()
        try: await asyncio.to_thread(p.wait, 5)
        except Exception: p.kill()
    shutil.rmtree(data["workdir"], ignore_errors=True)
    return "⏹ আপনার বট বন্ধ করা হয়েছে।"

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=update.effective_user.id
    record_user(update.effective_user)
    if q.data == "admin_stats":
        if uid != ADMIN_ID:
            await q.answer("শুধু Admin এই তথ্য দেখতে পারবেন।", show_alert=True)
            return
        with sqlite3.connect(DB_PATH) as db:
            total = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            recent = db.execute("SELECT telegram_id, username, first_name, game_uid, last_seen FROM users ORDER BY last_seen DESC LIMIT 100").fetchall()
        active = sum(1 for d in sessions.values() if d["process"].poll() is None)
        lines = ["👑 ADMIN DASHBOARD", "", f"👥 মোট রেকর্ড করা ব্যবহারকারী: {total}", f"🟢 বর্তমানে চালু সেশন: {active}", "", "সর্বশেষ ব্যবহারকারী (সর্বোচ্চ 50 জন):"]
        for tid, uname, fname, game_uid, seen in recent:
            label = ("@" + uname) if uname else (fname or "নাম নেই")
            lines.append(f"• {label} | TG ID: {tid} | UID: {game_uid or 'এখনও নেই'} | {seen}")
        await q.message.reply_text("\n".join(lines), reply_markup=keyboard(uid))
    elif q.data=="start":
        d=sessions.get(uid)
        if d and d["process"].poll() is None:
            await q.message.reply_text("আপনার বট ইতিমধ্যে চালু আছে।", reply_markup=keyboard(uid)); return
        pending[uid]={"step":"uid"}
        record_user(update.effective_user, started=True)
        await q.message.reply_text("UID : আপনার নিজের Free Fire Guest UID পাঠান:")
    elif q.data=="stop":
        pending.pop(uid, None)
        await q.message.reply_text(await stop_user(uid), reply_markup=keyboard(uid))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id; flow=pending.get(uid)
    if not flow:
        await update.effective_message.reply_text("মেনু থেকে Start Bot বা Stop Bot নির্বাচন করুন।", reply_markup=keyboard(uid)); return
    value=update.effective_message.text.strip()
    if flow["step"]=="uid":
        if not value.isdigit() or not 5<=len(value)<=20:
            await update.effective_message.reply_text("সঠিক সংখ্যাযুক্ত UID পাঠান:"); return
        flow.update(uid_value=value, step="pass")
        record_user(update.effective_user, game_uid=value)
        await update.effective_message.reply_text("PASS : এখন নিজের Guest Password পাঠান। গ্রুপে কখনো পাঠাবেন না।")
        return
    if not 12<=len(value)<=256:
        await update.effective_message.reply_text("Password-এর দৈর্ঘ্য ঠিক নয়। আবার পাঠান:"); return
    pending.pop(uid, None); workdir=tempfile.mkdtemp(prefix=f"tcp_{uid}_")
    try:
        for item in BASE.iterdir():
            if item.name in {"bot_control.py","README_BN.txt","requirements.txt","__pycache__"} or item.suffix==".zip": continue
            dest=Path(workdir)/item.name
            if item.is_dir(): shutil.copytree(item,dest,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
            elif item.is_file() and item.suffix!=".pyc": shutil.copy2(item,dest)
        env=os.environ.copy(); env.update(FF_UID=flow["uid_value"], FF_PASS=value, FF_REGION=REGION)
        p=subprocess.Popen([sys.executable,"main.py"],cwd=workdir,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        await asyncio.sleep(1.0)
        if p.poll() is not None:
            shutil.rmtree(workdir,ignore_errors=True)
            await update.effective_message.reply_text(
                "বটের মূল প্রোগ্রাম চালু হয়েই বন্ধ হয়ে গেছে। Termux-এ main.py সরাসরি চালিয়ে error দেখুন; লগ না দেখে কারণ নিশ্চিত করা যাচ্ছে না।",
                reply_markup=keyboard(uid))
            return
        sessions[uid]={"process":p,"workdir":workdir}
        await update.effective_message.reply_text(f"START BOT অনুরোধ পাঠানো হয়েছে।\nUID : {flow['uid_value']}\nPASS : [গোপন রাখা হয়েছে]\nADMIN : {ADMIN}\nTELEGRAM : {TELEGRAM}\n\nপ্রসেস চালু আছে; লগইন সফল হয়েছে কি না তা নিশ্চিত করতে লগ পরীক্ষা করুন।",reply_markup=keyboard(uid))
    except Exception as e:
        shutil.rmtree(workdir,ignore_errors=True)
        await update.effective_message.reply_text(f"চালু করা যায়নি: {type(e).__name__}",reply_markup=keyboard(uid))

async def shutdown(app):
    for uid in list(sessions): await stop_user(uid)

def main():
    init_db()
    if not TOKEN: raise SystemExit("প্রথমে নতুন Bot Token তৈরি করে TELEGRAM_BOT_TOKEN environment variable সেট করুন।")
    app=Application.builder().token(TOKEN).post_shutdown(shutdown).build()
    app.add_handler(CommandHandler("start",start_cmd)); app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler)); app.run_polling()
if __name__=="__main__": main()
