
import pygame, sys, random, time
import professor_algos as p_algos  # Import the professor’s algorithms for timing

###############################################################################
# Helper function to format array display (shows only the first few elements)
###############################################################################
def format_array(arr, max_elements=30):
    if len(arr) > max_elements:
        first_part = arr[:max_elements//2]
        last_part = arr[-max_elements//2:]
        return f"[{', '.join(map(str, first_part))} ... {', '.join(map(str, last_part))}]"
    return str(arr)

###############################################################################
# Helper function to truncate text so that it fits within a maximum width.
###############################################################################
def truncate_text(text, font, max_width):
    if font.size(text)[0] <= max_width:
        return text
    else:
        ellipsis = "..."
        max_width_ellipsis = font.size(ellipsis)[0]
        new_text = text
        while font.size(new_text)[0] > max_width - max_width_ellipsis and len(new_text) > 0:
            new_text = new_text[:-1]
        return new_text + ellipsis

###############################################################################
# UI CLASSES (based on SortVisual)
###############################################################################
class InputBox:
    def __init__(self, x, y, w, h, text='', font_size=28):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightgray')
        self.color_active   = pygame.Color('white')
        self.color = self.color_inactive
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)
        return None

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Button:
    def __init__(self, x, y, w, h, text, font_size=28):
        self.rect = pygame.Rect(x, y, w, h)
        self.bg_color = (100, 100, 100)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.txt_surface = self.font.render(text, True, pygame.Color('white'))
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)

class Checkbox:
    def __init__(self, x, y, text, font_size=24):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.txt_surface = self.font.render(text, True, pygame.Color('white'))
        self.checked = False

    def draw(self, screen):
        pygame.draw.rect(screen, pygame.Color('white'), self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, pygame.Color('white'),
                             (self.rect.x + 4, self.rect.y + 10),
                             (self.rect.x + 8, self.rect.y + 15), 2)
            pygame.draw.line(screen, pygame.Color('white'),
                             (self.rect.x + 8, self.rect.y + 15),
                             (self.rect.x + 16, self.rect.y + 5), 2)
        screen.blit(self.txt_surface, (self.rect.x + 30, self.rect.y))

###############################################################################
# SORTING ALGORITHMS (generator versions used for animation)
###############################################################################
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
                yield arr.copy()
        if not swapped:
            break
    yield arr.copy()

def merge_sort(arr):
    def merge(arr, start, mid, end):
        left, right = arr[start:mid], arr[mid:end]
        i = j = 0
        k = start
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
            yield arr.copy()
        while i < len(left):
            arr[k] = left[i]
            i += 1; k += 1
            yield arr.copy()
        while j < len(right):
            arr[k] = right[j]
            j += 1; k += 1
            yield arr.copy()

    def merge_sort_recursive(arr, start, end):
        if end - start > 1:
            mid = (start + end) // 2
            yield from merge_sort_recursive(arr, start, mid)
            yield from merge_sort_recursive(arr, mid, end)
            yield from merge(arr, start, mid, end)
        yield arr.copy()

    yield from merge_sort_recursive(arr, 0, len(arr))

def quick_sort(arr):
    def partition(arr, low, high):
        states = []
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                states.append(arr.copy())
        arr[i+1], arr[high] = arr[high], arr[i+1]
        states.append(arr.copy())
        return i+1, states

    def quick_sort_recursive(arr, low, high):
        if low < high:
            pivot_index, states = partition(arr, low, high)
            for state in states:
                yield state
            yield from quick_sort_recursive(arr, low, pivot_index-1)
            yield from quick_sort_recursive(arr, pivot_index+1, high)
        yield arr.copy()

    if len(arr) <= 1:
        yield arr.copy()
    else:
        yield from quick_sort_recursive(arr, 0, len(arr)-1)

def radix_sort(arr):
    def counting_sort(arr, exp):
        n = len(arr)
        output = [0] * n
        count = [0] * 10
        for i in range(n):
            index = (arr[i] // exp) % 10
            count[index] += 1
        for i in range(1, 10):
            count[i] += count[i-1]
        for i in range(n-1, -1, -1):
            index = (arr[i] // exp) % 10
            output[count[index]-1] = arr[i]
            count[index] -= 1
        for i in range(n):
            arr[i] = output[i]
            yield arr.copy()
    if not arr:
        yield arr.copy()
        return
    max_num = max(arr)
    exp = 1
    while max_num // exp > 0:
        yield from counting_sort(arr, exp)
        exp *= 10
    yield arr.copy()

# For Linear Search, the global target_value is used.
target_value = 50
def linear_search(arr):
    global target_value
    for i in range(len(arr)):
        yield arr.copy()
        if arr[i] == target_value:
            yield arr.copy()
    yield arr.copy()

# Dictionary mapping algorithm names to generator functions (for visualization).
algo_dict = {
    "Bubble Sort": bubble_sort,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Radix Sort": radix_sort,
    "Linear Search": linear_search
}

###############################################################################
# PERFORMANCE MEASUREMENT & GRAPH DRAWING – Using the professor’s algorithms
###############################################################################
# Create a dictionary mapping algorithm names to the professor’s pure functions.
perf_algo_dict = {
    "Bubble Sort": p_algos.bubble_sort,
    "Merge Sort": p_algos.merge_sort,
    "Quick Sort": p_algos.quick_sort,
    "Radix Sort": p_algos.lsd_radix_sort,
    "Linear Search": p_algos.linear_search_all
}

def measure_performance(arr):
    # Time the sorting algorithms from the professor module.
    perf = {}
    runs = 5  # Number of runs for averaging
    for name, func in perf_algo_dict.items():
        if name == "Linear Search":
            continue
        total_time = 0
        for _ in range(runs):
            arr_copy = arr.copy()
            start_time = time.perf_counter()
            func(arr_copy)  # Run the pure function to completion.
            total_time += time.perf_counter() - start_time
        perf[name] = total_time / runs
    return perf

def measure_linear_search_performance(arr):
    # Time the professor’s linear search.
    perf = {}
    runs = 5
    total_time = 0
    for _ in range(runs):
        arr_copy = arr.copy()
        start_time = time.perf_counter()
        p_algos.linear_search_all(arr_copy, target_value)
        total_time += time.perf_counter() - start_time
    perf["Linear Search"] = total_time / runs
    return perf

def draw_performance_graph(screen, graph_rect, performance, font, is_linear_search=False, animation_percent=100):
    if not performance: 
        return
    pygame.draw.rect(screen, (40, 40, 40), graph_rect)
    title_font = pygame.font.Font(None, 24)
    title = title_font.render("Algorithm Performance (milliseconds)", True, (255, 255, 255))
    title_x = graph_rect.x + (graph_rect.width - title.get_width()) // 2
    screen.blit(title, (title_x, graph_rect.y + 5))
    
    if is_linear_search:
        name = "Linear Search"
        t = performance.get(name, 0)
        t_ms = t * 1000
        bar_width = graph_rect.width - 20
        bar_height = min((graph_rect.height - 50) * 0.9, (graph_rect.height - 50))
        animated_height = bar_height * (animation_percent / 100.0)
        bar_x = graph_rect.x + 10
        bar_y = graph_rect.y + graph_rect.height - animated_height - 20
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, animated_height))
        name_surf = font.render(name, True, (255, 255, 255))
        time_surf = font.render(f"{t_ms:.3f} ms", True, (255, 255, 255))
        screen.blit(name_surf, (bar_x, bar_y - name_surf.get_height() - 2))
        screen.blit(time_surf, (bar_x + (bar_width - time_surf.get_width()) // 2, bar_y + animated_height + 2))
    else:
        bar_count = len(performance)
        bar_width = (graph_rect.width - 20) / bar_count
        max_time = max(performance.values()) if performance else 1
        scale_font = pygame.font.Font(None, 20)
        max_ms = max_time * 1000
        pygame.draw.line(screen, (150, 150, 150), 
                         (graph_rect.x + 5, graph_rect.y + 25), 
                         (graph_rect.x + 5, graph_rect.y + graph_rect.height - 20), 1)
        scale_surf = scale_font.render(f"{max_ms:.2f}", True, (200, 200, 200))
        screen.blit(scale_surf, (graph_rect.x + 7, graph_rect.y + 25))
        scale_surf = scale_font.render("0.00", True, (200, 200, 200))
        screen.blit(scale_surf, (graph_rect.x + 7, graph_rect.y + graph_rect.height - 25))
        i = 0
        for name, t in performance.items():
            t_ms = t * 1000
            bar_height = (t / max_time) * (graph_rect.height - 50)
            animated_height = bar_height * (animation_percent / 100.0)
            bar_x = graph_rect.x + 25 + i * bar_width
            bar_y = graph_rect.y + graph_rect.height - animated_height - 20
            bar_rect = pygame.Rect(bar_x, bar_y, bar_width - 5, animated_height)
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            pygame.draw.rect(screen, colors[i % len(colors)], bar_rect)
            name_surf = scale_font.render(name.split()[0], True, (255, 255, 255))
            name_x = bar_x + (bar_width - 5 - name_surf.get_width()) // 2
            screen.blit(name_surf, (name_x, bar_y - name_surf.get_height() - 2))
            time_surf = scale_font.render(f"{t_ms:.3f}", True, (255, 255, 255))
            time_x = bar_x + (bar_width - 5 - time_surf.get_width()) // 2
            screen.blit(time_surf, (time_x, bar_y + animated_height + 2))
            i += 1

###############################################################################
# MAIN FUNCTION (UI + Visualization + Control Panel + Performance Graph)
###############################################################################
def main():
    pygame.init()
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Rocket Fuel Sorting Visualizer")

    panel_width = 427                    
    panel_start_x = width - panel_width   
    vis_rect = pygame.Rect(0, 30, panel_start_x, height - 30)
    header_rect = pygame.Rect(0, 0, panel_start_x, 30)

    black      = (0, 0, 0)
    deep_gray  = (50, 50, 50)
    header_col = (113, 115, 120)
    text_color = (255, 255, 255)
    bar_color  = (0, 150, 255)
    highlight_color = (0, 255, 0)
    title_font   = pygame.font.Font(None, 32)
    regular_font = pygame.font.Font(None, 24)
    small_font   = pygame.font.Font(None, 20)

    content_start_x = panel_start_x + 15  
    curr_array_y            = 5           
    step1_title_y           = 35
    manual_input_label_y    = 60
    numbers_input_y         = 85
    or_label_y              = 115
    random_label_y          = 135
    random_input_y          = 160
    button_row_y            = 195
    step2_title_y           = 240
    algorithm_instr_y       = 265
    checkbox_start_y        = 290   
    target_label_y          = 400
    target_input_y          = 425
    step3_title_y           = 460
    chosen_algo_y           = 485
    launch_button_y         = 515  
    performance_graph_y     = 565  
    performance_graph_height= 145  

    numbers_input = InputBox(content_start_x, numbers_input_y, panel_width - 30, 25, font_size=24)
    random_size_input = InputBox(content_start_x, random_input_y, 140, 25, font_size=24)
    target_input = InputBox(content_start_x, target_input_y, 140, 25, font_size=24)

    button_width = (panel_width - 60) // 3  
    enter_button = Button(content_start_x, button_row_y, button_width, 35, "ENTER", font_size=24)
    pause_button = Button(content_start_x + button_width + 10, button_row_y, button_width, 35, "PAUSE", font_size=24)
    reset_button = Button(content_start_x + 2 * (button_width + 10), button_row_y, button_width, 35, "RESET", font_size=24)
    launch_button = Button(content_start_x, launch_button_y, panel_width - 30, 35, "LAUNCH ROCKET", font_size=24)

    algo_names = ["Bubble Sort", "Merge Sort", "Quick Sort", "Radix Sort", "Linear Search"]
    checkboxes = []
    for i, name in enumerate(algo_names):
        cb = Checkbox(content_start_x, checkbox_start_y + i * 20, name, font_size=22)
        checkboxes.append(cb)

    arr = [random.randint(1, 100) for _ in range(20)]
    original_arr = arr.copy()

    sorting = False
    current_step = None
    sort_completed = False
    performance = {}
    sorting_start_time = None
    visual_timing = None
    animation_percent = 0

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            numbers_input.handle_event(event)
            random_size_input.handle_event(event)
            if any(cb.checked and cb.text == "Linear Search" for cb in checkboxes):
                target_input.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for cb in checkboxes:
                    if cb.rect.collidepoint(event.pos):
                        for other in checkboxes:
                            other.checked = False
                        cb.checked = True

                if enter_button.rect.collidepoint(event.pos):
                    if numbers_input.text.strip():
                        try:
                            lst = [int(x.strip()) for x in numbers_input.text.split(',') if x.strip()]
                            if lst:
                                arr = lst.copy()
                                original_arr = lst.copy()
                                sort_completed = False
                            else:
                                print("No valid numbers found.")
                        except ValueError:
                            print("Invalid input: Use comma-separated integers")
                    elif random_size_input.text.strip():
                        try:
                            size = int(random_size_input.text)
                            if size > 0:
                                arr = [random.randint(1, 100) for _ in range(min(size, 100))]
                                original_arr = arr.copy()
                                sort_completed = False
                            else:
                                print("Enter a positive number for size")
                        except ValueError:
                            print("Invalid size input")
                    numbers_input.text = ""
                    numbers_input.txt_surface = numbers_input.font.render("", True, numbers_input.color)
                    random_size_input.text = ""
                    random_size_input.txt_surface = random_size_input.font.render("", True, random_size_input.color)

                elif pause_button.rect.collidepoint(event.pos):
                    sorting = not sorting

                elif reset_button.rect.collidepoint(event.pos):
                    numbers_input.text = ""
                    numbers_input.txt_surface = numbers_input.font.render("", True, numbers_input.color)
                    random_size_input.text = ""
                    random_size_input.txt_surface = random_size_input.font.render("", True, random_size_input.color)
                    target_input.text = ""
                    target_input.txt_surface = target_input.font.render("", True, target_input.color)
                    for cb in checkboxes:
                        cb.checked = False
                    arr = original_arr.copy()
                    sorting = False
                    current_step = None
                    sort_completed = False
                    performance = {}
                    visual_timing = None
                    animation_percent = 0

                elif launch_button.rect.collidepoint(event.pos):
                    selected_algo = None
                    for cb in checkboxes:
                        if cb.checked:
                            selected_algo = cb.text
                            break
                    if selected_algo is None:
                        print("No algorithm selected!")
                    else:
                        if selected_algo == "Linear Search":
                            if target_input.text.strip():
                                try:
                                    new_target = int(target_input.text)
                                    globals()['target_value'] = new_target
                                except ValueError:
                                    print("Invalid target value – using previous value")
                            target_input.text = ""
                            target_input.txt_surface = target_input.font.render("", True, target_input.color)
                            performance = measure_linear_search_performance(original_arr)
                        else:
                            performance = measure_performance(original_arr)
                            
                        arr = original_arr.copy()
                        current_step = algo_dict[selected_algo](arr.copy())
                        sorting = True
                        sort_completed = False
                        sorting_start_time = time.perf_counter()
                        visual_timing = None
                        animation_percent = 0
        
        if sorting:
            try:
                arr = next(current_step).copy()
            except StopIteration:
                sorting = False
                sort_completed = True
                if sorting_start_time is not None:
                    visual_timing = time.perf_counter() - sorting_start_time
                    sorting_start_time = None

        screen.fill(black)
        pygame.draw.rect(screen, header_col, header_rect)
        array_str = format_array(arr)
        truncated_array = truncate_text(array_str, title_font, header_rect.width - 20)
        array_surface = title_font.render(truncated_array, True, text_color)
        screen.blit(array_surface, (header_rect.x + 10, header_rect.y + (header_rect.height - array_surface.get_height()) // 2))
        
        pygame.draw.rect(screen, black, vis_rect)
        if arr:
            max_val = max(arr)
            if max_val == 0:
                max_val = 1
            bar_width = vis_rect.width / len(arr)
            for i, value in enumerate(arr):
                if any(cb.checked and cb.text == "Linear Search" for cb in checkboxes) and value == target_value:
                    color = highlight_color
                else:
                    color = bar_color
                bar_height = (value / max_val) * (vis_rect.height - 10)
                x = vis_rect.x + i * bar_width
                y = vis_rect.y + vis_rect.height - bar_height
                pygame.draw.rect(screen, color, (x, y, bar_width - 1, bar_height))

        pygame.draw.rect(screen, deep_gray, (panel_start_x, 0, panel_width, height))
        header_right = title_font.render("Sorting Visualization", True, text_color)
        screen.blit(header_right, (panel_start_x + (panel_width - header_right.get_width()) // 2, curr_array_y))
        
        step1_txt = title_font.render("Step 1:", True, text_color)
        screen.blit(step1_txt, (content_start_x, step1_title_y))
        manual_txt = regular_font.render("Enter comma separated Numbers:", True, text_color)
        screen.blit(manual_txt, (content_start_x, manual_input_label_y))
        numbers_input.draw(screen)
        or_txt = regular_font.render("Or", True, text_color)
        screen.blit(or_txt, (content_start_x + 160, or_label_y))
        random_txt = regular_font.render("Generate Random (Enter size):", True, text_color)
        screen.blit(random_txt, (content_start_x, random_label_y))
        random_size_input.draw(screen)
        enter_button.draw(screen)
        pause_button.draw(screen)
        reset_button.draw(screen)

        step2_txt = title_font.render("Step 2:", True, text_color)
        screen.blit(step2_txt, (content_start_x, step2_title_y))
        algo_instr = regular_font.render("Pick sorting Algorithm:", True, text_color)
        screen.blit(algo_instr, (content_start_x, algorithm_instr_y))
        for cb in checkboxes:
            cb.draw(screen)
        if any(cb.checked and cb.text == "Linear Search" for cb in checkboxes):
            target_label = regular_font.render("Pick target value:", True, text_color)
            screen.blit(target_label, (content_start_x, target_label_y))
            target_input.draw(screen)

        step3_txt = title_font.render("Step 3:", True, text_color)
        screen.blit(step3_txt, (content_start_x, step3_title_y))
        selected_algo = next((cb.text for cb in checkboxes if cb.checked), None)
        if selected_algo:
            choose_txt = regular_font.render("You choose: " + selected_algo, True, text_color)
            screen.blit(choose_txt, (content_start_x, chosen_algo_y))
        launch_button.draw(screen)

        perf_graph_rect = pygame.Rect(content_start_x, performance_graph_y, panel_width - 30, performance_graph_height)
        is_linear_search = any(cb.checked and cb.text == "Linear Search" for cb in checkboxes)
        
        if sort_completed and animation_percent < 100:
            animation_percent += 2
        
        draw_performance_graph(screen, perf_graph_rect, performance, small_font, is_linear_search, animation_percent)
        
        if sorting and current_step is not None and animation_percent > 0:
            animation_percent = 0
         
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
