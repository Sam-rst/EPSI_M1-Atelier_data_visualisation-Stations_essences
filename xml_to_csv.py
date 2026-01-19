#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour convertir le fichier XML PrixCarburants_instantane.xml en CSV
"""

import xml.etree.ElementTree as ET
import csv
import sys
from pathlib import Path


def parse_xml_to_csv(xml_file, csv_file):
    """
    Convertit un fichier XML de prix de carburants en CSV
    
    Args:
        xml_file: Chemin vers le fichier XML d'entrée
        csv_file: Chemin vers le fichier CSV de sortie
    """
    try:
        # Parser le fichier XML avec l'encodage ISO-8859-1
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Préparer les données pour le CSV
        rows = []
        
        # Parcourir tous les points de vente (pdv)
        for pdv in root.findall('pdv'):
            # Extraire les attributs du point de vente
            pdv_id = pdv.get('id', '')
            latitude = pdv.get('latitude', '')
            longitude = pdv.get('longitude', '')
            cp = pdv.get('cp', '')
            pop = pdv.get('pop', '')
            
            # Extraire l'adresse et la ville
            adresse = pdv.find('adresse')
            adresse_text = adresse.text if adresse is not None and adresse.text else ''
            
            ville = pdv.find('ville')
            ville_text = ville.text if ville is not None and ville.text else ''
            
            # Extraire les services (concaténés avec des points-virgules)
            services = pdv.find('services')
            services_list = []
            if services is not None:
                for service in services.findall('service'):
                    if service.text:
                        services_list.append(service.text)
            services_text = '; '.join(services_list)
            
            # Extraire tous les prix
            prix_list = pdv.findall('prix')
            
            if prix_list:
                # Si le point de vente a des prix, créer une ligne par prix
                for prix in prix_list:
                    prix_nom = prix.get('nom', '')
                    prix_id = prix.get('id', '')
                    prix_maj = prix.get('maj', '')
                    prix_valeur = prix.get('valeur', '')
                    
                    rows.append({
                        'pdv_id': pdv_id,
                        'latitude': latitude,
                        'longitude': longitude,
                        'code_postal': cp,
                        'pop': pop,
                        'adresse': adresse_text,
                        'ville': ville_text,
                        'services': services_text,
                        'prix_nom': prix_nom,
                        'prix_id': prix_id,
                        'prix_maj': prix_maj,
                        'prix_valeur': prix_valeur
                    })
            else:
                # Si le point de vente n'a pas de prix, créer quand même une ligne
                rows.append({
                    'pdv_id': pdv_id,
                    'latitude': latitude,
                    'longitude': longitude,
                    'code_postal': cp,
                    'pop': pop,
                    'adresse': adresse_text,
                    'ville': ville_text,
                    'services': services_text,
                    'prix_nom': '',
                    'prix_id': '',
                    'prix_maj': '',
                    'prix_valeur': ''
                })
        
        # Trier les lignes par prix_id (1, 2, 3, 4, 5, 6, 7, 8...)
        # Les lignes sans prix_id (vides) seront mises à la fin
        def sort_key(row):
            prix_id = row.get('prix_id', '')
            if prix_id == '':
                return (999999, row.get('pdv_id', ''))  # Mettre les lignes sans prix à la fin
            try:
                return (int(prix_id), row.get('pdv_id', ''))  # Trier par ID numérique puis par pdv_id
            except ValueError:
                return (999999, row.get('pdv_id', ''))  # Si l'ID n'est pas un nombre, mettre à la fin
        
        rows_sorted = sorted(rows, key=sort_key)
        
        # Écrire dans le fichier CSV
        if rows_sorted:
            fieldnames = ['pdv_id', 'latitude', 'longitude', 'code_postal', 'pop', 
                         'adresse', 'ville', 'services', 'prix_nom', 'prix_id', 
                         'prix_maj', 'prix_valeur']
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows_sorted)
            
            print(f"[OK] Conversion reussie !")
            print(f"  Fichier XML: {xml_file}")
            print(f"  Fichier CSV: {csv_file}")
            print(f"  Nombre de lignes creees: {len(rows_sorted)}")
            print(f"  Donnees triees par prix_id (1=Gazole, 2=SP95, 3=E85, 4=GPLc, 5=E10, 6=SP98, etc.)")
        else:
            print("[ATTENTION] Aucune donnee trouvee dans le fichier XML")
            
    except ET.ParseError as e:
        print(f"[ERREUR] Erreur lors du parsing XML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERREUR] Erreur: {e}")
        sys.exit(1)


def main():
    """Fonction principale"""
    # Définir les chemins des fichiers
    xml_file = Path('PrixCarburants_instantane.xml')
    csv_file = Path('PrixCarburants_instantane.csv')
    
    # Vérifier que le fichier XML existe
    if not xml_file.exists():
        print(f"[ERREUR] Le fichier {xml_file} n'existe pas")
        sys.exit(1)
    
    # Effectuer la conversion
    parse_xml_to_csv(xml_file, csv_file)


if __name__ == '__main__':
    main()
