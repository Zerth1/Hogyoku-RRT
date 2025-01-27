from enum import Enum, auto
from typing import *
from pyray import *
import os
import json
import math
import random
import string
import user_interface
RESOLUTION_X = 1450
RESOLUTION_Y = 800
RANKINGS = {
    "Mortal Mind": {
        "Points": 0,
    }, 
    "Rising Star": {
        "Points": 250,
    }, 
    "Mental Magician": {
        "Points": 750,
    }, 
    "Awakened Esper": {
        "Points": 1500,
    }, 
    "Divine Analyst": {
        "Points": 4000,
    }, 
    "Cerebral Sovereign": {
        "Points": 8000,
    }, 
    "Galactic Prodigy": {
        "Points": 12500,
    }, 
    "Ethereal Thinker": {
        "Points": 20000,
    },
    "Synesthetic Spatializer": {
        "Points": 30000,
    },  
    "IQ Grandmaster": {
        "Points": 40000,
    },
}
ORDERED_RANKINGS = ["Mortal Mind", "Rising Star", "Mental Magician", "Awakened Esper", "Divine Analyst", "Cerebral Sovereign", "Galactic Prodigy", "Ethereal Thinker", "Synesthetic Spatializer", "IQ Grandmaster"]
SETTINGS = {
    "Rank": "Mortal Mind",
    "Points": 0,
    "Settings": {
        "2D Spatial": {
            "Active": True,
            "Premises": 4,
        },
        "Chain Logic": {
            "Active": False,
            "ChainCount": 2,
            "NestedChainCount": 1,
            "ChainLengthMin": 2,
            "ChainLengthMax": 2,
        },
        "GarbageWordLength": 3,
    },
}
premise_page = 1
premises_per_page = 8
init_window(RESOLUTION_X, RESOLUTION_Y, "The Logic Forge")
set_target_fps(get_monitor_refresh_rate(get_current_monitor()))

premise_font = load_font("Fira_Sans/FiraSans-SemiBold.ttf")
set_texture_filter(premise_font.texture, TextureFilter.TEXTURE_FILTER_BILINEAR)
if os.path.getsize("settings_data.json") == 0:
    with open("settings_data.json", "w") as settings_file:
        settings_file.write(json.dumps(SETTINGS, indent=4))
with open("settings_data.json", "r") as file:
    settings_data = json.load(file)
deep_settings = False
is_settings = False
viewing_key = False

door_right = load_image("door_right.png")
door_left = load_image("door_left.png")
door_right_texture = load_texture_from_image(door_right)
door_left_texture = load_texture_from_image(door_left)
unload_image(door_right)
unload_image(door_left)
in_transition = False
delta_time = 0.0
def transition_room():
    global in_transition
    global delta_time
    delta_time += get_frame_time()
    if delta_time > 0.5:
        in_transition = False
        delta_time = 0.0
    else:
        draw_texture(door_left_texture, int(0 - ((RESOLUTION_X / 2) * min((delta_time * 2), 1.0))), 0, GRAY)
        draw_texture(door_right_texture, int((RESOLUTION_X / 2) + ((RESOLUTION_X / 2) * min((delta_time * 2), 1.0))), 0, GRAY)
settings_buttons = {}
settings_buttons["two_d_premises"] = user_interface.InputButton("2D Premises:", 25, Rectangle(50 + measure_text("2D Premises:", 25) + 10, 125, measure_text("00", 25), 25))
settings_buttons["two_d_active"] = user_interface.Button("2D Premises Active:", 25, Rectangle(50 + measure_text("2D Premises Active:", 25) + 10, 75, 25, 25))
settings_buttons["two_d_active"]._on = settings_data["Settings"]["2D Spatial"]["Active"]
settings_buttons["two_d_premises"].text = str(settings_data["Settings"]["2D Spatial"]["Premises"])

settings_buttons["chain_premises_active"] = user_interface.Button("Chain Premises Active:", 25, Rectangle(50 + measure_text("Chain Premises Active:", 25) + 10, 75, 25, 25))
settings_buttons["chain_count"] = user_interface.InputButton("Chains:", 25, Rectangle(50 + measure_text("Chains:", 25) + 10, 125, measure_text("00", 25), 25))
settings_buttons["nested_chain_count"] = user_interface.InputButton("Nested Chains:", 25, Rectangle(50 + measure_text("Nested Chains:", 25) + 10, 175, measure_text("00", 25), 25))
settings_buttons["chain_length_min"] = user_interface.InputButton("Chain Length Min:", 25, Rectangle(50 + measure_text("Chain Length Min:", 25) + 10, 225, measure_text("00", 25), 25))
settings_buttons["chain_length_max"] = user_interface.InputButton("Chain Length Max:", 25, Rectangle(50 + measure_text("Chain Length Max:", 25) + 10, 275, measure_text("00", 25), 25))
settings_buttons["chain_premises_active"]._on = settings_data["Settings"]["Chain Logic"]["Active"]
settings_buttons["chain_count"].text = str(settings_data["Settings"]["Chain Logic"]["ChainCount"])
settings_buttons["nested_chain_count"].text = str(settings_data["Settings"]["Chain Logic"]["NestedChainCount"])
settings_buttons["chain_length_min"].text = str(settings_data["Settings"]["Chain Logic"]["ChainLengthMin"])
settings_buttons["chain_length_max"].text = str(settings_data["Settings"]["Chain Logic"]["ChainLengthMax"])

settings_buttons["garbage_length"] = user_interface.InputButton("Garbage Word Length:", 25, Rectangle(50 + measure_text("Garbage Word Length:", 25) + 10, 180, measure_text("0", 25), 25))
settings_buttons["garbage_length"].text = str(settings_data["Settings"]["GarbageWordLength"])
blacklist_toggle = []
def redirect_settings():
    global deep_settings
    draw_text("Spatial Mode", 50, 80, 25, WHITE)
    draw_text("Chain Logic Mode", 50, 130, 25, WHITE)
    if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
        current_position = get_mouse_position()
        if check_collision_point_rec(current_position, Rectangle(50, 80, measure_text("Spatial Mode", 25), 25)):
            deep_settings = True
            settings_buttons["two_d_premises"].toggle()
            settings_buttons["two_d_active"].toggle()
        elif check_collision_point_rec(current_position, Rectangle(50, 130, measure_text("Chain Logic Mode", 25), 25)):
            deep_settings = True
            settings_buttons["chain_premises_active"].toggle()
            settings_buttons["chain_count"].toggle()
            settings_buttons["nested_chain_count"].toggle()
            settings_buttons["chain_length_min"].toggle()   
            settings_buttons["chain_length_max"].toggle()
background = load_image("koji_room.png")
settings_background = load_image("koji_room_2.png")
deep_settings_background = load_image("koji_room_3.png")
question_mat = load_image("koji_brain.jpeg")
question_mat_texture = load_texture_from_image(question_mat)
background_texture = load_texture_from_image(background)
settings_background_texture = load_texture_from_image(settings_background)
deep_settings_background_texture = load_texture_from_image(deep_settings_background)
unload_image(question_mat)
unload_image(background)
unload_image(settings_background)
unload_image(deep_settings_background)

is_generating = True
directions = ["North", "South", "East", "West", "North-East", "North-West", "South-East", "South-West"]
problem_spatial_code = {}
premises = []
chained_premises = []
conclusion = ""
answer = False
def generate_gibberish_word(word_length: int):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(word_length))
def generate_gibberish_words(object_count: int, word_length: int, black_list: List[str]):
    words_set = set()
    while len(words_set) < object_count:
        new_word = generate_gibberish_word(word_length)
        if new_word in black_list:
            continue
        words_set.add(new_word)
    return words_set
def get_direction(x_distance: int, y_distance: int):
    direction = ""
    y_flag = False
    if y_distance == 1:
        direction += "North"
        y_flag = True
    elif y_distance == -1:
        direction += "South"
        y_flag = True
    if x_distance == 1:
        if y_flag:
            direction += "-"
        direction += "East"
    elif x_distance == -1:
        if y_flag:
            direction += "-"
        direction += "West"
    return direction
def get_smallest_chain(chains: List[List[str]], chosen_one: str):
    smallest_weight = math.pow(10, 4)
    chain_index = -1
    for i, chain in enumerate(chains):
        old_weight = smallest_weight
        smallest_weight = min(smallest_weight, chain.index(chosen_one))
        if old_weight != smallest_weight:
            chain_index = i
    return chain_index
def get_largest_chain(chains: List[List[str]], chosen_one: str):
    largest_weight = 0
    chain_index = -1
    for i, chain in enumerate(chains):
        old_weight = largest_weight
        largest_weight = max(largest_weight, chain.index(chosen_one))
        if old_weight != largest_weight:
            chain_index = i
    return chain_index
chosen_gamemode = ""
while not window_should_close():
    begin_drawing()
    clear_background(BLACK)
    if is_generating:
        gamemode_options = []
        if settings_data["Settings"]["2D Spatial"]["Active"]:
            gamemode_options.append("2D Spatial")
        if settings_data["Settings"]["Chain Logic"]["Active"]:
            gamemode_options.append("Chain Logic")
        chosen_gamemode = random.choice(gamemode_options)
        is_generating = False
        if chosen_gamemode == "2D Spatial":
            letter_filter = list(string.ascii_uppercase)
            for i in range(len(directions)):
                a_1 = random.choice(letter_filter)
                letter_filter.remove(a_1)
                a_2 = random.choice(letter_filter)
                letter_filter.remove(a_2)
                problem_spatial_code[directions[i]] = a_1 + a_2
            grid_size = settings_data["Settings"]["2D Spatial"]["Premises"]
            object_amount = grid_size + 1
            objects = list(generate_gibberish_words(object_amount, settings_data["Settings"]["GarbageWordLength"], []))
            objects_location_x = [0]
            objects_location_y = [0]
            for i in range(object_amount - 1):
                random_direction_options = [-1, 0, 1]
                objects_location_x.append(objects_location_x[-1] + random.choice(random_direction_options))
                if objects_location_x[-1] - objects_location_x[-2] == 0:
                    random_direction_options.remove(0)
                if i == object_amount - 2:
                    if objects_location_y[-1] == 0 and 0 in random_direction_options:
                        random_direction_options.remove(0)
                    elif abs(objects_location_y[-1]) == 1:
                        random_direction_options.remove(-objects_location_y[-1])
                objects_location_y.append(objects_location_y[-1] + random.choice(random_direction_options))
            considered_relations = set()
            for i in range(object_amount - 1):
                x_distance = objects_location_x[i + 1] - objects_location_x[i]
                y_distance = objects_location_y[i + 1] - objects_location_y[i]
                direction = get_direction(x_distance, y_distance)
                considered_relations.add(direction)
                premises.append(objects[i] + " is " + problem_spatial_code[direction] + " of " + objects[i + 1])
            random.shuffle(premises)
            conclusion_obj_1 = objects[0]
            conclusion_obj_2 = objects[-1]
            total_x_distance = math.copysign(1, objects_location_x[-1])
            if objects_location_x[-1] == 0:
                total_x_distance = 0
            total_y_distance = math.copysign(1, objects_location_y[-1])
            if objects_location_y[-1] == 0:
                total_y_distance = 0
            conclusion_relation = ""
            if random.random() > 0.5:
                answer = True
                conclusion_relation = get_direction(total_x_distance, total_y_distance)
            else:
                answer = False
                conclusion_relation = get_direction(-total_x_distance, -total_y_distance)
            considered_relations.add(conclusion_relation)
            for i, relation in enumerate(set(directions) - considered_relations):
                problem_spatial_code.pop(relation)
            conclusion = conclusion_obj_1 + " is " + problem_spatial_code[conclusion_relation] + " of " + conclusion_obj_2
        elif chosen_gamemode == "Chain Logic":
            chain_logic_settings = settings_data["Settings"]["Chain Logic"]
            objects = []
            object_amount = random.randint(chain_logic_settings["ChainLengthMin"], chain_logic_settings["ChainLengthMax"]) * chain_logic_settings["ChainCount"]
            gibberish_words = list(generate_gibberish_words(object_amount, settings_data["Settings"]["GarbageWordLength"], []))
            chosen_object = random.choice(gibberish_words)
            gibberish_words.remove(chosen_object)
            for i in range(chain_logic_settings["ChainCount"]):
                objects.append([])
            current_j = 0
            for i in range(chain_logic_settings["ChainCount"]):
                for j in range(int(object_amount / chain_logic_settings["ChainCount"]) - 1):
                    objects[i].append(gibberish_words[current_j])
                    current_j += 1
            for obj in objects:
                random.shuffle(obj)
            for i in range(chain_logic_settings["ChainCount"]):
                objects[i].insert(random.randint(1, int(object_amount / chain_logic_settings["ChainCount"]) - 1), chosen_object)
            for i in range(chain_logic_settings["ChainCount"]):
                for j in range(int(object_amount / chain_logic_settings["ChainCount"]) - 1):
                    if random.random() > 0.5:
                        chained_premises.append(objects[i][j] + " is less than " + objects[i][j + 1])
                    else:
                        chained_premises.append(objects[i][j + 1] + " is more than " + objects[i][j])
            total_black_list = gibberish_words.copy()
            old_chosen_object = chosen_object
            previous_chain_index = get_largest_chain(objects, chosen_object)
            previous_chain = objects[previous_chain_index]
            objects.remove(previous_chain)
            total_black_list.append(old_chosen_object)
            for i in range(chain_logic_settings["NestedChainCount"]):
                chosen_object = random.choice(previous_chain[previous_chain.index(chosen_object):])
                nested_gibberish_words = list(generate_gibberish_words((object_amount / chain_logic_settings["ChainCount"]) - 1, settings_data["Settings"]["GarbageWordLength"], total_black_list))
                nested_gibberish_words.append(chosen_object)
                while nested_gibberish_words.index(chosen_object) == 0 or nested_gibberish_words.index(chosen_object) == len(nested_gibberish_words) - 1:
                    random.shuffle(nested_gibberish_words)
                previous_chain = nested_gibberish_words
                total_black_list += nested_gibberish_words.copy()
                for j in range(len(nested_gibberish_words) - 1):
                    if random.random() > 0.5:
                        chained_premises.append(nested_gibberish_words[j] + " is less than " + nested_gibberish_words[j + 1])
                    else:
                        chained_premises.append(nested_gibberish_words[j + 1] + " is more than " + nested_gibberish_words[j])                 
            random.shuffle(chained_premises)
            object_a = random.choice(objects)[0]
            object_b = previous_chain[-1]
            if random.random() > 0.5:
                answer = False
                object_a, object_b = object_b, object_a
            else:
                answer = True
            conclusion = object_a + " is less than " + object_b
            print(answer)
            print(chained_premises)
            print("Conclusion: " + conclusion)
    if is_settings:
        if deep_settings:
            draw_texture(deep_settings_background_texture, 0, 0, GRAY)
            if settings_buttons["garbage_length"]._enabled:
                settings_buttons["garbage_length"].toggle()
        else:
            draw_texture(settings_background_texture, 0, 0, GRAY)
            if not settings_buttons["garbage_length"]._enabled:
                settings_buttons["garbage_length"].toggle()
            redirect_settings()
    else:
        if settings_buttons["garbage_length"]._enabled:
            settings_buttons["garbage_length"].toggle()
        if viewing_key:
            i = 0
            for relation, word in problem_spatial_code.items():
                draw_text_ex(premise_font, word + " <---> " + relation, Vector2(int(RESOLUTION_X / 2), int(200 + (50 * i))), 50, 2, WHITE)
                i += 1
        else:
            draw_texture(background_texture, 0, 0, GRAY)
            draw_texture_ex(question_mat_texture, Vector2(int((RESOLUTION_X / 2) - 0.75 * (RESOLUTION_Y / 2)), 0.25 * (RESOLUTION_Y / 2)), 0.0, 0.75, Color(255, 255, 255, 64))
            draw_rectangle(int((RESOLUTION_X / 2) - 0.75 * (RESOLUTION_Y / 2)), int(0.25 * (RESOLUTION_Y / 2)), int(0.75 * RESOLUTION_Y), 50, WHITE)
            draw_text("Rank: " + settings_data["Rank"] + " | Pts: " + str(settings_data["Points"]), int((RESOLUTION_X / 2) - 0.75 * (RESOLUTION_Y / 2)) + 25, int(0.25 * (RESOLUTION_Y / 2)) + 12, 25, BLACK)
            draw_text("[A] <  " + str(premise_page) + "  > [D]", int((RESOLUTION_X / 2) - (measure_text("[A] <  " + str(premise_page) + "  > [D]", 50) / 2)), int(0.75 * (RESOLUTION_Y) + 25), 50, WHITE)
            draw_text("[V] View Key", RESOLUTION_X - 50 - measure_text("[V] View Key", 25), 30, 25, WHITE)
            if is_key_pressed(KeyboardKey.KEY_A):
                premise_page = max(premise_page - 1, 1)
            elif is_key_pressed(KeyboardKey.KEY_D):
                if chosen_gamemode == "2D Spatial":
                    premise_page = min(premise_page + 1, int(math.ceil(len(premises) / premises_per_page)))
                elif chosen_gamemode == "Chain Logic":
                    premise_page = min(premise_page + 1, int(math.ceil(len(chained_premises) / premises_per_page)))
            if chosen_gamemode == "2D Spatial":
                last_i = min(premises_per_page, len(premises) - (premises_per_page * (premise_page - 1)))
                for i in range(last_i):
                    current_premise = premises[(premises_per_page * (premise_page - 1)) + i]
                    draw_text_ex(premise_font, current_premise, Vector2(int((RESOLUTION_X / 2) - (measure_text_ex(premise_font, current_premise, 35, 2).x / 2)), int(0.25 * (RESOLUTION_Y / 2)) + 80 + (40 * i)), 35, 2, WHITE)
                if premise_page == int(math.ceil(len(premises) / premises_per_page)):
                    draw_text_ex(premise_font, "Conclusion: " + conclusion, Vector2(int((RESOLUTION_X / 2) - (measure_text_ex(premise_font, "Conclusion: " + conclusion, 35, 2).x / 2)), int(0.25 * (RESOLUTION_Y / 2)) + 80 + (40 * last_i)), 35, 2, WHITE)
                    draw_rectangle_lines_ex(Rectangle(int((RESOLUTION_X / 2) - (measure_text_ex(premise_font, "Conclusion: " + conclusion, 35, 2).x / 2)) - 5, int(0.25 * (RESOLUTION_Y / 2)) + 80 + (40 * last_i), measure_text_ex(premise_font, "Conclusion: " + conclusion, 35, 2).x + 10, 35), 5.0, BLUE)
            elif chosen_gamemode == "Chain Logic":
                last_i = min(premises_per_page, len(chained_premises) - (premises_per_page * (premise_page - 1)))
                for i in range(last_i):
                    current_premise = chained_premises[(premises_per_page * (premise_page - 1)) + i]
                    draw_text_ex(premise_font, current_premise, Vector2(int((RESOLUTION_X / 2) - (measure_text_ex(premise_font, current_premise, 35, 2).x / 2)), int(0.25 * (RESOLUTION_Y / 2)) + 80 + (40 * i)), 35, 2, WHITE)                
                if premise_page == int(math.ceil(len(chained_premises) / premises_per_page)):
                    draw_text_ex(premise_font, "Conclusion: " + conclusion, Vector2(int((RESOLUTION_X / 2) - (measure_text_ex(premise_font, "Conclusion: " + conclusion, 35, 2).x / 2)), int(0.25 * (RESOLUTION_Y / 2)) + 80 + (40 * last_i)), 35, 2, WHITE)
                    draw_rectangle_lines_ex(Rectangle(int((RESOLUTION_X / 2) - (measure_text_ex(premise_font, "Conclusion: " + conclusion, 35, 2).x / 2)) - 5, int(0.25 * (RESOLUTION_Y / 2)) + 80 + (40 * last_i), measure_text_ex(premise_font, "Conclusion: " + conclusion, 35, 2).x + 10, 35), 5.0, BLUE)            
            draw_text("[0] False", int((RESOLUTION_X / 2) - (0.75 * (RESOLUTION_Y / 2)) + (0.75 * RESOLUTION_Y) + 50), int((RESOLUTION_Y / 2) - 175), 50, WHITE)
            draw_text("[1] True", int((RESOLUTION_X / 2) - (0.75 * (RESOLUTION_Y / 2)) + (0.75 * RESOLUTION_Y) + 50), int((RESOLUTION_Y / 2) - 100), 50, WHITE)
            answered_flag = False
            result = None
            if is_key_pressed(KeyboardKey.KEY_ZERO):
                result = not answer
                answered_flag = True
            if is_key_pressed(KeyboardKey.KEY_ONE):
                result = answer
                answered_flag = True
            if answered_flag:
                if result:
                    if chosen_gamemode == "2D Spatial":
                        settings_data["Points"] += len(premises)
                    elif chosen_gamemode == "Chain Logic":
                        settings_data["Points"] += len(chained_premises)
                else:
                    if chosen_gamemode == "2D Spatial":
                        settings_data["Points"] -= len(premises)
                    elif chosen_gamemode == "Chain Logic":
                        settings_data["Points"] -= len(chained_premises)
                        settings_data["Points"] = max(0, settings_data["Points"])
                if settings_data["Rank"] != "IQ Grandmaster" and settings_data["Points"] >= RANKINGS[ORDERED_RANKINGS[ORDERED_RANKINGS.index(settings_data["Rank"]) + 1]]["Points"]:
                    settings_data["Rank"] = ORDERED_RANKINGS[ORDERED_RANKINGS.index(settings_data["Rank"]) + 1]
                if settings_data["Rank"] != "Mortal Mind" and settings_data["Points"] < RANKINGS[ORDERED_RANKINGS[ORDERED_RANKINGS.index(settings_data["Rank"])]]["Points"]:
                    settings_data["Rank"] = ORDERED_RANKINGS[ORDERED_RANKINGS.index(settings_data["Rank"]) - 1]
                is_generating = True
                problem_spatial_code = {}
                premises = []
                chained_premises = []
                conclusion = ""
                answer = False
                with open("settings_data.json", "w") as file:
                    json.dump(settings_data, file)
        if is_key_down(KeyboardKey.KEY_V):
            viewing_key = True
        elif is_key_released(KeyboardKey.KEY_V):
            viewing_key = False
    if not viewing_key:
        draw_text("[S] Settings", 50, 30, 25, WHITE)
    if is_key_pressed(KeyboardKey.KEY_S) and not viewing_key:
        in_transition = True
        if deep_settings:
            deep_settings = False
            for key, settings_object in settings_buttons.items():
                if settings_object._enabled:
                    blacklist_toggle.append(key)    
                    settings_object.toggle()
                else:
                    if key in blacklist_toggle:
                        blacklist_toggle.remove(key)
        else:
            is_settings = not is_settings
        settings_data["Settings"]["2D Spatial"]["Active"] = settings_buttons["two_d_active"]._on
        settings_data["Settings"]["2D Spatial"]["Premises"] = max(int(settings_buttons["two_d_premises"].text), 2)   
        
        settings_data["Settings"]["Chain Logic"]["Active"] = settings_buttons["chain_premises_active"]._on 
        settings_data["Settings"]["Chain Logic"]["ChainCount"] = max(int(settings_buttons["chain_count"].text), 2)
        settings_data["Settings"]["Chain Logic"]["NestedChainCount"] = int(settings_buttons["nested_chain_count"].text)
        settings_data["Settings"]["Chain Logic"]["ChainLengthMin"] = max(int(settings_buttons["chain_length_min"].text), 3)
        settings_data["Settings"]["Chain Logic"]["ChainLengthMax"] = max(int(settings_buttons["chain_length_max"].text), settings_data["Settings"]["Chain Logic"]["ChainLengthMin"], 3)
        settings_data["Settings"]["GarbageWordLength"] = int(settings_buttons["garbage_length"].text)
        with open("settings_data.json", "w") as file:
            json.dump(settings_data, file)
    for settings_object in settings_buttons.values():
        settings_object.update()
    if in_transition:
        transition_room()
    end_drawing()
unload_font(premise_font)
close_window()