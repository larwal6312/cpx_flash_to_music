import time
import array
import board
import audiobusio
import simpleio
import neopixel

#code borrowed and modified from
#https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/beb60b5fef3aa2d2002b746460f556735b6a0a58/Circuit_Playground_O_Phonor/freq_neopixel.py

#---| User Configuration |---------------------------
SAMPLERATE = 16000
SAMPLES = 160
THRESHOLD = 100
MIN_DELTAS = 5
DELAY = 0.1

FREQ_LOW = 150
FREQ_HIGH = 2000
COLORS = (
    (232, 17, 35) , # pixel 0
    (255, 241, 0) , # pixel 1
    (0, 158, 73) , # pixel 2
    (236, 0, 140) , # pixel 3
    (0, 178, 148) , # pixel 4
    (104, 33, 122) , # pixel 5
    (186, 216, 10) , # pixel 6
    (0, 24, 143) , # pixel 7
    (255, 140, 0) , # pixel 8
    (0, 188, 242) , # pixel 9
)

#----------------------------------------------------

# Create a buffer to record into
samples = array.array('H', [0] * SAMPLES)

# Setup the mic input
mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK,
                       board.MICROPHONE_DATA,
                       sample_rate=SAMPLERATE,
                       bit_depth=16)

# Setup NeoPixels
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, auto_write=False, brightness=1)

while True:
    # Get raw mic data
    #if cpx.switch:
    mic.record(samples, SAMPLES)

    # Compute DC offset (mean) and threshold level
    mean = int(sum(samples) / len(samples) + 0.5)
    threshold = mean + THRESHOLD

    # Compute deltas between mean crossing points
    # (this bit by Dan Halbert)
    deltas = []
    last_xing_point = None
    crossed_threshold = False
    for i in range(SAMPLES-1):
        sample = samples[i]
        if sample > threshold:
            crossed_threshold = True
        if crossed_threshold and sample < mean:
            if last_xing_point:
                deltas.append(i - last_xing_point)
            last_xing_point = i
            crossed_threshold = False

    # Try again if not enough deltas
    if len(deltas) < MIN_DELTAS:
        continue

    # Average the deltas
    mean = sum(deltas) / len(deltas)

    # Compute frequency
    freq = SAMPLERATE / mean

    print("crossings: {}  mean: {}  freq: {} ".format(len(deltas), mean, freq))

    # Show on NeoPixels
    pixels.fill(0)
    pixel = round(simpleio.map_range(freq, FREQ_LOW, FREQ_HIGH, 0, 9))
    pixels[pixel] = COLORS[pixel]
    pixels.show()

    time.sleep(DELAY)
