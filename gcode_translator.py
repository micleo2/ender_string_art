import sys
import math as m
import numpy as np
num_pins = 150
circle_diam = 180
inner_radius = (circle_diam-4) / 2
outer_radius = (circle_diam+4) / 2
length = 220
angle_step = np.radians(360 / num_pins)
center = length / 2
volume = (length, length, 250)
travel_z = 10
push_down_z = 3

def main():
    pin_sequence = read_from_file(sys.argv[1])
    output_contents = compile_to_gcode(pin_sequence)
    print(output_contents)

def compile_to_gcode(seq):
    gcode_body = translate_pins_to_gcode(seq)
    all_gcode = gcode_prologue + gcode_body + gcode_epilogue
    return "\n".join([l + " ;" for l in all_gcode])

def translate_pins_to_gcode(seq):
    instructions = []
    for i in range(1, len(seq)):
        prev_pin = seq[i-1]
        cur_pin = seq[i]
        move_from_to(instructions, prev_pin, cur_pin)
    return instructions

def move_from_to(instructions, prev_pin, cur_pin):
    begin_instr = None
    end_instr = None
    cw_dist = (num_pins - (cur_pin - prev_pin)) if cur_pin > prev_pin else prev_pin - cur_pin
    if (cw_dist > (num_pins/2)):
        begin_instr = instr_mov(*turn_cw(cur_pin, inner_radius))
        end_instr = instr_mov(*turn_ccw(cur_pin, inner_radius))
    else:
        begin_instr = instr_mov(*turn_ccw(cur_pin, inner_radius))
        end_instr = instr_mov(*turn_cw(cur_pin, inner_radius))
    instructions.append(begin_instr)
    instructions.append(instr_mov(*location_of_pin(cur_pin, outer_radius)))
    instructions.append(instr_mov(z=push_down_z))
    instructions.append(instr_mov(z=travel_z))
    instructions.append(end_instr)

def location_of_pin(i, r, angle_off=0):
    res = location_from_angle(angle_from_idx(i)+angle_off, r)
    return res

def turn_cw(i, r):
    return location_of_pin(i, -angle_step/2, r)

def turn_ccw(i, r):
    return location_of_pin(i, angle_step/2, r)

def location_from_angle(angle, r):
    decimal_places = 4
    x = np.around(center + r * m.cos(angle), decimal_places)
    y = np.around(center + r * m.sin(angle), decimal_places)
    return np.array([x, y])

def angle_from_idx(idx):
    return (2 * m.pi * idx / num_pins) + (m.pi/2)

def sample_seq():
    seq = []
    for i in range(0, num_pins):
        seq.append(i)
        seq.append(int((i+(num_pins/2)) % num_pins))
    return seq        

def instr_mov(x=None, y=None, z=None):
    x_arg = "" if x is None else f" X{x}"
    y_arg = "" if y is None else f" Y{y}"
    z_arg = "" if z is None else f" Z{z}"
    return f"G1{x_arg}{y_arg}{z_arg}"

def read_from_file(fname):
    f = open(fname, 'r')
    contents = f.read()
    return [int(p) for p in contents.split(",")]

wait = 'M25'
use_abs = 'G90'
home = 'G28'
use_mm = 'G21'
mov_center = instr_mov(center, center)
mov_to_pin_0 = instr_mov(*location_of_pin(0, outer_radius))
gcode_prologue = [use_abs, home, instr_mov(z=10), mov_center, wait, mov_to_pin_0, wait]
gcode_epilogue = [home]

if __name__ =="__main__":
    main()
