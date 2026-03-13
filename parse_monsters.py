import re
import json
import os

enum_path = "Shared/Enums.cs"
monsters_dir = "Server/MirObjects/Monsters/"

monsters_data = []

with open(enum_path, 'r', encoding='utf-8') as f:
    content = f.read()

enum_match = re.search(r'public enum Monster : ushort\s*\{([\s\S]*?)\}', content)
if not enum_match:
    print("Could not find Monster enum")
    exit(1)

enum_body = enum_match.group(1)

pattern = re.compile(r'^\s*([A-Za-z0-9_]+)\s*=\s*(\d+)\s*,?(?:\s*//(.*))?$', re.MULTILINE)

# Parse C# mechanics
def extract_mechanics_from_cs(filepath):
    mechanics = []
    tags = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # Check for Magic Attack
    if "DefenceType.MAC" in code or "DefenceType.MACAgility" in code:
        tags.add("Magic Attack")
        mechanics.append("Attacks bypass physical armor and hit Magic Defense (MAC).")
    elif "DefenceType.AC" in code or "DefenceType.ACAgility" in code:
        tags.add("Physical Attack")
    else:
        # Default physical if not specified, though some just call base.Attacked()
        tags.add("Physical Attack (Default)")

    # Check for Poison
    poison_matches = re.finditer(r'PoisonTarget\([^,]+,\s*\d+,\s*\d+,\s*PoisonType\.([A-Za-z]+)', code)
    poisons_found = set()
    for match in poison_matches:
        poisons_found.add(match.group(1))

    if poisons_found:
        tags.add("Poisonous")
        mechanics.append(f"Applies status effects: {', '.join(poisons_found)} poison.")

    # Check for Ranged Attacks
    if "CreateProjectile" in code or "ObjectRangeAttack" in code:
        tags.add("Ranged")
        mechanics.append("Capable of attacking from a distance with projectiles or magic.")

    # Check for Area of Effect (AoE)
    aoe_match = re.search(r'FindAllTargets\((\d+),', code)
    if aoe_match:
        radius = aoe_match.group(1)
        tags.add("AoE")
        mechanics.append(f"Deals Area of Effect (AoE) damage within a {radius}-tile radius.")

    # Check for Teleportation
    if "TeleportRandom" in code:
        tags.add("Teleports")
        mechanics.append("Can teleport to reposition or escape when surrounded.")

    # Check for Healing
    if "ChangeHP(" in code and "Envir.Time > " in code:
        pass # A bit hard to regex generic healing without context, but we can look for SetHP
    if "SetHP(Stats[Stat.HP])" in code:
         mechanics.append("Has the ability to fully regenerate its health under certain conditions.")

    return list(tags), mechanics

# Build the database
for match in pattern.finditer(enum_body):
    name = match.group(1)
    id_val = int(match.group(2))
    comment = match.group(3)

    comment = comment.strip() if comment else ""
    base_type = "Boss" if "BOSS" in comment.upper() else "Standard"

    tags = []
    mechanics = []

    # Check for custom logic file
    cs_file = os.path.join(monsters_dir, f"{name}.cs")
    if os.path.exists(cs_file):
        if base_type == "Standard":
            base_type = "Unique/Elite"

        extracted_tags, extracted_mechanics = extract_mechanics_from_cs(cs_file)
        tags.extend(extracted_tags)
        mechanics.extend(extracted_mechanics)
    else:
        # Default for basic mobs
        tags.append("Melee")
        tags.append("Physical Attack (Default)")

    monsters_data.append({
        "id": id_val,
        "name": name,
        "type": base_type,
        "tags": list(set(tags)),
        "mechanics": mechanics
    })

with open('GuideWebsite/monsters.json', 'w', encoding='utf-8') as f:
    json.dump(monsters_data, f, indent=4)

print(f"Saved {len(monsters_data)} monsters with advanced mechanics to monsters.json")
