import math as m
import numpy as np
num_pins = 150
# circle_diam = 180-4
circle_diam = 180+4
radius = circle_diam / 2
length = 220
angle_step = np.radians(360 / num_pins)
center = length / 2
volume = (length, length, 250)

def turn_cw(i):
    return location_from_angle(angle_from_idx(i) - angle_step/2)

def turn_ccw(i):
    return location_from_angle(angle_from_idx(i) + angle_step/2)

def angle_from_idx(idx):
    return (2 * m.pi * idx / num_pins) + (m.pi/2)

def location_from_angle(angle):
    x = np.around(center + radius * m.cos(angle))
    y = np.around(center + radius * m.sin(angle))
    return np.array([x, y])

def pin_locations(pins):
    location_map = []
    for i in range(0, pins):
        angle = angle_from_idx(i)
        location_map.append(location_from_angle(angle))
    return location_map

locations = pin_locations(num_pins)

def read_from_file(fname):
    f = open(fname, 'r')
    contents = f.read()
    return [int(p) for p in contents.split(",")]

def sample_seq():
    seq = []
    for i in range(0, num_pins):
        seq.append(i)
        seq.append(int((i+(num_pins/2)) % num_pins))
    return seq        

pin_sequence = read_from_file("./circle-steps.txt")

def instr_mov(x=None, y=None, z=None):
    x_arg = "" if x is None else f" X{x}"
    y_arg = "" if y is None else f" Y{y}"
    z_arg = "" if z is None else f" Z{z}"
    return f"G1{x_arg}{y_arg}{z_arg}"

wait = 'M25'
use_abs = 'G90'
home = 'G28'
use_mm = 'G21'
mov_center = instr_mov(center, center)
gcode_prologue = [use_abs, home, instr_mov(z=10), mov_center, wait, instr_mov(*locations[0]), wait]
gcode_epilogue = [home]

def translate_pins_to_gcode(seq):
    instructions = []
    for i in range(1, len(seq)):
        prev_pin = seq[i-1]
        cur_pin = seq[i]
        cw_dist = (num_pins - (cur_pin - prev_pin)) if cur_pin > prev_pin else prev_pin - cur_pin
        if (cw_dist > (num_pins/2)):
            instructions.append(instr_mov(*turn_cw(cur_pin)))
        else:
            instructions.append(instr_mov(*turn_ccw(cur_pin)))
    return instructions

def compile_to_gcode(seq):
    gcode_body = translate_pins_to_gcode(seq)
    all_gcode = gcode_prologue + gcode_body + gcode_epilogue
    return "\n".join([l + " ;" for l in all_gcode])

output_contents = compile_to_gcode(pin_sequence)
print(output_contents)
