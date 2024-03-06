# fileName: plugins/dm/callBack/inline_query/getpdf.py
# copyright ©️ 2021 nabilanavab
fileName = "plugins/dm/callBack/inline_query/getpdf.py"

import requests
from configs.log     import log
from plugins.work    import work
from logger          import logger
from bs4             import BeautifulSoup
from pyrogram        import Client as ILovePDF, filters
from pyrogram.types  import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument

async def pdf_drive(link):
    try:
        url = f"https://www.pdfdrive.com/{link}"
        
        firstPG = requests.get(url)
        firstSOUP = BeautifulSoup(firstPG.content, 'html.parser')
        code = firstSOUP.find("button", {"id":"previewButtonMain"})
        a = code.get_attribute_list("data-preview")[0]
        idHASH = a.replace("&", "=").split("=")
        return idHASH[1], idHASH[3]
        
    except Exception as e:
        logger.exception("🐞 %s: %s" %(fileName, e), exc_info = True)
        return False, False

async def download(name, download_link, bot, callbackQuery):
    try:
        response = requests.get(download_link, stream=True)
        total_size = int(response.headers.get("Content-Length", 0))
        block_size, current, percent = 1024, 0, 0
        cDIR = await work(callbackQuery, "check", False)
        if not cDIR:
            return await bot.edit_inline_reply_markup(
                inline_message_id = callbackQuery.inline_message_id,
                reply_markup = InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "♻️ TRY AGAIN ♻️",
                            callback_data = f"{callbackQuery.data}"
                        )
                    ]]
                ))
        path = f"{cDIR}/{name}"
        with open(path, "wb") as f:
            for data in response.iter_content(block_size):
                if not await work(callbackQuery, "check", False):
                    return False
                current = current + len(data)
                f.write(data)
                if int(current/total_size*10) > int(percent):
                    percent = int(current/total_size*10)
                    await bot.edit_inline_reply_markup(
                        inline_message_id = callbackQuery.inline_message_id,
                        reply_markup = InlineKeyboardMarkup(
                            [[
                                InlineKeyboardButton(
                                    "📥 تنزيل {:.2f}% 📥".format(
                                        current/total_size * 100
                                    ),
                                    callback_data = f"{callbackQuery.data}"
                                )
                            ],[
                                InlineKeyboardButton(
                                    "🗑️ الالغاء 🗑️",
                                    callback_data = f"c{callbackQuery.data[1:]}"
                                )
                            ]]
                        ))
        return path
    
    except Exception as e:
        logger.exception("🐞 %s: %s" %(fileName, e), exc_info=True)
        return False

pdfDRIVE = filters.create(lambda _, __, query: query.data.startswith("pD|"))
@ILovePDF.on_callback_query(pdfDRIVE)
async def pdfDriver(bot, callbackQuery):
    try:
        if not (callbackQuery.from_user.id == int(callbackQuery.data.split("|")[2])):
            return await callbackQuery.answer("رسالة ليست لك..")
        
        getMSG = await bot.get_messages(
            chat_id = int(log.LOG_CHANNEL),
            message_ids = int(callbackQuery.data.split("|")[1])
        )
        
        if getMSG.empty:
            return await callbackQuery.answer("طابور قديم..")
        
        if await work(callbackQuery, "check", False):
            return await callbackQuery.answer("يعمل الروبوت حاليا من أجلك..")
        await work(callbackQuery, "create", False)
        
        link = getMSG.caption.split("•")[1]
        id, hash = await pdf_drive(link)
        
        if not id or not hash:
            return await callbackQuery.answer("حدث خطأ ما..")
        await callbackQuery.answer("انتظر..")
        
        await bot.edit_inline_reply_markup(
            inline_message_id = callbackQuery.inline_message_id,
            reply_markup = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "تنزيل الان",
                        callback_data = f"{callbackQuery.data}"
                    )
                ],[
                    InlineKeyboardButton(
                        "🗑️ الالغاء 🗑️",
                        callback_data = f"c{callbackQuery.data[1:]}"
                    )
                ]]
            )
        )
        
        download_link = f"https://www.pdfdrive.com/download?id={id}&h={hash}&ext=pdf"
        
        telegram_can = True if float(getMSG.caption.split("¶")[1].split("·")[2].replace("MB", "")) < 20 else False

        if not telegram_can:
            name = link[1:60] + ".pdf"
            path = await download(name, download_link, bot, callbackQuery)
            if not path:
                return
            
            await bot.edit_inline_reply_markup(
                inline_message_id = callbackQuery.inline_message_id,
                reply_markup = InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "💁 تحميل 💁",
                            callback_data = f"{callbackQuery.data}"
                        )
                    ],[
                        InlineKeyboardButton(
                            "🗑️ الالغاء 🗑️",
                            callback_data = f"c{callbackQuery.data[1:]}"
                        )
                    ]]
                )
            )
        
        await bot.edit_inline_media(
            inline_message_id = callbackQuery.inline_message_id,
            media = InputMediaDocument(
                media = download_link if telegram_can else path,
                caption = getMSG.caption.split("°")[1]
            ),
            reply_markup = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        text = "♻️ ابحث مرة أخرى ♻️",
                        switch_inline_query_current_chat = ""
                    )
                ]]
            )
        )
        return await work(callbackQuery, "delete", False)
    
    except Exception as e:
        logger.exception("🐞 %s: %s" %(fileName, e), exc_info = True)
        await work(callbackQuery, "delete", False)


closeDRIVE = filters.create(lambda _, __, query: query.data.startswith("cD|"))
@ILovePDF.on_callback_query(closeDRIVE)
async def close(bot, callbackQuery):
    try:
        if not (callbackQuery.from_user.id == int(callbackQuery.data.split("|")[2])):
            return await callbackQuery.answer("رسالة ليست لك..")
        
        await callbackQuery.answer("🗑️")
        await work(callbackQuery, "delete", False)
    except Exception: pass
