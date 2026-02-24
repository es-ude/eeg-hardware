# 8-Channel EEG System

This repository contains the complete design and source files for a custom **8-Channel EEG System** (Electroencephalography) based on the Raspberry Pi Pico (RP2350A) and the Analog Devices AD7779 24-bit ADC.

The project is modular and covers the entire signal chain: from physical schematics and microcontroller firmware to data acquisition and visualization on the PC.

## Project Structure

The repository is organized into three main sections:

- **[`0_hardware/`](0_hardware/)**: KiCad projects for schematics and PCB layouts.
- **[`1_firmware/`](1_firmware/)**: C source code to be flashed onto the hardware.
- **[`2_pc_datahandler/`](2_pc_datahandler/)**: Python framework for control, data acquisition (LSL/HDF5), live plotting, and analysis.

---

## 0_Hardware

The hardware folder contains all electronic design files (KiCad).

**Key Components:**
*   **MCU:** Custom desgin based on the **RP2350A**.
*   **ADC:** [AD7779](https://www.analog.com/en/products/ad7779.html) (8-Channel, 24-Bit Sigma-Delta ADC).
*   **Signal Conditioning:** Variable gain settings via digital potentiometers (AD5142A).
*   **Modules:** Separate schematics for power management, impedance measurement, sensor interfaces, and active shielding reference.

---

## 1_Firmware

The firmware runs on the RP2350A and handles SPI communication with the ADC, I2C communication with digital potentiometers, and high-speed data transfer to the PC via USB.

**Features:**
*   **Sampling Rate:** Configurable sampling rate for the AD7779.
*   **Drivers:** Implemented for AD7779 (SPI), AD5142A (I2C), and GPIO shielding control.
*   **Protocol:** USB packet protocol with header/footer framing.
*   **Synchronization:** Microsecond-precision timestamping for every data packet.

**Build Instructions:**
Prerequisites: [Pico SDK](https://github.com/raspberrypi/pico-sdk) and CMake.

---

## 2_PC_DataHandler

This folder contains the Python-based host software to interface with the EEG hardware. It manages the USB connection, decodes the raw data stream, and integrates with the Lab Streaming Layer (LSL) ecosystem.

**Features:**
*   **Data Acquisition:** Reading from the USB serial port.
*   **LSL Integration:** Streams data as an 8-channel EEG signal onto the local network for use with tools like LabRecorder or our live plotter.
*   **Visualization:** Real-time plotting of time-series data.
*   **Analysis:** Signal quality verification.

**This project uses [`uv`](https://github.com/astral-sh/uv) for fast and reliable dependency management.**

Create a virtual environment and sync dependencies:
    ```bash
    uv sync
    ```