POLLOB YT — Telegram Control Panel (যুক্ত করা হয়েছে)

Termux-এ চালানোর নিয়ম:
1. ZIP Extract করে প্রজেক্ট ফোল্ডারে যান।
2. প্যাকেজ ইনস্টল করুন:
   pip install -r requirements.txt
3. Telegram BotFather থেকে নিজের BOT TOKEN নিয়ে সেট করুন:
   export TELEGRAM_BOT_TOKEN='YOUR_BOT_TOKEN'
4. প্যানেল চালু করুন:
   python bot_control.py

নোট:
- bot_control.py হলো যোগ করা Telegram Panel।
- Admin ID: 8591405777
- UID দেওয়ার পরে Password চাওয়া হবে; Password ডেটাবেসে লেখা হয় না।
- BOT TOKEN কাউকে দেবেন না। নিজের Free Fire অ্যাকাউন্টেই ব্যবহার করুন।
- Telegram-এ Password পাঠালে chat history-তে থাকতে পারে।
- third-party automation গেমের নিয়ম ভঙ্গ করতে পারে এবং অ্যাকাউন্টে ঝুঁকি তৈরি করতে পারে।

--- আগের প্যানেলের নির্দেশনা ---
POLLOB YT — Telegram Bot Controller

Termux:
1. ZIP extract করে সেই ফোল্ডারে যান।
2. pip install -r requirements.txt
3. export TELEGRAM_BOT_TOKEN='YOUR_BOT_TOKEN'
4. python telegram_control.py

Admin Telegram ID: 8591405777
UID-এর পর PASS নেওয়া হয়। PASS SQLite-এ রাখা হয় না।
ব্যবহারকারীর হিসাব users.sqlite3-এ থাকে। Dashboard শুধু নির্দিষ্ট Admin ID দেখতে পারবেন।
Active Bots হলো controller চলাকালীন tracked process-এর হিসাব; controller restart করলে আগের process-গুলোর tracking পুনরায় attach হয় না।
Free Fire-এর third-party automation গেমের নিয়ম ভঙ্গ করতে পারে এবং অ্যাকাউন্টে ঝুঁকি আনতে পারে। নিজের অ্যাকাউন্ট ব্যবহার করুন। PASS Telegram chat history-তে থাকতে পারে।
