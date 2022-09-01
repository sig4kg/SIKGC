import numpy
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

OUT_FILE_PREFIX = "../outputs/figs/"

def draw_stacked_plot(iters, xlabels, ylabel, width, bar_colors=[]):
    fig, ax = plt.subplots()
    last_iter = []
    rects = []
    for i in range(len(iters)):
        if len(last_iter) > 0:
            rect = ax.bar(xlabels,
                          [iters[i][x] - last_iter[x] for x in range(len(iters[i]))],
                          width,
                          label=f'iter{i}',
                          color=bar_colors[i],
                          bottom=last_iter)
            rects.append(rect)
        else:
            rect = ax.bar(xlabels, iters[i], width, label=f'iter{i}', color=bar_colors[i])
            rects.append(rect)
        last_iter = iters[i]
    plt.xticks(rotation=80)
    ax.set_ylabel(ylabel)
    ax.legend(handles=rects,
              labels=['iter1', 'iter2', 'iter3'],
              bbox_to_anchor=(0, 1),
              loc='lower left',
              ncol=3,
              fontsize='small')
    fig.tight_layout()
    plt.show()


def draw_spot_plot(iters, xlabels, ylabel, width, marker_colours):
    fig, ax = plt.subplots()
    ax.vlines(xlabels, 0, 1, linestyles='dotted')
    markers = []
    for i in range(len(iters)):
        iter_data = iters[i]
        y_transform = numpy.transpose(iter_data)
        handle, = ax.plot(xlabels, y_transform, '^', color=marker_colours[i])
        markers.append(handle)

    # plt.ylim(0, 1)
    plt.xticks(rotation=80)
    plt.tick_params(bottom=False)
    ax.set_ylabel(ylabel)
    # ax.set_title(title)
    ax.legend(handles=markers,
              labels=['iter1', 'iter2', 'iter3'],
              bbox_to_anchor=(0, 1),
              loc='lower left',
              ncol=3,
              fontsize='small')
    fig.tight_layout()
    plt.show()


def read_results(in_file, sheet_name):
    df_sheet = pd.read_excel(in_file, sheet_name=sheet_name, header=0)
    methods = df_sheet['method']
    headers = df_sheet.columns.values.tolist()
    iters_data = []
    for i in range(1, 4):
        f_cor = f'f_cor{i}'
        f_cov = f'f_cov{i}'
        f_con = f'f_con{i}'
        f_h = f'f_h{i}'
        if f_cor not in headers:
            break
        series_f_cor = df_sheet[f_cor]
        series_f_cov = df_sheet[f_cov]
        series_f_con = df_sheet[f_con]
        series_f_h = df_sheet[f_h]
        one_iter = dict()
        for ind in range(len(methods)):
            if pd.isna(series_f_cor[ind]):
                continue
            one_iter.update({methods[ind]: {'f_cor': series_f_cor[ind],
                                            'f_cov': series_f_cov[ind],
                                            'f_con': series_f_con[ind],
                                            'f_h': series_f_h[ind]
                                            }})
        iters_data.append(one_iter)
    return iters_data


def drawEL(iters, xlabels, xkeys, iter_num=3, span=0, with_legend=True, out_file=""):
    chart_keys = ['f_cor', 'f_cov', 'f_con', 'f_h']
    E_L_LT = {chart: [] for chart in chart_keys}
    for i in range(iter_num):
        i_data = iters[i]
        for chart in chart_keys:
            E_L_LT[chart].append([i_data[key][chart] if key in i_data else 0 for key in xkeys])
    fig, axs = plt.subplots(nrows=2, ncols=2)
    colors = ['Green', 'Orange', 'Red']
    rects = []

    def drawspot(subax, chart_data, y_label):
        subax.vlines(xlabels, 0, 1, linestyles='dotted')
        for i in range(len(chart_data)):
            iter_data = chart_data[i]
            y_transform = numpy.transpose(iter_data)
            ydata_list = y_transform.tolist()
            tmp_xlabels = []
            tmp_ydata = []
            for ind, v in enumerate(ydata_list):
                if v != 0:
                    tmp_xlabels.append(xlabels[ind])
                    tmp_ydata.append(ydata_list[ind])
            subax.plot(tmp_xlabels, tmp_ydata, '^', color=colors[i])
        subax.set_ylabel(y_label, fontsize=8)
        for tick in subax.get_xticklabels():
            tick.set_rotation(80)
            tick.set_fontsize(8)
        for tick in subax.get_yticklabels():
            tick.set_fontsize(8)
        xspans = []
        if span > 0:
            for r in range(span - 1):
                x = (len(xlabels) / span) * (r + 1) - 0.5
                xspans.append(x)
            subax.vlines(xspans, 0, 1, transform=subax.get_xaxis_transform(), colors='0.0', linewidths=0.75)

    def drawbar(subax, chart_data, y_label):
        last_iter = []
        for i in range(len(chart_data)):
            if len(last_iter) > 0:
                rec = subax.bar(xlabels,
                                [chart_data[i][x] - last_iter[x] if chart_data[i][x] != 0 else 0 for x in
                                 range(len(chart_data[i]))],
                                label=f'iter{i}',
                                color=colors[i],
                                bottom=last_iter)
                rects.append(rec)
            else:
                rec = subax.bar(xlabels, chart_data[i], label=f'iter{i}', color=colors[i])
                rects.append(rec)
            last_iter = chart_data[i]
        subax.set_ylabel(y_label, fontsize=8)
        subax.set_xlim(-0.5, len(xlabels) - 0.5)
        for tick in subax.get_xticklabels():
            tick.set_rotation(80)
            tick.set_fontsize(8)
        for tick in subax.get_yticklabels():
            tick.set_fontsize(8)
            xspans = []
        if span > 0:
            for r in range(span - 1):
                x = (len(xlabels) / span) * (r + 1) - 0.5
                xspans.append(x)
            subax.vlines(xspans, 0, 1, transform=subax.get_xaxis_transform(), colors='0.0', linewidths=0.75)

    drawspot(axs[0, 0], E_L_LT['f_cor'], '$f_{correctness}$')
    drawbar(axs[0, 1], E_L_LT['f_cov'], '$f_{coverage}$')
    drawspot(axs[1, 0], E_L_LT['f_con'], '$f_{consistency}$')
    drawspot(axs[1, 1], E_L_LT['f_h'], '$f_h$')
    if with_legend:
        fig.legend(handles=rects,
                   labels=['iter1', 'iter2', 'iter3'],
                   # bbox_to_anchor=(0, 1),
                   # loc='upper right',
                   ncol=3,
                   fontsize='small')
    fig.tight_layout()
    plt.subplots_adjust(top=0.92, left=0.1)
    if len(out_file):
        plt.savefig(out_file)
    plt.show()


def drawNELL():
    iters = read_results("../resources/sickle.xlsx", 'nell')
    label1 = [r'$Base_{TransE}$', r'$E_{TransE}$', r"$L_{TransE}$", r"$L_{TransE, type}$",
              r'$Base_{SimplE}$', r'$E_{SimplE}$', r"$L_{SimplE}$", r"$L_{SimplE, type}$",
              r'$Base_{ComplEx}$', r'$E_{ComplEx}$', r"$L_{ComplEx}$", r"$L_{ComplEx, type}$"]
    key1 = ['TransE', 'E_TransE', 'L_TransE', 'L_TransE,type',
            'SimplE', 'E_SimplE', 'L_SimplE', 'L_SimplE,type',
            'ComplEx', 'E_ComplEx', 'L_ComplEx', 'L_ComplEx,type']
    drawEL(iters, label1, key1, span=3, out_file=OUT_FILE_PREFIX + "nell1.png")

    label2 = ['M', 'L', 'R', 'R-M-L', 'M-R-L', 'R-L-M', 'parallel']
    key2 = ['M', 'L_TransE,type', 'R', 'R-M-L', 'M-R-L', 'R-L-M', 'M,L,R (parallel)']
    drawEL(iters, label2, key2, iter_num=3, span=0, out_file=OUT_FILE_PREFIX + "nell2.png")

    label3 = [r'$E_{TransE}$', '$E_{TransE,neg}$', r"$L_{TransE,type}$", r"$L_{TransE,type,neg}$",
              r'$E_{SimplE}$', r'$E_{SimplE,neg}$', r"$L_{SimplE,type}$", r"$L_{SimplE, type,neg}$",
              r'$E_{ComplEx}$', r'$E_{ComplEx,neg}$', r"$L_{ComplEx,type}$", r"$L_{ComplEx, type,neg}$"]
    key3 = ['E_TransE', 'E_TransE,neg', 'L_TransE,type', 'L_TransE,type,neg',
            'E_SimplE', 'E_SimplE,neg', 'L_SimplE,type', 'L_SimplE,type,neg',
            'E_ComplEx', 'E_ComplEx,neg', 'L_ComplEx,type', 'L_ComplEx,type,neg']
    drawEL(iters, label3, key3, iter_num=1, span=3, with_legend=False, out_file=OUT_FILE_PREFIX + "nell3.png")


def drawDBpedia():
    iters = read_results("../resources/sickle.xlsx", 'dbpedia')
    label1 = [r'$Base_{TransE}$', r'$E_{TransE}$', r"$L_{TransE}$",
              r'$Base_{SimplE}$', r'$E_{SimplE}$', r"$L_{SimplE}$",
              r'$Base_{ComplEx}$', r'$E_{ComplEx}$', r"$L_{ComplEx}$"]
    key1 = ['TransE', 'E_TransE', 'L_TransE',
            'SimplE', 'E_SimplE', 'L_SimplE',
            'ComplEx', 'E_ComplEx', 'L_ComplEx']
    drawEL(iters, label1, key1, iter_num=2, span=3, out_file=OUT_FILE_PREFIX + "dbped1.png")

    label2 = ['M', 'L', 'R', 'R-M-L', 'M-R-L', 'R-L-M', 'parallel']
    key2 = ['M', 'L_TransE', 'R', 'R-M-L', 'M-R-L', 'R-L-M', 'M,L,R (parallel)']
    drawEL(iters, label2, key2, iter_num=2, span=0, out_file=OUT_FILE_PREFIX + "dbped2.png")

    label3 = [r'$E_{TransE}$', '$E_{TransE,neg}$', r"$L_{TransE}$", r"$L_{TransE,neg}$",
              r'$E_{SimplE}$', r'$E_{SimplE,neg}$', r"$L_{SimplE}$", r"$L_{SimplE,neg}$",
              r'$E_{ComplEx}$', r'$E_{ComplEx,neg}$', r"$L_{ComplEx}$", r"$L_{ComplEx,neg}$"]
    key3 = ['E_TransE', 'E_TransE,neg', 'L_TransE', 'L_TransE,neg',
            'E_SimplE', 'E_SimplE,neg', 'L_SimplE', 'L_SimplE,neg',
            'E_ComplEx', 'E_ComplEx,neg', 'L_ComplEx', 'L_ComplEx,neg']
    drawEL(iters, label3, key3, iter_num=1, span=3, with_legend=False, out_file=OUT_FILE_PREFIX + "dbped3.png")


def drawTREAT():
    iters = read_results("../resources/sickle.xlsx", 'treat')
    label1 = [r'$Base_{TransE}$', r'$E_{TransE}$', r"$L_{TransE}$",
              r'$Base_{SimplE}$', r'$E_{SimplE}$', r"$L_{SimplE}$",
              r'$Base_{ComplEx}$', r'$E_{ComplEx}$', r"$L_{ComplEx}$"]
    key1 = ['TransE', 'E_TransE', 'L_TransE',
            'SimplE', 'E_SimplE', 'L_SimplE',
            'ComplEx', 'E_ComplEx', 'L_ComplEx']
    drawEL(iters, label1, key1, iter_num=3, span=3, out_file=OUT_FILE_PREFIX + "treat1.png")

    label2 = ['M', 'L', 'R', 'R-M-L', 'M-R-L', 'R-L-M', 'parallel']
    key2 = ['M', 'L_SimplE', 'R', 'R-M-L', 'M-R-L', 'R-L-M', 'M,L,R (parallel)']
    drawEL(iters, label2, key2, iter_num=2, span=0, out_file=OUT_FILE_PREFIX + "treat2.png")

    label3 = [r'$E_{TransE}$', '$E_{TransE,neg}$', r"$L_{TransE}$", r"$L_{TransE,neg}$",
              r'$E_{SimplE}$', r'$E_{SimplE,neg}$', r"$L_{SimplE}$", r"$L_{SimplE,neg}$",
              r'$E_{ComplEx}$', r'$E_{ComplEx,neg}$', r"$L_{ComplEx}$", r"$L_{ComplEx,neg}$"]
    key3 = ['E_TransE', 'E_TransE,neg', 'L_TransE', 'L_TransE,neg',
            'E_SimplE', 'E_SimplE,neg', 'L_SimplE', 'L_SimplE,neg',
            'E_ComplEx', 'E_ComplEx,neg', 'L_ComplEx', 'L_ComplEx,neg']
    drawEL(iters, label3, key3, iter_num=3, span=3, with_legend=False, out_file=OUT_FILE_PREFIX + "treat3.png")


if __name__ == "__main__":
    # drawNELL()
    drawDBpedia()
    # drawTREAT()
