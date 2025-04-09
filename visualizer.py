import pygame
import random
import time
import json
import os
from sorting_algorithms import SortingAlgorithms
import tracemalloc

WIDTH, HEIGHT = 800, 600
BAR_WIDTH = 5
BAR_COLOR = (0, 102, 204)
BG_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (150, 150, 150)
TEXT_COLOR = (0, 0, 0)

class SortVisualizer:
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0
        self.execution_time = 0
        self.start_ticks = 0
        self.is_sorting = False
        self.memory_usage = 0
        self.peak_memory = 0
        self.results_history = self.load_history()
        self.current_results = {}
        
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
        self.stats_button = pygame.Rect(350, 130, 200, 40)
        
        self.numbers = []
        self.generate_numbers()
        self.create_buttons()
        
        self.show_stats = False
        self.showing_results = False

    def load_history(self):
        """Charge l'historique des résultats depuis un fichier JSON"""
        if os.path.exists('sort_history.json'):
            try:
                with open('sort_history.json', 'r') as f:
                    return json.load(f)
            except:
                return {name: {"times": [], "memory": []} for name in [
                    "Selection Sort", "Bubble Sort", "Insertion Sort", 
                    "Merge Sort", "Quick Sort", "Heap Sort", "Comb Sort"
                ]}
        else:
            return {name: {"times": [], "memory": []} for name in [
                "Selection Sort", "Bubble Sort", "Insertion Sort", 
                "Merge Sort", "Quick Sort", "Heap Sort", "Comb Sort"
            ]}
    
    def save_history(self):
        """Sauvegarde l'historique des résultats dans un fichier JSON"""
        with open('sort_history.json', 'w') as f:
            json.dump(self.results_history, f)

    def generate_numbers(self):
        self.numbers = [random.randint(1, HEIGHT - 100) for _ in range(WIDTH // BAR_WIDTH)]

    def create_buttons(self):
        self.buttons = []
        for i, name in enumerate(self.algorithm_names):
            rect = pygame.Rect(100, 70 + 40 * i, 200, 30)
            self.buttons.append((rect, name))

    def draw_bars(self, highlighted_indices=None):
        self.screen.fill(BG_COLOR)
        highlighted_indices = highlighted_indices or []
        for i, value in enumerate(self.numbers):
            x = i * BAR_WIDTH
            color = SELECTED_COLOR if i in highlighted_indices else BAR_COLOR
            pygame.draw.rect(self.screen, color, (x, HEIGHT - value, BAR_WIDTH, value))

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
        
        # Bouton pour afficher les statistiques
        color = BUTTON_HOVER_COLOR if self.stats_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.stats_button)
        text = self.font.render("Statistiques / Moyennes", True, TEXT_COLOR)
        self.screen.blit(text, (self.stats_button.x + 10, self.stats_button.y + 10))

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
        if not self.showing_results:
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
            
            # Ajouter à l'historique
            self.results_history[algorithm_name]["times"].append(self.execution_time)
            self.results_history[algorithm_name]["memory"].append(self.peak_memory)
            
            # Sauvegarder l'historique
            self.save_history()

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

    def display_statistics(self):
        running = True
        
        while running:
            self.screen.fill(BG_COLOR)
            
            # Titre
            title = self.font.render("Statistiques moyennes", True, TEXT_COLOR)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
            
            # Calculer et afficher les moyennes
            headers = self.small_font.render("Algorithme                 Temps moyen (s)        Mémoire moyenne (KB)", True, TEXT_COLOR)
            self.screen.blit(headers, (100, 70))
            
            pygame.draw.line(self.screen, TEXT_COLOR, (100, 90), (700, 90), 1)
            
            y_pos = 110
            for i, name in enumerate(self.algorithm_names):
                times = self.results_history[name]["times"]
                memory = self.results_history[name]["memory"]
                
                avg_time = sum(times) / len(times) if times else 0
                avg_memory = sum(memory) / len(memory) if memory else 0
                
                # Formater les moyennes
                stats_text = self.small_font.render(
                    f"{name.ljust(25)} {avg_time:.6f}               {avg_memory:.2f}", 
                    True, TEXT_COLOR
                )
                self.screen.blit(stats_text, (100, y_pos))
                
                # Afficher le nombre d'essais
                trials_text = self.small_font.render(f"({len(times)} essais)", True, TEXT_COLOR)
                self.screen.blit(trials_text, (650, y_pos))
                
                y_pos += 30
            
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
                        
            self.clock.tick(60)

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
                        
                        # Vérifier le bouton "Statistiques"
                        if self.stats_button.collidepoint(event.pos):
                            self.display_statistics()
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