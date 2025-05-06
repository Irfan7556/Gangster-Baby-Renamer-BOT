from helper.utils import progress_for_pyrogram, convert
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.database import db
import os
import humanize
from PIL import Image
import time
import logging  # ✅ Added logging for debugging

# Enable debug logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # ✅ Change from INFO to DEBUG
)

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    type = update.data.split("_")[1]
    new_name = update.message.text
    new_filename = new_name.split(":-")[1]
    file_path = f"downloads/{new_filename}"
    file = update.message.reply_to_message

    # Debug: Checking file path before download
    logging.debug(f"🧐 Debug - Expected File Path: {file_path}")

    ms = await update.message.edit("⚠️ Please wait... Downloading file to my server...")
    c_time = time.time()
    
    try:
        path = await bot.download_media(
            message=file, 
            progress=progress_for_pyrogram,
            progress_args=("⚠️ Please wait...\nDownloading file...", ms, c_time)
        )
    except Exception as e:
        await ms.edit(f"❌ Error during download: {e}")
        logging.error(f"❌ Download failed: {e}")
        return
    
    # Debug: Confirming downloaded file path
    logging.debug(f"🧐 Debug - Downloaded File Path: {path}")
    
    splitpath = path.split("/downloads/")
    dow_file_name = splitpath[1]
    old_file_name = f"downloads/{dow_file_name}"
    
    os.rename(old_file_name, file_path)
    
    # Debug: Checking renamed file path
    logging.debug(f"🧐 Debug - Renamed File Path: {file_path}")
    
    if not os.path.exists(file_path):
        await ms.edit("⚠️ Error: File was not saved properly!")
        logging.error(f"❌ File missing after renaming: {file_path}")
        return

    duration = 0
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata and metadata.has("duration"):
            duration = metadata.get("duration").seconds
    except Exception as e:
        logging.warning(f"⚠️ Metadata extraction failed: {e}")

    user_id = int(update.message.chat.id)
    ph_path = None
    media = getattr(file, file.media.value)

    # ✅ Debugging Caption & Thumbnail Retrieval
    c_caption = await db.get_caption(update.message.chat.id)
    c_thumb = await db.get_thumbnail(update.message.chat.id)
    
    logging.debug(f"🧐 Debug - Retrieved Caption: {c_caption}")
    logging.debug(f"🧐 Debug - Retrieved Thumbnail: {c_thumb}")

    if c_caption:
        try:
            caption = c_caption.format(
                filename=new_filename, 
                filesize=humanize.naturalsize(media.file_size), 
                duration=convert(duration)
            )
        except Exception as e:
            await ms.edit(f"❌ Caption Error: {e}")
            logging.error(f"❌ Caption formatting failed: {e}")
            return
    else:
        caption = f"**{new_filename}**"

    if media.thumbs or c_thumb:
        if c_thumb:
            ph_path = await bot.download_media(c_thumb)
        else:
            ph_path = await bot.download_media(media.thumbs[0].file_id)

        Image.open(ph_path).convert("RGB").save(ph_path)
        img = Image.open(ph_path)
        img.resize((320, 320))
        img.save(ph_path, "JPEG")

    await ms.edit("⚠️ Processing file upload....")
    c_time = time.time()

    try:
        if type == "document":
            await bot.send_document(
                update.message.chat.id,
                document=file_path,
                thumb=ph_path,
                caption=caption,
                progress=progress_for_pyrogram,
                progress_args=("⚠️ Processing file upload....", ms, c_time)
            )
        elif type == "video":
            await bot.send_video(
                update.message.chat.id,
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("⚠️ Processing file upload....", ms, c_time)
            )
        elif type == "audio":
            await bot.send_audio(
                update.message.chat.id,
                audio=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("⚠️ Processing file upload....", ms, c_time)
            )
    except Exception as e:
        await ms.edit(f"❌ Upload Failed: {e}")
        logging.error(f"❌ Upload error: {e}")
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)
        return

    await ms.delete()
    os.remove(file_path)
    if ph_path:
        os.remove(ph_path)

    # ✅ Debug: Upload Successful
    logging.info(f"✅ File successfully uploaded: {file_path}")
