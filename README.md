# BitWhisper PoC: Thermal Exfiltration & Covert Channels

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Hardware](https://img.shields.io/badge/Hardware-NVIDIA_RTX_2060-green.svg)
![Security](https://img.shields.io/badge/Security-Red_Teaming-red.svg)

## 🌡️ Project Overview
This project is a **Proof of Concept (PoC)** for a thermal-based covert channel, inspired by research from Ben-Gurion University. It demonstrates how sensitive data (captured via a keylogger) can be exfiltrated from an air-gapped system by modulating hardware temperature through controlled CPU and GPU stress cycles.

Developed as a research project at **Warsaw University of Technology**.

## ⚙️ How It Works
The application establishes a "Thermal Bridge" using binary modulation:

1.  **Data Acquisition**: A background `Keylogger` thread captures keystrokes and converts them into an 8-bit binary ASCII stream.
2.  **Persistence**: The script ensures survivability by adding itself to the Windows Registry (`CurrentVersion\Run`) via the `winreg` module.
3.  **Thermal Modulation (The Bridge)**:
    * **Bit '1' (HEAT)**: Triggers a **90-second Stress Cycle**. It utilizes `multiprocessing` to max out CPU cores and `PyTorch (CUDA)` to engage GPU tensor cores for maximum thermal output.
    * **Bit '0' (COOL)**: Triggers a **90-second Cooling Cycle** (system idle) to allow temperature dissipation.
4.  **Real-time Processing**: Data is processed bit-by-bit in real-time, with 30-second guard intervals to ensure signal distinctness for the receiving thermal sensors.

## 🛠️ Technical Stack
* **Parallelism**: `multiprocessing` for concurrent CPU load and `threading` for non-blocking I/O.
* **GPU Acceleration**: `PyTorch` & `CUDA` implementing intensive matrix multiplications (`torch.matmul`) and batch normalization to stress NVIDIA silicon.
* **Low-Level Windows API**: `winreg` for persistence and `tempfile` for stealthy local logging.
* **Event Handling**: `pynput` for hardware-level keyboard event interception.

## 📂 Code Structure
* `Keylogger Class`: Handles stealthy logging, registry manipulation, and ASCII-to-binary conversion logic.
* `stress_cpu_hard()`: High-intensity mathematical workloads involving square roots, factorials, and trigonometry.
* `stress_gpu_nvidia()`: Heavy tensor operations designed to maximize power draw and heat on CUDA-enabled devices.
* `process_bit_immediately()`: The bridge controller responsible for the hardware "thermal heartbeat" based on the bitstream.

## ⚠️ Disclaimer
This software is provided for **educational and research purposes only**. Unauthorized use of this tool against systems without explicit permission is illegal. The authors are not responsible for any hardware damage resulting from prolonged stress testing.

## 📝 Authors
* **Michał Orliński** 
* **Jakub Pokorski**
* **Kacper Pietnoczka**
* **Krzysztof Biegaj**
