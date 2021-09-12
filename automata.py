import matplotlib.pyplot as plt
import numpy as np
import random
import math

from multiprocessing import Process, Manager, Queue


def perturb(initial_condition):
    length = len(initial_condition)

    for value in range(len(initial_condition)):
        if initial_condition[value] != 0:
            check = random.randint(0,1)

            if check == 0:
                if initial_condition[(value-1)%length] == 0:
                    initial_condition[(value-1)%length]=initial_condition[value]
                    initial_condition[value]=0
            elif check == 1:
                if initial_condition[(value+1)%length] == 0:
                    initial_condition[(value+1)%length]=initial_condition[value]
                    initial_condition[value]=0
            else:
                pass
    return initial_condition


def generate_initial(length, states, prob, geometry): #Generates a random init cond

    if geometry == "linear":
        initial = [0] * length

        for element in range(length):
            if random.randint(1,prob) == 1:
                initial[element] = random.randint(0, states-1)
            else:
                pass

        return initial

    elif geometry == "planar":
        initial = [0] * length
        for i in range(length):
            initial[i] = [0] * length
        for i in range(length):
            for j in range(length):
                if random.randint(1,prob) == 1:
                    initial[j][i] = random.randint(0, states-1)
                else:
                    pass
        return initial

    else:
        return


def generate_rules(states, neighbors, lam): #Generates a random set of rules for a 1D CA
    rules = {}

    #test = str(int_2_base(attempts,2,8))
    for i in range(states ** neighbors):
        #print(int_2_base(i, states, 3))
        if random.uniform(0,1) > lam:
            rules[int_2_base(i, states, neighbors)] = 0
        else:
            rules[int_2_base(i, states, neighbors)] = random.randint(1, states-1)
        #rules[int_2_base(i, states, 3)] = int(test[i])

    return rules


def turn(assign):
    return (assign[3]+assign[0]+assign[2]+assign[4]+assign[1])


def flip(assign):
    return (assign[4]+assign[1]+assign[2]+assign[3]+assign[0])


def make_symmetric(rules, neighbors):
    if neighbors == 3:
        for key in rules:
            rules[key[::-1]] = rules[key]
    elif neighbors == 5:
        for key in rules:
            rules[turn(key)] = rules[key]
            rules[turn(turn(key))] = rules[key]
            rules[turn(turn(turn(key)))] = rules[key]
            rules[flip(key)] = rules[key]
            rules[turn(flip(key))] = rules[key]
            rules[turn(turn(flip(key)))] = rules[key]
            rules[turn(turn(turn(flip(key))))] = rules[key]
    return rules


def int_2_base(val, base, envelope): #writes val in base 'base' as a string
    result = ""

    if val == 0:
        return "0" * envelope

    #bound = math.ceil(math.log(val, base))

    digit = val % base
    difference = 0
    for i in range(envelope):
        result = str(digit) + result
        difference += digit*base**i
        digit = int(((val - difference) % (base**(i+2)))/base**(i+1))

    return result


def export_figure_matplotlib(arr, f_name, dpi=120, resize_fact=1, plt_show=False):
    fig = plt.figure(frameon=False)
    fig.set_size_inches(arr.shape[1]/dpi, arr.shape[0]/dpi)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(arr, cmap='Spectral')
    plt.savefig(f_name, dpi=(dpi * resize_fact))
    if plt_show:
        plt.show()
    else:
        plt.close()


def linear_automata(WIDTH, DEPTH, rule_set, strip, attempts):
    #rule_set = {
    #"000" : random.randint(0,1),
    #"001" : random.randint(0,1),
    #"010" : random.randint(0,1),
    #"011" : random.randint(0,1),
    #"100" : random.randint(0,1),
    #"101" : random.randint(0,1),
    #"110" : random.randint(0,1),
    #"111" : random.randint(0,1)
    #}

    pixels = [0] * DEPTH

    for k in range(DEPTH): #initializes the matrix
        if k == 0:
            pixels[k] = strip
        else:
            pixels[k] = [0] * len(strip)

    for step in range(DEPTH-1): #computes next rows of automata
        for cell in range(len(strip)):

            param = str(pixels[step][(cell-1)%len(strip)]) + str(pixels[step][cell%len(strip)]) + str(pixels[step][(cell+1)%len(strip)])

            pixels[step+1][cell] = rule_set[param]

    for step in range(DEPTH): #scales for the color map
        for cell in range(len(strip)):
            pixels[step][cell] = pixels[step][cell] * 100


    X = np.array(pixels)
    export_figure_matplotlib(X, 'automata_test'+str(attempts), dpi=120, resize_fact=10, plt_show=False)

    return


def planar_automata(WIDTH, DEPTH, rule_set, queue, iteration):

    plane_initial = queue.get()

    plane_next = [0] * WIDTH

    for i in range(WIDTH): #initializes the new matrix
        plane_next[i] = [0] * WIDTH

    for i in range(WIDTH):
        for j in range(WIDTH):

            param = str(plane_initial[i][(j-1)%WIDTH]) + str(plane_initial[(i-1)%WIDTH][j]) + str(plane_initial[i][j]) + str(plane_initial[i][(j+1)%WIDTH]) + str(plane_initial[(i+1)%WIDTH][j])

            plane_next[i][j] = rule_set[param]

    queue.put(plane_next)

    X = np.array(plane_next)
    export_figure_matplotlib(X, 'automata_test'+str(iteration), dpi=120, resize_fact=10, plt_show=False)

    return


if __name__ == "__main__":

    RULE_FRACTION = 1/3

    WIDTH = 100 #size of the strip the automata iterates on (wraps around edge)

    TRIES = 1000 #number of loops

    DEPTH = 100 #number of iterations on the initial condition

    STATES = 10 #number of distinct states for each cell

    FILL = 10 #1/FILL = portion of initializer filled randomly

    geometry = "linear" #linear or planar automata


    if geometry == "linear":
        attempts = 0



        #print(rule_set)

        while attempts < TRIES:
            #strip = perturb(strip)

            fraction = (attempts / TRIES)*(1 - 1/STATES)

            rule_set = generate_rules(STATES, 3, fraction)

            rule_set = make_symmetric(rule_set, 3)

            #rule_set = {'111':0,'110':1,'101':1,'100':0,'011':1,'010':1,'001':1,'000':0}

            strip = generate_initial(WIDTH, STATES, FILL, geometry)

            p0 = Process(target = linear_automata, args = (WIDTH, DEPTH, rule_set, strip, attempts))
            p0.start()

            p0.join()

            print(str(attempts) + str(':'))
            print(rule_set)
            #print(pixels)

            attempts += 1

            #for element in range(len(strip)):
            #    strip[element] = int(strip[element]/100)
    elif geometry == "planar":
        iteration = 0

        rule_set = generate_rules(STATES, 5, RULE_FRACTION)

        rule_set = make_symmetric(rule_set, 5)

        plane = generate_initial(WIDTH, STATES, FILL, geometry)

        print(rule_set)

        #with Manager() as manager:

        #buffer = manager.list()

        #for i in range(WIDTH):
            #buffer.append(plane[i])

        queue = Queue()
        queue.put(plane)

        while iteration < DEPTH:
            print(iteration)
            p0 = Process(target = planar_automata, args = (WIDTH,DEPTH, rule_set, queue, iteration))
            p0.start()

            p0.join()

            iteration += 1


    else:
        print("Invalid Geometry")
