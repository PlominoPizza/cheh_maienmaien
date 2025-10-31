#!/usr/bin/env python3
"""
Script pour calculer les distances routières depuis Chez Mémé vers chaque spot de surf
en utilisant l'API OpenRouteService.
"""

import requests
import json
import time

# Coordonnées de départ : Chez Mémé
chez_meme = {
    'lat': 43.47007441987446,
    'lng': -1.5502231105144162
}

# Liste des spots avec leurs nouvelles coordonnées
spots = [
    {'name': 'Grande Plage', 'location': 'Biarritz', 'lat': 43.48505622591267, 'lng': -1.5574765227972476},
    {'name': 'Côte des Basques', 'location': 'Biarritz', 'lat': 43.47564359716611, 'lng': -1.5664002921277527},
    {'name': 'Chambre d\'Amour', 'location': 'Anglet', 'lat': 43.49427252956886, 'lng': -1.5456154571455343},
    {'name': 'Uhabia', 'location': 'Bidart', 'lat': 43.43108738144451, 'lng': -1.5989006378043706},
    {'name': 'Parlementia', 'location': 'Guéthary', 'lat': 43.427723562362054, 'lng': -1.6068852440572812},
    {'name': 'Hendaye Plage', 'location': 'Hendaye', 'lat': 43.3735961088257, 'lng': -1.7742203280832838},
    {'name': 'Santocha', 'location': 'Capbreton', 'lat': 43.64702883230817, 'lng': -1.4426945771349413},
    {'name': 'La Gravière', 'location': 'Hossegor', 'lat': 43.6737751398771, 'lng': -1.4391911691273902},
    {'name': 'Le Penon', 'location': 'Seignosse', 'lat': 43.709888795671304, 'lng': -1.4339030135463402},
    {'name': 'Roca Puta', 'location': 'Zumaia (Espagne)', 'lat': 43.30547054811386, 'lng': -2.240322543271815}
]

def get_distance_osrm(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Calcule la distance routière entre deux points en utilisant OSRM (Open Source Routing Machine).
    Service gratuit et public, pas besoin de clé API.
    """
    # OSRM endpoint public
    url = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}".format(
        origin_lng, origin_lat,
        dest_lng, dest_lat
    )
    
    params = {
        'overview': 'false',
        'alternatives': 'false',
        'steps': 'false'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'routes' in data and len(data['routes']) > 0:
                route = data['routes'][0]
                distance_km = route['distance'] / 1000  # Convertir en km
                duration_sec = route['duration']  # Durée en secondes
                duration_min = int(duration_sec / 60)  # Convertir en minutes
                return distance_km, duration_min
            else:
                print(f"  [WARNING] Pas de route trouvee dans la reponse")
                return None, None
        else:
            print(f"  [WARNING] Erreur {response.status_code}: {response.text[:100]}")
            return None, None
            
    except Exception as e:
        print(f"  [ERROR] Erreur lors de la requete: {e}")
        return None, None

def calculate_all_distances():
    """Calcule les distances pour tous les spots."""
    print("Calcul des distances depuis Chez Meme vers chaque spot de surf\n")
    print(f"Depart: Chez Meme ({chez_meme['lat']}, {chez_meme['lng']})\n")
    
    results = []
    
    for spot in spots:
        print(f"Calcul pour {spot['name']} ({spot['location']})...", end=" ")
        distance_km, duration_min = get_distance_osrm(
            chez_meme['lat'], chez_meme['lng'],
            spot['lat'], spot['lng']
        )
        
        if distance_km is not None:
            print(f"[OK] Distance: {distance_km:.2f} km, Temps: {duration_min} min")
            results.append({
                'name': spot['name'],
                'location': spot['location'],
                'lat': spot['lat'],
                'lng': spot['lng'],
                'distance_km': round(distance_km, 1),
                'temps_minutes': duration_min
            })
        else:
            print("[ECHEC]")
        
        # Pause pour éviter de surcharger l'API
        time.sleep(0.5)
    
    return results

if __name__ == '__main__':
    results = calculate_all_distances()
    
    print("\n" + "="*60)
    print("RÉSULTATS")
    print("="*60)
    
    for result in results:
        print(f"\n{result['name']} ({result['location']}):")
        print(f"  - Distance: {result['distance_km']} km")
        print(f"  - Temps: {result['temps_minutes']} minutes")
        print(f"  - Coordonnées: {result['lat']}, {result['lng']}")
    
    # Sauvegarder les résultats dans un fichier JSON
    with open('distances_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n[OK] Resultats sauvegardes dans 'distances_results.json'")

