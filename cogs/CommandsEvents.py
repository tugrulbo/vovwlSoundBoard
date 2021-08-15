import os
from os import walk
import glob
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.utils import get
import datetime
import json
import discord
from discord.ext import commands
import youtube_dl as yt
import youtube_dl
import asyncio
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import time



url =""
admin_id = ["add user"]

ytdl_format_options = {
        'format': 'bestaudio[ext=webm]',
        'outtmpl': 'video1.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
    }

ffmpeg_options = {
        'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource():
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)


class CommandsEvents(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    async def convertToGif(self):
        trimmed_video = VideoFileClip("test.mp4")
        trimmed_video.write_gif("test.gif",fps=10)
    
    @commands.command(name='play')
    async def play(self,ctx):
      if ctx.message.content.startswith('.play'):
          channel = ctx.message.author.voice.channel
          author_id = ctx.message.author.id
          if(author_id == admin_id[0] or author_id == admin_id[1]):
            voice = get(self.bot.voice_clients, guild=ctx.guild)
            sound_name = ctx.message.content
            sound_name = sound_name.replace(".play","")
            sound_name = sound_name.strip()
            if os.path.isfile("sounds/{}.webm".format(sound_name)):
              
              if voice and voice.is_connected():
                 await voice.move_to(channel)
              else:
                 voice = await channel.connect()
                 print(f"Bağlanılan Kanal: {channel}\n")
    
              await ctx.send(f"{channel} Girildi")

              async with ctx.typing():
                  #player = await YTDLSource.from_url("sounds/{}.webm".format(sound_name), loop=self.bot.loop, stream=True)
                  #ctx.voice_client.play(player, after=lambda e: print('Oynatıcı Hatası: %s' % e) if e else None)
                  ctx.voice_client.play(discord.FFmpegPCMAudio(executable="/app/vendor/ffmpeg/ffmpeg", source="sounds/{}.webm".format(sound_name)))
              await ctx.send('Şuan oynatılıyor: {}'.format(sound_name))

            else:
                await ctx.send("Ses bulunamadi.")
          else:
              await ctx.send("Sadece yetkili ses oynatabilir.")
      else:
          await ctx.send("Böyle bir komut yok.( Tanımlama şekli: .play ses_ismi)")


    @commands.command(name="deleteSound")
    async def deleteSound(self,ctx):
         if ctx.message.content.startswith('.deleteSound'):
          sound_name = ctx.message.content
          author_id = ctx.message.author.id
          if(author_id == admin_id[0] or author_id == admin_id[1]):
            sound_name = sound_name.replace(".deleteSound","")
            sound_name = sound_name.strip()
            if os.path.isfile("sounds/{}.webm".format(sound_name)):
                os.remove("sounds/{}.webm".format(sound_name))
                await ctx.send("{} dosyası silindi.".format(sound_name))
            else:
                await ctx.send("Böyle bir dosya zaten yok")
          else:
             await ctx.send("Sadece yetkili ses silebilir.")
         else:
             await ctx.send("Böyle bir komut yok.( Tanımlama şekli: .deleteSound ses_ismi)")

    @commands.command(name="trimVideo")
    async def trimmedVideo(self, ctx):
        if ctx.message.content.startswith('.trimVideo'):
            message = ctx.message.content
            author_id = ctx.message.author.id
            if(author_id == admin_id[0] or author_id == admin_id[1]):
                replace_prefix = message.replace('.trimVideo',"")
                split_content = replace_prefix.split('|')
                print(split_content)
                url = split_content[0]
                url = url.strip()
                start_time = split_content[1]
                start_time = start_time.strip()
                end_time = split_content[2]
                end_time= end_time.strip()
                video_name = split_content[3]
                video_name = video_name.strip()
                async with ctx.typing():
                    await YTDLSource.from_url(url, stream=False)
            
                ffmpeg_extract_subclip("video1.webm", int(start_time), int(end_time), targetname="sounds/{}.webm".format(video_name))
                os.remove("video1.webm")

            else:
                await ctx.send("Sadece yetkili ses kesebilir.")
        else:
            await ctx.send("Böyle bir komut yok.( Tanımlama şekli: .trimVideo url | start_time(saniye) | end_time(saniye) | ses_ismi )")
                
    
    @commands.command(name="add")
    async def add(self, ctx):
        if ctx.message.content.startswith('.add'):
            message = ctx.message.content
            author_id = ctx.message.author.id
            if(author_id == admin_id[0] or author_id == admin_id[1]):
                replace_prefix = message.replace('.add',"")
                split_content = replace_prefix.split('|')
                print(split_content)
                url = split_content[0]
                url = url.strip()
                video_name = split_content[1]
                video_name = video_name.strip()
                async with ctx.typing():
                    await YTDLSource.from_url(url, stream=False)
                    
                os.rename("video1.webm","sounds/{}.webm".format(video_name))
            else:
                 await ctx.send("Sadece yetkili ses ekleyebilir.")
        else:
            await ctx.send("Böyle bir komut yok.( Tanımlama şekli: .add url | ses_ismi )")
        
            
    @commands.command(name="soundList")
    async def soundList(self,ctx):
        sound_name_list=[]
        #sound_list = glob.glob("sounds/*.webm")
        #await ctx.send(sound_list)
        _,_,filenames = next(walk("sounds/"))
        for i in range(len(filenames)):
            sound_name_list = filenames[i].replace(".webm","")
            await ctx.send("{}. ses: {}".format(i+1,sound_name_list))
        
        
    
def setup(bot):
    bot.add_cog(CommandsEvents(bot))
