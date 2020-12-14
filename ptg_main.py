from svgwrite import Drawing
from pandas import ExcelFile
from os import path
from ast import literal_eval
from time import time
from datetime import timedelta
from copy import deepcopy

# Define LOG
log_list = list()

# Start Timer
timer_whole_script = time()
log_list.extend("\n --- TIMER HAS STARTED\n")


"""
Description: This part takes the rows and columns of the xlsx file and inserts them into a dictionary.
       
Example: input =

           |  A  |  B   |  C   |  D   |   E
         __|_____|______|______|______|________
         1 |     | Paws | Ribs | Size | Aquatic
         __|_____|______|______|______|________
         2 | Dog |  4   |  26  |  4   |   0
           |     |      |      |      |  

         output = {Dog: [4, 26, 4, 0]} 
"""

log_list.extend("\n===========================\n --- COMMENCING STEP 1\n===========================\n")

current_path = path.realpath(__file__)[:-11]
sheet = ExcelFile(f"{current_path}ptg_input.xlsx").parse("Sheet1")
unprocessed_data = dict()
for row in sheet.iterrows():
    index, data = row
    unprocessed_data.update({index: data.tolist()})

log_list.extend(f" - Unprocessed Data Dict: {len(list(unprocessed_data.keys()))}\n")
log_list.extend("\n ~~~ Step 1 Completed! ~~~\n")

log_list.extend("\n===========================\n --- COMMENCING STEP 2\n===========================\n")


def average_values(to_average_1, to_average_2):

    """
    Description: Averages 2 value lists and returns 1 list.

    Example: List_1 = [0, 2, 10]
             List_2 = [2, 6, 20]

             output = [(0 + 2) / 2,
                       (2 + 6) / 2,
                       (10 + 20) / 2]

             output = [1, 4, 15]
    """

    result = list()
    j = 0
    for value in to_average_1:
        value_pair = to_average_2[j]
        if value == "?" or value_pair == "?":
            result.append("?")

        else:
            result.append(((value + value_pair) / 2))
        j += 1
    return result


def get_max_trait_value(column_index):  # Returns the highest value in a column to be used as the trait max value

    """
    Description: Returns the highest value in a column from the initial spreadsheet to be used as the trait max value.

    Example:
               |  A  |    B
             __|_____|_________
             1 |     | Whiskers
             __|_____|_________
             2 | Dog |    20
             __|_____|_________
             3 | Cat |    24
             __|_____|_________
             4 | Rat |    4
               |     |

             output = 24
    """

    column_values = sheet[sheet.columns[column_index]].tolist()
    while "?" in column_values:
        column_values.remove("?")
    return max(column_values)


def calculate_initial_similarities(values_dict, monsters_to_compare):

    """
    Description: Using the initial hierarchy provided by reading the spreadsheet top to bottom, returns a new dictionary
                 with an entry for each possible combination of animals with an according similarity score.

    Example: initial_hierarchy = [Dog, Cat, Human]
             values_dict = {"Dog": [0,1,3],
                            "Cat": [0,1,5],
                            "Human": [2,5,3]}

             output_dict = {"Dog-Cat": 90,
                            "Dog-Human": 70,
                            "Cat-Human": 60}

    """

    calculated_similarities = dict()
    already_compared = list()
    # temp_monster_list = monsters_to_compare
    for item in monsters_to_compare:
        for item_pair in monsters_to_compare:
            if str(item) != str(item_pair) and item_pair not in already_compared:
                # Declare Variables
                list_to_compare_1 = values_dict[str(item)]
                list_to_compare_2 = values_dict[str(item_pair)]
                max_score = len(values_dict[str(item)])  # Pull max score from value databse
                score = 0
                trait_index = 0

                for trait in list_to_compare_1:
                    trait_pair = list_to_compare_2[trait_index]

                    if trait == trait_pair:  # If they are the same
                        score += 1
                    elif trait == "?" or trait_pair == "?":  # If any of them are "?"
                        max_score -= 1
                    elif trait != trait_pair:  # If they are different
                        trait_max = get_max_trait_value(trait_index)
                        score += 1 - (abs(trait - trait_pair) * (1 / trait_max))

                    trait_index += 1

                if "[" in item:
                    item = literal_eval(item)
                if "[" in item_pair:
                    item_pair = literal_eval(item_pair)
                calculated_similarities[str([item, item_pair])] = score / (max_score / 100)

        if "[" in item:
            item = literal_eval(item)
            already_compared.extend([item])
        else:
            already_compared.extend([item])

    return calculated_similarities


def calculate_new_similarities(new_pair, new_pair_values, values_dict, monsters_to_compare, previous_db):



    already_compared = list()
    for item in monsters_to_compare:
        if str(item) != str(new_pair) and new_pair not in already_compared:
            # Declare Variables
            list_to_compare_1 = values_dict[str(item)]
            list_to_compare_2 = new_pair_values
            max_score = len(new_pair_values)  # Pull max score from value databse
            score = 0
            trait_index = 0

            for trait in list_to_compare_1:
                trait_pair = list_to_compare_2[trait_index]

                if trait == trait_pair:  # If they are the same
                    score += 1
                elif trait == "?" or trait_pair == "?":  # If any of them are "?"
                    max_score -= 1
                elif trait != trait_pair:  # If they are different
                    trait_max = get_max_trait_value(trait_index)
                    score += 1 - (abs(trait - trait_pair) * (1 / trait_max))

                trait_index += 1

            if "[" in item:
                item = literal_eval(item)
            if "[" in new_pair:
                new_pair = literal_eval(new_pair)
            previous_db[str([item, new_pair])] = score / (max_score / 100)

        if "[" in item:
            item = literal_eval(item)
            already_compared.extend([item])
        else:
            already_compared.extend([item])

    return previous_db


monster_values_db = deepcopy(unprocessed_data)  # This is where all the values are pulled from
hierarchy = list(monster_values_db.keys())  # List to be organized into hierarchy


"""
STEP 2.2 - MAIN LOOP 
"""
log_list.extend(" - Main Loop Commencing \n")

loop_counter = 1
initial_hierarchy = deepcopy(hierarchy)
similarities_db = calculate_initial_similarities(monster_values_db, initial_hierarchy)

while len(hierarchy) > 2:  # MAIN LOOP: It will run until the hierarchy is done
    loop_timer = time()
    # Logging
    log_list.extend(f"{loop_counter} Hierarchy so far = ({len(hierarchy)})\n")
    log_list.extend(f"{loop_counter} Monster Values DB = ({len(monster_values_db)})\n")

    # Find Highest Similarity
    similarities_ranking = list()
    highest_similarity_pair = ""
    for key in similarities_db:
        similarities_ranking.extend([similarities_db[key]])
    highest_similarity = max(similarities_ranking)
    for key in similarities_db:
        if similarities_db[key] == highest_similarity:
            highest_similarity_pair = key
            break

    log_list.extend(f"{loop_counter} Highest Similarity = {highest_similarity} - {highest_similarity_pair}\n\n")

    highest_similarity_pair = literal_eval(highest_similarity_pair)  # Turn pair back into list
    # Rewrite Hierarchy
    hierarchy.remove(highest_similarity_pair[0])
    hierarchy.remove(highest_similarity_pair[1])
    hierarchy.extend([highest_similarity_pair])

    # Average Values
    averaged_values = average_values(monster_values_db[str(highest_similarity_pair[0])],
                                     monster_values_db[str(highest_similarity_pair[1])])

    # Calculate new similarities
    # 1. Delete old entries with [0] and [1] in them
    entries_to_be_deleted = []
    for entry in similarities_db:
        if str(highest_similarity_pair[0]) in str(entry) or str(highest_similarity_pair[1]) in str(entry):
            entries_to_be_deleted.append(entry)
    for entry in entries_to_be_deleted:
        del similarities_db[entry]
    # 2. Calculate new similarities
    hierarchy_copy = deepcopy(hierarchy)
    similarities_db = calculate_new_similarities(highest_similarity_pair, averaged_values, monster_values_db,
                                                 hierarchy_copy, similarities_db)

    # Remove unneeded entries from values database
    del monster_values_db[str(highest_similarity_pair[0])]
    del monster_values_db[str(highest_similarity_pair[1])]
    monster_values_db[str(highest_similarity_pair)] = averaged_values

    loop_counter += 1

log_list.extend(f" - Final Hierarchy = {hierarchy}\n\n")
log_list.extend("\n ~~~ Step 2 Completed! ~~~\n")


"""
STEP 3 - GENERATE SVG
"""
log_list.extend("\n===========================\n --- COMMENCING STEP 3\n===========================\n")


def write_text(label, label_coordinates):  # Simplifies writing text to SVG
    dwg.add(dwg.text(label,
                     stroke="none",
                     fill="#000000",
                     font_size="10px",
                     font_family="Verdana",
                     transform=str("translate(" + str(label_coordinates[0]) + "," + str(label_coordinates[1]) +
                                   ")rotate(-45)")))


def draw_line(line_coordinates_start, line_coordinates_end):   # Simplifies drawing lines to SVG
    dwg.add(dwg.line(start=(line_coordinates_start[0], line_coordinates_start[1]),
                     end=(line_coordinates_end[0], line_coordinates_end[1]),
                     fill="none",
                     stroke="#000000",
                     stroke_width=1))


def analyze_branch(branch_to_analyze, previous_serial):
    i = 0
    for sub_branch in branch_to_analyze:
        while True:
            if str(previous_serial + "-" + str(i)) not in nodes:
                node_serial = str(previous_serial + "-" + str(i))
                break
            else:
                i += 1
        if type(sub_branch) == list:
            nodes.append(node_serial)
            analyze_branch(sub_branch, node_serial)
        else:
            nodes.append(node_serial)
            string_nodes[sub_branch] = node_serial


# Analyze Hierarchy and generate Nodes
final_data = deepcopy(hierarchy)
string_nodes = dict()
nodes = ["0"]

analyze_branch(final_data, "0")

longest_node = ""
for node in nodes:
    if len(node) > len(longest_node):
        longest_node = node

# Find Longest Node for canvas dimensions
longest_node_length = len(longest_node.replace("-", ""))

# Settings
margin = 50
starting_coordinates = [margin, 100]
distance_between_names = 20
vertical_distance_between_nodes = 40
svg_width = (margin * 2) + (20 * len(list(unprocessed_data.keys())))
svg_height = (margin * 2) + (longest_node_length * vertical_distance_between_nodes) + 70

# Define File
dwg = Drawing(filename="ptg_export.svg", size=(svg_width, svg_height))
log_list.extend(f"Canvas Size = {svg_width} x {svg_height}\n")

"""
DRAWING ELEMENTS
"""
log_list.extend(f"\nDrawing Elements \n")

coordinate_dict = {}
current_coordinates = starting_coordinates
for key in string_nodes:
    write_text(key, current_coordinates)

    draw_line([current_coordinates[0], current_coordinates[1] + 2],
              [current_coordinates[0], current_coordinates[1] + vertical_distance_between_nodes + 2])
    coordinate_dict[string_nodes[key]] = [current_coordinates[0],
                                          current_coordinates[1] + vertical_distance_between_nodes + 2]
    current_coordinates[0] += distance_between_names

loop_counter = 1
while len(nodes) != 0:
    for node in nodes:

        if node == "0":
            nodes.remove(node)
        else:
            current_serial = node
            serial_root = current_serial[:-2]
            for serial in nodes:
                if (len(serial) == len(current_serial)
                        and serial[:-2] == serial_root
                        and serial != current_serial):
                    sister_serial = serial

            try:
                if sister_serial in coordinate_dict:
                    if coordinate_dict[current_serial][1] == coordinate_dict[sister_serial][1]:
                        draw_line(coordinate_dict[current_serial], coordinate_dict[sister_serial])
                    else:
                        if coordinate_dict[current_serial][1] > coordinate_dict[sister_serial][1]:
                            draw_line(coordinate_dict[sister_serial],
                                      [coordinate_dict[sister_serial][0], coordinate_dict[current_serial][1]])
                        else:
                            draw_line(coordinate_dict[current_serial],
                                      [coordinate_dict[current_serial][0], coordinate_dict[sister_serial][1]])

                        new_y = max([coordinate_dict[current_serial][1], coordinate_dict[sister_serial][1]])
                        coordinate_dict[current_serial][1] = new_y
                        coordinate_dict[sister_serial][1] = new_y
                        draw_line(coordinate_dict[current_serial], coordinate_dict[sister_serial])
                else:
                    draw_line(coordinate_dict[current_serial],
                              [coordinate_dict[current_serial][0],
                               coordinate_dict[current_serial][1] + vertical_distance_between_nodes])

                middle_coordinates = [((coordinate_dict[sister_serial][0] -
                                        coordinate_dict[current_serial][0]) / 2)
                                      + coordinate_dict[current_serial][0],
                                      coordinate_dict[current_serial][1] + vertical_distance_between_nodes]
                draw_line(middle_coordinates, [middle_coordinates[0],
                                               middle_coordinates[1] - vertical_distance_between_nodes])
                coordinate_dict[serial_root] = middle_coordinates
                nodes.remove(current_serial)
                nodes.remove(sister_serial)
            except KeyError:
                pass

    loop_counter += 1

dwg.save()  # Saves file

log_list.extend("\n ~~~ Step 3 Completed! ~~~\n")

# End Timer
log_list.extend(f"\n\n\n => Script Took: {timedelta(seconds=(time() - timer_whole_script))}\n")

# Print Log to file
log_file = open("ptg_log.txt", "w")
for line in log_list:
    log_file.write(line)

print(timedelta(seconds=(time() - timer_whole_script)))
