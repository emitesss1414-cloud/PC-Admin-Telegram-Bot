import psutil
import matplotlib.pyplot as plt
import os
import sys
import tempfile


def generate_performance_graphs() -> list[str]:
    """
    Создает графики производительности для CPU, RAM и диска.
    Возвращает список путей к сохраненным файлам изображений.
    """
    graph_paths = []

    # Prefer a writable 'graphs' folder next to the project source when running from source.
    # If that location is not writable (for example, when running a onefile PyInstaller exe),
    # fall back to the system temp directory.
    project_graph_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphs'))
    graph_dir = project_graph_dir
    try:
        os.makedirs(graph_dir, exist_ok=True)
        # ensure we can write there
        testfile = os.path.join(graph_dir, '.write_test')
        with open(testfile, 'w'):
            pass
        os.remove(testfile)
    except Exception:
        # fallback to a temp folder specific to this app
        graph_dir = os.path.join(tempfile.gettempdir(), 'pc_admin_bot_graphs')
        os.makedirs(graph_dir, exist_ok=True)

    # --- График CPU (частоты в MHz) ---
    try:
        plt.figure(figsize=(10, 6))
        freqs = psutil.cpu_freq(percpu=True)
        # cpu_freq может вернуть None для некоторых виртуальных сред, обработаем это
        if freqs and all(f is not None for f in freqs):
            cpu_mhz = [f.current for f in freqs]
            cores = [f'Core {i+1}' for i in range(len(cpu_mhz))]
            bars = plt.bar(cores, cpu_mhz, color='skyblue')
            plt.ylabel('Частота, MHz')
            plt.title('Текущая частота ядер CPU')
            for bar, val in zip(bars, cpu_mhz):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{val:.0f}', ha='center', va='bottom')
        else:
            # fallback: используем среднюю загрузку в процентах, но подписываем числа
            cpu_percent = psutil.cpu_percent(percpu=True, interval=1)
            cores = [f'Core {i+1}' for i in range(len(cpu_percent))]
            bars = plt.bar(cores, cpu_percent, color='skyblue')
            plt.ylabel('Загрузка, %')
            plt.title('Загрузка ядер CPU (fallback)')
            for bar, val in zip(bars, cpu_percent):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{val:.0f}%', ha='center', va='bottom')

        cpu_path = os.path.join(graph_dir, 'cpu_usage.png')
        plt.savefig(cpu_path)
        graph_paths.append(cpu_path)
        plt.clf()
    except Exception as e:
        print(f"Ошибка при создании графика CPU: {e}")

    # --- График RAM (числа в MB) ---
    try:
        plt.figure(figsize=(8, 6))
        ram = psutil.virtual_memory()
        used_mb = ram.used / (1024**2)
        free_mb = ram.available / (1024**2)
        labels = ['Использовано MB', 'Доступно MB']
        values = [used_mb, free_mb]
        bars = plt.bar(labels, values, color=['lightcoral', 'lightgreen'])
        plt.ylabel('МБ')
        plt.title(f'Использование RAM (Всего: {ram.total / (1024**2):.0f} MB)')
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{val:.0f}', ha='center', va='bottom')
        ram_path = os.path.join(graph_dir, 'ram_usage.png')
        plt.savefig(ram_path)
        graph_paths.append(ram_path)
        plt.clf()
    except Exception as e:
        print(f"Ошибка при создании графика RAM: {e}")

    # --- График диска (числа в GB) ---
    try:
        plt.figure(figsize=(8, 6))
        disk = psutil.disk_usage('/')
        used_gb = disk.used / (1024**3)
        free_gb = disk.free / (1024**3)
        labels = ['Использовано GB', 'Свободно GB']
        values = [used_gb, free_gb]
        bars = plt.bar(labels, values, color=['gold', 'lightskyblue'])
        plt.ylabel('GB')
        plt.title(f'Использование диска (Всего: {disk.total / (1024**3):.2f} GB)')
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{val:.2f}', ha='center', va='bottom')
        disk_path = os.path.join(graph_dir, 'disk_usage.png')
        plt.savefig(disk_path)
        graph_paths.append(disk_path)
        plt.clf()
    except Exception as e:
        print(f"Ошибка при создании графика диска: {e}")
    
    plt.close('all') # Закрываем все фигуры, чтобы освободить память
    return graph_paths
