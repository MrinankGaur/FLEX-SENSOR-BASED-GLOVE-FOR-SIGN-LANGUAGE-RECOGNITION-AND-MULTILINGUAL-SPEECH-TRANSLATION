import serial
import csv
import time
import os

print("--- Script started ---")  # DEBUG LINE

# --- 1. Configuration ---
SERIAL_PORT = 'COM6'
BAUD_RATE = 115200

# --- 2. Script Parameters ---
DATA_POINTS_PER_LINE = 11
LINES_PER_FILE = 120
OUTPUT_DIR = "C:\\mrinank\\COLLEGE\\PROJECT 1\\DATA_AQUISITION"  # Directory to save CSV files


# --- Column names for CSV ---
COLUMN_NAMES = [
    "flex_1", "flex_2", "flex_3", "flex_4", "flex_5",
    "GYRx", "GYRy", "GYRz",
    "ACCx", "ACCy", "ACCz"
]


# --- 3. Main Data Logging Logic ---
def start_data_logger():
    print("--- start_data_logger() function entered ---")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    file_counter = 1

    try:
        print(f"--- Attempting to open {SERIAL_PORT}... ---")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"--- Port opened successfully! ---")
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")
        print("Press Ctrl+C to stop.\n")

        # Print placeholder initial value
        print("Initial (no data yet): " + ",".join(["0"] * DATA_POINTS_PER_LINE))

        data_buffer = []
        start_time = time.monotonic()
        last_wait_msg = 0.0
        first_data_seen = False

        while True:
            line = ser.readline()  # returns b'' if timeout occurs

            if not line:
                # Print waiting message every second until data arrives
                now = time.monotonic()
                if not first_data_seen and now - last_wait_msg >= 1:
                    elapsed = int(now - start_time)
                    print(f"Waiting for data from {SERIAL_PORT}... {elapsed}s")
                    last_wait_msg = now
                continue

            try:
                line_str = line.decode('utf-8', errors='ignore').strip()
                if not line_str:
                    continue

                data_points = line_str.split(',')

                # Print first valid line once
                if not first_data_seen and len(data_points) == DATA_POINTS_PER_LINE:
                    print(f"\nFirst line from ESP: {line_str}")
                    first_data_seen = True

                # Ignore resting hand data
                if (float(data_points[8]) > -10 and float(data_points[8]) < -6):
                    print(f"Hand in resting position '{line_str}'")
                    continue

                # Append valid data to buffer
                if len(data_points) == DATA_POINTS_PER_LINE:
                    data_buffer.append(data_points)
                else:
                    print(f"Warning: Received malformed line: '{line_str}'")

                # Save buffer to CSV when full
                if len(data_buffer) == LINES_PER_FILE:
                    print(f"\nBuffer full. Saving {LINES_PER_FILE} lines...")
                    filename = f"data.csv"
                    filepath = os.path.join(OUTPUT_DIR, filename)

                    with open(filepath, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(COLUMN_NAMES)
                        writer.writerows(data_buffer)

                    print(f"SUCCESS: Saved data to {filepath}")
                    data_buffer = []

            except UnicodeDecodeError:
                print(f"Warning: Unicode decode error on line: {line}")
            except Exception as e:
                print(f"An error occurred while processing data: {e}")

    except serial.SerialException as e:
        print("---!!! SERIAL PORT ERROR !!!---")
        print(f"CRITICAL ERROR: Could not open port {SERIAL_PORT}. {e}")
        print("Please check port name, permissions, and ensure no other program is using it.")
    except KeyboardInterrupt:
        print("\nStopping data collection.")
    except Exception as e:
        print(f"---!!! AN UNKNOWN ERROR OCCURRED !!!---")
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Script finished ---")
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")


# --- 4. Run the script ---
if __name__ == "__main__":
    print("--- __name__ == __main__ check passed ---")
    start_data_logger()
