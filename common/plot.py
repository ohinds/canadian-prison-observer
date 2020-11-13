import os

import matplotlib.pylab as plt


def save_plot(title, out_dir=os.path.join('/', 'tmp')):
    plt.title(title, fontsize=11)
    min_y = plt.gca().get_ylim()[0]
    if min_y > 0:
        plt.gca().set_ylim([0, plt.gca().get_ylim()[1]])
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().tick_params('x', length=0)
    plt.gca().tick_params('y', length=0)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, title.replace(' ', '_') + '.png'))
    plt.cla()
