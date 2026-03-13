import re
import json
import os

enum_path = "Shared/Enums.cs"
monsters_dir = "Server/MirObjects/Monsters/"

monsters_data = []

# Manual Overrides for deep dives
manual_overrides = {
    "EvilCentipede": {
        "type": "Ambush / Stationary",
        "description": "The EvilCentipede is a deadly, stationary monster that waits hidden underground. It is completely invincible and regenerates health while hidden.",
        "mechanics": [
            "Ambush Trigger: It will burst from the ground when a player steps within 3 tiles of its location.",
            "Area of Effect: Once visible, it attacks every player within a massive 7-tile radius simultaneously.",
            "Dual Poison: Its strikes ignore physical defense (hitting Magic Defense instead) and apply two brutal poisons: Green (Damage over time) and Paralysis (Stun)."
        ],
        "strategy": "Do not cluster! Keep your distance. If all players move further than 7 tiles away, it will burrow back underground and heal to full health. Prepare high Magic Defense and poison resistance."
    },
    "EvilMir": {
        "type": "Mega Boss / Dragon",
        "description": "A legendary stationary dragon boss linked directly to the server's Dragon System. Defeating it is the primary way to level up the server-wide Dragon level.",
        "mechanics": [
            "Dynamic Attacks: It chooses between a devastating melee swipe hitting everything within 17 tiles, or a targeted fireball that explodes in a 2-tile radius.",
            "System Link: As you damage it, the Dragon System gains EXP. However, getting hit by it can actually decrease the server's Dragon level!",
            "Invincible Slumber: When reduced to 0 HP, it does not die. Instead, it grants a massive EXP bounty to the Dragon System and goes to sleep, becoming invincible for exactly 5 minutes before waking up at full health."
        ],
        "strategy": "This is a raid-level boss. You must coordinate to avoid the 17-tile wipe mechanic while managing the 2-tile fireball splash damage. Healing is crucial as both attacks apply severe Paralyze and Green poisons."
    },
    "WoomaTaurus": {
        "type": "Boss / Melee-Caster",
        "description": "The feared leader of the Wooma Temple. A powerful boss that relies on magical fire attacks and highly aggressive AI to prevent players from cornering him.",
        "mechanics": [
            "Magical Melee: Despite looking like physical punches, his attacks are actually magical fire blasts that bypass Armor and hit Magic Defense (MAC) instead.",
            "Enrage Stages: His health is divided into 7 stages. Every time he drops a stage, he enters an 8-second 'Enrage' mode where his movement and attack speed double.",
            "Anti-Surround: Every 10 seconds, he scans the 8 tiles around him. If 5 or more are blocked by players or pets, he will instantly cast a random teleport up to 4 tiles away to break the trap."
        ],
        "strategy": "Do not try to surround or trap him against a wall, as he will teleport out and reset his aggro. Kite him carefully, and back away when he enters one of his 8-second Enrage phases."
    }
}

with open(enum_path, 'r', encoding='utf-8') as f:
    content = f.read()

enum_match = re.search(r'public enum Monster : ushort\s*\{([\s\S]*?)\}', content)
if not enum_match:
    print("Could not find Monster enum")
    exit(1)

enum_body = enum_match.group(1)

pattern = re.compile(r'^\s*([A-Za-z0-9_]+)\s*=\s*(\d+)\s*,?(?:\s*//(.*))?$', re.MULTILINE)

for match in pattern.finditer(enum_body):
    name = match.group(1)
    id_val = int(match.group(2))
    comment = match.group(3)

    comment = comment.strip() if comment else ""

    base_type = "Boss" if "BOSS" in comment.upper() else "Standard"
    base_desc = "A creature found in the world of Mir."

    # Check for custom logic file
    cs_file = os.path.join(monsters_dir, f"{name}.cs")
    if os.path.exists(cs_file):
        if base_type == "Standard":
            base_type = "Unique"
        base_desc += " This monster possesses advanced combat logic and unique mechanics."

    # Override if we have deep-dive data
    if name in manual_overrides:
        override = manual_overrides[name]
        monsters_data.append({
            "id": id_val,
            "name": name,
            "type": override["type"],
            "description": override["description"],
            "mechanics": override["mechanics"],
            "strategy": override["strategy"]
        })
    else:
        monsters_data.append({
            "id": id_val,
            "name": name,
            "type": base_type,
            "description": base_desc,
            "mechanics": [],
            "strategy": "Engage with caution. Use appropriate skills for your class."
        })

with open('GuideWebsite/monsters.json', 'w', encoding='utf-8') as f:
    json.dump(monsters_data, f, indent=4)

print(f"Saved {len(monsters_data)} monsters to monsters.json")
