import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Bot Token'ını buraya ekle
TOKEN = "8021040258:AAFqKJw93quyeKLRZ8B_Xb6pDj3yznrc-GE"
YONETICI_ID = 7745135815

# Motivasyon mesajları listesi
MOTIVASYON_MESAJLARI = [
    "Başarı, sabır ve azimle gelir!",
    "Bugün harika bir gün olacak, inan bana!",
    "Düşlerindeki hayatı yaşamak için bugün bir adım at!",
    "Sen çok güçlüsün, bunu unutma!",
    "Her gün yeni bir başlangıçtır!",
    "İmkansız diye bir şey yoktur, sadece zaman alır!",
    "Küçük adımlar, büyük değişimler yaratır.",
    "Ne olursa olsun, pes etme!",
    "En karanlık gecenin bile bir sabahı vardır.",
    "Bugün, geleceğinin ilk günü olabilir!",
    "Söylesene onca hayal kuruşumuz boşa mıydı?",
    "Kapat gözünü ve hayal et, hayal edebiliyorsan imkansız değildir.",
    "Seni nasıl gazlayayım istiyorsun hı? Bakma öyle bön bön çarpacam!",
    "🔥İmkansız, sadece denemeye cesaret edemeyenler için vardır!",
    "Bugün kötü geçti diye üzülme, hayat bir tiyatro ve sen başroldesin. Senaryo değişecek!",
    "Ramazan ayındayız, orucunu ihmal etme. Kurduğun cümlelere dikkat et ki hayırlı bir kul olarak yaşayabilesin.",
    "Bugün harika olmasa da sen harikasın! Bunu unutma. Küçük bir adım bile olsa ilerliyorsun. Devam et! 💛",
    "Çay bile sıcak suyun içinde bekleyerek demlenir. Şu anda zorlanıyorsan, belki de en güçlü hale ulaşmak üzeresin. ☕✨",
    "Kimse mükemmel değil, ama herkes gelişebilir. Sen de her gün biraz daha kendinin en iyi versiyonuna dönüyorsun! 🔥",
    "Belki de şu an, 'Keşke vazgeçseydim' diyeceğin değil, 'İyi ki devam etmişim' diyeceğin yerdesindir. Biraz daha dayan!",
    "Önce insan olmayı dene, sonra motivasyon iste.",
]

# Doğruluk ve Cesaret listeleri
DOGRULUK_SORULARI = [
    "Hayatındaki en büyük pişmanlığın nedir?",
    "Birine söylediğin en büyük yalan neydi?",
    "Hoşlandığın biri var mı? Kim?",
    "En utanç verici anın neydi?",
    "Kimseye söylemediğin bir sırrını paylaşır mısın?",
    "Bir günlüğüne biriyle hayatını değiştirme şansın olsa, kim olurdu?",
    "Şu an aklından geçen şey ne?",
    "Scrabble beyi ne kadar seviyorsun? Sevmiyorsan adaya veda et!",
    "En son ne zaman birini kıskandın ve neden?",
    "Hiç garip bir takıntın var mı?",
    "Sosyal medyada en çok kimi stalklıyorsun? Yapmıyorum deme, enayi değiliz ;)",
]

CESARET_GOREVLERI = [
    "En son mesaj attığın kişiye 'Seni seviyorum' yaz!",
    "Bulunduğun odada en yakınındaki objeyi kokla ve yorum yap!",
    "Bütün grup içinde en sevdiğin kişiyi açıkla!",
    "Telefonundaki son mesajı paylaş!",
    "Ağzına en fazla kaç parmağını sığdırabilirsin? Deneyip göster!",
    "Şu an en sevdiğin şarkıyı söyle!",
    "Biriyle 10 saniye boyunca göz göze bak!",
    "Sosyal medyada rastgele bir takipçine “Sence ben nasıl biriyim?” diye DM at!",
    "5 dakika içerisinde gruptaki herkesi toplayıp eylem başlatın.",
    
]

async def start(update: Update, context: CallbackContext):
    await update.message.reply_photo(
        photo="https://r.resimlink.com/Zs9VoYI.jpg",
        caption="Merhaba!💖 Ben eğlence botuyum. \n\nBeni başka gruplara ekleyerek daha fazla eğlenebilirsin!🧚‍♀️\n\n/help komutuna tıklayarak detaylı bilgi edinebilirsin."
    )

# Yardım komutu
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("📌 Komutlar:\n/start - Beni başlat\n/help - Nasıl çalıştığımı öğren\n/motivasyon - Rastgele motivasyon mesajı al\n/d - Doğruluk sorusu al\n/c - Cesaret görevi al")

# Rastgele motivasyon mesajı
async def motivasyon(update: Update, context: CallbackContext):
    mesaj = random.choice(MOTIVASYON_MESAJLARI)
    await update.message.reply_text(mesaj)

# Rastgele doğruluk sorusu
async def dogruluk(update: Update, context: CallbackContext):
    soru = random.choice(DOGRULUK_SORULARI)
    kullanici_ismi = update.message.from_user.first_name
    await update.message.reply_text(f"[{kullanici_ismi}](tg://user?id={update.message.from_user.id}), 🧐 Doğruluk Sorusu: {soru}", parse_mode='Markdown')

# Rastgele cesaret görevi
async def cesaret(update: Update, context: CallbackContext):
    gorev = random.choice(CESARET_GOREVLERI)
    kullanici_ismi = update.message.from_user.first_name
    await update.message.reply_text(f"[{kullanici_ismi}](tg://user?id={update.message.from_user.id}), 🔥 Cesaret Görevi: {gorev}", parse_mode='Markdown')

# Kullanıcı mesajlarına cevap verme
async def handle_message(update: Update, context: CallbackContext):
    mesaj = update.message.text.lower()
    if mesaj == "/d":
        await dogruluk(update, context)
    elif mesaj == "/c":
        await cesaret(update, context)

async def handle_message(update: Update, context: CallbackContext):
    mesaj = update.message.text.lower()
    chat_id = update.message.chat.id  # Mesajın geldiği grup ID'si
    kullanici_id = update.message.from_user.id
    kullanici_adi = update.message.from_user.username or "Yok"
    kullanici_ismi = update.message.from_user.full_name
      
    # Kullanıcı bilgilerini konsola yazdır
    print(f"[{chat_id}] {kullanici_ismi} (@{kullanici_adi}) - ID: {kullanici_id} ➝ {mesaj}")


    # Log dosyasına kaydet
    with open("kullanici_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{chat_id}] {kullanici_ismi} (@{kullanici_adi}) - ID: {kullanici_id} ➝ {mesaj}\n")

# Bot uygulaması
app = Application.builder().token(TOKEN).build()

# Komutları ekleyelim
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("motivasyon", motivasyon))
app.add_handler(CommandHandler("d", dogruluk))
app.add_handler(CommandHandler("c", cesaret))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Botu çalıştır
if __name__ == "__main__":
    app.run_polling(),


