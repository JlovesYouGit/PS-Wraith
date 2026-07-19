"""
wallet.py — Mana Ciel Wallet
SHA-256 / Base58 P2PKH Bitcoin wallet generation with seed phrase.
Stores credentials in JSON.
"""

import hashlib
import json
import os
import secrets
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import base58
from ecdsa import SigningKey, SECP256k1

from engine.core.constants import ANCHOR_CONST, RANGE_MIN, RANGE_MAX

from mana_ciel.coordinate import SynergyCoordinate

BASE_WORDLIST = [
    "abandon","ability","able","about","above","absent","absorb","abstract","absurd","abuse",
    "access","accident","account","accuse","achieve","acid","acoustic","acquire","across","act",
    "action","actor","actual","adapt","add","addict","address","adjust","admit","adult",
    "advance","advice","aerobic","affair","afford","afraid","again","age","agent","agree",
    "ahead","aim","air","airport","aisle","alarm","album","alcohol","alert","alien",
    "all","alley","allow","almost","alone","alpha","already","also","alter","always",
    "amateur","amazing","among","amount","amused","analyst","anchor","ancient","anger","angle",
    "angry","animal","ankle","announce","annual","another","answer","antenna","antique","anxiety",
    "any","apart","apology","appear","apple","approve","april","arch","arctic","area",
    "arena","argue","armed","armor","army","around","arrange","arrest","arrive","arrow",
    "art","artefact","artist","artwork","ask","aspect","assault","asset","assist","assume",
    "asthma","athlete","atom","attack","attend","attitude","attract","auction","audit","august",
    "aunt","author","auto","autumn","average","avocado","avoid","awake","aware","awesome",
    "awful","awkward","axis","baby","bachelor","bacon","badge","bag","balance","balcony",
    "ball","bamboo","banana","banner","bar","barely","bargain","barrel","base","basic",
    "basket","battle","beach","bean","beauty","because","become","beef","before","begin",
    "behave","behind","believe","below","belt","bench","benefit","best","betray","better",
    "between","beyond","bicycle","bid","bike","bind","biology","bird","birth","bitter",
    "black","blade","blame","blanket","blast","bleak","bless","blind","blood","blossom",
    "blow","blue","blur","blush","board","boat","body","boil","bomb","bone",
    "bonus","book","boost","border","boring","borrow","boss","bottom","bounce","box",
    "boy","bracket","brain","brand","brass","brave","bread","breeze","brick","bridge",
    "brief","bright","bring","brisk","broccoli","broken","bronze","broom","brother","brown",
    "brush","bubble","buddy","budget","buffalo","build","bulb","bulk","bullet","bundle",
    "burden","burger","burst","bus","business","busy","butter","buyer","buzz","cabbage",
    "cabin","cable","cactus","cage","cake","call","calm","camera","camp","can",
    "canal","cancel","candy","cannon","canoe","canvas","canyon","capable","capital","captain",
    "car","carbon","card","cargo","carpet","carry","cart","case","cash","casino",
    "castle","casual","cat","catalog","catch","category","cattle","caught","cause","caution",
    "cave","ceiling","celery","cement","census","century","cereal","certain","chair","chalk",
    "champion","change","chaos","chapter","charge","chase","cheap","check","cheese","chef",
    "cherry","chest","chicken","chief","child","chimney","choice","choose","chronic","chuckle",
    "chunk","churn","citizen","city","civil","claim","clap","clarify","claw","clay",
    "clean","clerk","clever","click","client","cliff","climb","clinic","clip","clock",
    "clog","close","cloth","cloud","clown","club","clump","cluster","clutch","coach",
    "coast","coconut","code","coffee","coil","coin","collect","color","column","combine",
    "come","comfort","comic","common","company","concert","conduct","confirm","congress","connect",
    "consider","control","convince","cook","cool","copper","copy","coral","core","corn",
    "correct","cost","cotton","couch","country","couple","course","cousin","cover","coyote",
    "crack","cradle","craft","cram","crane","crash","crater","crawl","crazy","cream",
    "credit","creek","crew","cricket","crime","crisp","critic","crop","cross","crouch",
    "crowd","crucial","cruel","cruise","crumble","crunch","crush","cry","crystal","cube",
    "culture","cup","cupboard","curious","current","curtain","curve","cushion","custom","cute",
    "cycle","dad","damage","damp","dance","danger","daring","dash","daughter","dawn",
    "day","deal","debate","debris","decade","december","decide","decline","decorate","decrease",
    "deer","defense","define","defy","degree","delay","deliver","demand","demise","denial",
    "dentist","deny","depart","depend","deposit","depth","deputy","derive","describe","desert",
    "design","desk","despair","destroy","detail","detect","develop","device","devote","diagram",
    "dial","diamond","diary","dice","diesel","diet","differ","digital","dignity","dilemma",
    "dinner","dinosaur","direct","dirt","disagree","discover","disease","dish","dismiss","disorder",
    "display","distance","divert","divide","divorce","dizzy","doctor","document","dog","doll",
    "dolphin","domain","donate","donkey","donor","door","dose","double","dove","draft",
    "dragon","drama","drastic","draw","dream","dress","drift","drill","drink","drip",
    "drive","drop","drum","dry","duck","dumb","dune","during","dust","dutch",
    "duty","dwarf","dynamic","eager","eagle","early","earn","earth","easily","east",
    "easy","echo","ecology","economy","edge","edit","educate","effort","egg","eight",
    "either","elbow","elder","electric","elegant","element","elephant","elevator","elite","else",
    "embark","embody","embrace","emerge","emotion","employ","empower","empty","enable","enact",
    "end","endless","endorse","enemy","energy","enforce","engage","engine","enhance","enjoy",
    "enlist","enough","enrich","enroll","ensure","enter","entire","entry","envelope","episode",
    "equal","equip","era","erase","erode","erosion","error","erupt","escape","essay",
    "essence","estate","eternal","ethics","evidence","evil","evoke","evolve","exact","example",
    "excess","exchange","excite","exclude","excuse","execute","exercise","exhaust","exhibit","exile",
    "exist","exit","exotic","expand","expect","expire","explain","expose","express","extend",
    "extra","eye","eyebrow","fabric","face","faculty","fade","faint","faith","fall",
    "false","fame","family","famous","fan","fancy","fantasy","farm","fashion","fat",
    "fatal","father","fatigue","fault","favorite","feature","february","federal","fee","feed",
    "feel","female","fence","festival","fetch","fever","few","fiber","fiction","field",
    "figure","file","film","filter","final","find","fine","finger","finish","fire",
    "firm","fiscal","fish","fit","fitness","fix","flag","flame","flash","flat",
    "flavor","flee","flight","flip","float","flock","floor","flower","fluid","flush",
    "fly","foam","focus","fog","foil","fold","follow","food","foot","force",
    "forest","forget","fork","fortune","forum","forward","fossil","foster","found","fox",
    "fragile","frame","frequent","fresh","friend","fringe","frog","front","frost","frown",
    "fruit","fuel","fun","funny","furnace","fury","future","gadget","gain","galaxy",
    "gallery","game","gap","garage","garbage","garden","garlic","garment","gas","gasp",
    "gate","gather","gauge","gaze","general","genius","genre","gentle","genuine","gesture",
    "ghost","giant","gift","giggle","ginger","giraffe","girl","give","glad","glance",
    "glare","glass","glide","glimpse","globe","gloom","glory","glove","glow","glue",
    "goat","goddess","gold","good","goose","gorilla","gorilla","gospel","gossip","govern",
    "grace","grain","grant","grape","grass","gravity","great","green","grid","grief",
    "grit","grocery","group","grow","grunt","guard","guess","guide","guilt","guitar",
    "gun","gym","habit","hair","half","hammer","hamster","hand","happy","harbor",
    "hard","harsh","harvest","hat","have","hawk","hazard","head","health","heart",
    "heavy","hedgehog","height","hello","helmet","help","hen","hero","hidden","high",
    "hill","hint","hip","hire","history","hobby","hockey","hold","hole","holiday",
    "hollow","home","honey","hood","hope","horn","horror","horse","hospital","host",
    "hotel","hour","hover","hub","huge","human","humble","humor","hundred","hungry",
    "hunt","hurdle","hurry","hurt","husband","hybrid","ice","icon","idea","identify",
    "idle","ignore","ill","illegal","illness","image","imitate","immense","immune","impact",
    "impose","improve","impulse","inch","include","income","increase","index","indicate","indoor",
    "industry","infant","inflict","inform","inhale","inherit","initial","inject","injury","inmate",
    "inner","innocent","input","inquiry","insane","insect","inside","inspire","install","intact",
    "interest","into","invest","invite","involve","iron","island","isolate","issue","item",
    "ivory","jacket","jaguar","jar","jazz","jealous","jeans","jelly","jewel","job",
    "join","joker","journey","joy","judge","juice","jump","jungle","junior","junk",
    "just","kangaroo","keen","keep","ketchup","key","kick","kid","kidney","kind",
    "kingdom","kiss","kitchen","kite","kitten","kiwi","knee","knife","knock","know",
    "lab","label","labor","ladder","lady","lake","lamp","language","laptop","large",
    "later","latin","laugh","laundry","lava","law","lawn","lawsuit","layer","lazy",
    "leader","leaf","learn","leave","lecture","left","leg","legal","legend","leisure",
    "lemon","lend","length","lens","leopard","lesson","letter","level","liar","liberty",
    "library","license","life","lift","light","like","limb","limit","link","lion",
    "liquid","list","little","live","lizard","load","loan","lobster","local","lock",
    "logic","lonely","long","loop","lottery","loud","lounge","love","loyal","lucky",
    "luggage","lumber","lunar","lunch","luxury","lyrics","machine","mad","magic","magnet",
    "maid","mail","main","major","make","mammal","man","manage","mandate","mango",
    "mansion","manual","maple","marble","march","margin","marine","market","marriage","mask",
    "mass","master","match","material","math","matrix","matter","maximum","maze","meadow",
    "mean","measure","meat","mechanic","medal","media","melody","melt","member","memory",
    "mention","menu","mercy","merge","merit","merry","mesh","message","metal","method",
    "middle","midnight","milk","million","mimic","mind","minimum","minor","minute","miracle",
    "mirror","misery","miss","mistake","mix","mixed","mixture","mobile","model","modify",
    "mom","moment","monitor","monkey","monster","month","moon","moral","more","morning",
    "mosquito","mother","motion","motor","mountain","mouse","move","movie","much","muffin",
    "mule","multiply","muscle","museum","mushroom","music","must","mysterious","myth","naive",
    "name","napkin","narrow","nasty","nation","nature","near","neck","need","negative",
    "neglect","neither","nephew","nerve","nest","network","neutral","never","news","next",
    "nice","night","noble","noise","nominee","noodle","normal","north","nose","notable",
    "note","nothing","notice","novel","now","nuclear","number","nurse","nut","oak",
    "obey","object","oblige","obscure","observe","obtain","obvious","occur","ocean","october",
    "odor","offer","office","often","oil","okay","old","olive","olympic","omit",
    "once","one","onion","online","only","open","opinion","oppose","option","orange",
    "orbit","orchard","order","ordinary","organ","orient","original","orphan","ostrich","other",
    "outdoor","outer","output","outside","oval","oven","over","own","owner","oxygen",
    "oyster","ozone","pact","paddle","page","pair","palace","palm","panda","panel",
    "panic","panther","paper","parent","park","parrot","party","pass","patch","path",
    "patient","pattern","pause","pave","payment","peace","peanut","pear","peasant","pelican",
    "pen","penalty","pencil","people","pepper","perfect","permit","person","pet","phone",
    "photo","phrase","physical","piano","picnic","picture","piece","pig","pigeon","pill",
    "pilot","pink","pioneer","pipe","pistol","pitch","pizza","place","planet","plastic",
    "plate","play","please","pledge","pluck","plug","plunge","poem","poet","point",
    "polar","pole","police","pond","pony","pool","popular","portion","position","possible",
    "post","potato","pottery","poverty","powder","power","practice","praise","predict","prefer",
    "prepare","present","pretty","prevent","price","pride","primary","print","priority","prison",
    "private","prize","problem","process","produce","profit","program","project","promote","proof",
    "property","prosper","protect","proud","provide","public","pudding","pull","pulp","pulse",
    "pumpkin","punch","pupil","puppy","purchase","purity","purpose","purse","push","put",
    "puzzle","pyramid","quality","quantum","quarter","question","quick","quit","quiz","quote",
    "rabbit","raccoon","race","rack","radar","radio","rail","rain","raise","rally",
    "ramp","ranch","range","rapid","rare","rate","rather","raw","razen","read",
    "real","reason","rebel","rebuild","recall","receive","recipe","record","recycle","reduce",
    "reflect","reform","refuse","region","regret","regular","reject","relax","release","relief",
    "rely","remain","remember","remind","remove","render","renew","rent","reopen","repair",
    "repeat","replace","report","require","rescue","resemble","resist","resource","response","result",
    "retire","retreat","return","reunion","reveal","review","reward","rhythm","rib","ribbon",
    "rice","rich","ride","ridge","rifle","right","rigid","ring","riot","ripple",
    "risk","ritual","rival","river","road","roast","robot","robust","rocket","romance",
    "roof","rookie","room","rose","rotate","rough","round","route","royal","rubber",
    "rude","rug","rule","run","runway","rural","sad","saddle","sadness","safe",
    "sail","salad","salmon","salon","salt","salute","same","sample","sand","satisfy",
    "satoshi","sauce","sausage","save","say","scale","scan","scare","scatter","scene",
    "scheme","school","science","scissors","scorpion","scout","scrap","screen","script","scrub",
    "sea","search","season","seat","second","secret","section","security","seed","seek",
    "segment","select","sell","seminar","senior","sense","sentence","series","service","session",
    "settle","setup","seven","shadow","shaft","shallow","share","shed","shell","sheriff",
    "shield","shift","shine","ship","shiver","shock","shoe","shoot","shop","short",
    "shoulder","shove","shrimp","shrug","shuffle","shy","sibling","sick","side","siege",
    "sight","sign","silent","silk","silly","silver","similar","simple","since","sing",
    "siren","sister","situate","six","size","skate","sketch","ski","skill","skin",
    "skirt","skull","slab","slam","sleep","slender","slice","slide","slight","slim",
    "slogan","slot","slow","slush","small","smart","smile","smoke","smooth","snack",
    "snake","snap","sniff","snow","soap","soccer","social","sock","soda","soft",
    "solar","soldier","solid","solution","solve","someone","song","soon","sorry","sort",
    "soul","sound","soup","source","south","space","spare","spatial","speak","special",
    "speed","spell","spend","sphere","spice","spider","spike","spin","spirit","split",
    "sponsor","spoon","sport","spot","spray","spread","spring","spy","square","squeeze",
    "squirrel","stable","stadium","staff","stage","stairs","stamp","stand","start","state",
    "stay","steak","steel","stem","step","stereo","stick","still","sting","stock",
    "stomach","stone","stool","story","stove","strategy","street","strike","strong","struggle",
    "student","stuff","stumble","style","subject","submit","subway","success","such","sudden",
    "suffer","sugar","suggest","suit","summer","sun","sunny","sunset","super","supply",
    "supreme","sure","surface","surge","surprise","surround","survey","suspect","sustain","swallow",
    "swamp","swap","swarm","swear","sweet","swift","swim","swing","switch","sword",
    "symbol","symptom","syrup","system","table","tackle","tag","tail","talent","talk",
    "tank","tape","target","task","taste","tattoo","taxi","teach","team","tell",
    "ten","tenant","tennis","tent","term","test","text","thank","that","theme",
    "then","theory","there","they","thing","this","thought","three","thrive","throw",
    "thumb","thunder","ticket","tide","tiger","tilt","timber","time","tiny","tip",
    "tired","tissue","title","toast","tobacco","today","toddler","toe","together","toilet",
    "token","tomato","tomorrow","tone","tongue","tonight","tool","tooth","top","topic",
    "topple","torch","tornado","torpedo","total","tourist","toward","tower","town","toy",
    "track","trade","traffic","tragic","train","transfer","trap","trash","travel","tray",
    "treat","tree","trend","trial","tribe","trick","trigger","trim","trip","trophy",
    "trouble","truck","true","truly","trumpet","trust","truth","try","tube","tuition",
    "tumble","tuna","tunnel","turkey","turn","turtle","twelve","twenty","twice","twin",
    "twist","two","type","typical","ugly","umbrella","unable","unaware","uncle","uncover",
    "under","undo","unfair","unfold","unhappy","uniform","unique","unit","universe","unknown",
    "unlock","until","unusual","unveil","update","upgrade","uphold","upon","upper","upset",
    "urban","urge","usage","use","used","useful","useless","usual","utility","vacant",
    "vacuum","vague","valid","valley","valve","van","vanish","vapor","various","vast",
    "vault","vehicle","velvet","vendor","venture","venue","verb","verify","version","very",
    "vessel","veteran","viable","vibrant","vicious","victory","video","view","village","vintage",
    "violin","virtual","virus","visa","visit","visual","vital","vivid","vocal","voice",
    "void","volcano","volume","vote","voyage","wage","wagon","wait","walk","wall",
    "walnut","want","warfare","warm","warrior","wash","wasp","waste","water","wave",
    "way","wealth","weapon","wear","weasel","weather","web","wedding","weekend","weird",
    "welcome","west","wet","whale","what","wheat","wheel","when","where","whip",
    "whisper","wide","width","wife","wild","will","win","window","wine","wing",
    "wink","winner","winter","wire","wisdom","wise","wish","witness","wolf","woman",
    "wonder","wood","wool","word","work","world","worry","worth","wrap","wreck",
    "wrestle","wrist","write","wrong","yard","year","yellow","you","young","youth",
    "zebra","zero","zone","zoo"
]


def _entropy_to_mnemonic(entropy: bytes) -> list[str]:
    checksum = hashlib.sha256(entropy).digest()[: len(entropy) // 4]
    bits = int.from_bytes(entropy + checksum, "big")
    words: list[str] = []
    for _ in range(12):
        idx = bits & 0x7FF
        words.append(BASE_WORDLIST[idx])
        bits >>= 11
    return words[::-1]


def _mnemonic_to_seed(mnemonic: list[str], passphrase: str = "") -> bytes:
    salt = f"mnemonic{passphrase}".encode()
    return hashlib.pbkdf2_hmac("sha512", " ".join(mnemonic).encode(), salt, 2048, dklen=64)


def _seed_to_priv_key(seed: bytes) -> bytes:
    return hashlib.sha512(seed).digest()[:32]


class ManaCielWallet:
    """
    Bitcoin P2PKH wallet generated in Mana Ciel synergy space.
    Coordinates: -16 to 1000.
    """

    def __init__(self, storage_dir: str | None = None):
        if storage_dir is None:
            storage_dir = str(Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "wallets")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _formula_seed(self, coord: int | None = None) -> bytes:
        from mana_ciel.formula import cumulative_intelligence
        c = SynergyCoordinate(coord)
        n = cumulative_intelligence(10)
        return hashlib.sha256(f"{ANCHOR_CONST}:coord:{c.value}:n:{n}:MCIEL".encode()).digest()

    def _derive_from_seed(self, seed: bytes, coord_value: int | None = None) -> dict:
        if coord_value is None:
            coord_value = self._seed_to_coordinate(seed)
        priv_bytes = hashlib.sha512(seed).digest()[:32]
        sk = SigningKey.from_string(priv_bytes, curve=SECP256k1)
        vk = sk.verifying_key
        pub_bytes = vk.to_string()
        prefix = b"\x02" if pub_bytes[63] % 2 == 0 else b"\x03"
        compressed_pub = prefix + pub_bytes[:32]

        sha = hashlib.sha256(compressed_pub).digest()
        ripemd = hashlib.new("ripemd160")
        ripemd.update(sha)
        h160 = ripemd.digest()
        versioned = b"\x00" + h160
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        addr = base58.b58encode(versioned + checksum).decode("ascii")

        coord_obj = SynergyCoordinate(coord_value)
        utxo = int(h160.hex(), 16) % 1_000_000_000

        return {
            "label": "ManaCiel",
            "seed_phrase": " ".join(_entropy_to_mnemonic(seed[:16])),
            "seed_entropy_hex": seed[:16].hex(),
            "private_key_hex": priv_bytes.hex(),
            "public_key_hex": compressed_pub.hex(),
            "address": addr,
            "address_hash160": h160.hex(),
            "utxo_collective_value": utxo,
            "sha256_sum": hashlib.sha256(priv_bytes).hexdigest(),
            "coordinate": coord_obj.to_dict(),
            "base58_p2pkh": addr,
            "p2pkh_version": "00",
            "network": "mainnet",
            "formula_seed_hex": seed.hex(),
        }

    def _seed_to_coordinate(self, seed: bytes) -> int:
        raw = int.from_bytes(seed[:4], "big")
        return ((raw % (RANGE_MAX - RANGE_MIN)) + RANGE_MIN)

    def generate(self, coord: int | None = None, label: str = "ManaCiel") -> dict:
        seed = self._formula_seed(coord=coord)
        wallet = self._derive_from_seed(seed, coord_value=coord)
        wallet["label"] = label
        self.save(wallet)
        return wallet

    def derive_for_address(self, target_address: str) -> dict | None:
        seed = self._address_seed(target_address)
        wallet = self._derive_from_seed(seed, coord_value=None)
        wallet["label"] = f"ManaCiel:{target_address[:8]}"
        wallet["coordinate"]["derivation_mode"] = "target_address_direct"
        self.save(wallet)
        return wallet

    def _wallet_path(self, wallet: dict) -> Path:
        safe_label = wallet.get("label", "wallet").replace(" ", "_").replace("/", "_")
        safe_addr = wallet.get("address", "unknown").replace("/", "_")
        return self.storage_dir / f"{safe_label}__{safe_addr}.json"

    def save(self, wallet: dict) -> Path:
        path = self._wallet_path(wallet)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(wallet, f, indent=2, default=str)
        return path

    def load_latest(self) -> dict | None:
        if not self.storage_dir.exists():
            return None
        files = sorted(self.storage_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            return None
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)

    def load_all(self) -> list[dict]:
        if not self.storage_dir.exists():
            return []
        out = []
        for path in sorted(self.storage_dir.glob("*.json"), key=lambda p: p.stat().st_mtime):
            if path.name.lower() in {"readme.md", "thumbs.db", "desktop.ini"}:
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    out.append(json.load(f))
            except Exception:
                continue
        return out

    def collective_utxo(self) -> int:
        return sum(w.get("utxo_collective_value", 0) for w in self.load_all())

    def __repr__(self) -> str:
        latest = self.load_latest()
        if latest:
            return f"ManaCielWallet(addr={latest['address']}, coord={latest['coordinate']['value']})"
        return "ManaCielWallet(empty)"
