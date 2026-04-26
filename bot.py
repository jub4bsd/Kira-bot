#ملاحظات:
	#لازم ترفع البوت مشرف بالقناة الي حطيت يوزرها
	#ممنوع تبيع الملف
	#لعرض لوحة الادمن ارسل /admin
	#المطور: @R1yuke
	#ممنوع منعا باتا بيع الملف
import os
import telebot
import sqlite3
from telebot import types

if os.path.exists('bot_data.db'):
    os.remove('bot_data.db')

TOKEN = "8769295593:AAGoOIC3NFTanlc2_4oooE-6fwqCkA7wWJ8"
ADMIN_ID = 7546406264
CHANNEL_USERNAME = "@kir4_tech"
DEVELOPER_USERNAME = "@R1yuke"

bot = telebot.TeleBot(TOKEN)

def get_conn():
    return sqlite3.connect('bot_data.db')

conn = get_conn()
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT, file_id TEXT, file_type TEXT, description TEXT, photo_id TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS blocked (user_id INTEGER PRIMARY KEY)''')
conn.commit()
cursor.close()
conn.close()

user_states = {}

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('📢 اشترك في القناة', url=f'https://t.me/{CHANNEL_USERNAME.replace("@", "")}', style='danger'))
        markup.add(types.InlineKeyboardButton('✅ تحقق من الاشتراك', callback_data='check_sub', style='success'))
        bot.send_message(message.chat.id, '⚠️ يجب الاشتراك في القناة لاستخدام البوت', reply_markup=markup)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('📁 الملفات', callback_data='show_files', style='success'))
    markup.add(types.InlineKeyboardButton('👨‍💻 المطور', url=f'https://t.me/{DEVELOPER_USERNAME}', style='primary'))
    bot.send_message(message.chat.id, 'مرحباً بك في بوت الملفات', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_sub_callback(call):
    if check_subscription(call.from_user.id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('📁 الملفات', callback_data='show_files', style='success'))
        markup.add(types.InlineKeyboardButton('👨‍💻 المطور', url=f'https://t.me/{DEVELOPER_USERNAME}', style='primary'))
        bot.edit_message_text('✅ تم التحقق بنجاح', call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, '❌ لم تشترك بعد', show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'show_files')
def show_files(call):
    if not check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, '❌ يجب الاشتراك اولاً', show_alert=True)
        return
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT id, file_name, description, photo_id FROM files')
    files = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not files:
        bot.answer_callback_query(call.id, 'لا توجد ملفات')
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    colors = ['danger', 'primary'] * (len(files) // 2 + 1)
    for i, (fid, fname, fdesc, fphoto) in enumerate(files):
        btn_text = f"📄 {fname}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'view_{fid}', style=colors[i]))
    markup.add(types.InlineKeyboardButton('🔙 رجوع', callback_data='back_main', style='danger'))
    bot.edit_message_text('📁 قائمة الملفات:', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def view_file(call):
    if not check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, '❌ يجب الاشتراك اولاً', show_alert=True)
        return
    
    fid = int(call.data.split('_')[1])
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT file_name, file_id, file_type, description, photo_id FROM files WHERE id=?', (fid,))
    file = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not file:
        bot.answer_callback_query(call.id, 'الملف غير موجود')
        return
    
    fname, file_id, file_type, fdesc, photo_id = file
    
    if photo_id:
        try:
            bot.send_photo(call.message.chat.id, photo_id)
        except:
            pass
    
    if fdesc:
        bot.send_message(call.message.chat.id, f"📝 وصف الملف:\n{fdesc}")
    
    try:
        if file_type == 'document':
            bot.send_document(call.message.chat.id, file_id, caption=f"📁 {fname}")
        elif file_type == 'photo':
            bot.send_photo(call.message.chat.id, file_id)
        elif file_type == 'video':
            bot.send_video(call.message.chat.id, file_id)
        elif file_type == 'audio':
            bot.send_audio(call.message.chat.id, file_id)
        elif file_type == 'voice':
            bot.send_voice(call.message.chat.id, file_id)
    except:
        bot.send_message(call.message.chat.id, '❌ خطأ في ارسال الملف')
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'back_main')
def back_main(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('📁 الملفات', callback_data='show_files', style='success'))
    markup.add(types.InlineKeyboardButton('👨‍💻 المطور', url=f'https://t.me/{DEVELOPER_USERNAME}', style='primary'))
    bot.edit_message_text('مرحباً بك في بوت الملفات', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('➕ اضافة ملف', callback_data='admin_add', style='primary'),
        types.InlineKeyboardButton('🗑 حذف ملف', callback_data='admin_del', style='danger')
    )
    markup.add(
        types.InlineKeyboardButton('🚫 حظر عضو', callback_data='admin_block', style='danger'),
        types.InlineKeyboardButton('✅ الغاء حظر', callback_data='admin_unblock', style='success')
    )
    markup.add(types.InlineKeyboardButton('📢 نشر للكل', callback_data='admin_broadcast', style='primary'))
    bot.send_message(message.chat.id, '🛡 لوحة الادمن:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    if call.data == 'admin_add':
        user_states[call.from_user.id] = {'step': 'add_name'}
        msg = bot.send_message(call.message.chat.id, '✏️ ارسل اسم الملف (للتخطي ارسل .)')
        bot.register_next_step_handler(msg, add_step_name)
    elif call.data == 'admin_del':
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT id, file_name FROM files')
        files = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not files:
            bot.answer_callback_query(call.id, 'لا توجد ملفات')
            return
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for fid, fname in files:
            markup.add(types.InlineKeyboardButton(f'🗑 {fname}', callback_data=f'delconfirm_{fid}', style='danger'))
        bot.send_message(call.message.chat.id, 'اختر ملف للحذف:', reply_markup=markup)
    elif call.data == 'admin_block':
        msg = bot.send_message(call.message.chat.id, 'ارسل ايدي العضو للحظر (للتخطي ارسل .)')
        bot.register_next_step_handler(msg, block_step)
    elif call.data == 'admin_unblock':
        msg = bot.send_message(call.message.chat.id, 'ارسل ايدي العضو لالغاء الحظر (للتخطي ارسل .)')
        bot.register_next_step_handler(msg, unblock_step)
    elif call.data == 'admin_broadcast':
        user_states[call.from_user.id] = {'step': 'broadcast'}
        msg = bot.send_message(call.message.chat.id, 'ارسل المنشور نص او ملف (للتخطي ارسل .)')
        bot.register_next_step_handler(msg, broadcast_step)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delconfirm_'))
def delete_file(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    fid = int(call.data.split('_')[1])
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM files WHERE id=?', (fid,))
    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(call.message.chat.id, '✅ تم حذف الملف')

def add_step_name(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == '.':
        bot.send_message(message.chat.id, '⏭ تم تخطي اضافة الملف')
        return
    
    user_states[message.from_user.id] = {'step': 'add_file', 'name': message.text}
    msg = bot.send_message(message.chat.id, '📎 ارسل الملف (للتخطي ارسل .)')
    bot.register_next_step_handler(msg, add_step_file)

def add_step_file(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == '.':
        bot.send_message(message.chat.id, '⏭ تم تخطي اضافة الملف')
        return
    
    data = user_states.get(message.from_user.id, {})
    
    if message.content_type == 'document':
        file_id = message.document.file_id
        file_type = 'document'
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_type = 'photo'
    elif message.content_type == 'video':
        file_id = message.video.file_id
        file_type = 'video'
    elif message.content_type == 'audio':
        file_id = message.audio.file_id
        file_type = 'audio'
    elif message.content_type == 'voice':
        file_id = message.voice.file_id
        file_type = 'voice'
    else:
        bot.send_message(message.chat.id, '❌ نوع غير مدعوم')
        return
    
    data['file_id'] = file_id
    data['file_type'] = file_type
    data['step'] = 'add_desc'
    user_states[message.from_user.id] = data
    msg = bot.send_message(message.chat.id, '📝 ارسل وصف الملف (للتخطي ارسل .)')
    bot.register_next_step_handler(msg, add_step_desc)

def add_step_desc(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = user_states.get(message.from_user.id, {})
    if message.text == '.':
        data['desc'] = None
    else:
        data['desc'] = message.text
    
    data['step'] = 'add_photo'
    user_states[message.from_user.id] = data
    msg = bot.send_message(message.chat.id, '🖼 ارسل صورة للملف (للتخطي ارسل .)')
    bot.register_next_step_handler(msg, add_step_photo)

def add_step_photo(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = user_states.get(message.from_user.id, {})
    if message.text == '.':
        photo_id = None
    elif message.content_type == 'photo':
        photo_id = message.photo[-1].file_id
    else:
        photo_id = None
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO files (file_name, file_id, file_type, description, photo_id) VALUES (?,?,?,?,?)',
                   (data['name'], data['file_id'], data['file_type'], data['desc'], photo_id))
    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, '✅ تمت اضافة الملف بنجاح')
    user_states.pop(message.from_user.id, None)

def block_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == '.':
        bot.send_message(message.chat.id, '⏭ تم التخطي')
        return
    
    try:
        uid = int(message.text)
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO blocked (user_id) VALUES (?)', (uid,))
        conn.commit()
        cursor.close()
        conn.close()
        bot.send_message(message.chat.id, '✅ تم الحظر')
    except:
        bot.send_message(message.chat.id, '❌ ايدي غير صحيح')

def unblock_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == '.':
        bot.send_message(message.chat.id, '⏭ تم التخطي')
        return
    
    try:
        uid = int(message.text)
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM blocked WHERE user_id=?', (uid,))
        conn.commit()
        cursor.close()
        conn.close()
        bot.send_message(message.chat.id, '✅ تم الغاء الحظر')
    except:
        bot.send_message(message.chat.id, '❌ ايدي غير صحيح')

def broadcast_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    count = 0
    for (uid,) in users:
        try:
            if message.content_type == 'text' and message.text == '.':
                break
            
            if message.content_type == 'photo':
                bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video':
                bot.send_video(uid, message.video.file_id, caption=message.caption)
            elif message.content_type == 'document':
                bot.send_document(uid, message.document.file_id, caption=message.caption)
            elif message.content_type == 'audio':
                bot.send_audio(uid, message.audio.file_id, caption=message.caption)
            elif message.content_type == 'voice':
                bot.send_voice(uid, message.voice.file_id, caption=message.caption)
            elif message.content_type == 'text':
                bot.send_message(uid, message.text)
            count += 1
        except:
            pass
    
    bot.send_message(message.chat.id, f'✅ تم النشر لـ {count} مستخدم')

@bot.message_handler(func=lambda m: True)
def check_msg(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM blocked WHERE user_id=?', (message.from_user.id,))
    blocked = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if blocked:
        return
    
    if not check_subscription(message.from_user.id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('📢 اشترك في القناة', url=f'https://t.me/{CHANNEL_USERNAME.replace("@", "")}', style='danger'))
        markup.add(types.InlineKeyboardButton('✅ تحقق من الاشتراك', callback_data='check_sub', style='success'))
        bot.send_message(message.chat.id, '⚠️ يجب الاشتراك في القناة لاستخدام البوت', reply_markup=markup)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('📁 الملفات', callback_data='show_files', style='success'))
    markup.add(types.InlineKeyboardButton('👨‍💻 المطور', url=f'https://t.me/{DEVELOPER_USERNAME}', style='primary'))
    bot.send_message(message.chat.id, 'استخدم الازرار للتصفح', reply_markup=markup)

bot.polling()
