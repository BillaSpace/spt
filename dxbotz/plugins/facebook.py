# Copyright (C) 2024 DX-MODS
#Licensed under the  AGPL-3.0 License;
#you may not use this file except in compliance with the License.
#Author ZIYAN
#if you use our codes try to donate here https://www.buymeacoffee.com/ziyankp

from pyrogram import filters, Client
import bs4, requests,re,asyncio
import wget,os,traceback
from dxbotz import Dxbotz
from config import BUG as LOG_GROUP, LOG_GROUP as DUMP_GROUP

@Dxbotz.on_message(filters.regex(r'https?://.*facebook[^\s]+') & filters.incoming,group=-6)
async def link_handler(Dxbotz, message):
    link = message.matches[0].group(0)
    try:
       m = await message.reply_text("⏳")
       get_api=requests.get(f"https://yasirapi.eu.org/fbdl?link={link}").json()
       if get_api['success'] == "false":
          return await message.reply("Invalid Facebook video url. Please try again :)")
       if get_api['success'] == "ok":
          if get_api.get('result').get('hd'):
             try:
                 dump_file = await message.reply_video(get_api['result']['hd'],caption="Thank you for using - @SpotifyDownlodbot")
             except KeyError:
                 pass 
             except Exception:
                 try:
                     sndmsg = await message.reply(get_api['result']['hd'])
                     await asyncio.sleep(1)
                     dump_file = await message.reply_video(get_api['result']['hd'],caption="Thank you for using - @SpotifyDownlodbot")
                     await sndmsg.delete()
                 except Exception:
                     try:
                        down_file = wget.download(get_api['result']['hd'])
                        await message.reply_video(down_file,caption="Thank you for using - @SpotifyDownlodbot")
                        await sndmsg.delete()
                        os.remove(down_file)
                     except:
                         return await message.reply("Oops Failed To Send File Instead Of Link")
          else: 
             if get_api.get('result').get('sd'):
               try:
                   dump_file = await message.reply_video(get_api['result']['sd'],caption="Thank you for using - @BillaDLbot")
               except KeyError:
                   pass
               except Exception:
                   try:
                       sndmsg = await message.reply(get_api['result']['sd'])
                       await asyncio.sleep(1)
                       dump_file = await message.reply_video(get_api['result']['sd'],caption="Thank you for using - @SpotifyDownlodbot")
                       await sndmsg.delete()
                   except Exception:
                      try:
                        down_file = wget.download(get_api['result']['sd'])
                        await message.reply_video(down_file,caption="Thank you for using - @SpotifyDownlodbot")
                        await sndmsg.delete()
                        os.remove(down_file)
                      except:
                         return await message.reply("Oops Failed To Send File Instead Of Link")
    except Exception as e:
           if LOG_GROUP:
               await Dxbotz.send_message(LOG_GROUP,f"Facebook {e} {link}")
               await Dxbotz.send_message(LOG_GROUP, traceback.format_exc())          
    finally:
          if 'dump_file' in locals():
            if DUMP_GROUP:
               await dump_file.copy(DUMP_GROUP)
          await m.delete()     
