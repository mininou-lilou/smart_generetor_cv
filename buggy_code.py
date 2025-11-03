import os
import json
from typing import List, Dict

def calculate_sum(a, b):
    """Retourne la somme de a et b"""
    return a + b

def process_data(data: List[Dict]):
    results = []
    for item in data:
        name = item.get('name')
        age = item['age]
        if age > 18:
            results.append(f"{name} est majeur)
        else
            results.append(f"{name} est mineur")
    return results

def main()
    print("Démarrage du programme...")
    
    # Erreur de syntaxe : manque les deux-points après def main()
    # Erreur mypy : type de data non vérifié
    data = [
        {'name': 'Alice', 'age': 25},
        {'name: 'Bob', 'age': 17},
        {'name': 'Charlie'},  # Erreur mypy : clé 'age' manquante
    ]
    
    # Erreur pylint : variable non utilisée
    unused_var = 42
    
    # Erreur flake8 : ligne trop longue
    very_long_string = "Ceci est une ligne très très très très très très très très très très très très très très très très très très très très très très très très très très longue qui dépasse largement les 88 caractères recommandés par Black et flake8."
    
    # Erreur pylint : nom de fonction en snake_case manquant (devrait être calculate_sum)
    def CalculateTotal(x,y): return x+y
    
    # Erreur de syntaxe : indentation incorrecte
        indented_wrong = True
    
    total = calculate_sum(10, 20)
    print(f"Total: {total}")
    
    # Erreur mypy : appel avec mauvais type
    bad_sum = calculate_sum("10", 20)
    
    # Erreur flake8 : espace avant le deux-points
    print(f"Résultat : {bad_sum")
    
    # Erreur pylint : trop de variables locales (simulé)
    a,b,c,d,e,f,g,h,i,j,k,l,m = range(13)
    
    # Erreur Black : mélange d'espaces et tabulations + ligne mal alignée
    	weird_indentation = "mix tab and space"
    
    processed = process_data(data)
    for res in processed:
        print(res)
    
    # Erreur pylint : import non utilisé
    import math
    
    # Erreur de syntaxe : guillemet non fermé
    broken_string = "Ceci est une chaîne cassée
    
    return 0

if __name__ == "__main__":
    main()
