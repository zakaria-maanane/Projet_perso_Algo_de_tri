import pygame
import random
import time
import json
import os
from sorting_algorithms import SortingAlgorithms
import tracemalloc
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

WIDTH, HEIGHT = 800, 600
BAR_COLOR = (0, 102, 204)
BG_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (150, 150, 150)
TEXT_COLOR = (0, 0, 0)
INPUT_COLOR = (240, 240, 240)
INPUT_BORDER_COLOR = (150, 150, 150)
INPUT_ACTIVE_COLOR = (220, 220, 255)

class SortVisualizer:
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0
        self.execution_time = 0
        self.start_ticks = 0
        self.is_sorting = False
        self.memory_usage = 0
        self.peak_memory = 0
        self.current_results = {}
        self.performance_data = {name: {'sizes': [], 'times': []} for name in [
            "Selection Sort", "Bubble Sort", "Insertion Sort", 
            "Merge Sort", "Quick Sort", "Heap Sort", "Comb Sort"
        ]}
        
        # Ajouter un bouton pour réinitialiser le graphique
        self.reset_graph_button = pygame.Rect(350, 310, 200, 40)
    
        # Initialiser Pygame et la fenêtre
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tri Visuel")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        self.algorithms = [
            SortingAlgorithms.selection_sort,
            SortingAlgorithms.bubble_sort,
            SortingAlgorithms.insertion_sort,
            SortingAlgorithms.merge_sort,
            SortingAlgorithms.quick_sort,
            SortingAlgorithms.heap_sort,
            SortingAlgorithms.comb_sort,
        ]
        self.algorithm_names = [
            "Selection Sort",
            "Bubble Sort",
            "Insertion Sort",
            "Merge Sort",
            "Quick Sort",
            "Heap Sort",
            "Comb Sort"
        ]
        
        self.buttons = []
        self.return_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 60, 200, 40)
        self.run_all_button = pygame.Rect(350, 70, 200, 40)
        self.graph_button = pygame.Rect(350, 130, 200, 40)
        self.benchmark_button = pygame.Rect(350, 250, 200, 40)  # Ajout d'un bouton pour lancer les benchmarks
        
        # Configuration pour l'entrée du nombre d'éléments
        self.element_count = 100  # Valeur par défaut
        self.min_value = 1
        self.max_value = 1000000000000000000000000
        self.element_input_rect = pygame.Rect(350, 190, 200, 40)
        self.element_input_active = False
        self.element_input_text = str(self.element_count)
        
        self.bar_width = WIDTH // self.element_count if self.element_count <= WIDTH else 1
        
        self.numbers = []
        self.generate_numbers()
        self.create_buttons()
        
        self.showing_results = False
        self.showing_graph = False
        self.graph_surface = None

    def generate_numbers(self):
        self.numbers = [random.randint(1, HEIGHT - 100) for _ in range(self.element_count)]
        self.bar_width = WIDTH // self.element_count if self.element_count <= WIDTH else 1

    def create_buttons(self):
        self.buttons = []
        for i, name in enumerate(self.algorithm_names):
            rect = pygame.Rect(100, 70 + 40 * i, 200, 30)
            self.buttons.append((rect, name))

    def draw_bars(self, highlighted_indices=None):
        self.screen.fill(BG_COLOR)
        highlighted_indices = highlighted_indices or []
        
        # Adapter l'affichage en fonction du nombre d'éléments
        bar_width = self.bar_width
        for i, value in enumerate(self.numbers):
            if i >= WIDTH // bar_width:
                break  # Ne pas dessiner plus de barres que ce qui peut tenir à l'écran
                
            x = i * bar_width
            height = min(value % (HEIGHT - 100), HEIGHT - 100)  # Assurer que la hauteur est dans les limites
            color = SELECTED_COLOR if i in highlighted_indices else BAR_COLOR
            pygame.draw.rect(self.screen, color, (x, HEIGHT - height, bar_width, height))

        # Afficher les statistiques
        stats_text = self.font.render(f"Comparaisons: {self.comparisons} | Échanges: {self.swaps}", True, TEXT_COLOR)
        time_text = self.font.render(f"Temps d'exécution: {self.execution_time:.6f} secondes", True, TEXT_COLOR)
        memory_text = self.font.render(f"Mémoire: {self.memory_usage:.2f} KB | Pic: {self.peak_memory:.2f} KB", True, TEXT_COLOR)
        
        self.screen.blit(stats_text, (10, 10))
        self.screen.blit(time_text, (10, 40))
        self.screen.blit(memory_text, (10, 70))
        
        pygame.display.flip()

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        title = self.font.render("Algorithmes de tri:", True, TEXT_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        mouse_pos = pygame.mouse.get_pos()

        # Dessiner les boutons des algorithmes
        for i, (rect, _) in enumerate(self.buttons):
            color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, rect)
            text = self.font.render(self.algorithm_names[i], True, TEXT_COLOR)
            self.screen.blit(text, (rect.x + 10, rect.y + 5))

        # Bouton pour lancer tous les tris
        color = BUTTON_HOVER_COLOR if self.run_all_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.run_all_button)
        text = self.font.render("Lancer tous les tris", True, TEXT_COLOR)
        self.screen.blit(text, (self.run_all_button.x + 10, self.run_all_button.y + 10))
        
        # Bouton pour afficher le graphique de performance
        color = BUTTON_HOVER_COLOR if self.graph_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.graph_button)
        text = self.font.render("Graphique de performance", True, TEXT_COLOR)
        self.screen.blit(text, (self.graph_button.x + 10, self.graph_button.y + 10))
        
        # Bouton pour lancer les benchmarks
        color = BUTTON_HOVER_COLOR if self.benchmark_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.benchmark_button)
        text = self.font.render("Lancer les benchmarks", True, TEXT_COLOR)
        self.screen.blit(text, (self.benchmark_button.x + 10, self.benchmark_button.y + 10))
       
        # Bouton pour réinitialiser le graphique
        color = BUTTON_HOVER_COLOR if self.reset_graph_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.reset_graph_button)
        text = self.font.render("Réinitialiser graphique", True, TEXT_COLOR)
        self.screen.blit(text, (self.reset_graph_button.x + 10, self.reset_graph_button.y + 10))
    
        # Zone de saisie pour le nombre d'éléments
        input_color = INPUT_ACTIVE_COLOR if self.element_input_active else INPUT_COLOR
        pygame.draw.rect(self.screen, input_color, self.element_input_rect)
        pygame.draw.rect(self.screen, INPUT_BORDER_COLOR, self.element_input_rect, 2)
        
        input_label = self.font.render("", True, TEXT_COLOR)
        self.screen.blit(input_label, (self.element_input_rect.x - 200, self.element_input_rect.y + 10))
        
        input_text = self.font.render(self.element_input_text, True, TEXT_COLOR)
        self.screen.blit(input_text, (self.element_input_rect.x + 10, self.element_input_rect.y + 10))

        pygame.display.flip()

    def draw_return_button(self):
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER_COLOR if self.return_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.return_button)
        text = self.font.render("Retour au menu", True, TEXT_COLOR)
        self.screen.blit(text, (self.return_button.x + 25, self.return_button.y + 10))
        pygame.display.flip()

    def draw_swap(self, arr, i, j):
        # Effectuer l'échange et mettre à jour les statistiques
        arr[i], arr[j] = arr[j], arr[i]
        self.comparisons += 1
        self.swaps += 1

        # Mettre à jour le temps d'exécution
        self.execution_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0

        # Mettre à jour les stats de mémoire
        current, peak = tracemalloc.get_traced_memory()
        self.memory_usage = current / 1024
        self.peak_memory = max(self.peak_memory, peak / 1024)

        # Si on n'est pas en mode "affichage des résultats", dessiner l'animation
        if not self.showing_results and not self.showing_graph:
            self.draw_bars([i, j])
            
            # Ralentir légèrement l'animation pour mieux voir les changements
            pygame.time.delay(1)  # Petit délai pour l'animation
            
            # Gérer les événements pendant l'animation pour permettre de quitter
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    def measure_performance(self, sorting_function, algorithm_name=None, show_animation=True):
        # Réinitialiser les statistiques
        self.comparisons = 0
        self.swaps = 0
        self.execution_time = 0  
        self.memory_usage = 0
        self.peak_memory = 0
        
        # Définir si on doit montrer l'animation ou non
        self.showing_results = not show_animation

        # Créer une copie des nombres pour ne pas altérer l'original
        numbers_copy = self.numbers.copy()
        
        # Démarrer le suivi de la mémoire
        tracemalloc.start()
        self.start_ticks = pygame.time.get_ticks()
        
        # Exécuter l'algorithme de tri
        sorting_function(numbers_copy, self.draw_swap)
        
        # Si nous sommes en mode animation, mettre à jour les nombres triés
        if show_animation:
            self.numbers = numbers_copy

        # Calculer le temps total d'exécution
        self.execution_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
        
        # Obtenir l'utilisation finale de la mémoire
        current, peak = tracemalloc.get_traced_memory()
        self.memory_usage = current / 1024
        self.peak_memory = peak / 1024
        
        # Arrêter le suivi de la mémoire
        tracemalloc.stop()

        # Enregistrer les résultats si un nom d'algorithme est spécifié
        if algorithm_name:
            self.current_results[algorithm_name] = {
                "time": self.execution_time,
                "memory": self.peak_memory,
                "comparisons": self.comparisons,
                "swaps": self.swaps
            }
            
            # Enregistrer les données pour le graphique
            if algorithm_name in self.performance_data:
                # Vérifier si cette taille existe déjà dans les données
                if self.element_count in self.performance_data[algorithm_name]['sizes']:
                    # Mettre à jour le temps pour cette taille
                    index = self.performance_data[algorithm_name]['sizes'].index(self.element_count)
                    self.performance_data[algorithm_name]['times'][index] = self.execution_time
                else:
                    # Ajouter la nouvelle taille et son temps
                    self.performance_data[algorithm_name]['sizes'].append(self.element_count)
                    self.performance_data[algorithm_name]['times'].append(self.execution_time)

        # Afficher une dernière image des barres triées si en mode animation
        if show_animation:
            self.draw_bars()
            
        # Afficher dans le terminal
        print(f"{algorithm_name if algorithm_name else 'Algorithme'} - Temps: {self.execution_time:.6f}s | Mémoire: {self.peak_memory:.2f} KB | Comparaisons: {self.comparisons} | Échanges: {self.swaps}")
        
        return self.execution_time

    def run_all_algorithms(self):
        self.showing_results = True
        self.current_results = {}
        
        # Sauvegarde des nombres originaux
        original_numbers = self.numbers.copy()
        
        for i, algorithm in enumerate(self.algorithms):
            # Réinitialiser les nombres à chaque tri
            self.numbers = original_numbers.copy()
            self.measure_performance(algorithm, self.algorithm_names[i], False)
            
            # Petit délai entre chaque algorithme
            time.sleep(0.1)
        
        # Afficher les résultats
        self.display_results()

    def display_results(self):
        running = True
        
        # Trier les résultats par temps d'exécution et utilisation mémoire
        time_ranking = sorted(self.current_results.items(), key=lambda x: x[1]["time"])
        memory_ranking = sorted(self.current_results.items(), key=lambda x: x[1]["memory"])
        
        while running:
            self.screen.fill(BG_COLOR)
            
            # Titre
            title = self.font.render("Classement des algorithmes", True, TEXT_COLOR)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
            
            # Temps d'exécution
            time_title = self.font.render("Par temps d'exécution:", True, TEXT_COLOR)
            self.screen.blit(time_title, (100, 70))
            
            for i, (name, data) in enumerate(time_ranking):
                rank_text = self.small_font.render(f"{i+1}. {name}: {data['time']:.6f}s", True, TEXT_COLOR)
                self.screen.blit(rank_text, (100, 100 + i * 25))
            
            # Utilisation mémoire
            memory_title = self.font.render("Par utilisation mémoire:", True, TEXT_COLOR)
            self.screen.blit(memory_title, (450, 70))
            
            for i, (name, data) in enumerate(memory_ranking):
                rank_text = self.small_font.render(f"{i+1}. {name}: {data['memory']:.2f} KB", True, TEXT_COLOR)
                self.screen.blit(rank_text, (450, 100 + i * 25))
            
            # Bouton retour
            mouse_pos = pygame.mouse.get_pos()
            color = BUTTON_HOVER_COLOR if self.return_button.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, self.return_button)
            text = self.font.render("Retour au menu", True, TEXT_COLOR)
            self.screen.blit(text, (self.return_button.x + 25, self.return_button.y + 10))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.return_button.collidepoint(event.pos):
                        running = False
                        self.showing_results = False
                        
            self.clock.tick(60)

    def generate_performance_graph(self):
        # Création de la figure matplotlib
        fig = Figure(figsize=(8, 5))
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        ax.set_title("Temps d'exécution des algorithmes de tri selon la taille des données")
        ax.set_xlabel("Nombre de données (échelle log)")
        ax.set_ylabel("Temps d'exécution (s) (échelle log)")
        ax.grid(True)
    
        # Configurer les échelles logarithmiques
        ax.set_xscale('log')
        ax.set_yscale('log')

        colors = ['b', 'orange', 'g', 'r', 'c', 'purple', 'pink']

        # Garder une trace des algorithmes avec des données
        has_data = False

        for i, (algo_name, data) in enumerate(self.performance_data.items()):
            if data['sizes'] and data['times']:
                print(f"{algo_name}: sizes = {data['sizes']}, times = {data['times']}")
            
                # Trier les données par taille pour le tracé
                sorted_pairs = sorted(zip(data['sizes'], data['times']))
                sizes, times = zip(*sorted_pairs) if sorted_pairs else ([], [])
            
                if sizes and times:
                    has_data = True
                    # Tracer la ligne et les points
                    ax.plot(sizes, times, 
                           label=self.translate_algo_name(algo_name),
                           marker='o', 
                           color=colors[i % len(colors)],
                           linewidth=2,
                           markersize=8)  # Augmenter la taille des points
                
                     # Annoter chaque point avec la taille
                    for x, y in zip(sizes, times):
                        # Seulement ajouter des annotations si le nombre de points est limité
                        if len(sizes) <= 10:
                            ax.annotate(f"{x}", 
                                        xy=(x, y), 
                                       xytext=(5, 5),
                                       textcoords='offset points', 
                                       fontsize=8,
                                       bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

        # Si aucune donnée n'est disponible, ajouter un message
        if not has_data:
            ax.text(0.5, 0.5, "Aucune donnée disponible.\nLancez d'abord des benchmarks!", 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
        
        ax.legend(loc='upper left')
        fig.tight_layout()

        # Dessine la figure
        canvas.draw()

    # Obtenir les données d'image RGBA
        raw_data = canvas.buffer_rgba()
        size = canvas.get_width_height()

    # Conversion en tableau numpy
        image_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((size[1], size[0], 4))
        image_array = image_array[:, :, :3]  # Supprimer le canal alpha

    # Transposer et convertir en surface Pygame
        self.graph_surface = pygame.surfarray.make_surface(np.transpose(image_array, (1, 0, 2)))

    # Redimensionner pour s'adapter à l'écran si nécessaire
        max_width = WIDTH - 40
        max_height = HEIGHT - 100
        ratio = min(max_width / self.graph_surface.get_width(), max_height / self.graph_surface.get_height())
    
        if ratio < 1:
            new_size = (int(self.graph_surface.get_width() * ratio), 
                        int(self.graph_surface.get_height() * ratio))
            self.graph_surface = pygame.transform.scale(self.graph_surface, new_size)

    # Enregistrement en image
        fig.savefig("tri_performance.png")

    def translate_algo_name(self, name):
        """Traduit les noms d'algorithmes en français pour le graphique"""
        translations = {
            "Selection Sort": "Tri par sélection",
            "Bubble Sort": "Tri à bulles",
            "Insertion Sort": "Tri par insertion",
            "Merge Sort": "Tri par fusion",
            "Quick Sort": "Tri rapide",
            "Heap Sort": "Tri par tas",
            "Comb Sort": "Tri à peigne"
        }
        return translations.get(name, name)

    def run_benchmark_tests(self):
        """Exécute des tests de performance sur différentes tailles d'entrée"""
        test_sizes = [30, 100, 300, 500, 1000]  # Différentes tailles à tester
        
        # Sauvegarde de la valeur actuelle
        original_count = self.element_count
        original_numbers = self.numbers.copy()
        
        # Message de démarrage des benchmarks
        self.screen.fill(BG_COLOR)
        running_text = self.font.render("Exécution des benchmarks en cours...", True, TEXT_COLOR)
        self.screen.blit(running_text, (WIDTH // 2 - running_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        
        # Exécuter les tests pour chaque taille
        for size in test_sizes:
            self.element_count = size
            self.generate_numbers()
            
            test_numbers = self.numbers.copy()
            
            # Exécuter chaque algorithme
            for i, algorithm in enumerate(self.algorithms):
                # Afficher la progression
                self.screen.fill(BG_COLOR)
                progress_text = self.font.render(f"Test: {self.algorithm_names[i]} - Taille: {size}", True, TEXT_COLOR)
                self.screen.blit(progress_text, (WIDTH // 2 - progress_text.get_width() // 2, HEIGHT // 2))
                pygame.display.flip()
                
                self.numbers = test_numbers.copy()
                self.measure_performance(algorithm, self.algorithm_names[i], False)
                
                # Gérer les événements pour éviter que l'application ne semble bloquée
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
        
        # Restaurer la taille et les données originales
        self.element_count = original_count
        self.numbers = original_numbers
        
        # Régénérer le graphique avec les nouvelles données
        self.graph_surface = None
        self.generate_performance_graph()
        
        # Afficher le graphique
        self.display_graph()
    def reset_performance_data(self):
        """Réinitialise toutes les données de performance pour le graphique"""
        self.performance_data = {name: {'sizes': [], 'times': []} for name in self.algorithm_names}
        self.graph_surface = None  # Forcer la régénération du graphique
    
        # Afficher un message de confirmation
        self.screen.fill(BG_COLOR)
        message = self.font.render("Les données du graphique ont été réinitialisées!", True, TEXT_COLOR)
        self.screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(1000)  # Afficher le message pendant 1 seconde

    def display_graph(self):
        running = True
        self.showing_graph = True
        
        # Générer le graphique si ce n'est pas déjà fait
        if self.graph_surface is None:
            self.generate_performance_graph()
        
        while running:
            self.screen.fill(BG_COLOR)
            
            # Calculer la position pour centrer le graphique
            graph_rect = self.graph_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            
            # Afficher le graphique
            self.screen.blit(self.graph_surface, graph_rect)
            
            # Bouton retour
            mouse_pos = pygame.mouse.get_pos()
            color = BUTTON_HOVER_COLOR if self.return_button.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, self.return_button)
            text = self.font.render("Retour au menu", True, TEXT_COLOR)
            self.screen.blit(text, (self.return_button.x + 25, self.return_button.y + 10))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.return_button.collidepoint(event.pos):
                        running = False
                        self.showing_graph = False
                        
            self.clock.tick(60)

    def update_element_count(self):
        try:
            new_count = int(self.element_input_text)
            if new_count > 0:
                self.element_count = new_count
                self.generate_numbers()
        except ValueError:
            # Réinitialiser le texte à la valeur actuelle si la conversion échoue
            self.element_input_text = str(self.element_count)

    def run(self):
        running = True
        show_menu = True

        while running:
            if show_menu:
                self.draw_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Vérifier si la zone de saisie est cliquée
                        if self.element_input_rect.collidepoint(event.pos):
                            self.element_input_active = True

                        # Vérifier le bouton "Réinitialiser graphique"
                        if self.reset_graph_button.collidepoint(event.pos):
                            self.reset_performance_data()    
                        else:
                            if self.element_input_active:
                                self.element_input_active = False
                                self.update_element_count()
                            
                        # Vérifier les boutons des algorithmes individuels
                        for i, (rect, _) in enumerate(self.buttons):
                            if rect.collidepoint(event.pos):
                                self.generate_numbers()  # Générer un nouveau jeu de nombres
                                self.showing_results = False  # S'assurer que nous sommes en mode animation
                                execution_time = self.measure_performance(
                                    self.algorithms[i], 
                                    self.algorithm_names[i], 
                                    True
                                )
                                show_menu = False
                                break
                        
                        # Vérifier le bouton "Lancer tous les tris"
                        if self.run_all_button.collidepoint(event.pos):
                            self.generate_numbers()  # Générer un nouveau jeu de nombres
                            self.run_all_algorithms()
                        
                        # Vérifier le bouton "Graphique de performance"
                        if self.graph_button.collidepoint(event.pos):
                            self.display_graph()
                            
                        # Vérifier le bouton "Lancer les benchmarks"
                        if self.benchmark_button.collidepoint(event.pos):
                            self.run_benchmark_tests()
                    
                    elif event.type == pygame.KEYDOWN:
                        if self.element_input_active:
                            if event.key == pygame.K_RETURN:
                                self.element_input_active = False
                                self.update_element_count()
                            elif event.key == pygame.K_BACKSPACE:
                                self.element_input_text = self.element_input_text[:-1]
                            else:
                                # N'accepter que les chiffres
                                if event.unicode.isdigit():
                                    self.element_input_text += event.unicode
            else:
                self.draw_return_button()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.return_button.collidepoint(event.pos):
                            show_menu = True
            
            self.clock.tick(60)

        pygame.quit()