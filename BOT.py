import discord
from discord.ext import commands
import logging
import asyncio
import random
from datetime import datetime
from googletrans import Translator, LANGUAGES

TOKEN = "sizin_discord_tokeniniz"
intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

start_time = datetime.utcnow()
translator = Translator()

@bot.event
async def on_ready():
    print(f'Bot olarak giriş yapıldı: {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!yardım"))

@bot.event
async def on_member_join(member):
    await member.guild.system_channel.send(f"{member.mention}, sunucumuza hoş geldiniz!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Bilinmeyen komut. `!yardım` komutu ile mevcut komutları görebilirsiniz.')
    else:
        await ctx.send(f"Komutta bir hata oluştu: {str(error)}")
        logging.error(f"Komut {ctx.command} sırasında hata: {str(error)}")

@bot.command()
async def oynat(ctx, url):
    try:
        if ctx.author.voice and ctx.author.voice.channel:
            kanal = ctx.author.voice.channel
            ses_istemci = discord.utils.get(bot.voice_clients, guild=ctx.guild) or await kanal.connect()

            if not ses_istemci.is_playing():
                ses_istemci.play(discord.FFmpegPCMAudio(url))
            else:
                await ctx.send("Zaten bir şarkı oynatılıyor!")
        else:
            await ctx.send("Ses kanalında olmalısınız!")
    except Exception as e:
        await ctx.send(f"Hata: {str(e)}")

@bot.command()
async def duraklat(ctx):
    ses_istemci = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ses_istemci and ses_istemci.is_playing():
        ses_istemci.pause()
        await ctx.send("Şarkı duraklatıldı.")
    else:
        await ctx.send("Şu anda oynatılan bir şarkı yok.")

@bot.command()
async def devam(ctx):
    ses_istemci = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ses_istemci and ses_istemci.is_paused():
        ses_istemci.resume()
        await ctx.send("Şarkıya devam ediliyor.")
    else:
        await ctx.send("Şu anda duraklatılmış bir şarkı yok.")

@bot.command()
async def dur(ctx):
    ses_istemci = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ses_istemci and (ses_istemci.is_playing() or ses_istemci.is_paused()):
        ses_istemci.stop()
        await ctx.send("Şarkı durduruldu.")
    else:
        await ctx.send("Şu anda oynatılan ya da duraklatılan bir şarkı yok.")

@bot.command()
async def cik(ctx):
    ses_istemci = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ses_istemci:
        await ses_istemci.disconnect()
        await ctx.send("Ses kanalından çıkıldı.")
    else:
        await ctx.send("Bot şu anda herhangi bir ses kanalında değil.")

@bot.command()
async def ceviri(ctx, dil, *, metin):
    if dil not in LANGUAGES:
        await ctx.send(f"Desteklenmeyen dil kodu. Lütfen geçerli bir dil kodu girin. Örnek diller: {', '.join(list(LANGUAGES.keys())[:5])}...")
        return
    
    try:
        translated_text = translator.translate(metin, dest=dil).text
        await ctx.send(translated_text)
    except Exception as e:
        await ctx.send(f"Çeviri yapılırken bir hata oluştu: {str(e)}")

@bot.command()
async def yardim(ctx):
    help_embed = discord.Embed(title="Bot Komutları", color=discord.Color.blue())
    commands_description = """
    `!oynat [url]` - Belirtilen URL'den bir şarkı oynatır.
    `!duraklat` - Oynatılan şarkıyı duraklatır.
    `!devam` - Duraklatılan şarkıyı devam ettirir.
    `!dur` - Oynatılan şarkıyı durdurur.
    `!at [@üye] [sebep]` - Belirtilen üyeyi sunucudan atar.
    `!yasakla [@üye] [sebep]` - Belirtilen üyeyi sunucudan yasaklar.
    `!uptime` - Botun çalışma süresini gösterir.
    `!sunucu` - Sunucu hakkında bilgi verir.
    `!avatar [@üye]` - Belirtilen üyenin avatarını gösterir.
    `!ping` - Botun ping değerini gösterir.
    `!davet` - Botun davet linkini gönderir.
    """
    help_embed.description = commands_description
    await ctx.send(embed=help_embed)

@bot.command()
async def sustur(ctx, üye: discord.Member, süre: int = None):
    if ctx.author.guild_permissions.manage_roles:
        susturulmuş_rolü = discord.utils.get(ctx.guild.roles, name="Susturulmuş")

        if not susturulmuş_rolü:
            susturulmuş_rolü = await ctx.guild.create_role(name="Susturulmuş")
            for kanal in ctx.guild.channels:
                if isinstance(kanal, discord.TextChannel):
                    await kanal.set_permissions(susturulmuş_rolü, send_messages=False)
                elif isinstance(kanal, discord.VoiceChannel):
                    await kanal.set_permissions(susturulmuş_rolü, speak=False)

        await üye.add_roles(susturulmuş_rolü)

        response = f'{üye.mention} kullanıcısı {ctx.author.mention} tarafından susturuldu.'
        if süre:
            await asyncio.sleep(süre * 60)
            await üye.remove_roles(susturulmuş_rolü)
            response += f" {süre} dakika sonra susturma kaldırıldı."
        
        await ctx.send(response)
    else:
        await ctx.send("Bu işlemi gerçekleştirmek için gerekli izinlere sahip değilsiniz.")

@bot.command()
async def rolyarat(ctx, rol_ismi, renk: discord.Colour = discord.Colour.default()):
    if ctx.author.guild_permissions.manage_roles:
        if discord.utils.get(ctx.guild.roles, name=rol_ismi):
            await ctx.send(f"'{rol_ismi}' isminde bir rol zaten var!")
            return
        
        await ctx.guild.create_role(name=rol_ismi, color=renk)
        await ctx.send(f"'{rol_ismi}' isminde yeni bir rol oluşturuldu!")
    else:
        await ctx.send("Bu işlemi gerçekleştirmek için gerekli izinlere sahip değilsiniz.")

@bot.command()
async def rolver(ctx, üye: discord.Member, *, rol_ismi):
    if ctx.author.guild_permissions.manage_roles:
        rol = discord.utils.get(ctx.guild.roles, name=rol_ismi)
        if not rol:
            await ctx.send(f"'{rol_ismi}' isminde bir rol bulunamadı!")
            return
        
        await üye.add_roles(rol)
        await ctx.send(f"{üye.mention} kullanıcısına '{rol_ismi}' rolü verildi!")
    else:
        await ctx.send("Bu işlemi gerçekleştirmek için gerekli izinlere sahip değilsiniz.")

@bot.command()
async def rolsil(ctx, *, rol_ismi):
    if ctx.author.guild_permissions.manage_roles:
        rol = discord.utils.get(ctx.guild.roles, name=rol_ismi)
        if not rol:
            await ctx.send(f"'{rol_ismi}' isminde bir rol bulunamadı!")
            return
        
        await rol.delete()
        await ctx.send(f"'{rol_ismi}' ismindeki rol silindi!")
    else:
        await ctx.send("Bu işlemi gerçekleştirmek için gerekli izinlere sahip değilsiniz.")

@bot.command()
async def kullanici_bilgisi(ctx, hedef_uye: discord.Member = None):
    hedef_uye = hedef_uye or ctx.author
    durum = str(hedef_uye.status).capitalize()
    roller = ", ".join([rol.name for rol in hedef_uye.roles])
    bilgi_mesaji = (
        f"Kullanıcı: {hedef_uye.display_name}\n"
        f"ID: {hedef_uye.id}\n"
        f"Durum: {durum}\n"
        f"Roller: {roller}\n"
        f"Katılma Tarihi: {hedef_uye.joined_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Hesap Oluşturulma Tarihi: {hedef_uye.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await ctx.send(bilgi_mesaji)

@bot.command()
async def sunucu_ayarlar(ctx):
    sunucu = ctx.guild
    kanal_sayısı = len(sunucu.channels)
    üye_sayısı = len(sunucu.members)
    sunucu_ayarlari = (
        f"Sunucu Adı: {sunucu.name}\n"
        f"Kanal Sayısı: {kanal_sayısı}\n"
        f"Üye Sayısı: {üye_sayısı}\n"
        f"Sunucu Bölgesi: {sunucu.region}\n"
        f"Oluşturulma Tarihi: {sunucu.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await ctx.send(sunucu_ayarlari)

@bot.command()
async def temizle(ctx, miktar: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=miktar + 1)
        await ctx.send(f"{miktar} mesaj temizlendi.", delete_after=5)
    else:
        await ctx.send("Bu işlemi gerçekleştirmek için gerekli izinlere sahip değilsiniz.")

@bot.command()
async def resim_gonder(ctx):
    resim_url = "resim_urlsi"
    await ctx.send(f"İşte bir resim: {resim_url}")

@bot.command()
async def cevapla(ctx, kullanici: discord.User, mesaj):
    await kullanici.send(f"{ctx.author.display_name} size şunu dedi: {mesaj}")

@bot.command()
async def zamanlayici_komut(ctx, zaman_saniye: int, *, komut):
    await asyncio.sleep(zaman_saniye)
    await ctx.send(f"Zaman geldi! Komut çalıştırılıyor: {komut}")
    await ctx.invoke(bot.get_command(komut))

@bot.command()
async def emoji(ctx):
    custom_emoji = "<:custom_emoji:emoji_id>"
    await ctx.send(f"Özel emoji kullanımı: {custom_emoji}")

@bot.command()
async def rastgele_renk(ctx):
    renk = discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    await ctx.send(f"Rastgele renk: {renk}")

@bot.command()
async def katil(ctx, kanal: discord.VoiceChannel):
    ses_istemci = await kanal.connect()
    await ctx.send(f"Ses kanalına katıldım: {kanal.name}")

@bot.command()
async def ayril(ctx):
    ses_istemci = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ses_istemci:
        await ses_istemci.disconnect()
        await ctx.send("Ses kanalından ayrıldım.")
    else:
        await ctx.send("Bot şu anda herhangi bir ses kanalında değil.")

@bot.command()
async def rastgele_sayi(ctx, min_sayi: int, max_sayi: int):
    rastgele_sayi = random.randint(min_sayi, max_sayi)
    await ctx.send(f"Rastgele sayı: {rastgele_sayi}")

@bot.command()
async def oylama(ctx, *, soru):
    oylama_mesaji = await ctx.send(f"Oylama: {soru}\n\n:thumbsup: - Evet\n\n:thumbsdown: - Hayır")
    await oylama_mesaji.add_reaction("👍")
    await oylama_mesaji.add_reaction("👎")

@bot.command()
async def hava_durumu(ctx, sehir):
    # Hava durumu API'sini kullanarak hava durumu bilgilerini alın
    # Örnek bir API kullanılabilir: https://openweathermap.org/api
    # API'den alınan bilgileri işleyin ve mesaj olarak gönderin
    hava_durumu_bilgisi = "Ankara için hava durumu: Sıcaklık 25°C, Hava durumu: Parçalı bulutlu"
    await ctx.send(hava_durumu_bilgisi)

@bot.command()
async def rastgele_saka(ctx):
    # Rastgele bir şaka API'sini kullanarak bir şaka alın
    # Örnek bir API kullanılabilir: https://icanhazdadjoke.com/api
    # API'den alınan şakayı mesaj olarak gönderin
    rastgele_saka = "Neden tavuklar yolun karşısına geçer? Bilmiyorum, neden?"
    await ctx.send(rastgele_saka)

@bot.command()
async def ters_cevir(ctx, *, metin):
    ters_metin = metin[::-1]
    await ctx.send(f"Ters çevrilmiş metin: {ters_metin}")

@bot.command()
async def anket(ctx, *sorular):
    anket_mesaji = "Anket:\n"
    for i, soru in enumerate(sorular, 1):
        anket_mesaji += f"{i}. {soru}\n"
    await ctx.send(anket_mesaji)

@bot.command()
async def rol_bilgisi(ctx, rol: discord.Role):
    # Belirtilen rolün bilgilerini alın ve mesaj olarak gönderin
    rol_bilgisi = f"Rol Adı: {rol.name}\nRol ID: {rol.id}\nRenk: {rol.color}"
    await ctx.send(rol_bilgisi)

@bot.command()
async def sunucu_istatistikleri(ctx):
    sunucu = ctx.guild
    üye_sayısı = len(sunucu.members)
    kanal_sayısı = len(sunucu.channels)
    sunucu_istatistikleri = (
        f"Sunucu Adı: {sunucu.name}\n"
        f"Üye Sayısı: {üye_sayısı}\n"
        f"Kanal Sayısı: {kanal_sayısı}\n"
        f"Sunucu Sahibi: {sunucu.owner.display_name}"
    )
    await ctx.send(sunucu_istatistikleri)

@bot.command()
async def dosya_oku(ctx, dosya_adı):
    # Belirtilen adıyla metin dosyasını okuyun ve içeriği mesaj olarak gönderin
    # Dosya adınıza uygun bir dosya okuma işlemi yapmalısınız
    dosya_icerigi = "Dosya içeriği burada."
    await ctx.send(dosya_icerigi)

@bot.command()
async def zamanlayici_mesaj(ctx, zaman_saniye: int, mesaj):
    await asyncio.sleep(zaman_saniye)
    await ctx.send(f"Zaman geldi! Mesaj gönderiliyor: {mesaj}")

bot.run(TOKEN)
