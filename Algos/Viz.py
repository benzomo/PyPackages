


from IPython import get_ipython
ipython = get_ipython()


ipython.magic("%matplotlib tk")

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


import os, sys, subprocess

root_path = os.path.dirname(__file__) + '/'


class Bash():   
    def plot_dot(file, plot_dir=root_path):
        subprocess.Popen(["dot", "-T", "png", file, "-O"]).wait()
        img = plt.imread(file + '.png')
        
        return plt.imshow(img)