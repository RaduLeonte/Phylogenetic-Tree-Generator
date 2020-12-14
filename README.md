# Phylogenetic-Tree-Generator
Python 3.6 script that turns a spreadsheet with animals and their traits into a phylogenetic tree.

## Libraries needed
Libraries needed to run this script:
- pandas
- svgwrite

## Input
This script takes an .xlsx file as input using the following format:

           A             B           C
    1               Trait Name  Trait Name
    2 Animal Name       1           5   
    3 Animal Name       0           2
    4 Animal Name       1           0
    
Traits can either be [1] or [0] to represent [has trait] or [doesn't have trait], but they can also represent a scale. For more information refer to the example named "ptg_input_short_example.xlsx"

## Output
This script outputs an .svg file. The dimensions are determined during the analysis of the input based on how many animals and steps in the tree are present.
