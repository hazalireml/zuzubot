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

xp_data = {}
xp_dirty = False
XP_FILE = "xp_data.json"

def load_json(filename):
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"{filename} yükleme hatası: {e}")
        return {}
xp_data = load_json(XP_FILE)

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


def calculate_level(xp):

    return int(xp ** 0.5 // 10) + 1


def add_xp(user_id, amount):
    global xp_dirty

    user_id = str(user_id)

    if user_id not in xp_data:
        xp_data[user_id] = {
            "xp": 0 }
        
    xp_data[user_id]["xp"] += amount
    xp_dirty = True


def get_user_xp(user_id):

    user_id = str(user_id)

    if user_id not in xp_data:
        return 0

    return xp_data[user_id]["xp"]

async def user_reply(message, user, text):
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    full_text = f"{mention} {text}"
    await message.reply_text(text=full_text, parse_mode="Markdown")


DOGRULUK = [
    "En son kime mesaj attın?",
    "Bugün en çok kimi düşündün?",
    "Şu an gruptan en çok kimi merak ediyorsun?",
    "Hiç gruptan birine gizlice sinir oldun mu?",
    "Burada en çok kimin mesajlarını okuyorsun ama yazmıyorsun?",
    "Şu an birine sinirli misin? Kime?",
    "Son 24 saatte yalan söylediğin bir şey var mı?",
    "Grupta en “cool” bulduğun kişi kim?",
    "Buradaki birine crushın var mı? Kim?",
    "En utanç verici anını anlatmak zorunda olsan ne olurdu?",
    "Hiç stalk yaptığın biri var mı? Kim?",
    "Bu grupta sevgili yapmak istesen kimi seçerdin?",
    "En son kimi kıskandın ve neden?",
    "Şu an gruptan birini susturma hakkın olsa kim olurdu?",
    "Bir kişiyi gruptan silme hakkın olsa kim olurdu?",
    "En fake bulduğun kişi kim? (şaka amaçlı 😄)",
    "Burada “en deli” kişi kim sence?",
    "Kim bu grupta en çok drama çıkarıyor?",
    "Kendinde en çok sevmediğin ama değiştirmeye cesaret edemediğin şey ne?",
    "Kendine en çok yalan söylediğin konu ne?",
    "Gerçekte olduğun kişiyle olmak istediğin kişi arasında ne fark var?",
    "Seni en çok sen yapan şey sence ne?",
    "Son zamanlarda kendin hakkında fark ettiğin bir gerçek var mı?",
    "En son ne zaman gerçekten “iyi hissettim” dedin?",
    "İçinde tuttuğun ama kimseye söylemediğin bir düşünce var mı?",
    "Seni en çok ne yorar: insanlar mı, düşüncelerin mi?",
    "Bir şeyi asla unutamayacağını düşündüğün bir an var mı?",
    "Sessiz kaldığında aklına en çok ne geliyor?",
    "Bir insana güvenmen için ne olması gerekir?",
    "Hiç “hak etmiyor ama seviyorum” dediğin biri oldu mu?",
    "İnsanları hızlı mı yargılıyorsun yoksa şans mı verirsin?",
    "Birini gerçekten sevdiğini nasıl anlarsın?",
    "Seni en çok hayal kırıklığına uğratan şey insanlar mı beklentilerin mi?",
    "Keşke geri dönüp değiştirebilseydim dediğin bir an var mı?",
    "Geçmişin seni mi şekillendirdi yoksa seni mi kırdı?",
    "5 yıl önceki halin seni görse ne derdi?",
    "Gelecekteki sen bugünkü haline ne söylerdi?",
    "Hayatında “o an her şey değişti” dediğin bir an var mı?",
    "Mutluluk sence bir hedef mi yoksa alışkanlık mı?",
    "Kendinle yalnız kalmak sana iyi mi geliyor yoksa rahatsız mı ediyor?",
    "İnsanlar gerçekten değişir mi yoksa sadece maskelerini mi değiştirir?",
    "Hayatta en çok neyi anlamaya çalışıyorsun?",
    "Sence “kendin olmak” ne demek?",
    "En büyük pişmanlığın ne?",
    "En son kimi stalkladın?",
    "Hiç kimseye söylemediğin bir sır var mı?",
    "Şu an hoşlandığın biri var mı?",
    "Hayatındaki en utanç verici an neydi?"

]

CESARET = [

    "Şu anki ruh halini tek bir emoji ile anlat 💛",
    "En son dinlediğin şarkıyı yaz 🎧",
    "3 saniye içinde aklına gelen ilk kelimeyi söyle 🌼",
    "Kendine bugün bir iltifat yap 💬",
    "Grupta en çok güvendiğin kişiyi söyle 🌙",
    "Şu an aklından geçen ilk şeyi dürüstçe yaz ✨",
    "Bir kişiyi sadece 1 kelimeyle tanımla 💭",
    "Kendinle ilgili kimsenin bilmediği bir özelliği söyle 🌼",
    "Bugün pişman olduğun bir şeyi paylaş 💔",
    "En son utandığın anı kısaca anlat 🌷",
    "Bir kişiye gizli bir iltifat yap 💌",
    "En çok özlediğin kişiyi yaz 💭",
    "Bugün kim seni mutlu ettiyse söyle 🌸",
    "Şu anki ruh halini 1 cümleyle anlat 🌙",
    "En sevdiğin emojiyle kendini tanıt 💫",
    "Son düşündüğün şeyi yaz ✨",
    "Telefonundaki son fotoğrafın konusunu söyle 📸",
    "Bugün seni en çok ne güldürdü yaz 🌼",
    "Kimseye söylemediğin bir düşünceni paylaş ✨",
    "Kendinde değiştirmek istediğin bir şey nedir? 🌿",
    "Son zamanlarda seni değiştiren bir olay yaz 💭",
    "Birine içinden geçen ama söylemediğin bir şeyi yaz 🤍",
    "Zuzu’ya bugün nasıl hissettiğini anlat 🌼",
    "Zuzu’ya bir soru sorabilirsin 💫",
    "Zuzu seni tek kelimeyle tanımlasaydı ne olurdu? 🌙",
    "Zuzu’ya bir sır fısılda 🤍",
    "Zuzu’ya bir dilek bırak 🌸",
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
    "🤍 Kendine verdiğin değer, dünyaya nasıl baktığını değiştirir.",
    "🤍 Başkalarının sana inanmasını bekleme, önce kendine inan!"
]

SLAP_LIST = [ 


    "🩴 {a}, {b}'a terlikle girişti 😂",
    "📺 {a}, {b}'nin üstüne televizyon fırlattı.",
    "🥛 {a}, {b}'nin kafasına yoğurt döktü.",
    "🪑 {a}, {b}'a sandalye attı 💀",
    "🧃 {a}, {b}'nin suratına meyve suyu sıktı.",
    "🛏️ {a}, {b}’a yumuşak bir yastık fırlattı 🛏️",
    "✈️ {a}, {b}’nin kafasına kağıt uçak attı ✈️",
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
    "😼 Zuzu bugün sana güveniyor.",
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
    "☀️ Enerjin yükseliyor, bugün daha iyi hissedeceksin.",
    "🌙 Biraz kafa dinlemeye ihtiyacın var gibi.",
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
            f"• <b>Küçük etkileşimler sunarım</b>\n"
            f"• <b>XP sistemi ile rekabet oluştururum</b> 🐈\n\n"
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

    if not context.args:
        await update.message.reply_text("💘 Birini etiketlemelisin!\nÖrnek: /ship @kullanici")
        return

    user1 = update.message.from_user.first_name
    user2 = context.args[0]

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

async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    xp = get_user_xp(user.id)

    level = calculate_level(xp)

    sonraki_level_xp = (level * 10) ** 2

    text = (
        f"🏆 <b>{user.first_name} Profili</b>\n\n"
        f"⭐ Level: <b>{level}</b>\n"
        f"✨ XP: <b>{xp}</b>\n"
        f"🎯 Sonraki level için: <b>{sonraki_level_xp - xp} XP</b>"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )

async def lider(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not xp_data:
        await update.message.reply_text(
            "😿 Henüz kimse XP kazanmamış."
        )
        return

    sorted_users = sorted(
        xp_data.items(),
        key=lambda x: x[1]["xp"],
        reverse=True
    )

    text = "👑 <b>Zuzu'nun Liderleri</b>\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for index, (user_id, data) in enumerate(sorted_users[:10]):

        try:
            user = await context.bot.get_chat(user_id)
            name = user.first_name

        except:
            name = "Bilinmeyen Kullanıcı"
        xp = data["xp"]
        level = calculate_level(xp)

        if index < 3:
            icon = medals[index]
        else:
            icon = "✨"

        text += (
            f"{icon} <b>{name}</b>\n"
            f"└ ⭐ Level {level} • {xp} XP\n\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )

async def grup_id_ver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ Bu komut sadece gruplarda çalışır.")
        return
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title
    text = f"ℹ️ <b>Grup Bilgileri:</b>\n\n📛 <b>Grup Adı:</b> {chat_title}\n🆔 <b>Grup ID:</b> <code>{chat_id}</code>\n\n🤫"
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

async def message_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type == "private":
        return

    if not update.message:
        return

    user_id = update.effective_user.id

    add_xp(user_id, random.randint(2, 5))

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
    "• /roast → Zuzu seni roastlasın\n\n"

    "💞 <b>Sosyal</b>\n"
    "• /ship @kullanici → Uyumluluk testi 💕\n"
    "• /burc → Burç yorumu \n\n"
    "• /sans → Günlük şansın \n"
    "• /mood → Ruh hali analizi \n\n"

    "🏆 <b>Seviye Sistemi</b>\n"
    "• /rank → Profilin \n"
    "• /lider → Lider tablosu \n\n"

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
       
    
async def auto_save():
    global xp_dirty

    while True:
        await asyncio.sleep(30)

        if xp_dirty:
            save_json(XP_FILE, xp_data)
            xp_dirty = False
            logger.info("XP verisi kaydedildi.")


if __name__ == "__main__":

    keep_alive()

    app = Application.builder().token(TOKEN).build()

    async def post_init(app):
        asyncio.create_task(auto_save())

    app.post_init = post_init 

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("d", dogruluk))
    app.add_handler(CommandHandler("c", cesaret))
    app.add_handler(CommandHandler("soz", soz))
    app.add_handler(CommandHandler("ship", ship))
    app.add_handler(CommandHandler("burc", burc_yorumu))
    app.add_handler(CommandHandler("grup_id", grup_id_ver))
    app.add_handler(CommandHandler("rank", rank))
    app.add_handler(CommandHandler("slap", slap))
    app.add_handler(CommandHandler("lider", lider))
    app.add_handler(CommandHandler("sans", sans))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("roast", roast))


    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, log_private_messages))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_xp))
    
    app.add_error_handler(error_handler)

    logger.info("Bot çalışıyor...")
    app.run_polling(drop_pending_updates=True)