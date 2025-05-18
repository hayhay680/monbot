import discord
from discord.ext import commands
import random
import json
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Configuration initiale
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    raise ValueError("Token Discord non trouvé dans les variables d'environnement !")

# Initialisation du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Données complètes des cartes
cartes = {
    # Anime/Manga
    "Dragon Ball": {
        "Ultra Rare": ["Goku Ultra Instinct", "Vegeta Ultra Ego"],
        "Rare": ["Gohan Beast", "Piccolo Orange"],
        "Commune": ["Krillin", "Yamcha"]
    },
    "Naruto": {
        "Ultra Rare": ["Naruto Baryon Mode", "Sasuke Rinnegan"],
        "Super Rare": ["Madara Six Paths", "Obito Juubi"],
        "Rare": ["Itachi", "Kakashi Double Mangekyo"],
        "Commune": ["Sakura", "Hinata"]
    },
    "Demon Slayer": {
        "Ultra Rare": ["Tanjiro Sun Breathing", "Muzan Kibutsuji"],
        "Super Rare": ["Nezuko Demon Form", "Rengoku"],
        "Rare": ["Zenitsu", "Inosuke"],
        "Commune": ["Shinobu", "Tengen"]
    },
    "Death Note": {
        "Ultra Rare": ["Light Yagami (Kira)", "L"],
        "Super Rare": ["Ryuk", "Misa Amane"],
        "Rare": ["Near", "Mello"],
        "Commune": ["Soichiro Yagami", "Touta Matsuda"]
    },
    "Cookie Run Kingdom": {
        "Ultra Rare": ["Pure Vanilla Cookie", "Dark Cacao Cookie"],
        "Super Rare": ["Sea Fairy Cookie", "Moonlight Cookie"],
        "Rare": ["Espresso Cookie", "Milk Cookie"],
        "Commune": ["Gingerbrave", "Strawberry Cookie"]
    },
    "Pokemon": {
        "Ultra Rare": ["Mewtwo", "Rayquaza"],
        "Super Rare": ["Charizard", "Pikachu Libre"],
        "Rare": ["Eevee", "Lucario"],
        "Commune": ["Pidgey", "Rattata"]
    },

    # Jeux Vidéo
    "Zelda BOTW/TOTK": {
        "Ultra Rare": ["Link (Armure Divine)", "Zelda (Pouvoir Ancestral)"],
        "Super Rare": ["Mipha (Forme Spirituelle)", "Revali (Archer du Vent)"],
        "Rare": ["Sidon (Prince Zora)", "Tulin (Jeune Guerrier)"],
        "Commune": ["Bokoblin", "Korok"]
    },
    "Resident Evil": {
        "Ultra Rare": ["Leon S. Kennedy", "Albert Wesker"],
        "Super Rare": ["Jill Valentine", "Nemesis"],
        "Rare": ["Ada Wong", "Lady Dimitrescu"],
        "Commune": ["Zombie Classique", "Chien Cerbère"]
    },
    "Red Dead Redemption 2": {
        "Ultra Rare": ["Arthur Morgan", "Dutch van der Linde"],
        "Super Rare": ["John Marston", "Sadie Adler"],
        "Rare": ["Micah Bell", "Eagle Fly"],
        "Commune": ["Cheval Sauvage", "Coyote"]
    },
    "The Last of Us": {
        "Ultra Rare": ["Joel", "Ellie"],
        "Super Rare": ["Abby", "Clicker Évolué"],
        "Rare": ["Tess", "Dina"],
        "Commune": ["Fédra Soldier", "Runner"]
    },
    "Horizon Zero Dawn": {
        "Ultra Rare": ["Aloy", "Sylens"],
        "Super Rare": ["Erend", "Varl"],
        "Rare": ["Nil", "Talanah"],
        "Commune": ["Watcher", "Strider"]
    },
    "Final Fantasy": {
        "Ultra Rare": ["Cloud Strife", "Sephiroth"],
        "Super Rare": ["Tifa Lockhart", "Noctis Lucis Caelum"],
        "Rare": ["Aerith Gainsborough", "Vivi Ornitier"],
        "Commune": ["Chocobo", "Moogle"]
    },

    # Films/Séries
    "Scream": {
        "Ultra Rare": ["Ghostface", "Billy Loomis"],
        "Super Rare": ["Sidney Prescott", "Stu Macher"],
        "Rare": ["Dewey Riley", "Gale Weathers"],
        "Commune": ["Cotton Weary", "Casey Becker"]
    },
    "Miraculous": {
        "Ultra Rare": ["Ladybug", "Chat Noir"],
        "Super Rare": ["Rena Rouge", "Queen Bee"],
        "Rare": ["Carapace", "Mayura"],
        "Commune": ["Hawk Moth", "Lila Rossi"]
    }
}

chances = {
    "Ultra Rare": 1,
    "Super Rare": 5,
    "Rare": 14,
    "Commune": 80
}

# Gestion de l'inventaire
INVENTAIRE_FILE = "inventaire.json"

def charger_inventaire():
    if os.path.exists(INVENTAIRE_FILE):
        with open(INVENTAIRE_FILE, "r") as f:
            return {int(k): v for k, v in json.load(f).items()}
    return {}

def sauvegarder_inventaire(data):
    with open(INVENTAIRE_FILE, "w") as f:
        json.dump(data, f, indent=4)

inventaires = charger_inventaire()

# Système de keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot Gachapon en ligne!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Commandes du bot
@bot.event
async def on_ready():
    print(f'{bot.user.name} est connecté !')
    print('------')

def tirer_carte(univers):
    roll = random.random() * 100
    cumulative = 0
    rarete_tiree = None
    
    for rarete, proba in chances.items():
        cumulative += proba
        if roll <= cumulative:
            rarete_tiree = rarete
            break
    
    for rarete_dispo in cartes[univers]:
        if rarete_dispo.lower() == rarete_tiree.lower():
            return {
                "nom": random.choice(cartes[univers][rarete_dispo]),
                "rarete": rarete_tiree,
                "univers": univers,
                "id": random.randint(1000, 9999)
            }
    
    return {
        "nom": random.choice(cartes[univers]["Commune"]),
        "rarete": "Commune",
        "univers": univers,
        "id": random.randint(1000, 9999)
    }

@bot.command(name="pull")
async def pull(ctx, univers: str = None):
    user_id = ctx.author.id
    
    if univers is None:
        liste_univers = "\n".join(f"- `{u}`" for u in cartes.keys())
        await ctx.send(f"**Choisis un univers !**\n{liste_univers}\nEx: `!pull Dragon Ball`")
        return
    
    univers = univers.capitalize()
    if univers not in cartes:
        await ctx.send("❌ Univers invalide. Utilise `!pull` pour voir la liste.")
        return
    
    # Tirage de 2 cartes
    carte1 = tirer_carte(univers)
    carte2 = tirer_carte(univers)
    
    embed = discord.Embed(
        title=f"🎲 Choisis ta carte ! (15 secondes)",
        description=(
            f"**1️⃣ {carte1['nom']}** ({carte1['rarete']})\n"
            f"**2️⃣ {carte2['nom']}** ({carte2['rarete']})"
        ),
        color=0x7289DA
    )
    embed.set_footer(text="Réagis avec 1️⃣ ou 2️⃣ pour choisir.")
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["1️⃣", "2️⃣"] and reaction.message.id == msg.id
    
    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=15.0, check=check)
        
        carte_choisie = carte1 if str(reaction.emoji) == "1️⃣" else carte2
        
        if user_id not in inventaires:
            inventaires[user_id] = {}
        if univers not in inventaires[user_id]:
            inventaires[user_id][univers] = []
        
        inventaires[user_id][univers].append(carte_choisie)
        sauvegarder_inventaire(inventaires)
        
        embed_result = discord.Embed(
            title=f"🎉 Tu as choisi : **{carte_choisie['nom']}** !",
            description=(
                f"**Rareté** : {carte_choisie['rarete']}\n"
                f"**ID** : `{carte_choisie['id']}`\n"
                f"**Univers** : {univers}"
            ),
            color=0x00ff00 if "Ultra" in carte_choisie['rarete'] else 0xff9900
        )
        await ctx.send(embed=embed_result)
    
    except asyncio.TimeoutError:
        await ctx.send("⏰ Temps écoulé ! Ton tirage a été annulé.")

@bot.command(name="inventaire")
async def inventaire(ctx):
    user_id = ctx.author.id
    
    if user_id not in inventaires or not inventaires[user_id]:
        await ctx.send("📦 Ton inventaire est vide. Utilise `!pull` pour tirer des cartes !")
        return
    
    embed = discord.Embed(title=f"📦 Inventaire de {ctx.author.name}", color=0x7289DA)
    
    for univers, cartes_list in inventaires[user_id].items():
        cartes_str = "\n".join(
            f"`{carte['id']}` - {carte['nom']} ({carte['rarete']})"
            for carte in cartes_list
        )
        embed.add_field(
            name=f"**{univers}**",
            value=cartes_str,
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name="show")
async def show(ctx, carte_id: int):
    user_id = ctx.author.id
    
    if user_id not in inventaires or not inventaires[user_id]:
        await ctx.send("❌ Tu n'as aucune carte.")
        return
    
    carte_trouvee = None
    for univers, cartes_list in inventaires[user_id].items():
        for carte in cartes_list:
            if carte["id"] == carte_id:
                carte_trouvee = carte
                break
    
    if not carte_trouvee:
        await ctx.send("❌ Carte introuvable. Vérifie l'ID avec `!inventaire`.")
        return
    
    embed = discord.Embed(
        title=f"🃏 Carte #{carte_trouvee['id']}",
        description=(
            f"**Nom** : {carte_trouvee['nom']}\n"
            f"**Rareté** : {carte_trouvee['rarete']}\n"
            f"**Univers** : {carte_trouvee['univers']}"
        ),
        color=0x00ff00 if "Ultra" in carte_trouvee['rarete'] else 0xff9900
    )
    await ctx.send(embed=embed)

@bot.command(name="give")
@commands.has_permissions(administrator=True)
async def give(ctx, membre: discord.Member, univers: str):
    """Donne un tirage à un autre utilisateur (Admin uniquement)"""
    if membre.bot:
        await ctx.send("❌ Impossible de donner un tirage à un bot.")
        return
    
    univers = univers.capitalize()
    if univers not in cartes:
        await ctx.send("❌ Univers invalide.")
        return
    
    # Tirage de 2 cartes
    carte1 = tirer_carte(univers)
    carte2 = tirer_carte(univers)
    
    embed = discord.Embed(
        title=f"🎁 {ctx.author.name} offre un tirage à {membre.name} !",
        description=(
            f"**1️⃣ {carte1['nom']}** ({carte1['rarete']})\n"
            f"**2️⃣ {carte2['nom']}** ({carte2['rarete']})"
        ),
        color=0x7289DA
    )
    embed.set_footer(text=f"{membre.name}, réagis avec 1️⃣ ou 2️⃣ pour choisir.")
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")
    
    def check(reaction, user):
        return user == membre and str(reaction.emoji) in ["1️⃣", "2️⃣"] and reaction.message.id == msg.id
    
    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=15.0, check=check)
        
        carte_choisie = carte1 if str(reaction.emoji) == "1️⃣" else carte2
        user_id = membre.id
        
        if user_id not in inventaires:
            inventaires[user_id] = {}
        if univers not in inventaires[user_id]:
            inventaires[user_id][univers] = []
        
        inventaires[user_id][univers].append(carte_choisie)
        sauvegarder_inventaire(inventaires)
        
        embed_result = discord.Embed(
            title=f"🎉 {membre.name} a choisi : **{carte_choisie['nom']}** !",
            description=(
                f"**Rareté** : {carte_choisie['rarete']}\n"
                f"**ID** : `{carte_choisie['id']}`\n"
                f"**Offert par** : {ctx.author.name}"
            ),
            color=0x00ff00 if "Ultra" in carte_choisie['rarete'] else 0xff9900
        )
        await ctx.send(embed=embed_result)
    
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ {membre.name} n'a pas choisi à temps !")

# Lancement du bot
if __name__ == '__main__':
    # Démarrer le serveur Flask pour keep-alive
    Thread(target=run_flask).start()
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("\nERREUR : Token Discord invalide !")
        print("Vérifiez votre fichier .env ou les variables d'environnement")
