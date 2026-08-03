import os
import random
import asyncio
import logging
import json
import time

from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from weather import hd, weather_callback
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,  
    filters,
    ContextTypes
)

load_dotenv()

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Zuzu Bot Aktif!"

def run():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


LOG_CHANNEL_CHAT = -1003910477471
TOKEN = os.getenv("TOKEN")
COOLDOWN_SECONDS = 0.7
BOT_USERNAME = "zuzufunbot"              
SUPPORT_GROUP_URL = "https://t.me/zuzudestek"  
DUYURU_CHANNEL_URL = "https://t.me/zuzuduyuru" 
MY_PROFILE_URL = "https://t.me/heyzzil"  

user_cooldowns = {}
grup_ayarlari = {}



def save_json(filename, data):
    try:
        tmp_file = filename + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_file, filename)
    except Exception as e:
        logger.error(f"{filename} kaydetme hatası: {e}")

def is_spam(user_id):
   
    now = time.time()
    if user_id in user_cooldowns:
        last_time = user_cooldowns[user_id]
        if now - last_time < COOLDOWN_SECONDS:
            return True 
    user_cooldowns[user_id] = now
    return False


async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.effective_chat.type == "private":
        return True
    user_id = update.effective_user.id
    chat_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
    return chat_member.status in ["creator", "administrator"]


async def user_reply(message, user, text):
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    full_text = f"{mention} {text}"
    await message.reply_text(text=full_text, parse_mode="Markdown")


DOGRULUK = [
    "Çok başarılı ama yalnız bir hayat mı, sıradan ama seni gerçekten seven insanlarla dolu bir hayat mı?",
    "En son kime mesaj attın?",
    "Çevrendeki insanlara her şey yolundaymış gibi davranırken, içten içe 'Ben bu hayatı yönetmeyi beceremiyorum, herkes benden daha başarılı' diye düşündüğün bir dönem oldu mu?",
    "Bugün en çok kimi düşündün?",
    "Hayvanlarla konuşabilsen ilk hangi hayvana ne sorardın?",
    "Bir daha asla hata yapmayacağın ama hiçbir şey öğrenemeyeceğin bir hayat mı, yoksa bol hata yapıp sürekli gelişeceğin bir hayat mı?",
    "Şu an gruptan en çok kimi merak ediyorsun?",
    "Birinin sana söylediği, söyleyen kişinin muhtemelen unuttuğu ama senin hala dün gibi hatırladığın ve içini sızlatan o tek cümle nedir?",
    "İnsanların senden beklediği biri mi oldun, yoksa olmak istediğin biri mi?",
    "Geçmişini değiştirme şansın olsa ama bugünkü kişiliğini kaybedecek olsan kabul eder miydin?",
    "Hiç gruptan birine gizlice sinir oldun mu?",
    "Birine çok büyük bir iyilik yapacaksın ama bunu asla öğrenmeyecek. Yine de yapar mıydın?",
    "Hayatında yaptığın şeyleri gerçekten kendin istediğin için mi yapıyorsun, yoksa ailenden veya çevrenden 'Aferin, başardın' onayını duymak için mi çabalıyorsun?",
    "İnsanların seni yanlış anlamasına neden olan en büyük özelliğin ne?",
    "Şu an birine sinirli misin? Sinirliysen kime?",
    "En son kime bakıp 'vay be' dedin?",
    "Telefonunda gizli albüm var mı?",
    "Hayatının hangi dönemine gidip, oradaki zamanı sonsuza kadar dondurmak ve o yaşta/o ruh halinde kalmak isterdin?",
    "Son 24 saatte yalan söylediğin bir şey var mı?",
    "Bugün 10 yaşındaki halin karşına çıksa, senden gurur duyar mıydı?",
    "Çok büyük bir finansal kazanç veya kariyer fırsatı için, şu an hayatında çok önemli olan bir insanla bağlarını tamamen koparmayı göze alır mıydın?",
    "Grupta en “cool” bulduğun kişi kim?",
    "Seni herkes çok sevecek ama kimse gerçekten tanımayacak; yoksa seni az kişi sevecek ama seni tamamen tanıyacaklar mı?",
    "En utanç verici anını anlatmak zorunda olsan ne olurdu?",
    "Sana dünyanın en mutlu insanı olacağın garanti edilse ama bunun için bugünkü tüm anılarını silmen gerekse kabul eder misin?",
    "Hiç stalk yaptığın biri var mı? Kim?",
    "Her istediğini başaracağın ama hiçbir başarından mutlu olamayacağın bir hayatı kabul eder miydin?",
    "Bu grupta sevgili yapmak istesen kimi seçerdin?",
    "Çevrendeki herkesin seni onayladığı ama senin içten içe 'Beni alkışlıyorsunuz ama hiçbiriniz beni gerçekten anlamıyorsunuz' diye hissettiğin bir dönem oldu mu?",
    "En son kimi kıskandın ve neden?",
    "Şu an gruptan birini susturma hakkın olsa kim olurdu?",
    "Bir hata yüzünden bütün insanlar seni suçlayacak ama aslında masum olacaksın. Gerçeği kanıtlayamayacağını bilsen yine de susar mıydın?",
    "Bir kişiyi ömür boyu mutlu edebilirsin ama bunun karşılığında seni herkes yanlış tanıyacak. Kabul eder misin?",
    "En fake bulduğun kişi kim? (şaka amaçlı 😄)",
    "Sonsuza kadar genç kalmak mı, yoksa normal yaşlanıp sevdiklerinle aynı zamanı paylaşmak mı?",
    "Burada “en deli” kişi kim sence?",
    "Hayatında sadece bir kişiyi tamamen mutlu edebilirsin. Kendini mi seçerdin, başkasını mı?",
    "Eğer yarın bu dünyadan ayrılacağını bilsen ve sadece tek bir kişiye son bir mesaj gönderme hakkın olsa, o mesajı kime atardın ve içine ne yazardın?",
    "Kim bu grupta en çok drama çıkarıyor?",
    "Çok sevdiğin biri seni unutacak ama mutlu olacak. Onun seni hatırlayıp mutsuz olmasını mı, yoksa seni unutup mutlu olmasını mı isterdin?",
    "Kendinde en çok sevmediğin ama değiştirmeye cesaret edemediğin şey ne?",
    "Kendine en çok yalan söylediğin konu ne?",
    "İnsanların sana her zaman doğruyu söylemesi mi, yoksa seni hiç incitmemeleri mi?",
    "Bir günlüğüne geleceğini görmek mi isterdin, yoksa geçmişindeki bütün gerçekleri öğrenmek mi?",
    "Gerçekte olduğun kişiyle olmak istediğin kişi arasında ne fark var?",
    "Bir arkadaşını kurtarmak için hayatının en büyük hayalinden vazgeçer miydin?",
    "Hayatında sadece bir kişiye tüm sırlarını anlatabileceksin. O kişi seni terk ederse bütün sırların ortaya çıkacak. Yine de anlatır mıydın?",
    "Bir ilişkiyi bitiren en büyük sebep sence yalan mı, ilgisizlik mi? Bunu yaşadın mı?",
    "Seni en çok sen yapan şey sence ne?",
    "Son zamanlarda kendin hakkında fark ettiğin bir gerçek var mı?",
    "Hayatında hiç üzülmeyeceksin ama hiçbir şeye de gerçekten bağlanamayacaksın. Bunu ister miydin?",
    "En son ne zaman gerçekten “iyi hissettim” dedin?",
    "İçinde tuttuğun ama kimseye söylemediğin bir düşünce var mı?",
    "Bir insanın hayatını kurtaracaksın ama bunun bedeli olarak en yakın arkadaşını kaybedeceksin. Ne yapardın?",
    "Seni en çok ne yorar: insanlar mı, düşüncelerin mi?",
    "Bir şeyi asla unutamayacağını düşündüğün bir an var mı?",
    "Sana 100 bin TL verseler rehberindeki hangi kişiyi aramaya cesaret edemezdin?",
    "Telefonunda silmeye korktuğun ama kimsenin görmesini istemediğin şey ne?",
    "Hiç birini stalklarken yanlışlıkla fotoğrafını beğendin mi?",
    "Hayatında attığın en pişmanlık dolu mesaj neydi?",
    "Bir arkadaşını 24 saat susturma hakkın olsa kimi sustururdun?",
    "Şu an gruptan biri senin yerine telefonunu kullansa en çok neden utanırdın?",
    "En son kimin profilinde gereğinden fazla dolaştın?",
    "Eski sevgilin sana 'özledim' yazsa ilk tepkin ne olurdu?",
    "Şu an rehberinden bir kişiyi sonsuza kadar silmen gerekse kim olurdu?",
    "Hiç sırf meraktan fake hesap açıp birini izledin mi?",
    "Bir gün boyunca sadece dürüst olsan başına en büyük bela ne açılırdı?",
    "Hayatındaki en büyük 'iyi ki kimse öğrenmedi' olayı ne?",
    "Sonsuza kadar yaşayacaksın ama sevdiğin herkes senden önce ölecek. Kabul eder miydin?",
    "Sessiz kaldığında aklına en çok ne geliyor?",
    "Geçmişini tamamen unutup sıfırdan başlamak mı, tüm hatalarınla yaşamaya devam etmek mi?",
    "Bir insana güvenmen için ne olması gerekir?",
    "Hiç “hak etmiyor ama seviyorum” dediğin biri oldu mu?",
    "Şu an gruptan biriyle kahve içecek olsan kimi seçerdin?",
    "İlk görüşte aşk mı, zamanla aşk mı?",
    "En son hoşlandığın kişiyi ne zaman düşündün?",
    "Bir gün boyunca burnundan makarna çıksa mı yoksa kulaklarından ketçap aksa mı?",
    "Sana 1 milyon TL verseler telefonunu 24 saat annene verir misin?",
    "Hayatın boyunca tek bir emoji kullanacak olsan hangisi olurdu?",
    "Mesajı hemen mi açarsın yoksa bekletir misin?",
    "İlk adımı atar mısın, karşı taraftan mı beklersin?",
    "Birinin seni etkilemesi için ilk neye dikkat edersin?",
    "Eski sevgiline tekrar şans verir miydin?",
    "En çekici bulduğun özellik nedir?",
    "Bugüne kadar aldığın en tatlı iltifat neydi?",
    "Bir dinozor evcil hayvanın olsa adını ne koyardın?",
    "Şu an biriyle sevgili olmak zorunda olsan gruptan kimi seçerdin?",
    "Hoşlandığın biri sana yazsa şu an ne yaparsın?",
    "Sevdiğin kişi seni unutacak ama çok mutlu olacak. Yoksa seni hatırlayacak ama mutsuz olacak. Hangisini seçerdin?",
    "İnsanları hızlı mı yargılıyorsun yoksa şans mı verirsin?",
    "Birini gerçekten sevdiğini nasıl anlarsın?",
    "Sence gerçek dostluk nedir?",
    "Çok zengin olacaksın ama kimse seni yaptıkların için değil, paran için sevecek. Kabul eder miydin?",
    "Seni en çok hayal kırıklığına uğratan şey insanlar mı beklentilerin mi?",
    "Keşke geri dönüp değiştirebilseydim dediğin bir an var mı?",
    "Bir günlüğüne görünmez olmak mı, bir günlüğüne herkesin aklını okumak mı?",
    "Geçmişin seni mi şekillendirdi yoksa seni mi kırdı?",
    "Mesajına geç cevap veren biri seni sinirlendirir mi?",
    "5 yıl önceki halin seni görse ne derdi?",
    "Hiç bir arkadaşını yanlış tanıdığını fark ettin mi?",
    "Hiç 'keşke yazsaydım' dediğin biri oldu mu?",
    "Bir daha hiç yalan duymayacaksın ama bütün gerçekler canını yakacak. Kabul eder miydin?",
    "Gelecekteki sen bugünkü haline ne söylerdi?",
    "Hayatında “o an her şey değişti” dediğin bir an var mı?",
    "Bir arkadaşını kardeşin gibi görüyorsan kim?",
    "Birini kurtarmak için bütün başarılarını kaybetmen gerekse kabul eder miydin?",
    "Mutluluk sence bir hedef mi yoksa alışkanlık mı?",
    "Kendinle yalnız kalmak sana iyi mi geliyor yoksa rahatsız mı ediyor?",
    "Hiç kimse seni unutmayacak ama kimse seni özlemeyecek. Bunu ister miydin?",
    "İnsanlar gerçekten değişir mi yoksa sadece maskelerini mi değiştirir?",
    "Sana '5 yıl sonra hayatın mükemmel olacak.' deseler ama o güne kadar çok zorlanacağını bilsen sabreder miydin?",
    "Hayatta en çok neyi anlamaya çalışıyorsun?",
    "Hiç reddedilmeyeceğin ama hiç âşık da olamayacağın bir hayat mı?",
    "Sence “kendin olmak” ne demek?",
    "Seni herkes doğru anlayacak ama kimse seni gerçekten merak etmeyecek. Kabul eder miydin?",
    "En büyük pişmanlığın ne?",
    "Hayatındaki herkes sana bir kez tamamen dürüst olacak. Duymaya cesaret eder miydin?",
    "En son kimi stalkladın?",
    "Hiç kimseye söylemediğin bir sır var mı?",
    "Bütün sorularının cevabını öğrenmek mi, hayatın boyunca hiç pişman olmamak mı?",
    "Şu an hoşlandığın biri var mı?",
    "Hayatındaki en utanç verici an neydi?",
    "İnsanların senin hakkındaki en büyük yanılgısı nedir ve bu yanlış algının devam etmesine neden izin veriyorsun?",
    "Birine söylemen gereken ama henüz zamanı değil diyerek sürekli ertelediğin o en ağır veya en önemli cümle nedir?",
    "Çok yakın bir dostunun, aslında onun iyiliği için olan ama onun asla öğrenmemesi gereken bir sırrını, dostluğunu kaybetme pahasına başkasına anlatır mıydın?",
    "Kendi mutluluğun ya da huzurun için, bir başkasının mutsuz olmasına bilerek göz yumduğun bir an oldu mu?",
    "Eğer hayatın bir film olsaydı, izleyiciler senin hikayenin kahramanı mı yoksa başkasının hikayesindeki yan karakter mi olduğunu düşünürdü? Neden?",
    "Son 2-3 yıl içinde karakterinde, fikirlerinde veya hayata bakışında yaşadığın en büyük, en radikal değişim ne oldu? Seni bu değişime tam olarak ne zorladı?",
    "En son ne zaman kendini çok yalnız hissettin ve o an seni en çok ne teselli etti?",
    "Eğer bir gün boyunca tamamen görünmez olsaydın ve yaptığın hiçbir şeyin yasal ya da ahlaki bir sonucu olmasaydı, yapacağın ilk bencilce şey ne olurdu?",
    "Sırf yalnız kalmamak veya bir gruba, bir çevreye ait hissetmek için normalde asla onaylamayacağın bir şeye göz yumduğun oldu mu?",
    "Bu gruptaki insanlardan birine en büyük sırrını emanet etmek zorunda kalsaydın, bunu en çok kime güvenerek yapardın, kime ise asla anlatmazdın?",
    "İnsanlara gösterdiğin o güçlü, neşeli veya umursamaz maskenin arkasında, aslında tek başına kaldığında seni en çok ağlatan ya da korkutan şey ne?",
    "Hayatında birine karşı çok büyük bir haksızlık yaptığını, o kişinin tamamen haklı olduğunu bildiğin ama gururundan dolayı asla gidip özür dilemediğin bir durum var mı?",
    "Sevdiğin bir insanı mutlu etmek için bugüne kadar kendinden en büyük neyi ödün verdin? Buna değdi mi?",
    "Sana göre dost ile arkadaş arasındaki en büyük fark nedir?",
    "Sence uzun yıllar süren arkadaşlıkların sırrı nedir?",
    "Arkadaşlıkta kıskançlık normal mi?",
    "Hiç bir arkadaşını ikinci kez tanıma şansın olsa yine arkadaş olur muydun?",
    "Bir arkadaşın zor durumda olsa onun için nelerden vazgeçebilirsin?",
    "Bir arkadaşının seni gerçekten tanıdığını düşünüyor musun?",
    "Arkadaşlıkta güven mi sadakat mi daha önemlidir?",
    "Hiç arkadaşına söyleyemediğin bir şey oldu mu?",
    "Sence bir arkadaşını tamamen tanımak mümkün mü?",
    "İyi bir arkadaş sence hangi özelliklere sahip olmalı?",
    "Arkadaşlıkta en çok kırıldığın davranış ne olur?",
    "Bir arkadaşın seni eleştirirse bunu nasıl karşılarsın?",
    "Sence arkadaşlık zamanla mı oluşur yoksa ilk andan belli olur mu?",
    "Arkadaşlıkta fedakârlığın bir sınırı olmalı mı?",
    "Hiç seni kıskandığını düşündüğün bir arkadaşın oldu mu?",
    "Bir arkadaşın senden yardım istese, ne olursa olsun yardım eder misin?",
    "Arkadaşlıkta sessizlik mi, açık konuşmak mı daha değerlidir?",
    "Bir arkadaşının başarısını görünce gerçekten mutlu olur musun?",
    "Sence insanlar en çok neden yalnız kalır?",
    "Bir arkadaşını affetmekte en çok zorlanacağın şey ne olurdu?",
    "Sence insanlar neden arkadaşlarını kaybeder?",
    "Hiç arkadaşın için gözyaşı döktün mü?",
    "Bir arkadaşın seni hayal kırıklığına uğrattı mı?",
    "Arkadaşlıkta gurur mu daha önemlidir, özür dilemek mi?",
    "Bir arkadaşının sırrını sonsuza kadar saklayabilir misin?",
    "Hiç arkadaşın tarafından dışlandığını hissettin mi?",
    "En yakın arkadaşın seni üç kelimeyle nasıl anlatırdı?",
    "Sence arkadaşlık mesafeyle biter mi?"
    "Birinin seni yıllardır yanlış tanıdığını öğrensen, onu düzeltmek için uğraşır mıydın yoksa öyle kalmasını mı isterdin?",
    "Kendin hakkında değiştirebileceğin tek bir özellik olsaydı, karakterini mi değiştirirdin yoksa dış görünüşünü mü? Neden?",
    "Hiç sırf birini üzmemek için mutluymuş gibi davrandığın oldu mu? Bu sana ne hissettirdi?",
    "Sana ait bütün anılar silinecek ama tek bir anıyı sonsuza kadar saklayabileceksin. Hangisini seçersin?",
    "Arkadaş grubundaki herkes seni dürüstçe puanlasa, en düşük puanı hangi konuda alacağını düşünüyorsun?",
    "Bugün burada bulunan kişilerden biri seni arkanı dönünce sürekli eleştiriyor olsa, bunun kim olabileceğini düşünürdün? Neden?",
    "İnsanların seni övdüğü ama senin aslında kendinde hiç görmediğin bir özellik var mı?",
    "Şu an burada bulunan herkes seni tamamen dürüstçe değerlendirse, sence en çok hangi yönünü eleştirirlerdi?",
    ""
]

CESARET = [

    "Şu anki ruh halini tek bir emoji ile anlat 💛",
    "Bir dakika boyunca sadece emoji kullanarak konuş.",
    "En son dinlediğin şarkıyı yaz 🎧",
    "3 saniye içinde aklına gelen ilk kelimeyi söyle 🌼",
    "Kendine bugün bir iltifat yap 💬",
    "Grupta en çok güvendiğin kişiyi söyle 🌙",
    "Şu an aklından geçen ilk şeyi dürüstçe yaz ✨",
    "Bir kişiyi sadece 1 kelimeyle tanımla 💭",
    "Kendini 30 saniye boyunca bir reklam spikeri gibi öv. 🎤",
    "Kendinle ilgili kimsenin bilmediği bir özelliği söyle 🌼",
    "Bir dakika boyunca sadece GIF veya emoji ile cevap ver.",
    "Bugün pişman olduğun bir şeyi paylaş 💔",
    "İsmin yerine herkes sana yeni bir lakap bulsun, 10 dakika onu kullan.",
    "En son utandığın anı kısaca anlat 🌷",
    "Beş kelimeyle korku hikayesi yaz. 👻",
    "Bir kişiye gizli bir iltifat yap 💌",
    "En çok özlediğin kişiyi yaz 💭",
    "Bugün kim seni mutlu ettiyse söyle 🌸",
    "Bir kapıyı şiir yazar gibi öv.",
    "Şu anki ruh halini 1 cümleyle anlat 🌙",
    "En sevdiğin emojiyle kendini tanıt 💫",
    "Son düşündüğün şeyi yaz ✨",
    "Klavyendeki otomatik önerilerle bir cümle oluştur ve paylaş.",
    "Telefonundaki son fotoğrafın konusunu söyle 📸",
    "Bir çizgi film karakteri gibi 1 dakika konuş. 🎤",
    "Bugün seni en çok ne güldürdü yaz 🌼",
    "Kimseye söylemediğin bir düşünceni paylaş ✨",
    "Gruptaki 3 kişiyi tek kelimeyle tanımla.",
    "Kendinde değiştirmek istediğin bir şey nedir? 🌿",
    "Bir dakika boyunca kendi kendini eleştir.",
    "Son zamanlarda seni değiştiren bir olay yaz 💭",
    "Birine içinden geçen ama söylemediğin bir şeyi yaz 🤍",
    "Kendini satılık bir ürünmüş gibi tanıt.", 
    "En çok özlediğin anı yaz 💭",
    "Hayatında seni en çok etkileyen kişi kim? 🌿",
    "Kendinle ilgili en gurur duyduğun şey ne? 💛",
    "Bugün kendine ne söylemek isterdin? ✨",
    "Bir şeyi yeniden yaşama şansın olsa ne olurdu? 🌙",
    "Aynaya bakıp kendine iltifat et.",
    "Şu an sevdiğin şarkıyı söyle 🎤",
    "Son konuştuğun kişiye 'seni özledim' yaz 😈",
    "5 saniye boyunca garip bir ses çıkar 😂"

]

SOZ = [

    "🤍 Her gün aynı kişi olmak zorunda değilsin, yavaş yavaş değişmen de yeter.",
    "🤍 Kendini anlamaya çalışmak bile bir ilerlemedir.",
    "🤍 Herkesin temposu farklı, sen kendi yolunda gecikmiş değilsin.",
    "🤍 Bugün hissettiklerin kalıcı değil, ama seni şekillendirebilir.",
    "🤍 Kendine karşı biraz daha sabırlı olman bile büyük bir başlangıçtır.",
    "🤍 Bazen çözüm bulmak değil, sadece devam etmek gerekir.",
    "🤍 İçinde sessizlik varsa, bu bazen kaybolduğun anlamına gelmez.",
    "🤍 Her şeyi aynı anda anlamak zorunda değilsin.",
    "🤍 Bazı duygular cevap istemez, sadece hissedilmek ister.",
    "🤍 Zorlanmak, yanlış yolda olduğunu değil; büyüdüğünü gösterir.",
    "🤍 Hayat net bir harita değil, yürüdükçe oluşan bir yol.",
    "🤍 Her şey hemen anlamlı olmak zorunda değil.",
    "🤍 Bugün anlamadığın şey, yarın yolunun bir parçası olabilir.",
    "🤍 Bazı insanlar hayatına bir ömür kalmak için değil, sana kendini hatırlatıp gitmek için girer. Onlar gittikten sonra eksilen kişi onlar değil, eski sen olursun.",
    "🤍 Bir insanın gerçek değeri, mutlu günlerinde yanında olanlarla değil; en sessiz zamanlarında kapısını çalmaya devam edenlerle anlaşılır.",
    "🤍 Herkes bir gün unutulur derler. Oysa unutulmayan insanlar vardır; çünkü bazıları hatıra olmaz, insanın karakterine karışır.",
    "🤍 Bazen uzun uzun konuşmak hiçbir şeyi değiştirmez. Doğru insan, sustuğunda bile içinde kopan fırtınayı anlayabilendir.",
    "🤍 En derin yaralar, düşmanlardan değil; en çok güvendiklerinden gelir. Çünkü yabancılar hayal kırıklığı yaratamaz.",
    "🤍 İnsan zamanla herkesi affedebilir. Ama kendini affetmek, bazen bütün bir ömür sürer.",
    "🤍 Bir kalbin yorulduğunu anlamak için ağlamasını bekleme. Bazı insanlar gülümserken de sessizce tükenir.",
    "🤍 Hayat bazen sana istediğini vermez. Çünkü hak ettiğin şey, istediğinden çok daha farklı bir yerde seni bekliyordur.",
    "🤍 En güzel vedalar bile biraz hüzün taşır. Çünkü gerçekten değer verilen hiçbir şey tamamen geride bırakılamaz.",
    "🤍 Her insan bir iz bırakır. Kimisi yüzünde bir tebessüm, kimisi kalbinde kapanmayan bir boşluk olur.",
    "🤍 Kendini herkese anlatmaya çalışma. Seni anlamak isteyen biri, cümlelerinden önce sessizliğini dinler.",
    "🤍 Güven, yavaş yavaş büyüyen bir ağaç gibidir; ama devrilmesi için tek bir yanlış yeter.",
    "🤍 İnsan bazen yanlış insanlara değil, yanlış zamanlara denk gelir. Belki de en büyük talihsizlik budur.",
    "🤍 Hayatta bazı yollar yalnız yürünür. Çünkü insanın en büyük hesaplaşması, kendisiyle olandır.",
    "🤍 Bir gün herkes seni olduğun gibi kabul etmeyebilir. Ama en önemlisi, senin kendinden vazgeçmemendir.",
    "🤍 Bazı özürler çok geç gelir. Çünkü zaman, kırılan kalbin beklemeyi bıraktığı yerde durmaz.",
    "🤍 Mutluluk, her istediğine sahip olmak değil; sahip olduklarının kıymetini kaybetmeden bilmektir.",
    "🤍 Bir insanın kalbine dokunmak kolay değildir. Ama kırmak için çoğu zaman tek bir cümle yeter.",
    "🤍 En güzel insanlar, en çok acıyı yaşamış ama bunu başkalarına yaşatmamayı seçmiş olanlardır.",
    "🤍 İnsan en çok, artık hiçbir şey hissetmediğini sandığı gün yeniden kırılır.",
    "🤍 Kaybolmuş hissetmek bazen yön bulmanın başlangıcıdır.",
    "🤍 Küçük adımlar bile seni olduğun yerden çıkarır.",
    "🤍 Kendini sürekli eleştirmek, gelişmekle aynı şey değildir.",
    "🤍 Bazen en doğru cevap, biraz beklemektir.",
    "🤍 Kendinle konuşma şeklin, hayatını belirler.",
    "🤍 Sessiz kaldığında bile büyümeye devam ediyorsun.",
    "🤍 Kendini anlamaya çalışmak, çoğu şeyden daha değerlidir.",
    "🤍 Bugün iyi hissetmiyorsan, bu senin bozuk olduğun anlamına gelmez.",
    "🤍 Herkes güçlü görünmez, herkes güçlü de değildir zaten.",
    "🤍 Bazı günler sadece “dayanmak” yeterlidir.",
    "🤍 İyileşmek düz bir çizgi değildir.",
    "🤍 İnsan bazen en çok, anlatmaya çalıştığı şey anlaşılmadığında yorulur. Çünkü bazı duyguların sesi vardır ama kelimesi yoktur.",
    "🤍 Birini unutmak, adını hatırlamamak değildir. Onu hatırladığında canının artık eskisi kadar acımamasıdır.",
    "🤍 Hayat sana herkesi neden kaybettiğini değil, yanında kalanların neden kaldığını öğrettiğinde büyümeye başlarsın.",
    "🤍 Herkes bir gün gider. Kimisi kapıyı çarparak, kimisi sessizce... Ama en çok, hiçbir şey söylemeden gidenler eksik kalır içinde.",
    "🤍 Bir kalbi kırmak için yüksek sesle konuşmaya gerek yoktur. Bazen söylenmeyen tek bir cümle, söylenen bin cümleden daha çok incitir.",
    "🤍 Zaman yaraları iyileştirmez; sadece acıyla yaşamayı öğretir. İyileşen şey yara değil, insandır.",
    "🤍 İnsan, en çok değer verdiği kişiye karşı kırılır. Çünkü yabancıların yaptığı hiçbir şey, sevdiklerinin sessizliği kadar can yakmaz.",
    "🤍 Bazı insanlar hayatına mutluluk getirmez. Ama gittiklerinde, sana kendini tanımayı öğretirler.",
    "🤍 Kimse aynı insan olarak kalmaz. Ya yaşadıkları değiştirir onu ya da sustukları.",
    "🤍 Güven, bir kez kırıldığında yeniden kurulabilir belki; ama hiçbir zaman ilk hâli kadar masum olmaz.",
    "🤍 Herkes seni tanıyabilir ama çok az insan seni gerçekten anlayabilir. Çünkü görmek başka, hissetmek başkadır.",
    "🤍 Bazen bir insanı affedersin ama ona eskisi gibi bakamazsın. Çünkü kalp unutmaktan önce kırılmayı öğrenir.",
    "🤍 En güzel insanlar kusursuz olanlar değil, kırıldığı hâlde kimseyi kırmamayı seçenlerdir.",
    "🤍 İnsan bazı geceler uyuyamaz. Çünkü gözlerini kapattığında aklı susar ama kalbi konuşmaya devam eder.",
    "🤍 Hayatta herkes bir şeyler kaybeder. Önemli olan neyi kaybettiğin değil, kaybettikten sonra nasıl biri olduğundur.",
    "🤍 Bir gün dönüp arkana baktığında pişman olacağın şey, yaptıkların değil; yapmaya cesaret edemediklerin olacak.",
    "🤍 Her vedanın bir sesi vardır. Kimisi gözyaşıdır, kimisi sessizlik... Ama en çok da yarım kalan cümleler yankılanır insanın içinde.",
    "🤍 İnsan bazen güçlü olduğu için değil, başka seçeneği olmadığı için dimdik durur.",
    "🤍 Bazı yollar yanlış olduğu hâlde yürünür. Çünkü insan bazen doğru yolu değil, doğru dersi arar.",
    "🤍 Kendini herkese anlatmaya çalışma. Seni gerçekten anlamak isteyen biri, sessizliğinde bile ne söylemek istediğini hisseder.",
    "🤍 Kendine verdiğin değer, dünyaya nasıl baktığını değiştirir.",
    "🤍 Başkalarının sana inanmasını bekleme, önce kendine inan!"
]

SLAP_LIST = [ 


    "🩴 {a}, {b}'a terlikle girişti 😂",
    "📺 {a}, {b}'nin üstüne televizyon fırlattı.",
    "🪑 {a}, {b}'a sandalye attı 💀",
    "🧃 {a}, {b}'nin suratına meyve suyu sıktı.",
    "🛏️ {a}, {b}’a yumuşak bir yastık fırlattı 🛏️",
    "{a}, {b}'yi ensesinden yakalayıp yere yapıştırdı. 💥",
    "{a}, {b}'yi tek hamlede duvara çarptı. 🧱",
    "{a}, {b}'yi havaya savurup yere indirdi. 🌪️",
    "{a}, {b}'yi yakaladığı gibi yere çiviledi. ⚡",
    "{a}, {b}'yi tuttuğu gibi masanın üstüne fırlattı. 💢",
    "{a}, {b}'yi boğuşmanın ortasında yere serdi. 😈",
    "{a}, {b}'yi tekmeyle birkaç metre öteye savurdu. 👢",
    "{a}, {b}'yi yumruk yağmuruna tuttu. 👊",
    "{a}, {b}'yi kolundan yakalayıp duvara yasladı. 💥",
    "{a}, {b}'yi sırtüstü yere düşürdü. 🌀",
    "📺 {a}, {b}’a uzaktan kumandayla saldırdı 📺",
    "🥊 {a}, {b}’a uçan tekme attı! 🥊"
    "💥 {a}, {b}’nin ensesine Osmanlı Tokadı attı! 💥",
    "☄️ {a}, {b}’i tutup duvardan duvara vurdu! ☄️",
    "🌪️ {a}, {b}’i tutup camdan aşağı fırlattı! 🌪️",
    "🪑 {a}, {b}’a sandalye savurdu 🪑",
    "📺 {a}, {b}’nin kafasında tüplü televizyon kırdı! 📺",
    "🪵 {a}, {b}’a oklava ile daldı! 🪵",
    "🧱 {a}, {b}’nin kafasına tuğla fırlattı! 🧱",
    "🩴 {a}, {b}’a 120 km hızla uçan anne terliği fırlattı! 🩴",
    "🫖 {a}, {b}’a kaynar çaydanlık fırlattı! 🫖",
    "💥 {a}, {b}’i elektrik direğine bağlayıp sabaha kadar dövdü! 💥",
    "🔨 {a}, {b}’nin kafasına 5 kiloluk balyoz indirdi! 🔨",
    "💣 {a}, {b}’nin kucağına pimi çekilmiş el bombası bıraktı! 💣",
    "🚜 {a}, {b}’nin üzerinden belediye dozeriyle geçti! 🚜",
    "🏗️ {a}, {b}’nin kafasına şantiye vinci düşürdü! 🏗️",
    "🚀 {a}, {b}’i sırtına roket bağlayıp Mars’a fırlattı! 🚀",
    "🌋 {a}, {b}’i tutup aktif yanardağın içine fırlattı! 🌋",
    "🍽️ {a}, {b}’nin suratına porselen tabak fırlattı! 🍽️",


]

BURC_YORUMLARI = {
    "koc": "♈ Koç: Bu hafta enerjin yüksek ama biraz dağınık olabilir. Aynı anda birkaç işe birden yönelmek isteyebilirsin fakat bu durum seni yorabilir. Özellikle iletişimde daha sakin kalmak önemli olacak. Hafta ortasında bazı küçük gerilimler yaşansa da hızlı toparlanıyorsun. Hafta sonuna doğru daha rahat ve motive hissedeceksin.",
    "boga": "♉ Boğa: Bu hafta maddi konular ve güven duygusu ön planda. Harcamalarını biraz kontrol altında tutman gerekebilir. Aynı zamanda beklemediğin küçük bir fırsat kapını çalabilir. Duygusal olarak daha sakin ama içe dönük olabilirsin. Hafta sonuna doğru rahatlama ve huzur artıyor.",
    "ikizler": "♊ İkizler: Bu hafta iletişim trafiğin oldukça yoğun. Çok fazla insanla görüşebilir, eski konuların tekrar gündeme geldiğini görebilirsin. Zihinsel olarak hızlı ama biraz dağınık olman mümkün. Bu yüzden önemli kararları aceleye getirmemelisin. Hafta sonuna doğru netleşme yaşayacaksın.",
    "yengec": "♋ Yengeç: Bu hafta duygusal anlamda biraz hassas olabilirsin. Geçmişle ilgili bazı düşünceler tekrar aklına gelebilir. Kendini fazla zorlamadan ilerlemek sana iyi gelecek. Yakın çevrenden destek görmek moralini yükseltebilir. Hafta sonunda daha dengeli hissedeceksin.",
    "aslan": "♌ Aslan: Bu hafta dikkat çeken bir enerjiye sahipsin. İnsanlar seni daha çok fark ediyor ve söylediklerin önem kazanıyor. Ancak ego çatışmalarına dikkat etmen gerekebilir. Özellikle sosyal ortamlarda yanlış anlaşılmalar olabilir. Hafta sonu keyifli gelişmeler var.",
    "basak": "♍ Başak: Bu hafta sorumlulukların artabilir ve yoğun bir tempo seni bekliyor olabilir. Planlı hareket edersen birçok işi rahatlıkla halledebilirsin. Detaylara fazla takılmak seni yorabilir. Küçük molalar vermek önemli olacak. Hafta sonunda rahatlama hissediyorsun.",
    "terazi": "♎ Terazi: Bu hafta ilişkiler ve sosyal çevre ön planda. Yeni insanlarla tanışabilir ya da mevcut ilişkilerde önemli konuşmalar yapabilirsin. Kararsızlık yaşadığın bir konuda netleşme olabilir. Denge kurmaya çalıştıkça daha rahat ilerleyeceksin. Hafta sonu sosyal açıdan hareketli.",
    "akrep": "♏ Akrep: Bu hafta sezgilerin oldukça güçlü. İnsanların niyetlerini daha kolay fark edebilirsin. Gizli kalan bazı konular netleşebilir. Duygusal olarak derin düşünceler içinde olabilirsin. Kontrolü kaybetmeden ilerlemek önemli.",
    "yay": "♐ Yay: Bu hafta yeni planlar ve değişiklik isteği artıyor. Rutinden sıkılabilir ve farklı şeyler denemek isteyebilirsin. Seyahat veya yeni başlangıç fikirleri gündeme gelebilir. Acele kararlar yerine biraz düşünmek daha iyi olur. Hafta sonu daha özgür hissedeceksin.",
    "oglak": "♑ Oğlak: Bu hafta hedeflerin ve sorumlulukların ön planda. Yoğun bir tempo içinde olabilirsin ama bu seni ileriye taşıyacak. Sabırlı ilerlemek önemli olacak. Küçük ilerlemeler bile uzun vadede büyük sonuçlar getirebilir. Hafta sonunda rahatlama geliyor.",
    "kova": "♒ Kova: Bu hafta farklı fikirler ve ani gelişmeler dikkat çekiyor. Planlarında değişiklik yapmak zorunda kalabilirsin. Esnek kalmak sana avantaj sağlar. Sosyal çevrende beklenmedik konuşmalar olabilir. Hafta sonu zihinsel olarak daha rahat hissedeceksin.",
    "balik": "♓ Balık: Bu hafta iç dünyana yönelme eğilimin artıyor. Duyguların biraz yoğun olabilir ve bazı şeyleri fazla düşünme eğilimi gösterebilirsin. Hayal gücün güçlü ama gerçeklerle denge kurmak önemli. Sakin kalmak sana iyi gelecek. Hafta sonunda iç huzur artıyor."
}

SHIP_YORUMLARI = {
    "0-20": [
        "💔 Aranızda pek uyum yok gibi ama arkadaşlık daha mantıklı olabilir.",
        "🥶 Enerjiler biraz ters, zorlamaya gerek yok.",
        "🚫 Bu kombinasyon biraz riskli görünüyor."
    ],
    "21-40": [
        "😬 Arada bir çekim var ama iletişim zorlayabilir.",
        "💭 Biraz çaba ile yürüyebilir ama kolay değil.",
        "⚖️ Uyum orta seviyede, inişli çıkışlı olabilir."
    ],
    "41-60": [
        "🙂 Fena değil, arada güzel anlar olabilir.",
        "💫 Uyum var ama sabır gerekiyor.",
        "🤝 Doğru zamanda güzel bir bağ oluşabilir."
    ],
    "61-80": [
        "💖 Güzel bir uyum yakalanmış, enerji oldukça iyi!",
        "✨ Birbirinizi tamamlayabilirsiniz.",
        "🔥 Aranızda güçlü bir çekim var!"
    ],
    "81-100": [
        "💘 Mükemmel uyum! Enerjiniz çok iyi eşleşiyor!",
        "🌟 Neredeyse ruh ikizi seviyesi!",
        "🔥 Bu ilişki ciddi potansiyel taşıyor!"
    ]
}

SANS_YORUMLARI = [
    "🍀 Bugün evren senden yana.",
    "✨ Şans kapında ama biraz cesaret lazım.",
    "💫 Beklenmedik güzel bir haber alabilirsin.",
    "🌙 Bugün enerjin oldukça yüksek.",
    "🪐 Ufak aksiliklere dikkat et.",
    "🔥 Şans seviyen resmen patlıyor.",
    "🍀 Bugün şans senin tarafında. Cesur davranırsan güzel bir sürprizle karşılaşabilirsin.",
    "🌤️ Şansın bugün inişli çıkışlı. Büyük kararları biraz ertelemek iyi olabilir.",
    "✨ Beklenmedik bir haber yüzünü güldürebilir.",
    "💸 Küçük bir maddi kazanç kapını çalabilir.",
    "❤️ Kalbinle ilgili güzel bir gelişme yaşayabilirsin.",
    "📩 Uzun zamandır beklediğin bir mesaj bugün gelebilir.",
    "🎯 Şansın özellikle yeni başlangıçlarda seninle.",
    "🌙 Bugün sezgilerine güven; sana doğru yolu gösterebilir.",
    "🎲 Risk alırsan kazanma ihtimalin düşündüğünden yüksek.",
    "🦋 Küçük bir tesadüf büyük bir mutluluğa dönüşebilir.",
    "🌈 Bugün güldüğün kadar şansın da artacak.",
    "⚠️ Acele kararlar şansını tersine çevirebilir.",
    "🔮 Şans kapını çalacak ama fark etmen gerekecek.",
    "🍀 Beklenmedik biri sana iyilik yapabilir.",
    "🎁 Bugün güzel bir sürpriz seni bekliyor olabilir.",
    "🌟 Şans yıldızın parlıyor; kendine güven.",
    "💭 İçinden geçen ilk fikir bugün sana kazandırabilir.",
    "🕊️ Bugün huzur, en büyük şansın olacak.",
    "🎉 Şansın, doğru insanlarla karşılaşmanda saklı.",
    "🌌 Her şey planladığın gibi gitmeyebilir ama sonunda yüzün gülecek.",
    "🪙 Küçük bir risk, büyük bir fırsata dönüşebilir.",
    "🌸 Bugün bir tebessüm bile şansını değiştirebilir.",
    "⏳ Sabırlı olursan beklediğin kapı açılacak.",
    "📚 Yeni bir şey öğrenmek sana beklenmedik fırsatlar getirebilir.",
    "🧩 Bugün eksik kalan bir parçayı tamamlayacaksın.",
    "🔥 Cesaretin kadar şansın da büyüyor.",
    "🌊 Akışına bıraktığın işler daha güzel sonuçlanabilir.",
    "💎 Bugünün en büyük şansı, fark etmediğin küçük ayrıntılarda gizli.",
    "🎈Şans bazen sadece doğru zamanda gülümsemektir.",
    "☁️ Bugün bulutlu görünse de günün sonunda güneş senin için açacak."
    "🍀 Bugün küçük bir şans kapını çalabilir, gözünü açık tut.",
    "✨ Beklemediğin bir yerden güzel bir gelişme gelebilir.",
    "💫 Şansın orta seviyede ama gün içinde artabilir.",
    "🔥 Bugün risk alırsan karşılığını alabilirsin.",
    "🪐 Evren senden yana çalışıyor gibi.",
    "😼 Zuzu bugün seni şanslı buldu.",
    "🌙 Küçük tesadüfler büyük sonuçlar doğurabilir.",
    "⚡ Ani bir fırsat yakalayabilirsin.",
    "🍃 Sabırlı olursan gün sana döner.",
    "🎯 Hedeflerine yaklaşacağın bir gün olabilir.",
    "🧿 Şansın koruma altında gibi hissedebilirsin."
]

MOOD_YORUMLARI = [
    "🌧️ İçine kapanık hissediyorsun ama geçecek.",
    "🌤️ Bugün her şeye karşı biraz umursamaz hissediyorsun.",
    "🌙 Kafan dolu ama nedenini tam sen de bilmiyorsun.",
    "☁️ Sessiz kalmak bugün konuşmaktan daha iyi geliyor.",
    "🌧️ Biraz kırgın hissediyorsun ama belli etmemeyi seçiyorsun.",
    "🌊 Duyguların bugün sürekli değişiyor.",
    "🌼 Bugün kırılgan hissedebilirsin ama bu seni güçsüz yapmaz.",
    "🌼 Küçük bir tebessüm bütün gününün yönünü değiştirebilir.",
    "🌼 Bugün beklentilerini biraz azaltırsan kendini daha hafif hissedebilirsin.",
    "🌼 Kendine göstereceğin anlayış bugün en çok ihtiyacın olan şey olabilir."
    "🌸 Küçük şeyler bile yüzünü güldürebilir.",
    "🌤️ İçten içe güzel bir haber bekliyorsun.",
    "🌫️ Bugün hiçbir şey yapmak istemiyorsun.",
    "🌈 İçinde sebebini bilmediğin bir umut var.",
    "🌙 Geçmişi biraz fazla düşünüyorsun.",
    "🌧️ Bugün duyguların mantığının önüne geçebilir.",
    "🌿 Bugün kafandaki gürültü biraz azalıyor. Kendini uzun zamandır hissetmediğin kadar sakin hissedebilirsin.",
    "💭 Bugün bazı şeyleri sorgulamak isteyeceksin. Cevap bulamasan bile düşünmek sana iyi gelebilir.",
    "☕ Bugün enerjini herkese yetiştirmeye çalışma. Birazını da kendin için sakla.",
    "🌙 Bugün geçmişe dalıp gitmen mümkün. Ama orada uzun süre kalmamaya çalış.",
    "🫶 Bugün birinin samimiyeti bütün ruh halini değiştirebilir.",
    "✨ İçinde küçük de olsa bir umut var. Onu büyütmek tamamen senin elinde.",
    "🌧️ Bugün kendini biraz hassas hissedebilirsin. Her şeyi kişisel algılamamaya çalış.",
    "🌸 Bugün kendine karşı daha sabırlı olman gereken bir gün olabilir.",
    "🍃 Bugün hayatı biraz akışına bırakmak sana düşündüğünden daha iyi gelecek.",
    "🌼 Küçük bir mola, bugün ihtiyacın olan en değerli şey olabilir.",
    "💫 Bugün iç sesin sana doğru yolu göstermeye çalışıyor. Onu duymaya çalış.",
    "🌿 Bugün huzuru büyük olaylarda değil, küçük anlarda bulacaksın.",
    "🕊️ Bugün kimseyi kırmak istemeyeceksin. Kalbin her zamankinden biraz daha yumuşak.",
    "🌙 Bugün sessizlik sana rahatsız edici değil, aksine iyi gelecek.",
    "☁️ Bugün dalgın olabilirsin. Zihnin senden birkaç adım önde gidiyor gibi.",
    "💭 Bugün vereceğin kararları aceleye getirmemek en doğrusu olabilir.",
    "✨ Bugün içinde yeni bir başlangıç yapma isteği hissedebilirsin.",
    "🌊 Bugün duyguların sık sık değişebilir. Kendine bunu yaşamak için izin ver.",
    "🍂 Bugün geçmişi değil, bugünü yaşamaya çalışırsan kendini daha hafif hissedebilirsin.",
    "🌤️ Bugün moralin yavaş yavaş yerine geliyor. Kendine biraz zaman tanı.",
    "🤍 Bugün seni en çok mutlu edecek şey, beklemediğin bir ilgi olabilir.",
    "🎧 Bugün sevdiğin müzikler ruh haline düşündüğünden daha çok dokunabilir.",
    "📖 Bugün kendin hakkında yeni bir şey fark edebilirsin.",
    "🌱 Bugün küçük de olsa attığın her adım seni ilerletecek.",
    "💛 Bugün biri seni düşündüğünü belli edebilir ve bu bütün gününe yansıyabilir.",
    "🌅 Bugün yeni bir sayfa açmak için kötü bir gün değil.",
    "🪴 Bugün zihnini dinlendirecek küçük alışkanlıklar edinmek isteyebilirsin.",
    "🫧 Bugün içindeki yükü biraz olsun bırakmaya hazırsın gibi görünüyor.",
    "🌠 Bugün her şeyi çözmeye çalışma. Bazen sadece günü yaşamak yeterlidir.",
    "😌 Bugün kendini olduğun gibi kabul etmek sana en büyük huzuru verebilir.",
    "🍂 Eski anılar aklına sık sık geliyor.",
    "🌼 Ufak şeylerden mutlu olabilecek bir gündesin.",
    "🌪️ Kafan biraz karışık ama toparlanacak.",
    "⭐ Bugün enerjin beklediğinden daha yüksek olabilir.",
    "🌙 Bugün içine dönük olabilirsin. Her zaman konuşmak zorunda değilsin.",
    "🌙 İnsanlardan biraz uzak durmak istemen tamamen normal.",
    "🌙 Bugün kendi düşüncelerinle vakit geçirmek sana iyi gelebilir.",
    "🌙 Sessiz geçen bir gün bazen en huzurlu gün olabilir.",
    "🌤️ İnsanlarla konuşmak sana iyi gelebilir.",
    "🌧️ Biraz yalnız kalmak isteyebilirsin.",
    "🌊 Bugün duygusal olma ihtimalin yüksek.",
    "🍃 Kendini sakin hissediyorsun.",
    "🌙 İçinde açıklayamadığın bir boşluk hissi var.",
    "☀️ Bugün pozitif olman daha kolay olacak.",
    "🌦️ Biraz kararsız hissediyorsun.",
    "🌸 İçinden yeni bir başlangıç yapmak geliyor.",
    "🌫️ Dalgınlığın bugün kendini belli edebilir.",
    "🌤️ Bugün enerjin yüksek. Yeni şeyler denemek için güzel bir gün.",
    "🌙 Biraz dinlenmeye ihtiyacın var gibi görünüyor. Kendine zaman ayır.",
    "☕ Ruh halin sakin ama içinde söylemek istediğin çok şey var.",
    "🌸 Bugün küçük şeylerden mutlu olacağın bir gün.",
    "⚡ Enerjin dalgalı. Acele kararlar vermemeye çalış.",
    "🎵 Bugün en iyi ilacın sevdiğin bir şarkı olabilir.",
    "🍀 Moralini yükseltecek güzel bir haber kapıda olabilir.",
    "🌧️ Biraz duygusalsın ama bu da geçecek.",
    "😌 Bugün huzur arıyorsun. Kalabalıklardan biraz uzaklaşmak iyi gelebilir.",
    "🔥 Motivasyonun zirvede! Başlamak için doğru zaman.",
    "🦋 Bugün yeni insanlarla tanışmaya açıksın.",
    "💭 Kafanı kurcalayan bir konu var ama cevabı düşündüğünden daha yakın.",
    "🌊 Akışına bıraktığın şeyler seni daha mutlu edecek.",
    "📚 Bugün kendine yeni bir şey katmak isteyebilirsin.",
    "☀️ Gülümsemen bugün bir başkasının gününü güzelleştirebilir.",
    "🌌 Biraz yalnız kalmak sana iyi gelebilir.",
    "🎯 Odaklandığın her işte başarılı olabilecek bir ruh halindesin.",
    "🕊️ İç huzurun bugün en büyük gücün olacak.",
    "🍫 Kendini ödüllendirmeyi unutma; bunu hak ediyorsun.",
    "💤 Uykunu ihmal etmiş gibisin. Biraz dinlenmek sana iyi gelecek.",
    "🎈 Bugün kahkaha atacağın güzel bir an yaşayabilirsin.",
    "🌿 Hayatın temposunu biraz yavaşlatmak sana iyi gelecek.",
    "🤍 Kalbin kırgın olsa da umudunu kaybetme.",
    "🚀 İçinde büyük bir potansiyel var; bugün onu gösterebilirsin.",
    "🌠 Sezgilerin bugün sana doğru yolu gösterebilir.",
    "🎨 Yaratıcılığın bugün zirvede.",
    "🌼 Geçmişi düşünmek yerine bugünü yaşamayı dene.",
    "🌙 Bazı cevaplar sessizlikte saklıdır.",
    "💎 Kendine güvendiğin an her şey değişmeye başlayacak."
    "🌈 İçten içe her şeyin düzeleceğine inanıyorsun.",
    "💭 Bugün çok düşünecek, az konuşacaksın.",
    "⚡ Sabrın bugün biraz daha çabuk tükenebilir.",
    "🌊 Hislerini içinde yaşamayı tercih ediyorsun.",
    "🌻 Küçük bir ilgi bile moralini yükseltebilir.",
    "🌤️ Bugün her şey mükemmel gitmeyebilir ama moralini bozacak kadar da kötü görünmüyor.",
    "🍂 Bugün biraz kendi hâlinde olmayı tercih edebilirsin. Bunun için kendini suçlama.",
    "☕ Bugün yavaş ilerlemek sana daha iyi gelecek. Her şeye yetişmek zorunda değilsin.",
    "🌸 Bugün beklemediğin küçük bir şey yüzünü gülümsetebilir.",
    "🌙 Bugün biraz düşüncelisin. Belki de zihnin sadece kısa bir mola istiyordur.",
    "🎧 Bugün kulaklığını takıp kendi dünyana çekilmek isteyebilirsin.",
    "💭 Bugün bazı şeyleri fazla düşünebilirsin. Kendine biraz nefes alacak alan bırak.",
    "🌧️ Bugün duyguların biraz karışık olabilir. Bu da insan olmanın bir parçası.",
    "🌿 Bugün huzuru kalabalıkta değil, sessizlikte bulabilirsin.",
    "🌈 Bugün uzun zamandır hissetmediğin kadar hafif hissedebilirsin.",
    "✨ Bugün kendine güvenin yavaş yavaş yerine geliyor gibi.",
    "🫶 Bugün biri sana farkında olmadan iyi gelebilir.",
    "🌊 Bugün bazı şeyleri oluruna bırakmak en doğru seçim olabilir.",
    "📖 Bugün eski bir anı aklına düşebilir ve yüzünde küçük bir tebessüm bırakabilir.",
    "🌼 Bugün küçük mutlulukları fark ettiğinde günün daha güzel geçecek.",
    "🕊️ Bugün içini sıkan şeyleri biraz olsun geride bırakabilecek gibisin.",
    "🎈 Bugün sebepsiz yere bile mutlu hissedebilirsin. Tadını çıkar.",
    "🔥 Bugün motivasyonun yüksek. Başlamak için bahane arama.",
    "🌌 Bugün biraz yalnız kalmak sana sandığından daha iyi gelebilir.",
    "🌞 Bugün enerjin çevrendekilere de yansıyacak gibi görünüyor.",
    "🍀 Bugün şansından çok, tavrın günü güzelleştirecek.",
    "🌠 Bugün içinden gelen ilk his seni doğru yere götürebilir.",
    "🎵 Bugün tek bir şarkı bile bütün modunu değiştirebilir.",
    "💤 Bugün bedenin kadar zihnin de dinlenmek istiyor olabilir.",
    "🧩 Bugün uzun zamandır eksik hissettiğin bir parçayı tamamlayacak bir konuşma yaşayabilirsin.",
    "🌺 Bugün kendine biraz daha nazik davranmayı dene.",
    "📸 Bugün hatırlamaya değer küçük bir an yaşayabilirsin.",
    "🤍 Bugün seni mutlu edecek şey büyük değil, samimi olacak.",
    "🪴 Bugün biraz yavaşlamak sana düşündüğünden daha fazla iyi gelebilir.",
    "🌙 Bugün her şeyi çözmek zorunda değilsin; bazen sadece günü tamamlamak yeterlidir."
    "🌠 Bugün sürprizlere açık bir ruh halindesin.",
    "🔮 Bugün sezgilerin mantığından daha güçlü olabilir.",
    "🌙 İç sesin sana bir şey anlatmaya çalışıyor.",
    "✨ Beklenmedik bir karşılaşma gününü değiştirebilir.",
    "🌌 Bugün tesadüf gibi görünen şeylere dikkat edeceksin.",
    "🍀 Şansın küçük detaylarda saklı olabilir.",
    "💫 İçinde tarif edemediğin bir heyecan var.",
    "💭 Bugün düşünceli bir ruh halindesin. Zihnin sürekli bir şeylerle meşgul olabilir.",
    "💭 Bazı soruların cevabını bugün bulamayabilirsin. Her cevabın hemen gelmesi gerekmiyor.",
    "💭 Gelecekle ilgili planlar aklını fazlasıyla meşgul edebilir.",
    "💭 Bugün kendinle baş başa kalmak sana iyi gelebilir.",
    "🌠 Uzun zamandır ertelediğin bir şeyi hatırlayabilirsin.",
    "🌙 Kalbinin sesi bugün daha baskın olabilir.",
    "☄️ Beklenmedik bir mesaj moralini değiştirebilir.",
    "🌈 Bugün duyguların seni şaşırtabilir.",
    "☀️ Enerjin yükseliyor, bugün daha iyi hissedeceksin.",
    "🌙 Biraz kafa dinlemeye ihtiyacın var gibi.",
    "🌧️ Bugün biraz hassassın. Normalde takılmayacağın şeyler bile canını sıkabilir.",
    "🌧️ Kendine bugün biraz daha nazik davran. Her günü aynı güçle geçirmek zorunda değilsin.",
    "🌧️ Bugün duygularını bastırmak yerine kabul etmek sana daha iyi gelebilir.",
    "🌧️ Küçük bir yanlış anlaşılma bile moralini etkileyebilir. Hemen kötü düşünmemeye çalış.",
    "💫 Duygusal ama güçlü bir moddasın.",
    "🫧 Kendine fazla yükleniyorsun.",
    "🌿 Sessizlik sana iyi gelebilir bugün.",
    "🌧️ Biraz içe dönük ve düşünceli bir moddasın.",
    "☀️ Enerjin yavaş yavaş yükseliyor.",
    "🫧 Duyguların biraz karışık olabilir ama geçici.",
    "🔥 Motivasyonun geri gelmeye başladı.",
    "🌙 Bugün sessizlik sana iyi gelebilir.",
    "⚖️ Denge arayışındasın.",
    "💭 Çok fazla düşünüyorsun, biraz rahatla.",
    "🌊 Dalgalı ama kontrol edilebilir bir ruh hali.",
    "✨ İçinde yeni bir başlangıç isteği var.",
    "🫶 Bugün duygusal bir moddasın. Eski bir fotoğraf, bir şarkı ya da küçük bir anı seni geçmişe götürebilir.",
    "🫶 Kalbin bugün olaylara biraz daha hassas yaklaşabilir. Bunun kötü bir şey olduğunu düşünme.",
    "🫶 Bugün sevdiklerinden gelecek küçük bir ilgi bile bütün modunu değiştirebilir.",
    "🫶 İçinden geçenleri anlatmak isteyebilirsin ama doğru kelimeleri bulmakta zorlanabilirsin.",
    "Bakıyorum da keyifler gıcır. Güneş açmış, kuşlar uçuyor, senin de için kıpır kıpır olmuş sanki. Bu modunu hiç bozma olur mu? 🌸",
    "Bugün üzerinde çok tatlı bir dinginlik var. Aceleyle iş yapacak modda değilsin, her şeyi ağırdan alıp anın tadını çıkarıyorsun sanki. Aynen böyle devam! 🍃",
    "Senin modun bugün resmen 'Error 404: Enerji Bulunamadı.' Pilin bitmiş, bataryan sıfırlanmış gibi duruyorsun. Sana acilen iki satır tatlı söz ve biraz dinlenmek lazım... 💤",
    "Şşşt, bugün herkese trip atasın, önüne gelene ters cevap veresin var gibi bir his aldım. Kim bozdu senin asabını, söyle çabuk ona kick atayım! 💥",
    "Bugün modun tam olarak: 'Sessizce köşeme çekileyim ama arkadan gizlice kaos çıkarıp izleyeyim.' Ortalığı karıştıracak bir muziplik var gözlerinde, seziyorum! 😈",
    "Bugün grupta kimseye rahat vermeyecek, herkesle tatlı tatlı uğraşacak bir moddasın. Enerjini dökebileceğin bir kurban arıyorsun resmen, hadi hayırlısı! 🎯",
    "Tam bir gizli ajan modundasın. Grupta yazılan her şeyi sessizce okuyup arkada sinsice gülümsüyorsun sanki. Çık ortaya, yakalandın! 🕵️‍♀️",
    "Bakıyorum da üzerinde tam bir 'Bugün hiçbir şey yapasım yok, okul da neymiş?' havası var. Haklısın, bazen sadece boş duvara bakıp hiçbir şey düşünmemek en iyi moddur. 🛌",
    "Senin modun bugün tam olarak: 'Bu YKS ne zaman bitecek?' ağlaması. Kafanda bin tane ders notu uçuşuyor, kitaplara boş boş bakıyorsun gibi bir bıkkınlık sezdim. Sabret, az kaldı! 📚",
    "Bugün senin modun tam olarak: 'Telefonu sessize alıp akşama kadar abur cubur yiyerek dizi izlemek.' Dünyanın geri kalanı umrunda bile değil, tam bir inziva havası. 🍿",
    "Şu an dünyaları verseler parmağını bile oynatmayacak bir üşengeçlik modundasın değil mi? Seni çok iyi anlıyorum, bazen en güzel aktivite hiçbir şey yapmamaktır. 💤",
    "🧠 Zihnin dolu ama toparlanıyor.",
    "💤 Biraz yorgunluk hissi olabilir."

]

ZUZU_CEVAPLARI = [
    "Efendim? 🌸",
    "Buradayım. 😊",
    "Beni mi çağırdın? 👀",
    "Dinliyorum seni. 💛",
    "Ne oldu bakalım? 😌",
    "Yine mi ben? 😂",
    "Hazırım! Söyle bakalım. ✨",
    "Beni özledin galiba. 😼",
    "Çağırdığına göre önemli bir şey var. 🤔",
    "Buyur, seni dinliyorum. 🌼",

    "Of... Daha yeni oturmuştum. 😮‍💨",
    "Ne var yine? 😒",
    "Bir dakika dinleneyim dedim... 😩",
    "Yine mi 'Zuzu'? 😭",
    "İsmimi bu kadar sevmen biraz korkutucu olmaya başladı. 👀",
    "Tam uyuyordum... 😴",
    "Şikâyet etmiyorum ama bugün çok çağrıldım. 🤧",
    "Bir gün de beni ben çağırayım. 😤",
    "Bana seslenmeden de duramıyorsun. 😌",
    "Tam çay içiyordum... ☕",

    "İyi misin? Öyle seslendin sanki. 🥹",
    "Merak ettim, neden çağırdın? 💭",
    "Bugün nasıl hissediyorsun? 🌸",
    "Ben buradayım, sen yeter ki yaz. 🤍",
    "Çağrıldım ve geldim. 🚶",
]

ROAST_LIST = [
    "😭 Senin motivasyon seviyesi telefonun %1 şarjı gibi.",
    "💀 Sen ders çalışırken internet hızın düşüyor olabilir.",
    "😼 Zuzu senden daha düzenli uyuyor.",
    "🪫 Enerjin powerbank arıyor gibi duruyor.",
    "🍞 Hayat seni tost yapmış biraz.",
    "📉 Beynin şu an loading ekranında olabilir.",
    "🐢 Reflekslerin Internet Explorer hızında.",
    "😼 Senin motivasyonun düşük batarya modunda çalışıyor.",
    "💀 Plan yapıyorsun ama uygulama hiç açılmıyor.",
    "🐢 Hızın “yükleniyor…” ekranı gibi.",
    "📉 Disiplinin hafta sonu modu gibi.",
    "🪫 Enerjin powerbank bile reddediyor.",
    "🍞 Hayat seni tost makinesine sokmuş gibi.",
    "😴 Üretkenliğin uyku moduna alınmış.",
    "📱 Bildirimlerin var ama aksiyon yok.",
    "🧃 Enerjin sulandırılmış meyve suyu gibi.",
    "🎮 Oyunda AFK kalmış gibisin.",
    "💻 Kodların bile senden daha stabil.",
    "📶 Bağlantın var ama sinyal yok gibi."
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_chat.id)

    kullanici = update.message.from_user.first_name
    chat_type = update.effective_chat.type

    if chat_type == "private":
        text = (
            f"🐾 <b>Selam {kullanici}! Ben Zuzu!</b>\n\n"
            f"Gruplar içinde sohbeti daha canlı ve eğlenceli hale getirmek için geliştirilmiş bir botum.😻\n\n"
            f"• <b>Oyunlar oynatırım</b>\n"
            f"• <b>Küçük etkileşimler sunarım</b>\n\n"
            f"👇 Aşağıdaki menüden tüm komutlarıma ulaşabilirsin ✨"
        )

        keyboard = [
            [InlineKeyboardButton("📜 Komutlar & Açıklamalar", callback_data="help_menu")],
            [InlineKeyboardButton("📢 Duyurular", url=DUYURU_CHANNEL_URL), InlineKeyboardButton("💬 Destek / Sorun", url=SUPPORT_GROUP_URL)],
            [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"), InlineKeyboardButton("👤 İletişim", url=MY_PROFILE_URL)]
        ]
    else:
        text = (
            f"✨ <b>Zuzu grupta aktif!</b>\n\n"
            f"👤 Hoş geldin {kullanici}!\n"
            f"🎯 Eğlenmek ve oyun oynamak için komutlarımı kullanabilirsin.\n\n"
            f"👇 Komut listesini görmek için aşağıdaki butona tıkla!"
        )
        keyboard = [[InlineKeyboardButton("📜 Tüm Komutlar", callback_data="help_menu")]]

    await update.message.reply_text(text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    

async def ship(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if is_spam(update.effective_user.id):
        return

    user1 = update.message.from_user.first_name
 
    if update.message.reply_to_message:
        user2 = update.message.reply_to_message.from_user.first_name

    elif context.args:
        user2 = context.args[0]
    else:
        await update.message.reply_text(
            "💘 Bir kullanıcı etiketle veya bir mesaja yanıt ver!"
        )
        return
    oran = random.randint(0, 100)

    if oran <= 20:
     yorum = random.choice(SHIP_YORUMLARI["0-20"])
    elif oran <= 40:
        yorum = random.choice(SHIP_YORUMLARI["21-40"])
    elif oran <= 60:
        yorum = random.choice(SHIP_YORUMLARI["41-60"])
    elif oran <= 80:
        yorum = random.choice(SHIP_YORUMLARI["61-80"])
    else:
        yorum = random.choice(SHIP_YORUMLARI["81-100"])

    text = f"💘 {user1} 💞 {user2}\n📊 Uyum: %{oran}\n\n{yorum}"

    await update.message.reply_text(text)

async def burc_yorumu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_spam(update.effective_user.id): 
        return
        
    
    if not update.message:
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔮 **Haftalık Burç Yorumu için bir burç adı yazmalısın.**\nÖrnek: `/burc koç`",
                parse_mode="Markdown"
            )
        return

    
    if not context.args:
        try:
            await update.message.reply_text(
                "🔮 **Haftalık Burç Yorumu için bir burç adı yazmalısın.**\n"
                "Örnek: `/burc koç` veya `/burc aslan`",
                parse_mode="Markdown"
            )
        except Exception as e:
            if "Message to be replied not found" in str(e):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🔮 **Haftalık Burç Yorumu için bir burç adı yazmalısın.**\nÖrnek: `/burc koç`",
                    parse_mode="Markdown"
                )
            else:
                raise e
        return 

  
    secilen_burc = (
        context.args[0]
        .lower()
        .replace("ı", "i")
        .replace("ş", "s")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ö", "o")
        .replace("ç", "c")
    )

   
    if secilen_burc in BURC_YORUMLARI:
        yorum = BURC_YORUMLARI[secilen_burc]
        cevap = f"🔮 <b>{secilen_burc.capitalize()} Burcu Haftalık Yorumu</b> 🔮\n\n{yorum}"
    else:
        
        cevap = f"🔮 <b>{secilen_burc.capitalize()}</b> adında bir burç bulamadım. Lütfen doğru yazdığından emin ol."

    
    try:
        await update.message.reply_text(cevap, parse_mode="HTML")
    except Exception as hata:
        if "Message to be replied not found" in str(hata):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=cevap,
                parse_mode="HTML"
            )
        else:
            raise hata

async def dogruluk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_spam(update.effective_user.id):
        await update.message.reply_text("⚠️ Çok hızlısın! Lütfen 3 saniye bekle.")
        return
    soru = random.choice(DOGRULUK)

    user = update.message.from_user
    
    await user_reply(

        update.message,
        user,

        f"doğruluk seçtin \n\n🧐 Soru:\n{soru}"
    )

async def cesaret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_spam(update.effective_user.id):
        await update.message.reply_text("⚠️ Çok hızlısın! Lütfen 3 saniye bekle.")
        return
    gorev = random.choice(CESARET)

    user = update.message.from_user

    await user_reply(

        update.message,
        user,

        f"cesaret seçtin 🔥\n\n😈 Görev:\n{gorev}"
    )
async def zuzu_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    if text.startswith("/"):
        return

    if "zuzu" in text:
        await update.message.reply_text(random.choice(ZUZU_CEVAPLARI))


async def soz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_spam(update.effective_user.id):
        await update.message.reply_text("⚠️ Çok hızlısın! Lütfen 3 saniye bekle.")
        return
    mesaj = random.choice(SOZ)

    user = update.message.from_user

    mention = f"[{user.first_name}](tg://user?id={user.id})"

    text = f"{mention}\n{mesaj}"
 
    await update.message.reply_text(
        text=text,
        parse_mode="Markdown"
    )

async def grup_id_ver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ Bu komut sadece gruplarda çalışır.")
        return
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title
    text = f"ℹ️ <b>Grup Bilgileri:</b>\n\n📛 <b>Grup Adı:</b> {chat_title}\n🆔 <b>Grup ID:</b> <code>{chat_id}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_spam(update.effective_user.id):
        await update.message.reply_text(
            "⚠️ Çok hızlısın! Lütfen 3 saniye bekle."
        )
        return

    user = update.message.from_user.first_name

    if update.message.reply_to_message:
        hedef = update.message.reply_to_message.from_user.first_name

   
    elif context.args:
        hedef = context.args[0]

    mesaj = random.choice(SLAP_LIST)

    await update.message.reply_text(
        mesaj.format(a=user, b=hedef)
    )

async def sans(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if is_spam(update.effective_user.id):
        return

    user = update.message.from_user
    mention = f"[{user.first_name}](tg://user?id={user.id})"

    oran = random.randint(1, 100)
    yorum = random.choice(SANS_YORUMLARI)

    text = f"{mention} 🍀 Bugünkü şansın %{oran}\n\n{yorum}"

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )


async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if is_spam(update.effective_user.id):
        return

    user = update.message.from_user
    mention = f"[{user.first_name}](tg://user?id={user.id})"

    yorum = random.choice(MOOD_YORUMLARI)

    text = f"{mention} {yorum}"

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )


async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if is_spam(update.effective_user.id):
        return

    user = update.message.from_user
    mention = f"[{user.first_name}](tg://user?id={user.id})"

    mesaj = random.choice(ROAST_LIST)

    text = f"{mention} {mesaj}"

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if is_spam(query.from_user.id): return
    try: await query.answer()
    except: pass

    if query.data == "dogruluk":
        await user_reply(query.message, query.from_user, f"doğruluk seçtin 😈\n\n🧐 Soru:\n{random.choice(DOGRULUK)}")
        return  

   
    elif query.data == "cesaret":
        await user_reply(query.message, query.from_user, f"cesaret seçtin 🔥\n\n😈 Görev:\n{random.choice(CESARET)}")
        return

    
    elif query.data == "soz":
        await user_reply(query.message, query.from_user, random.choice(SOZ))
        return
        
    
    elif query.data == "help_menu":
        help_text = (
    "📖 <b>Zuzu Komut Rehberi</b>\n\n"

    "🎮 <b>Eğlence</b>\n"
    "• /d → Doğruluk sorusu\n"
    "• /c → Cesaret görevi\n"
    "• /soz → Günlük motivasyon\n"
    "• /slap @kullanici → Minik şaka\n"
    "• /roast → Zuzu seni roastlasın\n"
    "• /hd → Hava Durumu (şehir)\n\n"

    "💞 <b>Sosyal</b>\n"
    "• /ship @kullanici → Uyumluluk testi 💕\n"
    "• /burc → Burç yorumu \n"
    "• /sans → Günlük şansın \n"
    "• /mood → Ruh hali analizi \n\n"

    "✨ Zuzu burada seni eğlendirmek için var 🐾"
)
        await query.message.edit_text(text=help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Ana Menüye Dön", callback_data="back_to_start")]]))
        return
        
    
    elif query.data == "back_to_start":
        kullanici = query.from_user.first_name
        chat_type = query.message.chat.type

        if chat_type == "private":
            text = (
                f"🐾 <b>Selam {kullanici}! Ben Zuzu!</b>\n\n"
                f"Gruplarınızı canlandırmak, eğlenceli oyunlar oynamak ve "
                f"Kısacası grubunuzun kedisiyim.🐈\n\n"
                f"👇 Aşağıdaki menüden tüm komutlarıma ulaşabilir, benimle iletişime geçebilir "
                f"ya da beni direkt kendi grubuna davet edebilirsin!"
            )
            keyboard = [
                [InlineKeyboardButton("📜 Komutlar & Açıklamalar", callback_data="help_menu")],
                [InlineKeyboardButton("📢 Duyurular", url=DUYURU_CHANNEL_URL), InlineKeyboardButton("💬 Destek / Sorun", url=SUPPORT_GROUP_URL)],
                [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"), InlineKeyboardButton("👤 İletişim", url=MY_PROFILE_URL)]
            ]
        else:
            text = (
                f"✨ <b>Zuzu grupta aktif!</b>\n\n"
                f"👤 Hoş geldin {kullanici}!\n"
                f"🎯 Eğlenmek ve oyun oynamak için komutlarımı kullanabilirsin.\n\n"
                f"👇 Komut listesini görmek için aşağıdaki butona tıkla!"
            )
            keyboard = [[InlineKeyboardButton("📜 Tüm Komutlar", callback_data="help_menu")]]
            
        await query.message.edit_text(text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    else:
        await query.message.answer("❌ Geçersiz işlem")

async def log_private_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if update.effective_chat and update.effective_chat.type == "private":
        user = update.effective_user
        if not update.message or not update.message.text:
            return

        mesaj_metni = update.message.text
        
       
        if mesaj_metni.startswith("/"):
            return

        
        user_link = f'<a href="tg://user?id={user.id}">{user.first_name} {user.last_name or ""}</a>'

        log_mesaji = (
            f"📩 <b>[DM MESAJ LOGU]</b>\n\n"
            f"👤 <b>Kullanıcı:</b> {user_link}\n"
            f"🆔 <b>Kullanıcı ID:</b> <code>{user.id}</code>\n"
            f"✍️ <b>Kullanıcı Adı:</b> @{user.username or 'Yok'}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💬 <b>Mesajı:</b>\n<i>{mesaj_metni}</i>"
        )

        try:
            
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_CHAT,
                text=log_mesaji,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Log kanalına mesaj gönderilemedi: {e}")

async def error_handler(update, context):
    logger.exception(context.error)

    hata_mesaji = (
        f"🚨 <b>[BOT ÇÖKME / HATA LOGU]</b>\n\n"
        f"❌ <b>Hata Detayı:</b>\n<code>{context.error}</code>\n\n"
        f"📌 <i>Lütfen konsolu veya bot.log dosyasını kontrol et!</i>"
    )
    
    try:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_CHAT,
            text=hata_mesaji,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Hata log kanalına gönderilemedi: {e}")
       
    
if __name__ == "__main__":

        keep_alive()

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("d", dogruluk))
app.add_handler(CommandHandler("c", cesaret))
app.add_handler(CommandHandler("soz", soz))
app.add_handler(CommandHandler("ship", ship))
app.add_handler(CommandHandler("burc", burc_yorumu))
app.add_handler(CommandHandler("grup_id", grup_id_ver))
app.add_handler(CommandHandler("slap", slap))
app.add_handler(CommandHandler("sans", sans))
app.add_handler(CommandHandler("mood", mood))
app.add_handler(CommandHandler("roast", roast))
app.add_handler(CommandHandler("hd", hd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, zuzu_listener))
app.add_handler(CallbackQueryHandler(weather_callback, pattern=r"^hd"))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, log_private_messages))
   
    
app.add_error_handler(error_handler)

logger.info("Bot çalışıyor...")
app.run_polling(drop_pending_updates=True)