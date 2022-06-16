import frontmatter
import re
import csv
import numpy as np

def InputTill(input_file,output_file):
    recipe = frontmatter.load(input_file)
    ingridients = recipe['Zutaten']
    name = recipe['title']
    servings = recipe['servings']
    returns = [(name, servings, "")]

    for ingridient in ingridients:
        amount = re.findall('^[0-9]*', ingridient)
        possible_units = ['g', 'kg', 'ml', 'l', 'tbsp', 'tsp', 'fl oz', 'oz', 'pint', 'quart', 'gallon', 'cup', 'pack', 'pcs', 'Teaspoon', 'Tablespoon', 'Pint', 'Quart', 'Gallon', 'Cup', 'Pack', 'Pcs']
        u = 0
        for unit in possible_units:
            u = re.findall('^[0-9]*\ '+unit, ingridient)
            if u:
                break
        if u:
            unit = str(u[0]).replace(str(amount[0])+' ', '')
            ing = ingridient.replace(str(amount[0])+' '+unit+' ', '')
        else:
            unit = input("Enter Unit for "+ingridient+" - no unit detected: ")
            ing = ingridient.replace(str(amount[0])+' ', '')
        returns.append((amount[0], unit, ing))
    array = np.asarray(returns)
    file = open(output_file, 'w+', newline ='')

    with file:
        write = csv.writer(file, delimiter='\t')
        write.writerows(array)
