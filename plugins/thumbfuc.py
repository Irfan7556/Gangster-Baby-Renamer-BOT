from pyrogram import Client, filters
from helper.database import db
import logging  # ✅ Added logging for debugging

# Enable debug logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # ✅ Change from INFO to DEBUG
)

@Client.on_message(filters.private & filters.command(['viewthumb']))
async def viewthumb(client, message):    
    user_id = message.from_user.id  # ✅ Fix callback handling
    thumb = await db.get_thumbnail(user_id)

    # ✅ Debugging Thumbnail Retrieval
    logging.debug(f"🧐 Debug - Retrieved thumbnail → {thumb}")

    if thumb:
       await client.send_photo(chat_id=message.chat.id, photo=thumb)
    else:
        await message.reply_text("😔**Sorry ! No thumbnail found...**😔") 
        logging.warning(f"⚠️ No thumbnail found for user {user_id}")

@Client.on_message(filters.private & filters.command(['delthumb']))
async def removethumb(client, message):
    user_id = message.from_user.id  # ✅ Fix callback handling
    await db.set_thumbnail(user_id, file_id=None)
    await message.reply_text("**Thumbnail deleted successfully**✅️")

    # ✅ Debugging Thumbnail Deletion
    logging.debug(f"🗑️ Debug - Thumbnail deleted for user {user_id}")

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    user_id = message.from_user.id  # ✅ Fix callback handling
    LazyDev = await message.reply_text("Please Wait ...")
    await db.set_thumbnail(user_id, file_id=message.photo.file_id)

    # ✅ Debugging Thumbnail Storage
    logging.debug(f"✅ Debug - Thumbnail saved for user {user_id}: {message.photo.file_id}")

    await LazyDev.edit("**Thumbnail saved successfully**✅️")
