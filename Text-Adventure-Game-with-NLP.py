import random
import time
import os
import textwrap
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored terminal text
init(autoreset=True)

class EnhancedTextAdventure:
    def __init__(self):
        # Game state
        self.current_room = "cabin"
        self.inventory = ["map", "flashlight"]
        self.game_over = False
        self.move_count = 0
        self.current_quest = "find_key"
        self.quests_completed = set()
        self.health = 100
        self.maximum_health = 100
        self.energy = 100
        self.maximum_energy = 100
        self.discovered_rooms = {"cabin"}
        self.room_visits = {"cabin": 1}
        self.auto_help = True  # Show help on first visit to new areas
        self.events_triggered = set()
        self.companions = []
        self.screen_width = 80
        self.tutorial_tips_shown = set()
        self.knowledge = set()
        self.in_combat = False
        self.current_encounter = None
        
        # Define rooms and connections
        self.rooms = {
            "cabin": {
                "name": "Abandoned Cabin",
                "description": "A small wooden cabin with dust covering most surfaces. Faint sunlight filters through cracked windows.",
                "detailed_description": "The cabin looks like it was abandoned years ago. A small bed sits in the corner with a worn mattress. A wooden table in the center has various items scattered on it. The door to the east leads outside into a dense forest.",
                "connections": {"east": "forest_path"},
                "items": ["old_journal", "rusty_key"],
                "hints": ["The journal might have useful information.", "Perhaps the rusty key opens something nearby."],
                "first_visit_text": "You wake up in an unfamiliar cabin with no memory of how you got here. Your head throbs slightly as you try to piece together what happened."
            },
            "forest_path": {
                "name": "Forest Path",
                "description": "A narrow dirt path winding through tall pine trees. The air is fresh and birds can be heard chirping.",
                "detailed_description": "The forest is dense with ancient trees towering above you. The path is well-worn, suggesting frequent travel. You notice various animal tracks in the soft dirt. The cabin lies to the west, while the path continues south deeper into the forest.",
                "connections": {"west": "cabin", "south": "forest_clearing", "east": "river_bend"},
                "items": ["strange_mushrooms", "bird_feather"],
                "hints": ["The path branches in multiple directions. Perhaps exploring will help you understand where you are."],
                "danger_level": 1,
                "encounters": ["forest_sprite", "lost_traveler"]
            },
            "forest_clearing": {
                "name": "Forest Clearing",
                "description": "A wide open area where sunlight breaks through the canopy. Wildflowers grow in patches.",
                "detailed_description": "The clearing is roughly circular, about thirty feet across. Sunlight bathes the area in a warm glow. Various wildflowers in purple, yellow, and blue create a colorful carpet. At the center stands an unusual stone pedestal with symbols carved into it.",
                "connections": {"north": "forest_path", "southwest": "ancient_ruins", "southeast": "swamp_entrance"},
                "items": ["colorful_stone", "herb_pouch"],
                "hints": ["The stone pedestal seems important. Perhaps it requires something to activate it."],
                "danger_level": 1,
                "encounters": ["peaceful_deer", "herbalist"]
            },
            "river_bend": {
                "name": "River Bend",
                "description": "A clear, rushing river curves around moss-covered rocks. The water looks cool and refreshing.",
                "detailed_description": "The river is about fifteen feet wide, flowing with clear mountain water. Large smooth rocks create a natural crossing point. Fish can be seen swimming in the deeper pools. A rope hangs from a tree branch, possibly used for crossing or swimming.",
                "connections": {"west": "forest_path", "north": "waterfall", "east": "fishing_spot"},
                "items": ["fishing_line", "smooth_stone"],
                "hints": ["The river might be crossable at certain points.", "The fishing line could be useful for catching food or crafting."],
                "first_visit_text": "As you approach the river, you feel a strange sense of peace wash over you. Something about the flowing water seems to clear your mind.",
                "danger_level": 1
            },
            "ancient_ruins": {
                "name": "Ancient Ruins",
                "description": "Crumbling stone structures covered in vines and moss. The air feels heavy with history.",
                "detailed_description": "These ruins appear to be thousands of years old. Stone columns rise from the ground, some still standing while others have toppled. Strange symbols are carved into the walls, similar to those you saw on the pedestal in the clearing. A partially collapsed doorway leads to a dark chamber.",
                "connections": {"northeast": "forest_clearing", "south": "underground_chamber"},
                "items": ["stone_tablet", "ancient_coin"],
                "locks": {"south": {"item": "rusty_key", "message": "The door to the underground chamber is locked. It looks like it needs a key."}},
                "hints": ["The symbols might tell a story or contain instructions.", "The stone tablet looks like it might fit somewhere."],
                "danger_level": 2,
                "encounters": ["guardian_statue", "archaeologist"]
            },
            "swamp_entrance": {
                "name": "Swamp Entrance",
                "description": "The ground becomes soggy and the trees are draped with hanging moss. A misty haze hangs in the air.",
                "detailed_description": "The forest gradually gives way to wetlands. The ground squishes beneath your feet, and the air is thick with humidity. Strange sounds echo from deeper in the swamp - croaks, splashes, and occasionally something that sounds almost like whispering.",
                "connections": {"northwest": "forest_clearing", "south": "deepswamp"},
                "items": ["mud_poultice", "strange_tooth"],
                "hints": ["The swamp looks dangerous, but might contain valuable resources.", "Moving quietly might be wise here."],
                "danger_level": 3,
                "encounters": ["will_o_wisp", "swamp_creature"]
            },
            "waterfall": {
                "name": "Waterfall",
                "description": "A magnificent waterfall cascades down a rocky cliff. Rainbow mist rises where the water crashes below.",
                "detailed_description": "The waterfall is about forty feet high, thundering down into a deep pool below. The constant spray has created a lush microclimate with ferns and moss covering everything. Behind the waterfall, you can just make out what appears to be a cave entrance.",
                "connections": {"south": "river_bend", "west": "hidden_cave"},
                "locks": {"west": {"special": "waterfall_cave", "message": "You can see a cave behind the waterfall, but the rushing water makes it impossible to reach."}},
                "items": ["glowing_crystal", "water_flask"],
                "hints": ["There seems to be something behind the waterfall.", "The crystal pulses with an inner light when pointed toward certain areas."],
                "danger_level": 2
            },
            "fishing_spot": {
                "name": "Fishing Spot",
                "description": "A calm pool in the river where fish are abundant. A crude wooden dock extends a few feet into the water.",
                "detailed_description": "This wider section of the river forms a deep pool where the current slows. Various fish can be seen swimming lazily beneath the surface. The small wooden dock looks relatively recent compared to other structures you've found. A wooden sign has fishing instructions carved into it.",
                "connections": {"west": "river_bend"},
                "items": ["fishing_rod", "bait_jar"],
                "hints": ["With the right equipment, you could catch fish here for food.", "The jar contains some kind of bait that might attract more than just fish."],
                "danger_level": 1,
                "encounters": ["friendly_fisher", "river_guardian"]
            },
            "underground_chamber": {
                "name": "Underground Chamber",
                "description": "A vast chamber beneath the ruins. Strange crystals in the walls provide dim illumination.",
                "detailed_description": "The chamber is roughly circular with a domed ceiling about twenty feet high. Embedded crystals pulse with a blue-green light that creates shifting shadows. The walls are covered with intricate carvings depicting battles, rituals, and strange creatures. A stone altar stands in the center of the room.",
                "connections": {"north": "ancient_ruins", "east": "crystal_tunnel"},
                "items": ["ceremonial_dagger", "glowing_orb"],
                "hints": ["The altar seems designed to hold something specific.", "The orb glows brighter when brought near certain carvings on the wall."],
                "danger_level": 3,
                "encounters": ["shadow_guardian", "lost_explorer"]
            },
            "deepswamp": {
                "name": "Deep Swamp",
                "description": "Dark, murky water surrounds twisted trees. The ground is treacherous with hidden sinkholes.",
                "detailed_description": "The swamp becomes increasingly difficult to navigate here. Patches of seemingly solid ground can give way to deep mud without warning. The trees have grown into grotesque shapes, their branches reaching like gnarled fingers. Eyes seem to watch you from the shadows between the trees.",
                "connections": {"north": "swamp_entrance", "southeast": "witch_hut"},
                "items": ["swamp_orchid", "mysterious_vial"],
                "hints": ["Moving carefully is essential here - test each step before putting your full weight down.", "The orchid seems to glow faintly in the darkness."],
                "danger_level": 4,
                "encounters": ["swamp_lurker", "lost_soul"]
            },
            "hidden_cave": {
                "name": "Hidden Cave",
                "description": "A spacious cave behind the waterfall. The walls glitter with mineral deposits.",
                "detailed_description": "The cave extends about thirty feet into the cliff face. The constant mist from the waterfall has created stunning mineral formations that sparkle when your light hits them. The air is cool and damp, and the roar of the waterfall is muffled here. At the back of the cave is a small shrine of some sort.",
                "connections": {"east": "waterfall"},
                "items": ["sacred_amulet", "cave_mushrooms"],
                "hints": ["The shrine appears dedicated to some kind of water deity.", "The amulet feels strangely warm to the touch."],
                "danger_level": 2,
                "encounters": ["cave_dweller"]
            },
            "crystal_tunnel": {
                "name": "Crystal Tunnel",
                "description": "A narrow tunnel where massive crystals of various colors jut from the walls, ceiling, and floor.",
                "detailed_description": "The tunnel twists and turns, forcing you to navigate around huge crystal formations. They range in color from deep purple to pale blue and vibrant green. When your light source hits them, they create dazzling rainbow patterns on the walls. The air feels charged with some kind of energy.",
                "connections": {"west": "underground_chamber", "east": "crystal_heart"},
                "items": ["crystal_shard", "energy_stone"],
                "hints": ["The crystals seem to respond to sound, vibrating slightly when you speak.", "The shard might be useful as a tool or component."],
                "danger_level": 3,
                "encounters": ["crystal_elemental", "lost_miner"]
            },
            "witch_hut": {
                "name": "Witch's Hut",
                "description": "A small wooden structure standing on stilts above the swamp water. Herbs and strange objects hang from the eaves.",
                "detailed_description": "The hut is surprisingly sturdy despite its appearance. Strange symbols are painted on the door and windows, and bundles of dried herbs, feathers, and bones hang from strings around the perimeter. A rocking chair sits on the small porch, swaying slightly despite the lack of wind.",
                "connections": {"northwest": "deepswamp"},
                "items": ["spell_book", "potion_bottle"],
                "hints": ["The book contains information about local plants and their magical properties.", "The bottle is empty but smells of something sweet and enticing."],
                "danger_level": 3,
                "encounters": ["swamp_witch", "familiar"]
            },
            "crystal_heart": {
                "name": "Crystal Heart",
                "description": "A massive chamber dominated by an enormous heart-shaped crystal pulsing with light and energy.",
                "detailed_description": "This vast chamber seems to be the center of the entire crystal cave system. The heart-shaped crystal formation in the center is at least fifteen feet tall and pulses with a rhythmic light, almost like a heartbeat. Smaller crystals throughout the room pulse in sync with it. The air is thick with energy that makes your skin tingle.",
                "connections": {"west": "crystal_tunnel"},
                "items": ["heart_shard", "energy_flask"],
                "hints": ["The central crystal seems to be the source of power for the entire region.", "The flask seems designed to capture some of the crystal's energy."],
                "danger_level": 5,
                "encounters": ["crystal_guardian", "energy_spirit"],
                "boss": "crystal_overlord"
            }
        }
        
        # Define items and their properties
        self.items = {
            "old_journal": {
                "name": "Old Journal",
                "description": "A weathered leather journal with many pages filled with handwritten notes.",
                "examine_text": "The journal belongs to someone named Elara who was researching the ancient ruins and crystals in the area. The last entry mentions discovering a 'heart of power' and a warning about 'those who would misuse it'.",
                "usable": True,
                "use_text": "You read through the journal carefully, noting important information about the area. It mentions the dangerous swamp to the south, ruins with powerful artifacts, and legends of a crystal heart that powers the entire region.",
                "use_effect": "quest_info"
            },
            "rusty_key": {
                "name": "Rusty Key",
                "description": "An old iron key with elaborate decorative patterns. Despite the rust, it looks usable.",
                "examine_text": "The key has strange symbols etched into it that match some of the carvings you've seen on ancient stones in the area. It's heavy and feels important.",
                "usable": True,
                "use_text": "This key isn't something you use directly - it will automatically unlock certain paths when you have it in your inventory.",
                "unlock": "ancient_ruins"
            },
            "flashlight": {
                "name": "Flashlight",
                "description": "A sturdy metal flashlight with LED bulbs. The batteries seem to be in good condition.",
                "examine_text": "A reliable light source that will help you explore dark areas. It has a brightness adjustment dial and seems to be waterproof.",
                "usable": True,
                "use_text": "You turn on the flashlight, providing illumination in dark areas.",
                "use_effect": "light"
            },
            "map": {
                "name": "Map",
                "description": "A partial map of the area, hand-drawn on yellowed parchment.",
                "examine_text": "The map shows the cabin, forest path, and hints at other locations. Some areas are marked with warning symbols, and others with question marks. It's not complete, but it's better than nothing.",
                "usable": True,
                "use_text": "You study the map carefully, gaining a better understanding of the area layout.",
                "use_effect": "show_map"
            },
            "strange_mushrooms": {
                "name": "Strange Mushrooms",
                "description": "A cluster of small blue mushrooms with red speckles. They glow faintly in the dark.",
                "examine_text": "These don't look like any mushrooms you're familiar with. The blue and red coloration is striking, and they emit a faint light. They might be medicinal, hallucinogenic, poisonous, or something else entirely.",
                "usable": True,
                "use_text": "After careful consideration, you decide to crush one of the mushrooms and apply it to a small scratch. It creates a cooling sensation and the scratch seems to heal slightly faster.",
                "use_effect": "small_heal"
            },
            "bird_feather": {
                "name": "Iridescent Feather",
                "description": "A large feather that shimmers with colors that seem to shift as you move it.",
                "examine_text": "This is no ordinary feather. It's about eight inches long and changes color in the light - blue to purple to green. It feels warm to the touch and occasionally seems to vibrate slightly.",
                "usable": True,
                "use_text": "As you hold the feather, it begins to glow and point in a specific direction before returning to normal.",
                "use_effect": "directional_hint"
            },
            "colorful_stone": {
                "name": "Colorful Stone",
                "description": "A smooth, palm-sized stone with swirling patterns of blue, green, and purple.",
                "examine_text": "The stone seems to have been polished by water over centuries. The patterns aren't just on the surface but seem to move slightly within the stone itself. It feels pleasantly warm.",
                "usable": True,
                "use_text": "As you hold the stone and concentrate, you feel a brief connection to the natural world around you. The sounds of the forest become clearer, and you sense the location of nearby water.",
                "use_effect": "nature_sense"
            },
            "herb_pouch": {
                "name": "Herb Pouch",
                "description": "A small leather pouch containing various dried herbs and plants.",
                "examine_text": "The pouch contains a variety of medicinal herbs. You recognize some as having healing properties, while others might be useful for creating poultices or teas.",
                "usable": True,
                "use_text": "You select a combination of herbs that should help with minor injuries and bruises. After preparing them properly, you apply the mixture to your wounds.",
                "use_effect": "medium_heal"
            },
            "fishing_line": {
                "name": "Fishing Line",
                "description": "A spool of strong, transparent fishing line.",
                "examine_text": "About twenty feet of high-quality fishing line. It's strong enough to support significant weight while being nearly invisible in water.",
                "usable": True,
                "use_text": "This would be most useful with a proper fishing rod or as a component in crafting.",
                "crafting_component": True
            },
            "smooth_stone": {
                "name": "Smooth River Stone",
                "description": "A perfectly flat and smooth stone worn by years in the river current.",
                "examine_text": "The stone is gray with flecks of quartz that catch the light. It's about the size of your palm and perfectly balanced. It feels somehow significant.",
                "usable": True,
                "use_text": "You run your fingers over the smooth surface of the stone. It has a calming effect.",
                "use_effect": "restore_energy"
            },
            "stone_tablet": {
                "name": "Ancient Tablet",
                "description": "A stone tablet covered in strange symbols and pictures.",
                "examine_text": "The tablet depicts a ritual of some kind involving crystals. One image shows a heart-shaped crystal with power emanating from it. Another shows figures bowing before it. The symbols might be a form of writing, but you can't decipher it.",
                "usable": True,
                "use_text": "You study the tablet carefully, trying to understand its meaning. Some of the images begin to make sense - they tell a story about the crystal heart being the source of life and power for the region.",
                "use_effect": "quest_info"
            },
            "ancient_coin": {
                "name": "Ancient Coin",
                "description": "A heavy gold coin with unfamiliar markings.",
                "examine_text": "The coin is made of what appears to be solid gold, though it's discolored with age. One side shows a crystal formation, the other a humanoid figure with rays emanating from its head.",
                "usable": False,
                "value": "high"
            },
            "mud_poultice": {
                "name": "Mud Poultice",
                "description": "A mixture of special swamp mud and herbs wrapped in a large leaf.",
                "examine_text": "The mud has a distinctive earthy smell with hints of mint and other herbs. It seems to be a medicinal preparation of some kind.",
                "usable": True,
                "use_text": "You apply the mud poultice to your skin. It has a cooling effect and seems to draw out toxins and reduce inflammation.",
                "use_effect": "heal_and_antidote"
            },
            "strange_tooth": {
                "name": "Large Fang",
                "description": "A curved, serrated tooth about four inches long from some unknown creature.",
                "examine_text": "The tooth is deeply unsettling. It's from no animal you recognize - too large for a snake, wrong shape for a crocodile. Whatever it came from must be formidable.",
                "usable": False,
                "crafting_component": True
            },
            "glowing_crystal": {
                "name": "Glowing Crystal",
                "description": "A small crystal that emits a soft blue light continuously without any apparent power source.",
                "examine_text": "The crystal is about two inches long, pointed at one end and flat at the other. It glows brighter when you approach certain areas, almost as if it's responding to something.",
                "usable": True,
                "use_text": "You hold the crystal out in front of you. Its glow intensifies and pulses in a specific direction.",
                "use_effect": "crystal_guide"
            },
            "water_flask": {
                "name": "Crystal Water Flask",
                "description": "A flask filled with water from the pool beneath the waterfall.",
                "examine_text": "The water in the flask seems unusually clear and pure. It occasionally catches the light in strange ways, as if it's more than just water.",
                "usable": True,
                "use_text": "You drink some of the crystal-clear water. It's incredibly refreshing and seems to invigorate you.",
                "use_effect": "restore_health_and_energy"
            },
            "fishing_rod": {
                "name": "Handcrafted Fishing Rod",
                "description": "A simple but effective fishing rod made from a flexible branch, some line, and a hook.",
                "examine_text": "Someone put decent effort into making this rod. The branch has been carefully selected for flexibility, and the line is attached securely. It should work well for catching fish.",
                "usable": True,
                "use_text": "This would be most useful at a good fishing spot.",
                "use_effect": "fishing",
                "use_location": "fishing_spot"
            },
            "bait_jar": {
                "name": "Jar of Bait",
                "description": "A small glass jar containing wriggling worms and grubs.",
                "examine_text": "The jar contains various types of fishing bait - earthworms, grubs, and what appear to be some kind of insect larvae. They're alive and wriggling. Perfect for fishing.",
                "usable": False,
                "companion_item": "fishing_rod"
            },
            "ceremonial_dagger": {
                "name": "Ceremonial Dagger",
                "description": "An ornate dagger with a crystal blade and inscribed hilt.",
                "examine_text": "The dagger doesn't appear designed for combat - it's more likely ritualistic. The crystal blade glows faintly with the same blue-green light as the crystals in the chamber. The inscriptions on the hilt match symbols you've seen elsewhere.",
                "usable": True,
                "use_text": "The dagger seems to have significance beyond being a weapon. It might be important for specific tasks or locations.",
                "combat_power": 2
            },
            "glowing_orb": {
                "name": "Ancient Orb",
                "description": "A spherical stone object that glows with an inner light.",
                "examine_text": "The orb is made of some kind of polished stone with crystal inclusions. It fits comfortably in your palm and pulses with light in a pattern that almost feels like a heartbeat.",
                "usable": True,
                "use_text": "As you focus on the orb, visions flash through your mind - glimpses of the ancient civilization that built these ruins and their connection to the crystal heart.",
                "use_effect": "vision",
                "quest_item": True
            }
        }
        
        # Encounters and their outcomes
        self.encounters = {
            "forest_sprite": {
                "name": "Forest Sprite",
                "description": "A tiny humanoid creature with leaf-like clothing and glowing eyes.",
                "friendly": True,
                "dialogue": [
                    "The sprite flits around you curiously before speaking in a high-pitched voice.",
                    "'Hello stranger! Not many humans come this way. Are you lost?'",
                    "The sprite listens to your story and nods sympathetically.",
                    "'The crystal heart has been acting strangely lately. Its energy affects everything in these woods.'",
                    "'If you seek answers, look to the ruins. But beware the deeper swamp - dark things lurk there.'"
                ],
                "reward": {"item": "colorful_stone", "chance": 0.7},
                "knowledge": "crystal_heart_location"
            },
            "lost_traveler": {
                "name": "Lost Traveler",
                "description": "A haggard-looking man with tattered clothes and a wild beard.",
                "friendly": True,
                "dialogue": [
                    "The man startles when he sees you, then relaxes slightly.",
                    "'Another one trapped here? I've been wandering these woods for... I don't even know how long.'",
                    "'There's powerful magic in these lands. The crystal caverns, the ancient ruins, the witch in the swamp...'",
                    "'I've tried to leave many times, but the paths always lead me back here.'",
                    "'Take this. Maybe you'll have better luck than me.'"
                ],
                "reward": {"item": "water_flask", "chance": 0.8},
                "knowledge": "escape_difficulty"
            },
            "peaceful_deer": {
                "name": "White Deer",
                "description": "An unusually large deer with pure white fur and intelligent eyes.",
                "friendly": True,
                "dialogue": [
                    "The magnificent deer watches you calmly, showing no fear.",
                    "As you approach, it nods its head as if in greeting.",
                    "The deer turns and walks a few paces, then looks back at you expectantly.",
                    "It leads you to a small hidden cache before bounding away into the forest."
                ],
                "reward": {"item": "herb_pouch", "chance": 0.9},
                "knowledge": "hidden_paths"
            },
            "herbalist": {
                "name": "Forest Herbalist",
                "description": "An elderly person wearing clothes made from plants and leather, gathering herbs in a basket.",
                "friendly": True,
                "dialogue": [
                    "The herbalist looks up as you approach, smiling warmly.",
                    "'Ah, a visitor! Few come to these parts anymore, especially since the crystal heart began to pulse more strongly.'",
                    "'Are you feeling well? The energies here can affect those not accustomed to them.'",
                    "'Here, take these herbs. Brew them in hot water if you feel weak or disoriented.'",
                    "'If you seek the heart, you must first understand its purpose. The ruins hold that knowledge.'"
                ],
                "reward": {"item": "mud_poultice", "chance": 1.0},
                "knowledge": "crystal_purpose"
            },
            "guardian_statue": {
                "name": "Animated Stone Guardian",
                "description": "A stone statue of a warrior that suddenly begins to move, its eyes glowing with blue light.",
                "friendly": False,
                "combat": True,
                "health": 40,
                "damage": 15,
                "victory_text": "The stone guardian finally crumbles, the light in its eyes fading. As the dust settles, you notice something among the rubble.",
                "defeat_text": "The stone guardian's powerful blow sends you reeling. You barely manage to escape, battered and bruised.",
                "reward": {"item": "ancient_coin", "chance": 1.0},
                "escape_chance": 0.6,
                "escape_damage": 10
            },
            "archaeologist": {
                "name": "Amateur Archaeologist",
                "description": "A middle-aged woman with glasses and exploration gear, taking notes on the ruins.",
                "friendly": True,
                "dialogue": [
                    "The woman looks up from her notebook, surprised to see another person.",
                    "'Oh! Hello there! Are you studying these ruins too? Fascinating structures, aren't they?'",
                    "'I've been documenting the symbols and trying to decipher their meaning. They refer repeatedly to a 'heart of crystal' that sustains the land.'",
                    "'There's mention of a ritual chamber underneath us. I haven't found the entrance yet, but I'm sure it's here somewhere.'",
                    "'Here, take a copy of my notes. Maybe they'll help you understand this place.'"
                ],
                "reward": {"item": "stone_tablet", "chance": 0.8},
                "knowledge": "underground_chamber"
            },
            "will_o_wisp": {
                "name": "Will-o'-Wisp",
                "description": "A floating ball of eerie bluish light that bobs and weaves through the swamp.",
                "friendly": False,
                "combat": False,
                "dialogue": [
                    "The mysterious light floats just out of reach, seeming to beckon you deeper into the swamp.",
                    "As you follow, you feel a strange compulsion pulling you forward, though something in your mind warns of danger.",
                    "The light suddenly splits into three, then five, creating a disorienting pattern around you.",
                    "You realize you've wandered off the path and are now ankle-deep in murky water. The lights continue to dance mockingly around you."
                ],
                "effect": "confusion",
                "damage": 5,
                "escape_chance": 0.7,
                "knowledge": "wisp_danger"
            },
            "swamp_creature": {
                "name": "Swamp Creature",
                "description": "A humanoid figure covered in moss and swamp vegetation, with glowing yellow eyes.",
                "friendly": False,
                "combat": True,
                "health": 30,
                "damage": 10,
                "victory_text": "The swamp creature sinks back into the murky water, defeated. Something it was carrying floats to the surface.",
                "defeat_text": "The creature overpowers you, dragging you partially into the muck before you manage to break free and retreat.",
                "reward": {"item": "strange_tooth", "chance": 0.9},
                "escape_chance": 0.5,
                "escape_damage": 15
            },
            "friendly_fisher": {
                "name": "Elderly Fisher",
                "description": "An old man sitting peacefully on the dock with a fishing rod and a small pile of fish.",
                "friendly": True,
                "dialogue": [
                    "The old man nods as you approach, but keeps his eyes on his fishing line.",
                    "'Nice day for fishing, isn't it? The water's been strange lately - more fish than usual, but they're... different.'",
                    "'Been fishing these waters for fifty years, and I've never seen them glow like they do now.'",
                    "'Something's changed in the deep caves where the river starts. The water carries the energy down.'",
                    "'Here, take this old rod of mine. Might come in handy if you need to eat. Fish are plentiful here.'"
                ],
                "reward": {"item": "fishing_rod", "chance": 0.8},
                "knowledge": "water_energy"
            },
            "river_guardian": {
                "name": "River Spirit",
                "description": "A translucent, flowing humanoid figure that rises from the water, composed entirely of liquid.",
                "friendly": True,
                "conditional_friendly": {"item": "ceremonial_dagger", "friendly": False},
                "dialogue": [
                    "The water coalesces into a vaguely human shape that regards you with curiosity.",
                    "A voice like flowing water speaks directly into your mind.",
                    "'Human visitor, you walk a dangerous path. The heart grows unstable, and with it, all the land.'",
                    "'Seek the waterfall cave. Behind the curtain of water lies knowledge you will need.'",
                    "'Take this token of the river's blessing. It will help you breathe when waters rise.'"
                ],
                "combat": {
                    "condition": {"item": "ceremonial_dagger", "present": True},
                    "health": 45,
                    "damage": 12,
                    "victory_text": "The river spirit dissolves back into the water, a look of sadness in its fluid features. A small whirlpool forms, revealing something at its center.",
                    "defeat_text": "The spirit's watery form engulfs you briefly, filling your lungs with water before releasing you. You crawl to shore, coughing and sputtering."
                },
                "reward": {"item": "glowing_crystal", "chance": 0.9},
                "escape_chance": 0.4,
                "escape_damage": 20,
                "knowledge": "waterfall_cave"
            },
            "shadow_guardian": {
                "name": "Shadow Guardian",
                "description": "A humanoid figure composed of swirling darkness with glowing red eyes.",
                "friendly": False,
                "combat": True,
                "health": 50,
                "damage": 18,
                "weakness": "glowing_crystal",
                "weakness_text": "The shadow guardian recoils from the crystal's light, its form becoming less substantial and more vulnerable.",
                "victory_text": "The shadow disperses with a hollow cry, leaving behind a small object that gleams in the dim light.",
                "defeat_text": "The shadow overwhelms you, its cold essence draining your strength. You barely escape with your life.",
                "reward": {"item": "ceremonial_dagger", "chance": 0.7},
                "escape_chance": 0.3,
                "escape_damage": 25
            },
            "lost_explorer": {
                "name": "Lost Explorer",
                "description": "A disheveled man in tattered explorer gear, his eyes wide with fear and madness.",
                "friendly": False,
                "dialogue": [
                    "The man scrambles away as you approach, raising a makeshift weapon defensively.",
                    "'Stay back! I won't let you take it from me! The orb is MINE!'",
                    "His eyes dart nervously around the chamber, never focusing on one spot for long.",
                    "'The voices... they speak through the crystals. They promised me power if I bring the orb to the heart!'",
                    "He suddenly lunges at you, his face contorted with desperate rage."
                ],
                "combat": True,
                "health": 25,
                "damage": 10,
                "victory_text": "The explorer collapses, dropping his weapon. 'The voices... they lied...' he whispers before losing consciousness.",
                "defeat_text": "The explorer's frenzied attack drives you back. He uses the opportunity to flee deeper into the ruins.",
                "reward": {"item": "glowing_orb", "chance": 0.8},
                "escape_chance": 0.6,
                "escape_damage": 15,
                "knowledge": "corrupting_influence"
            },
            "swamp_lurker": {
                "name": "Swamp Lurker",
                "description": "A massive reptilian creature with multiple eyes and jagged teeth, mostly submerged in the murky water.",
                "friendly": False,
                "combat": True,
                "health": 60,
                "damage": 20,
                "victory_text": "The lurker thrashes wildly before sinking beneath the surface, leaving behind a trail of viscous blood. Something floats up from where it disappeared.",
                "defeat_text": "The creature's powerful jaws close around your leg, dragging you toward deeper water. You fight desperately and break free, but not without serious injury.",
                "reward": {"item": "strange_tooth", "chance": 1.0},
                "escape_chance": 0.2,
                "escape_damage": 30
            },
            "lost_soul": {
                "name": "Lost Soul",
                "description": "A translucent, glowing figure that seems to be the ghost of someone who died in the swamp.",
                "friendly": True,
                "dialogue": [
                    "The spectral figure approaches slowly, sorrow evident in its translucent features.",
                    "'Traveler... beware this cursed place. I came seeking the witch's wisdom and never left.'",
                    "'The heart's power grows unstable, affecting all beings connected to this land.'",
                    "'The witch knows more than she admits. Approach with caution, but do not miss her counsel.'",
                    "The spirit points toward a barely visible path before fading slowly away."
                ],
                "effect": "reveal_path",
                "knowledge": "witch_knowledge"
            },
            "cave_dweller": {
                "name": "Cave Hermit",
                "description": "An ancient-looking person wrapped in furs, with skin as pale as milk from years without sunlight.",
                "friendly": True,
                "dialogue": [
                    "The hermit squints at you in the dim light, tilting their head curiously.",
                    "'A visitor? It has been... many seasons since I last saw another person.'",
                    "'I came here long ago to study the waters and their connection to the crystal heart.'",
                    "'The waterfall is no ordinary water - it carries the essence of the heart itself.'",
                    "'Take this amulet. I crafted it from materials blessed by the waters. It may protect you from the heart's more... volatile energies.'"
                ],
                "reward": {"item": "sacred_amulet", "chance": 1.0},
                "knowledge": "heart_volatility"
            },
            "crystal_elemental": {
                "name": "Crystal Elemental",
                "description": "A humanoid figure composed entirely of living crystal that shifts and reforms as it moves.",
                "friendly": False,
                "combat": True,
                "health": 45,
                "damage": 15,
                "weakness": "ceremonial_dagger",
                "weakness_text": "The ceremonial dagger seems to resonate with the elemental's crystalline structure, causing fractures to appear where it strikes.",
                "victory_text": "The elemental shatters into thousands of glittering fragments. Among them, one piece stands out.",
                "defeat_text": "The elemental's crystalline limbs cut into you like glass. You retreat, bleeding from multiple lacerations.",
                "reward": {"item": "crystal_shard", "chance": 1.0},
                "escape_chance": 0.5,
                "escape_damage": 20
            },
            "lost_miner": {
                "name": "Crystal Miner",
                "description": "A middle-aged woman with a pickaxe and collection bag, covered in crystal dust.",
                "friendly": True,
                "dialogue": [
                    "The woman jumps at your approach, raising her pickaxe defensively before relaxing slightly.",
                    "'Don't sneak up on me like that! These tunnels aren't safe anymore.'",
                    "'I've been mining crystals here for years, but lately they've been... changing. Growing faster, pulsing with energy.'",
                    "'Something's happening at the heart chamber. The crystals closest to it have started forming into conscious entities.'",
                    "'Here, take this energy stone. It might help you if you're heading deeper in. Just be careful - the guardian at the heart has been acting erratically.'"
                ],
                "reward": {"item": "energy_stone", "chance": 0.9},
                "knowledge": "crystal_transformation"
            },
            "swamp_witch": {
                "name": "Swamp Witch",
                "description": "An imposing woman with wildly tangled hair adorned with bones and feathers, wearing robes of moss and bark.",
                "friendly": True,
                "conditional_friendly": {"knowledge": "witch_secret", "friendly": False},
                "dialogue": [
                    "The witch studies you with piercing green eyes that seem to see right through you.",
                    "'I've been expecting someone. The heart grows restless, and the land with it.'",
                    "'You seek answers, yes? About why you're here, about the strange power in these lands?'",
                    "'The crystal heart is ancient - older than humans in this region. It sustained a civilization long ago, but they grew greedy and tried to harness too much of its power.'",
                    "'Take this book. Study it well. If you wish to either restore balance or claim the heart's power for yourself, you'll need this knowledge.'"
                ],
                "combat": {
                    "condition": {"knowledge": "witch_secret", "present": True},
                    "health": 70,
                    "damage": 25,
                    "victory_text": "The witch falls to her knees, blood seeping from a wound. 'You fool,' she gasps. 'Without me to perform the ritual, the heart will never be stable again.' She collapses.",
                    "defeat_text": "The witch's magic overwhelms you, crushing you with invisible force. 'Leave this place,' she commands, 'before I decide to end your miserable existence.'"
                },
                "reward": {"item": "spell_book", "chance": 0.8},
                "escape_chance": 0.4,
                "escape_damage": 30,
                "knowledge": "heart_ritual"
            },
            "familiar": {
                "name": "Witch's Familiar",
                "description": "A large raven with unusually intelligent eyes and a few white feathers forming a star pattern on its chest.",
                "friendly": True,
                "dialogue": [
                    "The raven cocks its head, studying you with uncanny intelligence.",
                    "To your shock, it speaks in a raspy voice: 'Another seeker of the heart? How ambitious.'",
                    "'My mistress sees much, but reveals little. Watch her carefully if you value your life.'",
                    "'The heart has called many to it over the centuries. Few return unchanged... if they return at all.'",
                    "The raven flutters to a shelf and knocks something down before flying to a perch in the rafters."
                ],
                "reward": {"item": "potion_bottle", "chance": 0.7},
                "knowledge": "witch_secret"
            },
            "crystal_guardian": {
                "name": "Heart Guardian",
                "description": "A twelve-foot humanoid composed of pulsing crystal, with a core of brilliant light visible in its chest.",
                "friendly": False,
                "combat": True,
                "health": 100,
                "damage": 30,
                "weakness": ["ceremonial_dagger", "sacred_amulet"],
                "weakness_text": "The guardian falters as your artifacts disrupt the flow of energy through its crystalline form.",
                "victory_text": "With a sound like a thousand bells breaking, the guardian collapses into fragments. The way to the heart crystal is now clear.",
                "defeat_text": "The guardian's overwhelming power forces you to retreat, battered and on the verge of unconsciousness.",
                "reward": {"item": "heart_shard", "chance": 0.5},
                "escape_chance": 0.3,
                "escape_damage": 40
            },
            "energy_spirit": {
                "name": "Energy Spirit",
                "description": "A swirling vortex of pure energy with occasional glimpses of a face-like pattern within it.",
                "friendly": True,
                "conditional_friendly": {"knowledge": "heart_purpose", "friendly": True},
                "dialogue": [
                    "The energy coalesces into a more defined shape as you approach, forming a vaguely humanoid figure composed of swirling light.",
                    "It speaks without sound, the words forming directly in your mind.",
                    "'You have come far, seeker. The heart calls to those who might help it.'",
                    "'Long ago, we were the guardians of this power, but our physical forms have long since passed. Now we exist only as energy bound to the heart.'",
                    "'If you truly wish to help, take this flask. Capture the essence of the heart within it, then use the ceremonial dagger at the altar in the underground chamber.'"
                ],
                "combat": {
                    "condition": {"knowledge": "heart_purpose", "present": False},
                    "health": 60,
                    "damage": 20,
                    "victory_text": "The spirit disperses with a silent cry, fragments of its energy scattering throughout the chamber before reforming at a distance, weaker now.",
                    "defeat_text": "The spirit's energy overwhelms your senses, sending searing pain through your body before dropping you to the ground."
                },
                "reward": {"item": "energy_flask", "chance": 1.0},
                "escape_chance": 0.5,
                "escape_damage": 25,
                "knowledge": "ritual_components"
            },
            "crystal_overlord": {
                "name": "Crystal Overlord",
                "description": "A massive, sentient formation of crystal that has grown to engulf part of the heart. Gleaming facets reflect your image distortedly as it pulses with power.",
                "boss": True,
                "friendly": False,
                "dialogue": [
                    "The massive crystal formation vibrates, sending shards flying around the chamber.",
                    "A booming voice resonates from it, shaking the very ground.",
                    "'MORTAL. YOU SEEK THE HEART'S POWER. ALL DO. ALL FAIL.'",
                    "'I HAVE MERGED WITH THE HEART. ITS POWER IS MINE. SOON ALL WILL BE CRYSTAL.'",
                    "'SURRENDER YOUR FLESH FORM AND JOIN THE PURITY OF CRYSTAL CONSCIOUSNESS... OR BE DESTROYED.'"
                ],
                "combat": True,
                "phases": 3,
                "health": 150,
                "damage": [20, 30, 40],
                "special_attacks": [
                    {"name": "Crystal Barrage", "damage": 25, "effect": "multiple_cuts"},
                    {"name": "Energy Pulse", "damage": 35, "effect": "stun"},
                    {"name": "Crystal Absorption", "effect": "heal", "amount": 20}
                ],
                "weakness": ["ceremonial_dagger", "sacred_amulet", "energy_flask"],
                "weakness_text": "Your special items disrupt the overlord's connection to the heart, causing visible fissures in its structure.",
                "victory_text": "With a deafening crack, the crystal overlord shatters, releasing the heart from its corrupting influence. The heart's pulsing stabilizes, and a sense of balance returns to the chamber.",
                "defeat_text": "The overlord's power proves too great. Your consciousness fades as crystal begins to form on your skin. You have failed.",
                "reward": {"item": "heart_essence", "chance": 1.0},
                "escape_chance": 0.1,
                "escape_damage": 50,
                "knowledge": "heart_freedom"
            }
        }
        
        # Special effects dictionary
        self.effects = {
            "light": lambda: f"{Fore.YELLOW}The area around you is illuminated, making it easier to see details.",
            "small_heal": self.effect_small_heal,
            "medium_heal": self.effect_medium_heal,
            "large_heal": self.effect_large_heal,
            "restore_energy": self.effect_restore_energy,
            "restore_health_and_energy": self.effect_restore_health_and_energy,
            "show_map": self.effect_show_map,
            "crystal_guide": self.effect_crystal_guide,
            "directional_hint": self.effect_directional_hint,
            "nature_sense": self.effect_nature_sense,
            "heal_and_antidote": self.effect_heal_and_antidote,
            "vision": self.effect_vision,
            "quest_info": self.effect_quest_info,
            "fishing": self.effect_fishing,
            "confusion": self.effect_confusion,
            "reveal_path": self.effect_reveal_path,
            "multiple_cuts": self.effect_multiple_cuts,
            "stun": self.effect_stun
        }
        
        # Tutorial tips to show based on actions
        self.tutorial_tips = {
            "movement": "Use 'go [direction]' or simply '[direction]' to move. For example: 'go north' or just 'north'.",
            "look": "Use 'look' to examine your surroundings or 'look at [object]' to examine specific things.",
            "inventory": "Type 'inventory' or 'i' to see what you're carrying.",
            "take": "Use 'take [item]' to pick up objects you find.",
            "use": "Type 'use [item]' to use or activate items in your inventory.",
            "help": "Type 'help' at any time to see available commands.",
            "stats": "Check your health and energy with the 'stats' command.",
            "combat": "In combat, you can 'attack', 'use [item]', or try to 'flee'.",
            "talk": "Use 'talk' when you encounter someone or something that might communicate with you.",
            "examine": "Use 'examine [item]' to get detailed information about something in your inventory or surroundings."
        }
        
        # Quest information
        self.quests = {
            "find_key": {
                "name": "Mysterious Surroundings",
                "description": "Explore your surroundings and try to figure out where you are and why you're here.",
                "objective": "Explore at least 3 different areas.",
                "completion_condition": "rooms_visited",
                "completion_value": 3,
                "reward": {"health_boost": 10, "energy_boost": 10},
                "next_quest": "ruins_exploration"
            },
            "ruins_exploration": {
                "name": "Ancient Secrets",
                "description": "The ruins seem to hold information about this place. Find a way into the underground chamber.",
                "objective": "Find and enter the underground chamber beneath the ruins.",
                "completion_condition": "visit_room",
                "completion_value": "underground_chamber",
                "reward": {"item": "energy_stone"},
                "next_quest": "heart_investigation"
            },
            "heart_investigation": {
                "name": "The Crystal Heart",
                "description": "Discover the nature and purpose of the Crystal Heart that seems to power this region.",
                "objective": "Find the Crystal Heart chamber.",
                "completion_condition": "visit_room",
                "completion_value": "crystal_heart",
                "reward": {"health_boost": 20, "energy_boost": 20},
                "next_quest": "heart_restoration"
            },
            "heart_restoration": {
                "name": "Restoring Balance",
                "description": "The Crystal Heart has been corrupted and is becoming unstable. Perform the ritual to restore it.",
                "objective": "Defeat the Crystal Overlord and use the ritual components at the heart.",
                "completion_condition": "special_event",
                "completion_value": "heart_ritual_completed",
                "reward": {"game_completion": True},
                "next_quest": None
            }
        }
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def wrap_text(self, text, width=80):
        """Wrap text to specified width"""
        return textwrap.fill(text, width)
    
    def print_header(self):
        """Print game header with stats"""
        self.clear_screen()
        print(Fore.CYAN + "=" * self.screen_width)
        print(Fore.YELLOW + "CRYSTAL HEART ADVENTURE".center(self.screen_width))
        print(Fore.CYAN + "=" * self.screen_width)
        print(f"{Fore.GREEN}Health: {self.health}/{self.maximum_health} | {Fore.BLUE}Energy: {self.energy}/{self.maximum_energy} | Location: {self.rooms[self.current_room]['name']}")
        
        # Show active quest
        if self.current_quest:
            quest = self.quests[self.current_quest]
            print(f"{Fore.MAGENTA}Quest: {quest['name']} - {quest['objective']}")
        
        print(Fore.CYAN + "-" * self.screen_width)
    
    def get_room_description(self, detailed=False):
        """Get current room description"""
        room = self.rooms[self.current_room]
        
        # Choose which description to use
        if detailed:
            desc = room["detailed_description"]
        else:
            desc = room["description"]
        
        # Add items information
        if room["items"]:
            item_list = ", ".join([self.items[item]["name"] for item in room["items"]])
            desc += f"\n\nYou see: {item_list}"
        
        # Add exit information
        exits = []
        for direction, destination in room["connections"].items():
            # Check if exit is locked
            if "locks" in room and direction in room["locks"]:
                lock = room["locks"][direction]
                if "item" in lock and lock["item"] in self.inventory:
                    exits.append(direction)
                elif "special" in lock and lock["special"] in self.events_triggered:
                    exits.append(direction)
            else:
                exits.append(direction)
        
        exit_list = ", ".join(exits)
        desc += f"\n\nExits: {exit_list}"
        
        return desc
    
    def move(self, direction):
        """Attempt to move in a direction"""
        room = self.rooms[self.current_room]
        
        # Check if direction is valid
        if direction not in room["connections"]:
            return f"{Fore.RED}You can't go {direction} from here."
        
        # Check if direction is locked
        if "locks" in room and direction in room["locks"]:
            lock = room["locks"][direction]
            if "item" in lock and lock["item"] not in self.inventory:
                return f"{Fore.RED}{lock['message']}"
            elif "special" in lock and lock["special"] not in self.events_triggered:
                return f"{Fore.RED}{lock['message']}"
        
        # Energy cost for movement
        self.energy = max(0, self.energy - 2)
        
        # Move to next room
        next_room = room["connections"][direction]
        self.current_room = next_room
        self.move_count += 1
        
        # Update discovered rooms and visits
        self.discovered_rooms.add(next_room)
        self.room_visits[next_room] = self.room_visits.get(next_room, 0) + 1
        
        # Check for first visit text
        first_visit_text = ""
        if self.room_visits[next_room] == 1 and "first_visit_text" in self.rooms[next_room]:
            first_visit_text = f"\n\n{Fore.YELLOW}{self.rooms[next_room]['first_visit_text']}"
        
        # Show tutorial tip for new players
        if self.auto_help and self.move_count < 5:
            tutorial_tip = f"\n\n{Fore.CYAN}Tip: {self.tutorial_tips['look']}"
        else:
            tutorial_tip = ""
        
        # Check for random encounter
        encounter_text = ""
        if "encounters" in self.rooms[next_room] and random.random() < 0.3:
            encounter = random.choice(self.rooms[next_room]["encounters"])
            encounter_text = f"\n\n{Fore.YELLOW}You encounter a {self.encounters[encounter]['name']}!\nType 'talk' to interact or 'look at {self.encounters[encounter]['name'].lower()}' to observe."
            self.current_encounter = encounter
        else:
            self.current_encounter = None
        
        # Check for quest update
        self.check_quest_progress()
        
        # Return combined description
        full_description = f"{self.get_room_description(detailed=True)}{first_visit_text}{tutorial_tip}{encounter_text}"
        
        return full_description
    
    def take(self, item_name):
        """Take an item from current room"""
        room = self.rooms[self.current_room]
        
        # Find matching item
        matching_item = None
        for item_id in room["items"]:
            if item_name.lower() in self.items[item_id]["name"].lower():
                matching_item = item_id
                break
        
        # Check if item exists in room
        if not matching_item:
            return f"{Fore.RED}There is no {item_name} here that you can take."
        
        # Add to inventory and remove from room
        self.inventory.append(matching_item)
        room["items"].remove(matching_item)
        
        # Show tutorial tip for new players
        if self.auto_help and "inventory" not in self.tutorial_tips_shown:
            self.tutorial_tips_shown.add("inventory")
            tutorial_tip = f"\n\n{Fore.CYAN}Tip: {self.tutorial_tips['inventory']}"
        else:
            tutorial_tip = ""
        
        return f"{Fore.GREEN}You picked up the {self.items[matching_item]['name']}.{tutorial_tip}"
    
    def drop(self, item_name):
        """Drop an item in current room"""
        # Find matching item
        matching_item = None
        for item_id in self.inventory:
            if item_name.lower() in self.items[item_id]["name"].lower():
                matching_item = item_id
                break
        
        # Check if item is in inventory
        if not matching_item:
            return f"{Fore.RED}You don't have a {item_name}."
        
        # Add to room and remove from inventory
        room = self.rooms[self.current_room]
        room["items"].append(matching_item)
        self.inventory.remove(matching_item)
        
        return f"{Fore.YELLOW}You dropped the {self.items[matching_item]['name']}."
    
    def show_inventory(self):
        """Display player's inventory"""
        if not self.inventory:
            return f"{Fore.YELLOW}Your inventory is empty."
        
        inventory_text = f"{Fore.CYAN}Inventory:\n"
        for item_id in self.inventory:
            inventory_text += f"- {self.items[item_id]['name']}: {self.items[item_id]['description']}\n"
        
        # Show tutorial tip for new players
        if self.auto_help and "examine" not in self.tutorial_tips_shown:
            self.tutorial_tips_shown.add("examine")
            inventory_text += f"\n{Fore.CYAN}Tip: {self.tutorial_tips['examine']}"
        
        return inventory_text
    
    def examine(self, thing_name):
        """Examine an item in inventory or environment"""
        # Check inventory first
        for item_id in self.inventory:
            if thing_name.lower() in self.items[item_id]["name"].lower():
                return f"{Fore.CYAN}{self.items[item_id]['examine_text']}"
        
        # Check room items
        room = self.rooms[self.current_room]
        for item_id in room["items"]:
            if thing_name.lower() in self.items[item_id]["name"].lower():
                return f"{Fore.CYAN}{self.items[item_id]['examine_text']}"
        
        # Check for current encounter
        if (self.current_encounter and 
            thing_name.lower() in self.encounters[self.current_encounter]["name"].lower()):
            return f"{Fore.CYAN}{self.encounters[self.current_encounter]['description']}"
        
        # Check general room features
        if thing_name.lower() in room["name"].lower():
            return f"{Fore.CYAN}{room['detailed_description']}"
        
        return f"{Fore.RED}You don't see anything special about that."
    
    def use_item(self, item_name):
        """Use an item from inventory"""
        # Find matching item
        matching_item = None
        for item_id in self.inventory:
            if item_name.lower() in self.items[item_id]["name"].lower():
                matching_item = item_id
                break
        
        # Check if item exists in inventory
        if not matching_item:
            return f"{Fore.RED}You don't have a {item_name} to use."
        
        # Check if item is usable
        item = self.items[matching_item]
        if not item.get("usable", False):
            return f"{Fore.RED}You're not sure how to use the {item['name']}."
        
        # Check for location-specific items
        if "use_location" in item and item["use_location"] != self.current_room:
            return f"{Fore.YELLOW}This doesn't seem to be the right place to use the {item['name']}."
        
        # Get use text
        use_text = f"{Fore.GREEN}{item['use_text']}"
        
        # Apply effect if any
        effect_text = ""
        if "use_effect" in item and item["use_effect"] in self.effects:
            effect_func = self.effects[item["use_effect"]]
            effect_text = effect_func()
        
        return f"{use_text}\n\n{effect_text}" if effect_text else use_text
    
    def talk(self):
        """Talk to the current encounter if there is one"""
        if not self.current_encounter:
            return f"{Fore.RED}There's no one here to talk to."
        
        encounter = self.encounters[self.current_encounter]
        
        # Check for conditional friendliness
        if "conditional_friendly" in encounter:
            condition = encounter["conditional_friendly"]
            if "item" in condition and condition["item"] in self.inventory:
                is_friendly = condition["friendly"]
            elif "knowledge" in condition and condition["knowledge"] in self.knowledge:
                is_friendly = condition["friendly"]
            else:
                is_friendly = encounter.get("friendly", True)
        else:
            is_friendly = encounter.get("friendly", True)
        
        # Handle conversation or combat
        if is_friendly:
            dialogue = encounter.get("dialogue", ["They don't seem interested in talking."])
            conversation = f"{Fore.CYAN}"
            for line in dialogue:
                conversation += line + "\n\n"
            
            # Add knowledge if applicable
            if "knowledge" in encounter:
                self.knowledge.add(encounter["knowledge"])
                conversation += f"{Fore.YELLOW}You've learned something new about {encounter['knowledge'].replace('_', ' ')}."
            
            # Check for reward
            reward_text = ""
            if "reward" in encounter:
                reward = encounter["reward"]
                if random.random() < reward.get("chance", 0.5):
                    reward_item = reward["item"]
                    if reward_item not in self.inventory:
                        self.inventory.append(reward_item)
                        reward_text = f"\n\n{Fore.GREEN}You received: {self.items[reward_item]['name']}"
            
            # Clear encounter after talking
            self.current_encounter = None
            
            return conversation + reward_text
        else:
            # Initiate combat if encounter is hostile
            if encounter.get("combat", False):
                return self.initiate_combat(encounter)
            elif "effect" in encounter:
                # Apply special effect
                effect_func = self.effects.get(encounter["effect"])
                if effect_func:
                    effect_text = effect_func()
                    self.current_encounter = None
                    return f"{Fore.RED}{effect_text}"
                else:
                    self.current_encounter = None
                    return f"{Fore.RED}The encounter ends without incident."
            else:
                self.current_encounter = None
                return f"{Fore.RED}They don't seem interested in talking."
    
    def initiate_combat(self, encounter):
        """Start combat with an entity"""
        # Check for conditional combat
        if "combat" in encounter and isinstance(encounter["combat"], dict):
            condition = encounter["combat"]["condition"]
            should_fight = False
            
            if "item" in condition and condition["item"] in self.inventory:
                should_fight = condition.get("present", True)
            elif "knowledge" in condition and condition["knowledge"] in self.knowledge:
                should_fight = condition.get("present", True)
            
            if not should_fight:
                self.current_encounter = None
                return f"{Fore.YELLOW}The {encounter['name']} decides not to fight you."
            
            # Set up combat parameters from condition
            combat_params = encounter["combat"]
        else:
            combat_params = encounter
        
        # Initialize combat
        self.in_combat = True
        self.combat_entity = encounter["name"]
        self.combat_health = combat_params.get("health", 20)
        self.combat_max_health = self.combat_health
        self.combat_damage = combat_params.get("damage", 5)
        if isinstance(self.combat_damage, list):  # For phased bosses
            self.combat_damage = self.combat_damage[0]
        self.combat_phase = 0
        
        return f"{Fore.RED}Combat initiated with {encounter['name']}!\n{Fore.CYAN}You can 'attack', 'use [item]', or try to 'flee'."
    
    def combat_attack(self):
        """Player attacks in combat"""
        if not self.in_combat:
            return f"{Fore.RED}You're not in combat."
        
        # Calculate player damage (5-10 base damage)
        player_damage = random.randint(5, 10)
        
        # Check for weapon in inventory
        for item_id in self.inventory:
            if "combat_power" in self.items[item_id]:
                player_damage += self.items[item_id]["combat_power"]
        
        # Apply damage to enemy
        self.combat_health -= player_damage
        
        # Check if enemy is defeated
        if self.combat_health <= 0:
            return self.combat_victory()
        
        # Enemy attacks back
        enemy_damage = random.randint(max(1, self.combat_damage - 3), self.combat_damage)
        self.health -= enemy_damage
        
        # Check if player is defeated
        if self.health <= 0:
            self.health = 1  # Prevent actual death, just severe injury
            self.in_combat = False
            
            # Get defeat text
            encounter = self.encounters[self.current_encounter]
            defeat_text = encounter.get("defeat_text", f"You are defeated by the {encounter['name']} and barely escape with your life.")
            
            self.current_encounter = None
            return f"{Fore.RED}{defeat_text}\n\n{Fore.RED}You are severely injured and need to recover."
        
        # Check for boss phase transition
        encounter = self.encounters[self.current_encounter]
        if "phases" in encounter and self.combat_health <= self.combat_max_health * (1 - (self.combat_phase + 1) / encounter["phases"]):
            self.combat_phase += 1
            if isinstance(encounter["damage"], list) and len(encounter["damage"]) > self.combat_phase:
                self.combat_damage = encounter["damage"][self.combat_phase]
            
            phase_text = f"\n\n{Fore.MAGENTA}The {encounter['name']} enters a new phase! It becomes more aggressive!"
        else:
            phase_text = ""
        
        return f"{Fore.GREEN}You attack the {encounter['name']} for {player_damage} damage!\n{Fore.RED}The {encounter['name']} strikes back for {enemy_damage} damage!\n\n{Fore.YELLOW}Your Health: {self.health}/{self.maximum_health}\n{encounter['name']}'s Health: {self.combat_health}/{self.combat_max_health}{phase_text}"
    
    def combat_use_item(self, item_name):
        """Use an item during combat"""
        if not self.in_combat:
            return f"{Fore.RED}You're not in combat."
        
        # Find matching item
        matching_item = None
        for item_id in self.inventory:
            if item_name.lower() in self.items[item_id]["name"].lower():
                matching_item = item_id
                break
        
        # Check if item exists in inventory
        if not matching_item:
            return f"{Fore.RED}You don't have a {item_name} to use."
        
        # Check if item is usable
        item = self.items[matching_item]
        if not item.get("usable", False):
            return f"{Fore.RED}You're not sure how to use the {item['name']} in combat."
        
        # Get use text
        use_text = f"{Fore.GREEN}{item['use_text']}"
        
        # Apply effect if any
        effect_text = ""
        if "use_effect" in item and item["use_effect"] in self.effects:
            effect_func = self.effects[item["use_effect"]]
            effect_text = effect_func()
        
        # Check if item is a weakness for the enemy
        encounter = self.encounters[self.current_encounter]
        weakness_text = ""
        if "weakness" in encounter:
            weaknesses = encounter["weakness"]
            if not isinstance(weaknesses, list):
                weaknesses = [weaknesses]
            
            if matching_item in weaknesses:
                # Extra damage for using a weakness
                self.combat_health -= 15
                weakness_text = f"\n\n{Fore.YELLOW}{encounter.get('weakness_text', f'The {item['name']} seems particularly effective against the {encounter['name']}!')}"
                
                # Check for victory
                if self.combat_health <= 0:
                    return f"{use_text}\n\n{effect_text}\n\n{weakness_text}\n\n{self.combat_victory()}"
        
        # Enemy still attacks
        enemy_damage = random.randint(max(1, self.combat_damage - 3), self.combat_damage)
        self.health -= enemy_damage
        
        # Check if player is defeated
        if self.health <= 0:
            self.health = 1  # Prevent actual death
            self.in_combat = False
            
            # Get defeat text
            defeat_text = encounter.get("defeat_text", f"You are defeated by the {encounter['name']} and barely escape with your life.")
            
            self.current_encounter = None
            return f"{use_text}\n\n{effect_text}\n\n{weakness_text}\n\n{Fore.RED}{defeat_text}\n\n{Fore.RED}You are severely injured and need to recover."
        
        return f"{use_text}\n\n{effect_text}\n\n{weakness_text}\n\n{Fore.RED}The {encounter['name']} attacks for {enemy_damage} damage!\n\n{Fore.YELLOW}Your Health: {self.health}/{self.maximum_health}\n{encounter['name']}'s Health: {self.combat_health}/{self.combat_max_health}"
    
    def combat_flee(self):
        """Attempt to flee from combat"""
        if not self.in_combat:
            return f"{Fore.RED}You're not in combat."
        
        encounter = self.encounters[self.current_encounter]
        escape_chance = encounter.get("escape_chance", 0.5)
        
        if random.random() < escape_chance:
            self.in_combat = False
            self.current_encounter = None
            return f"{Fore.GREEN}You successfully escape from the {encounter['name']}!"
        else:
            # Take damage from failed escape
            escape_damage = encounter.get("escape_damage", self.combat_damage)
            self.health -= escape_damage
        
        # Check if player is defeated
        if self.health <= 0:
            self.health = 1  # Prevent actual death
            self.in_combat = False
            
            # Get defeat text
            defeat_text = encounter.get("defeat_text", f"You are defeated by the {encounter['name']} and barely escape with your life.")
            
            self.current_encounter = None
            return f"{Fore.RED}You fail to escape and take {escape_damage} damage in the process!\n\n{Fore.RED}{defeat_text}\n\n{Fore.RED}You are severely injured and need to recover."
        
        return f"{Fore.RED}You fail to escape and take {escape_damage} damage in the process!\n\n{Fore.YELLOW}Your Health: {self.health}/{self.maximum_health}\n{encounter['name']}'s Health: {self.combat_health}/{self.combat_max_health}"

    def combat_victory(self):
        """Handle victory in combat"""
        encounter = self.encounters[self.current_encounter]
        
        # Get victory text
        victory_text = encounter.get("victory_text", f"You have defeated the {encounter['name']}!")
        
        # Check for reward
        reward_text = ""
        if "reward" in encounter:
            reward = encounter["reward"]
            if random.random() < reward.get("chance", 0.5):
                reward_item = reward["item"]
                if reward_item not in self.inventory:
                    self.inventory.append(reward_item)
                    reward_text = f"\n\n{Fore.GREEN}You received: {self.items[reward_item]['name']}"
        
        # Add knowledge if applicable
        knowledge_text = ""
        if "knowledge" in encounter:
            self.knowledge.add(encounter["knowledge"])
            knowledge_text = f"\n\n{Fore.YELLOW}You've learned something new about {encounter['knowledge'].replace('_', ' ')}."
        
        # Reset combat state
        self.in_combat = False
        self.current_encounter = None
        
        return f"{Fore.GREEN}{victory_text}{reward_text}{knowledge_text}"

    # Item effect methods
    def effect_light(self):
        """Effect for items that provide light"""
        return f"{Fore.YELLOW}The area around you is illuminated, making it easier to see details."

    def effect_small_heal(self):
        """Heal a small amount of health"""
        heal_amount = 10
        self.health = min(self.maximum_health, self.health + heal_amount)
        return f"{Fore.GREEN}You recover {heal_amount} health points. Current health: {self.health}/{self.maximum_health}"

    def effect_medium_heal(self):
        """Heal a medium amount of health"""
        heal_amount = 25
        self.health = min(self.maximum_health, self.health + heal_amount)
        return f"{Fore.GREEN}You recover {heal_amount} health points. Current health: {self.health}/{self.maximum_health}"

    def effect_large_heal(self):
        """Heal a large amount of health"""
        heal_amount = 50
        self.health = min(self.maximum_health, self.health + heal_amount)
        return f"{Fore.GREEN}You recover {heal_amount} health points. Current health: {self.health}/{self.maximum_health}"

    def effect_restore_energy(self):
        """Restore energy"""
        energy_amount = 30
        self.energy = min(self.maximum_energy, self.energy + energy_amount)
        return f"{Fore.BLUE}You recover {energy_amount} energy points. Current energy: {self.energy}/{self.maximum_energy}"

    def effect_restore_health_and_energy(self):
        """Restore both health and energy"""
        heal_amount = 30
        energy_amount = 30
        self.health = min(self.maximum_health, self.health + heal_amount)
        self.energy = min(self.maximum_energy, self.energy + energy_amount)
        return f"{Fore.GREEN}You recover {heal_amount} health and {energy_amount} energy. Current stats: Health {self.health}/{self.maximum_health}, Energy {self.energy}/{self.maximum_energy}"

    def effect_show_map(self):
        """Show a map of discovered areas"""
        map_text = f"{Fore.CYAN}You look at the map, which shows the areas you've discovered:\n\n"
        for room_id in sorted(self.discovered_rooms):
            if room_id == self.current_room:
                map_text += f"{Fore.YELLOW}> {self.rooms[room_id]['name']} (You are here)\n"
            else:
                map_text += f"  {self.rooms[room_id]['name']}\n"
        return map_text

    def effect_crystal_guide(self):
        """Effect for crystal that guides to important locations"""
        # Find nearest quest-related location
        if self.current_quest == "find_key":
            target = "ancient_ruins"
        elif self.current_quest == "ruins_exploration":
            target = "underground_chamber"
        elif self.current_quest == "heart_investigation":
            target = "crystal_tunnel"
        else:
            target = "crystal_heart"
        
        # Determine direction (simplified)
        room_connections = self.rooms[self.current_room]["connections"]
        if target in room_connections.values():
            # Direct connection
            for direction, room in room_connections.items():
                if room == target:
                    return f"{Fore.CYAN}The crystal pulses strongly, pointing {direction}."
        else:
            # Indirect connection, give general direction
            return f"{Fore.CYAN}The crystal glows steadily, but doesn't indicate a specific direction. You might need to explore more areas."

    def effect_directional_hint(self):
        """Give a hint about an interesting direction"""
        # Find unexplored connection
        room_connections = self.rooms[self.current_room]["connections"]
        unexplored = [direction for direction, room in room_connections.items() 
                    if room not in self.discovered_rooms]
        
        if unexplored:
            direction = random.choice(unexplored)
            return f"{Fore.CYAN}You sense something interesting might be to the {direction}."
        else:
            # All connections explored, hint about quest
            if self.current_quest == "find_key":
                return f"{Fore.CYAN}You feel drawn to explore the ancient ruins."
            elif self.current_quest == "ruins_exploration":
                return f"{Fore.CYAN}The underground chamber seems to hold important secrets."
            else:
                return f"{Fore.CYAN}You sense the crystal heart's energy growing stronger."

    def effect_nature_sense(self):
        """Enhance awareness of natural surroundings"""
        room = self.rooms[self.current_room]
        
        # Check if in natural area
        if "forest" in self.current_room or "river" in self.current_room or "swamp" in self.current_room:
            # Reveal hidden item if any
            if "hidden_items" in room:
                hidden_item = random.choice(room["hidden_items"])
                room["items"].append(hidden_item)
                room["hidden_items"].remove(hidden_item)
                return f"{Fore.GREEN}Your heightened awareness reveals a hidden {self.items[hidden_item]['name']}!"
            else:
                return f"{Fore.GREEN}You sense the natural energies around you, feeling more in tune with your surroundings."
        else:
            return f"{Fore.YELLOW}You sense that this area is less connected to natural energies."

    def effect_heal_and_antidote(self):
        """Heal and cure any negative status effects"""
        heal_amount = 20
        self.health = min(self.maximum_health, self.health + heal_amount)
        # Clear any negative effects (would be implemented in a more complex system)
        return f"{Fore.GREEN}The poultice heals your wounds and draws out any toxins. You recover {heal_amount} health and feel purified."

    def effect_vision(self):
        """Provide a vision or flashback"""
        visions = [
            "You see flashes of an ancient civilization, their technology and magic intertwined with crystal energy.",
            "A vision shows a ritual where robed figures channel energy into a massive heart-shaped crystal.",
            "You witness the moment when something went wrong - the crystal pulsing erratically, energy lashing out.",
            "The final vision shows a method to stabilize the heart using specific artifacts placed around it."
        ]
        
        vision_text = f"{Fore.MAGENTA}As you focus on the orb, visions flood your mind:\n\n"
        vision_text += random.choice(visions)
        
        # Add knowledge
        self.knowledge.add("heart_ritual")
        self.knowledge.add("crystal_purpose")
        
        return vision_text

    def effect_quest_info(self):
        """Provide information about current quest"""
        if self.current_quest == "find_key":
            return f"{Fore.YELLOW}You learn that exploring the ruins might reveal more about your situation."
        elif self.current_quest == "ruins_exploration":
            return f"{Fore.YELLOW}The tablet reveals that the underground chamber contains an altar connected to the crystal heart."
        elif self.current_quest == "heart_investigation":
            return f"{Fore.YELLOW}You discover that the crystal heart requires specific artifacts to be stabilized: the ceremonial dagger, sacred amulet, and energy flask."
        else:
            return f"{Fore.YELLOW}The ritual to restore the heart requires placing the artifacts around it in a specific pattern, then using the dagger to channel energy."

    def effect_fishing(self):
        """Attempt to catch fish"""
        if self.current_room != "fishing_spot":
            return f"{Fore.YELLOW}This doesn't seem like a good spot for fishing."
        
        # Check for bait
        has_bait = "bait_jar" in self.inventory
        
        if has_bait:
            success_chance = 0.8
        else:
            success_chance = 0.4
        
        if random.random() < success_chance:
            self.health = min(self.maximum_health, self.health + 15)
            self.energy = min(self.maximum_energy, self.energy + 15)
            return f"{Fore.GREEN}You successfully catch a fish and cook it. The meal restores 15 health and 15 energy."
        else:
            return f"{Fore.YELLOW}You spend some time fishing but don't catch anything. Maybe you need better bait."

    def effect_confusion(self):
        """Apply confusion effect"""
        # Simulate getting lost
        directions = ["north", "south", "east", "west"]
        random_direction = random.choice(directions)
        
        # Move in random direction if possible
        room = self.rooms[self.current_room]
        if random_direction in room["connections"]:
            self.current_room = room["connections"][random_direction]
            self.energy -= 5  # Extra energy cost
            return f"{Fore.RED}You become disoriented and wander aimlessly, finding yourself in a different location."
        else:
            self.energy -= 10  # Even more energy cost for being lost
            return f"{Fore.RED}You become disoriented and wander in circles, losing time and energy before finding your way back."

    def effect_reveal_path(self):
        """Reveal a hidden path"""
        room = self.rooms[self.current_room]
        
        # Check if there's a hidden connection
        if "hidden_connections" in room and room["hidden_connections"]:
            direction, destination = random.choice(list(room["hidden_connections"].items()))
            room["connections"][direction] = destination
            del room["hidden_connections"][direction]
            return f"{Fore.GREEN}You discover a hidden path leading {direction}!"
        else:
            return f"{Fore.YELLOW}You sense there are other paths to explore, but not from here."

    def effect_multiple_cuts(self):
        """Effect for taking multiple small cuts"""
        damage = random.randint(5, 10)
        self.health -= damage
        return f"{Fore.RED}You suffer multiple cuts, taking {damage} damage!"

    def effect_stun(self):
        """Stun effect that causes player to miss a turn"""
        # In a turn-based implementation, this would skip the player's next turn
        damage = random.randint(5, 15)
        self.health -= damage
        return f"{Fore.RED}You are stunned and disoriented, taking {damage} damage!"

    def check_quest_progress(self):
        """Check if current quest has been completed"""
        if not self.current_quest:
            return
        
        quest = self.quests[self.current_quest]
        completed = False
        
        # Check completion condition
        if quest["completion_condition"] == "rooms_visited":
            if len(self.discovered_rooms) >= quest["completion_value"]:
                completed = True
        elif quest["completion_condition"] == "visit_room":
            if quest["completion_value"] == self.current_room:
                completed = True
        elif quest["completion_condition"] == "item_acquired":
            if quest["completion_value"] in self.inventory:
                completed = True
        elif quest["completion_condition"] == "special_event":
            if quest["completion_value"] in self.events_triggered:
                completed = True
        
        # Handle quest completion
        if completed and self.current_quest not in self.quests_completed:
            self.quests_completed.add(self.current_quest)
            
            # Apply rewards
            reward_text = f"{Fore.GREEN}Quest completed: {quest['name']}\n"
            
            if "health_boost" in quest["reward"]:
                self.maximum_health += quest["reward"]["health_boost"]
                self.health = self.maximum_health
                reward_text += f"Maximum health increased by {quest['reward']['health_boost']}!\n"
            
            if "energy_boost" in quest["reward"]:
                self.maximum_energy += quest["reward"]["energy_boost"]
                self.energy = self.maximum_energy
                reward_text += f"Maximum energy increased by {quest['reward']['energy_boost']}!\n"
            
            if "item" in quest["reward"]:
                reward_item = quest["reward"]["item"]
                if reward_item not in self.inventory:
                    self.inventory.append(reward_item)
                    reward_text += f"Received: {self.items[reward_item]['name']}\n"
            
            # Update to next quest
            if quest["next_quest"]:
                self.current_quest = quest["next_quest"]
                next_quest = self.quests[self.current_quest]
                reward_text += f"\n{Fore.YELLOW}New quest: {next_quest['name']}\n{next_quest['description']}"
            else:
                # Game completion
                if "game_completion" in quest["reward"] and quest["reward"]["game_completion"]:
                    self.game_over = True
                    reward_text += f"\n{Fore.CYAN}Congratulations! You have completed the final quest and restored balance to the crystal heart!"
                    reward_text += f"\n{Fore.CYAN}The end. Thank you for playing!"
                else:
                    self.current_quest = None
                    reward_text += f"\n{Fore.YELLOW}All quests completed!"
            
            print(reward_text)
            input("Press Enter to continue...")

    def show_help(self):
        """Display available commands"""
        help_text = f"{Fore.CYAN}Available Commands:\n\n"
        help_text += "- go [direction]: Move in a direction (north, south, east, west)\n"
        help_text += "- look: Examine your surroundings\n"
        help_text += "- look at [object]: Examine something specific\n"
        help_text += "- take [item]: Pick up an item\n"
        help_text += "- drop [item]: Drop an item\n"
        help_text += "- inventory (or i): Check what you're carrying\n"
        help_text += "- use [item]: Use an item from your inventory\n"
        help_text += "- examine [item]: Get detailed information about an item\n"
        help_text += "- talk: Interact with someone or something\n"
        help_text += "- stats: Display your health and energy\n"
        help_text += "- map: Show discovered areas (if you have a map)\n"
        help_text += "- quest: Show current quest details\n"
        help_text += "- help: Show this help message\n"
        help_text += "- quit: Exit the game\n\n"
        
        # Combat-specific commands
        help_text += "Combat Commands:\n"
        help_text += "- attack: Attack the enemy\n"
        help_text += "- use [item]: Use an item during combat\n"
        help_text += "- flee: Try to escape from combat\n"
        
        return help_text
        
    def show_stats(self):
        """Display player stats"""
        stats_text = f"{Fore.CYAN}Player Statistics:\n\n"
        stats_text += f"Health: {self.health}/{self.maximum_health}\n"
        stats_text += f"Energy: {self.energy}/{self.maximum_energy}\n"
        stats_text += f"Rooms Discovered: {len(self.discovered_rooms)}/{len(self.rooms)}\n"
        stats_text += f"Quests Completed: {len(self.quests_completed)}/{len(self.quests)}\n"
        
        if self.current_quest:
            stats_text += f"\nCurrent Quest: {self.quests[self.current_quest]['name']}\n"
            stats_text += f"Objective: {self.quests[self.current_quest]['objective']}\n"
        
        return stats_text
    
    def show_map(self):
        """Show map if player has one"""
        if "map" in self.inventory:
            return self.effect_show_map()
        else:
            return f"{Fore.RED}You don't have a map."
    
    def show_quest(self):
        """Show current quest details"""
        if not self.current_quest:
            return f"{Fore.YELLOW}You don't have any active quests right now."
        
        quest = self.quests[self.current_quest]
        quest_text = f"{Fore.MAGENTA}Current Quest: {quest['name']}\n\n"
        quest_text += f"{quest['description']}\n\n"
        quest_text += f"Objective: {quest['objective']}\n"
        
        return quest_text
    
    def process_command(self, command):
        """Process player command"""
        # Convert to lowercase and split into words
        command = command.lower().strip()
        words = command.split()
        
        if not words:
            return "Please enter a command."
        
        # Handle movement shortcuts (just typing the direction)
        if words[0] in ["north", "south", "east", "west", "n", "s", "e", "w"]:
            direction = words[0][0]
            direction_map = {"n": "north", "s": "south", "e": "east", "w": "west"}
            if direction in direction_map:
                direction = direction_map[direction]
            return self.move(direction)
        
        # Handle regular commands
        action = words[0]
        
        # Combat-specific commands
        if self.in_combat:
            if action == "attack":
                return self.combat_attack()
            elif action == "flee":
                return self.combat_flee()
            elif action == "use" and len(words) > 1:
                item_name = " ".join(words[1:])
                return self.combat_use_item(item_name)
        
        # General commands
        if action == "go" and len(words) > 1:
            direction = words[1]
            return self.move(direction)
        elif action == "look" and len(words) == 1:
            return self.get_room_description(detailed=True)
        elif action == "look" and len(words) > 2 and words[1] == "at":
            thing_name = " ".join(words[2:])
            return self.examine(thing_name)
        elif action == "take" and len(words) > 1:
            item_name = " ".join(words[1:])
            return self.take(item_name)
        elif action == "drop" and len(words) > 1:
            item_name = " ".join(words[1:])
            return self.drop(item_name)
        elif action in ["inventory", "i"]:
            return self.show_inventory()
        elif action == "examine" and len(words) > 1:
            item_name = " ".join(words[1:])
            return self.examine(item_name)
        elif action == "use" and len(words) > 1:
            item_name = " ".join(words[1:])
            return self.use_item(item_name)
        elif action == "talk":
            return self.talk()
        elif action == "help":
            return self.show_help()
        elif action == "stats":
            return self.show_stats()
        elif action == "map":
            return self.show_map()
        elif action == "quest":
            return self.show_quest()
        elif action in ["quit", "exit"]:
            self.game_over = True
            return "Thanks for playing!"
        else:
            return f"{Fore.RED}I don't understand that command. Type 'help' for a list of commands."
    
    def main_game_loop(self):
        """Main game loop"""
        # Show introduction
        self.print_header()
        print(f"{Fore.YELLOW}Welcome to Crystal Heart Adventure!\n")
        print(self.wrap_text("You find yourself in a mysterious world with no memory of how you got here. The land seems to pulse with strange energy emanating from what locals call the 'Crystal Heart'."))
        print("\nType 'help' for a list of commands.\n")
        print(self.get_room_description(detailed=True))
        
        # Tutorial tip for new players
        print(f"\n{Fore.CYAN}Tip: {self.tutorial_tips['movement']}")
        
        # Main loop
        while not self.game_over:
            # Get command
            command = input(f"\n{Fore.WHITE}> ")
            
            # Process command
            result = self.process_command(command)
            
            # Print result
            self.print_header()
            print(self.wrap_text(result))
            
            # Energy depletion check
            if self.energy <= 0 and not self.game_over:
                print(f"\n{Fore.RED}You are exhausted and need to rest. Your vision blurs...")
                self.health = max(1, self.health - 5)  # Lose health when out of energy
                self.energy = 10  # Recover a small amount
                time.sleep(2)  # Dramatic pause
            
            # Health check
            if self.health <= 0 and not self.game_over:
                print(f"\n{Fore.RED}You collapse from your injuries. Everything goes dark...")
                print(f"\n{Fore.YELLOW}You wake up later, barely alive. Someone or something must have helped you.")
                self.health = 10
                self.energy = 10
                time.sleep(2)  # Dramatic pause

# Run the game if script is executed directly
if __name__ == "__main__":
    game = EnhancedTextAdventure()
    game.main_game_loop()