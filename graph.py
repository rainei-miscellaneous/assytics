import re, argparse, argcomplete, csv, os
from collections import namedtuple
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter

def sec_to_mm_ss_str(sec):
    rs = round(sec, 2)
    s = '{0:02.0f}'.format(rs % 60)
    return f"{int(rs / 60):02d}:{s}"

def str2s(hmrstr):
    mre = re.match("([0-9]+):([0-9]{2}):([0-9.]+)", hmrstr)
    h = int(mre[1])
    m = int(mre[2])
    s = float(mre[3])
    return ((h * 60) + m) * 60 + s

parser = argparse.ArgumentParser(description='graph data from libass_profiler_graph (assytics)')
parser.add_argument('-i', '--inputcsv', default='statistics.csv', required=False,
                    help='name of the CSV file').completer = argcomplete.completers.FilesCompleter(['csv'], directories=False)
parser.add_argument('-o', '--output', default=None, help='output PNG file')
parser.add_argument('--xtick-interval', type=int, default=180, 
                    help='major tick interval on x-axis in seconds (default: 300 = 5 minutes)')
args = parser.parse_args()

frame_stat_names = ['time', 'total_image_size', 'largest_image_size', 'image_count', 'time_benchmark']
Frame_Statistics = namedtuple('Frame_Statistics', frame_stat_names)
frame_graph_labels = [
    'total bitmap sizes for frame',
    'largest bitmap size in frame',
    'bitmap counts',
    'frame render time',
]
frame_stat_y_axis_labels = [
    'bytes',
    'bytes',
    'counts',
    'seconds',
]

def Base10BytesFormatter(max_y):
    if max_y > 1000 ** 3:
        return lambda y, pos: f"{int(y / 1000 ** 3):03d} GB"
    elif max_y > 1000 ** 2:
        return lambda y, pos: f"{int(y / 1000 ** 2):03d} MB"
    elif max_y > 1000:
        return lambda y, pos: f"{int(y / 1000):03d} kB"
    else:
        return lambda y, pos: f"{int(y):03d}"

def ZeroPadFormatter(y, pos):
    return f"{int(y):03d}"

def graph_libass_stats(samples, title, output=None, xtick_interval=180):
    zs = list(zip(*samples))
    time_domain = [str2s(t) for t in zs[0]]
    datasets = zs[1:]

    fig, subplots = plt.subplots(
        len(datasets), 1,
        figsize=(18, 10),
        dpi=180,
        constrained_layout=False
    )

    # Background noir
    fig.patch.set_facecolor("#1e1e1e")
    for ax in subplots:
        ax.set_facecolor("#1e1e1e")

    # White title 
    fig.suptitle(f'Analytics for {os.path.basename(title)}',
                 fontsize=16, y=0.99, color="white")

    for subplot, dataset, graph_label, y_label in zip(subplots, datasets, frame_graph_labels, frame_stat_y_axis_labels):
        float_data = [float(a) for a in dataset]
        max_y = max(float_data)
        subplot.ticklabel_format(style='plain')

        # X-axis ticks
        subplot.xaxis.set_major_locator(MultipleLocator(xtick_interval))  
        subplot.xaxis.set_minor_locator(MultipleLocator(
            xtick_interval // 5 if xtick_interval >= 60 else max(1, xtick_interval // 2)
        ))
        subplot.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: sec_to_mm_ss_str(x)))

        # Light-white grid
        subplot.grid(visible=True, which='major', axis='x',
                     color='white', alpha=0.3, linewidth=0.8)
        subplot.grid(visible=True, which='minor', axis='x',
                     color='white', alpha=0.15, linestyle=":", linewidth=0.6)

        # White tick / label
        subplot.tick_params(colors='white')
        subplot.xaxis.label.set_color('white')
        subplot.yaxis.label.set_color('white')

        # Y-axis formatter
        if y_label == "bytes":
            subplot.yaxis.set_major_formatter(Base10BytesFormatter(max_y))
        elif y_label == "counts":
            subplot.yaxis.set_major_formatter(FuncFormatter(ZeroPadFormatter))
        else:
            subplot.set_ylabel(y_label, color="white")

        subplot.set_xlim([time_domain[0], time_domain[-1]])

        if graph_label == "frame render time":
            subplot.set_ylim([0, 0.3])
        else:
            subplot.set_ylim([0, max_y])

        subplot.plot(time_domain, float_data, linewidth=1.0, alpha=0.9, color="deepskyblue")
        subplot.set_title(graph_label, fontsize=11, color="white")

        # Rotate ticks + monospace
        plt.setp(subplot.get_xticklabels(), rotation=30, ha="right", fontsize=9, family="monospace")
        plt.setp(subplot.get_yticklabels(), family="monospace")

        if graph_label == "frame render time":
            subplot.axhline(y=0.25, color="red", linestyle="--", label="0.25s threshold")

            max_val = max(float_data)
            max_idx = float_data.index(max_val)
            max_time = time_domain[max_idx]

            subplot.scatter([max_time], [max_val], color="orange", zorder=5,
                            label=f"Max: {max_val:.3f}s | {sec_to_mm_ss_str(max_time)}")

            subplot.legend(loc='upper right', fontsize=8, facecolor="#1e1e1e", edgecolor="white", labelcolor="white")

    fig.tight_layout(rect=[0, 0, 1, 0.96])

    if output:
        plt.savefig(output, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    else:
        plt.show()

data_list = []
with open(args.inputcsv, newline='') as csvfile:
    reader = csv.reader(csvfile)
    title = next(reader)[0]
    next(reader)
    for row in reader:
        data = Frame_Statistics(*row)
        data_list.append(data)

graph_libass_stats(data_list, title, args.output, args.xtick_interval)