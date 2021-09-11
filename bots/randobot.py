import re
from grammar import *

BACKUS_NAUR = """
<bot-script> ::= <defrule> | <bot-script> "\n" <defrule>
<defrule> ::= "(defrule\n" <conditions> "\n=>\n" <actions> "\n)"

<conditions> ::= "\t(" <condition> ")" | <conditions> "\n\t(" <condition> ")"
<actions> ::= "\t(" <action> ")" | <actions> "\n\t(" <action> ")"

<condition> ::= <binary-op> " (" <condition> ") (" <condition> ")"
                | <unary-op> " (" <condition> ")"
                | "true"
                | "false"
                | <number-comparable-fact> " " <rel-op> " " <number>
                | "current-age " <rel-op> " " <age>
                | "difficulty " <rel-op> " " <difficulty>
                | "civ-selected " <civ>
                | "building-available " <building>
                | "research-available " <research-item>
                | "unit-available " <unit>
                | "can-afford-building " <building>
                | "can-afford-complete-wall " <perimeter> " " <wall-type>
                | "can-afford-research " <research-item>
                | "can-build " <building>
                | "can-build-wall " <perimeter> " " <wall-type>
                | "can-build-gate " <perimeter>
                | "can-train " <unit>
                | "can-research " <research-item>
                | "death-match-game"
                | "enemy-buildings-in-town"
                | "enemy-captured-relics"
                | "player-" ("computer" | "human" | "in-game" | "number" | "resigned" | "valid") " " <player-number>
                | "players-civ " <player-number> " " <civ>
                | "players-current-age " <player-number> " " <rel-op> " " <age>
                | "regicide-game"
                | "resource-found " <resource-type>
                | "sheep-and-forage-too-far"
                | "starting-age " <rel-op> " " <age>
                | "town-under-attack"

<number-comparable-fact> ::= "current-age"
                      | ("defend" | "attack") "-" ("soldier" | "warboat") "-count"
                      | ("military" | "civilian") "-population"
                      | "building-count" ("-total" | "")
                      | "building-type-count" ("-total" | "") " " <building>
                      | "unit-count" ("-total" | "")
                      | "unit-type-count" ("-total" | "") " " <unit>
                      | "commodity-" ("buying" | "selling") "-price " <commodity>
                      | "current-age-time"
                      | "current-score"
                      | "dropsite-min-distance " <resource-type>
                      | <resource-type> "-amount"
                      | "game-time"
                      | "housing-headroom"
                      | "idle-farm-count"
                      | "players-building-count " <player-number>
                      | "players-building-type-count " <player-number> " " <building>
                      | "players-civilian-population " <player-number>
                      | "players-current-age-time " <player-number>
                      | "players-military-population " <player-number>
                      | "players-population " <player-number>
                      | "players-score " <player-number>
                      | "players-tribute " <player-number> " " <resource-type>
                      | "players-tribute-memory " <player-number> " " <resource-type>
                      | "players-unit-count " <player-number>
                      | "players-unit-type-count " <player-number> " " <unit>
                      | "players-current-age-time " <player-number>
                      | "players-current-age-time " <player-number>
                      | "population"
                      | "population-cap"
                      | "population-headroom"
                      | "random-number"
                      | "soldier-count"
                      | "wall-completed-percentage " <perimeter>
                      | "wall-invisible-percentage " <perimeter>

<action> ::= "build" ("-forward" | "") " " <building>
             | "train " <unit>
             | "research " <research-item>
             | "do-nothing"
             | "attack-now"
             | ("sell" | "buy") "-commodity " <commodity>
             | "chat-to-" ("all" | "allies" | "enemies") ' "' <chat-message> '"'
             | "disable-self"

<building> ::= "archery-range" | "barracks" | "blacksmith" | "bombard-tower" | "castle" | "dock" | "farm" | "fish-trap" | "guard-tower" | "house" | "keep" | "lumber-camp" | "market" | "mill" | "mining-camp" | "monastery" | "outpost" | "siege-workshop" | "stable" | "town-center" | "university" | "watch-tower" | "wonder" | "watch-tower-line"
<unit> ::= "archer-line" | "cavalry-archer-line" | "skirmisher-line" | "eagle-warrior-line" | "militiaman-line" | "spearman-line" | "berserk-line" | "cataphract-line" | "chu-ko-nu-line" | "conquistador-line" | "huskarl-line" | "jaguar-man-line" | "janissary-line" | "longbowman-line" | "mameluke-line" | "mangudai-line" | "plumed-archer-line" | "samurai-line" | "tarkan-line" | "teutonic-knight-line" | "throwing-axeman-line" | "war-elephant-line" | "war-wagon-line" | "woad-raider-line" | "cannon-galleon-line" | "demolition-ship-line" | "fire-ship-line" | "galley-line" | "longboat-line" | "turtle-ship-line" | "battering-ram-line" | "mangonel-line" | "scorpion-line" | "camel-line" | "knight-line" | "scout-cavalry-line" | "arbalest" | "archer" | "cavalry-archer" | "crossbowman" | "elite-skirmisher" | "hand-cannoneer" | "heavy-cavalry-archer" | "skirmisher" | "champion" | "eagle-warrior" | "elite-eagle-warrior" | "halberdier" | "long-swordsman" | "man-at-arms" | "militiaman" | "pikeman" | "spearman" | "two-handed-swordsman" | "berserk" | "cataphract" | "chu-ko-nu" | "conquistador" | "elite-berserk" | "elite-cataphract" | "elite-chu-ko-nu" | "elite-conquistador" | "elite-huskarl" | "elite-jaguar-man" | "elite-janissary" | "elite-longbowman" | "elite-mameluke" | "elite-mangudai" | "elite-plumed-archer" | "elite-samurai" | "elite-tarkan" | "elite-teutonic-knight" | "elite-throwing-axeman" | "elite-war-elephant" | "elite-war-wagon" | "elite-woad-raider" | "huskarl" | "jaguar-man" | "janissary" | "longbowman" | "mameluke" | "mangudai" | "petard" | "plumed-archer" | "samurai" | "tarkan" | "teutonic-knight" | "throwing-axeman" | "trebuchet" | "war-elephant" | "war-wagon" | "woad-raider" | "cannon-galleon" | "demolition-ship" | "elite-cannon-galleon" | "elite-longboat" | "elite-turtle-ship" | "fast-fire-ship" | "fire-ship" | "fishing-ship" | "galleon" | "galley" | "heavy-demolition-ship" | "longboat" | "trade-cog" | "transport-ship" | "turtle-ship" | "war-galley" | "trade-cart" | "missionary" | "monk" | "battering-ram" | "bombard-cannon" | "capped-ram" | "heavy-scorpion" | "mangonel" | "onager" | "scorpion" | "siege-onager" | "siege-ram" | "camel" | "cavalier" | "heavy-camel" | "hussar" | "knight" | "light-cavalry" | "paladin" | "scout-cavalry" | "villager"
<research-item> ::= "feudal-age" | "castle-age" | "imperial-age" | "ri-arbalest" | "ri-crossbow" | "ri-elite-skirmisher" | "ri-hand-cannon" | "ri-heavy-cavalry-archer" | "ri-champion" | "ri-elite-eagle-warrior" | "ri-halberdier" | "ri-long-swordsman" | "ri-man-at-arms" | "ri-parthian-tactics" | "ri-pikeman" | "ri-squires" | "ri-thumb-ring" | "ri-tracking" | "ri-two-handed-swordsman" | "ri-blast-furnace" | "ri-bodkin-arrow" | "ri-bracer" | "ri-chain-barding" | "ri-chain-mail" | "ri-fletching" | "ri-forging" | "ri-iron-casting" | "ri-leather-archer-armor" | "ri-padded-archer-armor" | "ri-plate-barding" | "ri-plate-mail" | "ri-ring-archer-armor" | "ri-scale-barding" | "ri-scale-mail" | "ri-conscription" | "ri-hoardings" | "ri-sappers" | "ri-elite-berserk" | "ri-elite-cataphract" | "ri-elite-chu-ko-nu" | "ri-elite-huskarl" | "ri-elite-janissary" | "ri-elite-longbowman" | "ri-elite-mameluke" | "ri-elite-mangudai" | "ri-elite-samurai" | "ri-elite-teutonic-knight" | "ri-elite-throwing-axeman" | "ri-elite-war-elephant" | "ri-elite-woad-raider" | "my-unique-research" | "ri-cannon-galleon" | "ri-careening" | "ri-deck-guns" | "ri-dry-dock" | "ri-elite-longboat" | "ri-fast-fire-ship" | "ri-galleon" | "ri-heavy-demolition-ship" | "ri-shipwright" | "ri-war-galley" | "ri-bow-saw" | "ri-double-bit-axe" | "ri-two-man-saw" | "ri-banking" | "ri-caravan" | "ri-cartography" | "ri-coinage" | "ri-guilds" | "ri-crop-rotation" | "ri-heavy-plow" | "ri-horse-collar" | "ri-gold-mining" | "ri-gold-shaft-mining" | "ri-stone-mining" | "ri-stone-shaft-mining" | "ri-atonement" | "ri-block-printing" | "ri-faith" | "ri-fervor" | "ri-heresy" | "ri-illumination" | "ri-redemption" | "ri-sanctity" | "ri-theocracy" | "ri-bombard-cannon" | "ri-capped-ram" | "ri-heavy-scorpion" | "ri-onager" | "ri-scorpion" | "ri-siege-onager" | "ri-siege-ram" | "ri-bloodlines" | "ri-cavalier" | "ri-heavy-camel" | "ri-husbandry" | "ri-hussar" | "ri-light-cavalry" | "ri-paladin" | "ri-hand-cart" | "ri-loom" | "ri-town-patrol" | "ri-town-watch" | "ri-wheel-barrow" | "ri-architecture" | "ri-ballistics" | "ri-bombard-tower" | "ri-chemistry" | "ri-fortified-wall" | "ri-guard-tower" | "ri-heated-shot" | "ri-keep" | "ri-masonry" | "ri-murder-holes" | "ri-siege-engineers" | "ri-stonecutting"

<perimeter> ::= "1" | "2"
<wall-type> ::= "stone-wall-line" | "palisade-wall"

<difficulty> ::= "easiest" | "standard" | "moderate" | "hard" | "hardest"
<resource-type> ::= <commodity>
<commodity> ::= "wood" | "food" | "gold" | "stone"
<player-number> ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8"
<age> ::= "dark-age" | "feudal-age" | "castle-age" | "imperial-age"
<civ> ::= "aztec" | "berbers" | "briton" | "burmese" | "byzantine" | "celtic" | "chinese" | "ethiopian" | "frankish" | "gothic" | "hun" | "incan" | "indian" | "italian" | "japanese" | "khmer" | "korean" | "magyar" | "malay" | "malian" | "mayan" | "mongol" | "persian" | "portuguese" | "saracen" | "slavic" | "spanish" | "teutonic" | "turkish" | "vietnamese" | "viking"

<binary-op> ::= "and" | "or" | "nand" | "nor"
<unary-op> ::= "not"
<rel-op> ::= "==" | "!=" | ">" | "<" | ">=" | "<="

<number> ::= <digit> | <non_zero_digit> <number>
<digit> ::= "0" | <non_zero_digit>
<non_zero_digit> ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<chat-message> ::= <word> | <chat-message> " " <word>
<word> ::= <letter> | <word> <letter>
<letter> ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
"""

SKELETON = """(defrule
    (true)
=>
    (set-strategic-number sn-enable-new-building-system 1)
    (set-strategic-number sn-percent-building-cancellation 20)
    (set-strategic-number sn-cap-civilian-builders 200)
    (set-strategic-number sn-percent-civilian-explorers 0)
    (set-strategic-number sn-cap-civilian-explorers 0)
    (set-strategic-number sn-total-number-explorers 1)
    (set-strategic-number sn-number-explore-groups 1)
    (set-strategic-number sn-initial-exploration-required 0)
    (set-difficulty-parameter ability-to-maintain-distance 0)
    (set-difficulty-parameter ability-to-dodge-missiles 0)
    (set-strategic-number sn-percent-attack-soldiers 100)
    (set-strategic-number sn-percent-attack-boats 100)
    (set-strategic-number sn-attack-intelligence 1)
    (set-strategic-number sn-livestock-to-town-center 1)
    (set-strategic-number sn-enable-patrol-attack 1)
    (set-strategic-number sn-intelligent-gathering 1)
    (set-strategic-number sn-local-targeting-mode 1)
    (set-strategic-number sn-retask-gather-amount 0)
    (set-strategic-number sn-target-evaluation-siege-weapon 500)
    (set-strategic-number sn-ttkfactor-scalar 500)
    (set-strategic-number sn-percent-enemy-sighted-response 100)
    (set-strategic-number sn-task-ungrouped-soldiers 0)
    (set-strategic-number sn-gather-defense-units 1)
    (set-strategic-number sn-defer-dropsite-update 1)
    (set-strategic-number sn-do-not-scale-for-difficulty-level 1)
    (set-strategic-number sn-number-build-attempts-before-skip 5)
    (set-strategic-number sn-max-skips-per-attempt 5)
)
(defrule
    (unit-type-count-total villager <= 20)
=>
    (set-strategic-number sn-wood-gatherer-percentage 20)
    (set-strategic-number sn-food-gatherer-percentage 80)
    (set-strategic-number sn-gold-gatherer-percentage 0)
    (set-strategic-number sn-stone-gatherer-percentage 0)
    (disable-self)
)
(defrule
    (not (unit-type-count-total villager <= 20))
=>
    (set-strategic-number sn-wood-gatherer-percentage 37)
    (set-strategic-number sn-food-gatherer-percentage 37)
    (set-strategic-number sn-gold-gatherer-percentage 18)
    (set-strategic-number sn-stone-gatherer-percentage 8)
    (disable-self)
)
(defrule
    (population-headroom != 0)
    (up-pending-objects c: house == 0)
    (can-build house)
    (housing-headroom < 10)
=>
    (build house)
)
(defrule
    (dropsite-min-distance wood > 2)
    (dropsite-min-distance wood != -1)
    (resource-found wood)
    (up-pending-objects c: lumber-camp == 0)
    (can-build lumber-camp)
=>
    (build lumber-camp)
)
(defrule
    (or (dropsite-min-distance gold > 3) (and (unit-type-count 579 == 0) (and (unit-type-count 581 == 0) (strategic-number sn-gold-gatherer-percentage > 0))))
    (dropsite-min-distance gold != -1)
    (resource-found gold)
    (up-pending-objects c: mining-camp == 0)
    (can-build mining-camp)
    (current-age >= feudal-age)
=>
    (build mining-camp)
)
(defrule
    (dropsite-min-distance stone > 3)
    (dropsite-min-distance stone != -1)
    (resource-found stone)
    (up-pending-objects c: mining-camp == 0)
    (can-build mining-camp)
    (current-age >= feudal-age)
=>
    (build mining-camp)
)
(defrule
    (can-build mill)
    (building-type-count-total lumber-camp >= 1)
    (building-type-count-total mill == 0)
    (game-time >= 360)
=>
    (build mill)
)

(defrule
    (true)
=>
    (up-get-fact resource-amount wood 1)
    (up-get-fact escrow-amount wood 2)
    (up-modify-goal 1 g:- 2)
    (up-get-fact resource-amount food 3)
    (up-get-fact escrow-amount food 4)
    (up-modify-goal 3 g:- 4)
    (up-get-fact resource-amount gold 5)
    (up-get-fact escrow-amount gold 6)
    (up-modify-goal 5 g:- 6)
)
(defrule
    (true)
=>
    (enable-timer 1 60)
    (disable-self)
)
(defrule
    (strategic-number sn-wood-gatherer-percentage >= 2)
    (up-compare-goal 1 c:> 300)
    (strategic-number sn-food-gatherer-percentage >= 2)
    (up-compare-goal 3 c:> 300)
    (strategic-number sn-gold-gatherer-percentage <= 96)
    (up-compare-goal 5 c:<= 300)
    (timer-triggered 1)
=>
    (up-modify-sn sn-wood-gatherer-percentage c:- 2)
    (up-modify-sn sn-food-gatherer-percentage c:- 2)
    (up-modify-sn sn-gold-gatherer-percentage c:+ 4)
)
(defrule
    (strategic-number sn-wood-gatherer-percentage >= 2)
    (up-compare-goal 1 c:> 300)
    (strategic-number sn-gold-gatherer-percentage >= 2)
    (up-compare-goal 5 c:> 300)
    (strategic-number sn-food-gatherer-percentage <= 96)
    (up-compare-goal 3 c:<= 300)
    (timer-triggered 1)
=>
    (up-modify-sn sn-wood-gatherer-percentage c:- 2)
    (up-modify-sn sn-gold-gatherer-percentage c:- 2)
    (up-modify-sn sn-food-gatherer-percentage c:+ 4)
)
(defrule
    (strategic-number sn-wood-gatherer-percentage >= 4)
    (up-compare-goal 1 c:> 300)
    (strategic-number sn-food-gatherer-percentage <= 98)
    (up-compare-goal 3 c:<= 300)
    (strategic-number sn-gold-gatherer-percentage <= 98)
    (up-compare-goal 5 c:<= 300)
    (timer-triggered 1)
=>
    (up-modify-sn sn-wood-gatherer-percentage c:- 4)
    (up-modify-sn sn-food-gatherer-percentage c:+ 2)
    (up-modify-sn sn-gold-gatherer-percentage c:+ 2)
)
(defrule
    (strategic-number sn-food-gatherer-percentage >= 2)
    (up-compare-goal 3 c:> 300)
    (strategic-number sn-gold-gatherer-percentage >= 2)
    (up-compare-goal 5 c:> 300)
    (strategic-number sn-wood-gatherer-percentage <= 96)
    (up-compare-goal 1 c:<= 300)
    (timer-triggered 1)
=>
    (up-modify-sn sn-food-gatherer-percentage c:- 2)
    (up-modify-sn sn-gold-gatherer-percentage c:- 2)
    (up-modify-sn sn-wood-gatherer-percentage c:+ 4)
)
(defrule
    (strategic-number sn-food-gatherer-percentage >= 4)
    (up-compare-goal 3 c:> 300)
    (strategic-number sn-wood-gatherer-percentage <= 98)
    (up-compare-goal 1 c:<= 300)
    (strategic-number sn-gold-gatherer-percentage <= 98)
    (up-compare-goal 5 c:<= 300)
    (timer-triggered 1)
=>
    (up-modify-sn sn-food-gatherer-percentage c:- 4)
    (up-modify-sn sn-wood-gatherer-percentage c:+ 2)
    (up-modify-sn sn-gold-gatherer-percentage c:+ 2)
)
(defrule
    (strategic-number sn-gold-gatherer-percentage >= 4)
    (up-compare-goal 5 c:> 300)
    (strategic-number sn-wood-gatherer-percentage <= 98)
    (up-compare-goal 1 c:<= 300)
    (strategic-number sn-food-gatherer-percentage <= 98)
    (up-compare-goal 3 c:<= 300)
    (timer-triggered 1)
=>
    (up-modify-sn sn-gold-gatherer-percentage c:- 4)
    (up-modify-sn sn-wood-gatherer-percentage c:+ 2)
    (up-modify-sn sn-food-gatherer-percentage c:+ 2)
)
(defrule
    (timer-triggered 1)
=>
    (disable-timer 1)
    (enable-timer 1 60)
)

(defrule
    (true)
=>
    (up-get-fact unit-type-count villager 7)
    (up-modify-goal 7 s:* sn-food-gatherer-percentage)
    (up-modify-goal 7 c:/ 100)
    (up-get-fact building-type-count-total farm 8)
)
(defrule
    (up-compare-goal 8 g:< 7)
    (can-build farm)
=>
    (build farm)
)
(defrule
    (true)
=>
    (set-escrow-percentage food 10)
    (disable-self)
    (set-escrow-percentage gold 10)
)
(defrule
    (current-age >= imperial-age)
=>
    (set-escrow-percentage food 0)
    (disable-self)
    (set-escrow-percentage gold 0)
)
(defrule
    (can-research-with-escrow feudal-age)
=>
    (release-escrow food)
    (research feudal-age)
)
(defrule
    (can-research-with-escrow castle-age)
=>
    (release-escrow food)
    (release-escrow gold)
    (research castle-age)
)
(defrule
    (can-research-with-escrow imperial-age)
=>
    (release-escrow food)
    (release-escrow gold)
    (research imperial-age)
)
(defrule
    (can-build blacksmith)
    (building-type-count-total blacksmith < 1)
=>
    (build blacksmith)
)
(defrule
    (can-build monastery)
    (building-type-count-total monastery < 1)
=>
    (build monastery)
)
(defrule
    (can-build siege-workshop)
    (building-type-count-total siege-workshop < 1)
=>
    (build siege-workshop)
)
(defrule
    (can-build university)
    (building-type-count-total university < 1)
=>
    (build university)
)
(defrule
    (can-build barracks)
    (building-type-count-total barracks < 1)
    (current-age >= feudal-age)
=>
    (build barracks)
)
(defrule
    (can-build stable)
    (building-type-count-total stable < 1)
=>
    (build stable)
)
(defrule
    (can-build archery-range)
    (building-type-count-total archery-range < 1)
=>
    (build archery-range)
)
{}
(defrule
    (can-train villager)
    (unit-type-count-total villager < 120)
=>
    (train villager)
)
"""

MAX_RULES = 2224
RULE_HEADROOM = sum("(defrule" in line for line in SKELETON.split("\n"))
BUILDING_LIMIT = 5

def create_bot():
    grammar = Grammar(BACKUS_NAUR)
    return "\n".join([grammar.random_chain(grammar.keys["defrule"].results) for x in range(MAX_RULES - RULE_HEADROOM)])

def ensure(bot):
    insertions = []
    lines = bot.split("\n")
    for i, line in enumerate(lines):
        match = re.match(r"^\s*\((build|train|research)\s*([a-z\-]+)\)\s*$", line)
        if match:
            action = match.group(1)
            operand = match.group(2)
            for j in range(i - 1, 0, -1):
                if "=>" in lines[j]:
                    insertions.append((j, f"  (can-{action} {operand})"))
                    if action == "build":
                        insertions.append((j, f"  (building-type-count-total {operand} < {BUILDING_LIMIT})"))
                    break

    for insertion in insertions[::-1]:
        lines.insert(*insertion)

    return "\n".join(lines)

file = open(r"E:\games\SteamLibrary\steamapps\common\Age2HD\resources\_common\ai\randobot.per", "w")
file.write(SKELETON.format(ensure(create_bot())))
file.close()
