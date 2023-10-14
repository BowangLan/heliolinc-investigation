# from start import *
from config import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import astropy.units as u
from matplotlib.gridspec import GridSpec


def separate_linked(linked_id_list, obj_table):
    linked_obj_list = obj_table[obj_table['ObjID'].isin(linked_id_list)]
    not_linked_obj_list = obj_table[~obj_table['ObjID'].isin(linked_id_list)]
    return linked_obj_list, not_linked_obj_list


def plot_parameter_grid_linked_diff(linked_obj_list, not_linked_obj_list, ax=None, c_linked="blue", c_not_linked="orange"):
    if not ax:
        ax = plt
    ax.scatter(not_linked_obj_list['helioDist'],
               not_linked_obj_list['helioVel'], s=0.5, c=c_not_linked)
    ax.scatter(linked_obj_list['helioDist'],
               linked_obj_list['helioVel'], s=0.5, c=c_linked)
    ax.xlabel("r (AU)")
    ax.ylabel("rdot (AU/day)")


def plot_hist2d(linked_obj_list, not_linked_obj_list):
    fig = plt.figure(layout="constrained", figsize=(12, 8))
    gs = GridSpec(2, 2, figure=fig)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[:, 1])

    maxDist = max(linked_obj_list['helioDist'].max(), not_linked_obj_list['helioDist'].max())
    minDist = min(linked_obj_list['helioDist'].min(), not_linked_obj_list['helioDist'].min())
    maxVel = max(linked_obj_list['helioVel'].max(), not_linked_obj_list['helioVel'].max())
    minVel = min(linked_obj_list['helioVel'].min(), not_linked_obj_list['helioVel'].min())
    r = [[minDist, maxDist], [minVel, maxVel]]
    bins = 120
    counts_a, _, _, _ = ax1.hist2d(
        linked_obj_list['helioDist'], linked_obj_list['helioVel'],
        range=r,
        cmap='hot', bins=bins)
    ax1.set_title("Linked objects")
    ax1.set_xlabel("r (AU)")
    ax1.set_ylabel("rdot (AU/day)")
    counts_b, _, _, _ = ax2.hist2d(
        not_linked_obj_list['helioDist'], not_linked_obj_list['helioVel'],
        range=r,
        cmap='hot', bins=bins)
    ax2.set_title("Not linked objects")
    ax2.set_xlabel("r (AU)")
    ax2.set_ylabel("rdot (AU/day)")
    # colormap_data = counts_a.T / (counts_a.T + counts_b.T)
    colormap_data = np.nan_to_num(counts_a.T / (counts_a.T + counts_b.T), nan=0)
    img = ax3.imshow(colormap_data, cmap='hot')
    ax3.set_title("Linked / (Linked + Not linked)")
    # ax3.set_xlabel("r (AU)")
    # ax3.set_ylabel("rdot (AU/day)")
    fig.colorbar(img)
    fig.show()


if __name__ == "__main__":
    helio_extracted = pd.read_feather(out_hl_extracted_file)
    obj_table = pd.read_feather(object_table_file)
    guess_table = pd.read_csv(guess_file, delimiter=' ')

    linked_id_list = set(helio_extracted['idstring'].unique())
    l_obj_list, not_l_obj_list = separate_linked(linked_id_list, obj_table)
    # plot_parameter_grid_linked_diff(l_obj_list, not_l_obj_list)
    # plt.scatter(guess_table['#r(AU)'],
    #             guess_table['rdot(AU/day)'], s=2, c="black")

    plot_hist2d(l_obj_list, not_l_obj_list)

    plt.show()

    # start = time.time()

    # # build guess-object relationship
    # obj_to_guesses = {oid: set() for oid in obj_table['ObjID']}
    # guess_to_objs = {}

    # for i in range(len(guess_table)):
    #     g = (guess_table['#r(AU)'][i], guess_table['rdot(AU/day)'][i])
    #     guess_to_objs[g] = set()

    # ho_id_list = helio_extracted['idstring'].values
    # ho_dist_list = helio_extracted['heliodist'].values
    # ho_vel_list = (helio_extracted['heliovel'].values * (u.km / u.s).to(u.au / u.day)).round(3)
    # for i in range(len(helio_extracted)):
    #     oid = ho_id_list[i]
    #     g = (ho_dist_list[i], ho_vel_list[i])
    #     guess_to_objs[g].add(oid)
    #     obj_to_guesses[oid].add(g)

    # # plot parameter grid with linked and not linked objects by one guess
    # g1 = list(guess_to_objs.keys())[168]
    # linked_id_list = guess_to_objs[(g1[0], g1[1])]
    # plot_parameter_grid_linked_diff(linked_id_list, obj_table)

    # end = time.time()
    # duration = end - start
    # print(f"Time to finish plotting: {duration:.2f} seconds")

    # plt.scatter([g1[0]], [g1[1]], s=18, c='black')
    # plt.show()
