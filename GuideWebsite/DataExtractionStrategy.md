# Monster Data Extraction Strategy for Mir 2 Guide

Given the massive scale of the Legend of Mir 2 bestiary (hundreds of monsters defined in `Shared/Enums.cs` and `Server/MirObjects/Monsters/`), manually analyzing each one as deeply as the Bosses is inefficient. Here is the strategy to automate and scale the extraction process for the guide website:

## 1. Categorization Tiers
We will divide the extraction effort into three tiers based on the complexity of the monster's code:

*   **Tier 1: Bosses & Unique Mechanics (Manual Deep Dive)**
    *   *Identification:* Any file in `Server/MirObjects/Monsters/` that overrides complex functions like `ProcessAI()`, `CompleteAttack()`, `ChangeHP()`, or has large switch statements for `CurrentAction`.
    *   *Action:* Continue the deep-dive analysis (like WoomaTaurus or EvilMir) to write comprehensive strategy guides for these key encounters.

*   **Tier 2: Elite/Special Ability Mobs (Semi-Automated Analysis)**
    *   *Identification:* Monsters that inherit from `MonsterObject` but override specific combat functions like `Attack()` (e.g., to add poison, ranged projectiles, or AoE damage). Examples: `FlamingWooma`, `ToxicGhoul`.
    *   *Action:* Use bash scripting to grep for `PoisonTarget`, `CreateProjectile`, or `FindAllTargets` within the `Monsters/` directory. Create a template that automatically fills in their damage type (Physical vs. Magic) and status effects.

*   **Tier 3: Standard Melee/Fodder Mobs (Fully Automated)**
    *   *Identification:* Monsters that either don't have a dedicated `.cs` file in the `Monsters/` folder, or just have a basic constructor that inherits `base(info)`.
    *   *Action:* Write a script (e.g., Python or Node.js) to parse the server's database files (if available in the repo as XML/SQL) or parse `Enums.cs`. We can dynamically generate HTML cards for these basic mobs stating their name, basic stats (HP, Level, AC, MAC), and standard physical attack type.

## 2. Technical Implementation Plan
1.  **Extract `Enums.cs`:** Parse `Shared/Enums.cs` to get the master list of all monster IDs and Names. This acts as our checklist.
2.  **Scan `Server/MirObjects/Monsters/`:** Map each Name from the Enum to a `.cs` file. If a file exists, it's at least Tier 2. If it has overridden `ProcessAI()`, it's Tier 1.
3.  **JSON Generation:** Instead of hardcoding HTML (like we did for the first three), the final goal should be to run a script that generates a `monsters.json` file containing all extracted data.
4.  **Website Integration:** Update `GuideWebsite/monsters.html` to use JavaScript (`app.js`) to fetch `monsters.json` and dynamically render the `<article class="monster-card">` elements. This allows for sorting, filtering (e.g., "Show only Bosses"), and easy updates.