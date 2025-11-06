import tkinter as tk
from tkinter import ttk, messagebox

HAS_PLOTTING = True
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    import numpy as np
except Exception:
    HAS_PLOTTING = False

DARK_BG = '#FFFFFF'
FRAME_BG = '#3a3a3a'
WIDGET_BG = '#4a4a4a'
FG = '#eaeaea'
ACCENT = '#4fc3f7'
GRID_COLOR = '#6b6b6b'

if HAS_PLOTTING:
    try:
        plt.style.use('dark_background')
        plt.rcParams['figure.facecolor'] = FRAME_BG
        plt.rcParams['axes.facecolor'] = FRAME_BG
        plt.rcParams['savefig.facecolor'] = FRAME_BG
        plt.rcParams['axes.edgecolor'] = FG
        plt.rcParams['xtick.color'] = FG
        plt.rcParams['ytick.color'] = FG
        plt.rcParams['text.color'] = FG
        plt.rcParams['grid.color'] = GRID_COLOR
    except Exception:
        pass


def int_to_bytes(n: int) -> bytes:
    if n == 0:
        return b"\x00"
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, byteorder='big', signed=False)


def bytes_to_bits(b: bytes) -> list:
    bits = []
    for byte in b:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits

SAMPLES_PER_BIT = 100


def make_time(nbits):
    if not HAS_PLOTTING:
        return None
    return np.linspace(0, nbits, nbits * SAMPLES_PER_BIT, endpoint=False)


def expand_bits(bits, per_bit=SAMPLES_PER_BIT):
    if not HAS_PLOTTING:
        return None
    arr = np.repeat(bits, per_bit)
    return arr


def nrz_unipolar(bits):
    if not HAS_PLOTTING:
        return None, None
    sig = expand_bits(bits)
    t = make_time(len(bits))
    return t, sig.astype(float)


def nrz_bipolar(bits):
    if not HAS_PLOTTING:
        return None, None
    mapped = [1.0 if b == 1 else -1.0 for b in bits]
    return make_time(len(bits)), np.repeat(mapped, SAMPLES_PER_BIT)


def rz_unipolar(bits):
    if not HAS_PLOTTING:
        return None, None
    sig = []
    for b in bits:
        if b == 1:
            sig.extend([1.0] * (SAMPLES_PER_BIT // 2))
            sig.extend([0.0] * (SAMPLES_PER_BIT - SAMPLES_PER_BIT // 2))
        else:
            sig.extend([0.0] * SAMPLES_PER_BIT)
    return make_time(len(bits)), np.array(sig)


def rz_bipolar(bits):
    if not HAS_PLOTTING:
        return None, None
    sig = []
    for b in bits:
        level = 1.0 if b == 1 else -1.0
        sig.extend([level] * (SAMPLES_PER_BIT // 2))
        sig.extend([0.0] * (SAMPLES_PER_BIT - SAMPLES_PER_BIT // 2))
    return make_time(len(bits)), np.array(sig)


def ami(bits):
    if not HAS_PLOTTING:
        return None, None
    sig = []
    last = -1.0
    for b in bits:
        if b == 0:
            sig.extend([0.0] * SAMPLES_PER_BIT)
        else:
            last *= -1.0
            sig.extend([last] * SAMPLES_PER_BIT)
    return make_time(len(bits)), np.array(sig)


def manchester(bits):
    if not HAS_PLOTTING:
        return None, None
    sig = []
    for b in bits:
        if b == 1:
            sig.extend([-1.0] * (SAMPLES_PER_BIT // 2))
            sig.extend([1.0] * (SAMPLES_PER_BIT - SAMPLES_PER_BIT // 2))
        else:
            sig.extend([1.0] * (SAMPLES_PER_BIT // 2))
            sig.extend([-1.0] * (SAMPLES_PER_BIT - SAMPLES_PER_BIT // 2))
    return make_time(len(bits)), np.array(sig)


def mark(bits):
    if not HAS_PLOTTING:
        return None, None
    mapped = [1.0 if b == 1 else 0.0 for b in bits]
    return make_time(len(bits)), np.repeat(mapped, SAMPLES_PER_BIT)


def space(bits):
    if not HAS_PLOTTING:
        return None, None
    mapped = [1.0 if b == 0 else 0.0 for b in bits]
    return make_time(len(bits)), np.repeat(mapped, SAMPLES_PER_BIT)


ENCODERS = [
    ("NRZ - Unipolar", nrz_unipolar),
    ("NRZ - Bipolar", nrz_bipolar),
    ("RZ - Unipolar", rz_unipolar),
    ("RZ - Bipolar", rz_bipolar),
    ("AMI", ami),
    ("Manchester", manchester),
    ("MARK", mark),
    ("SPACE", space),
]


def clock(bits):
    if not HAS_PLOTTING:
        return None, None
    nb = len(bits)
    per = SAMPLES_PER_BIT
    half = per // 2
    sig = []
    for _ in range(nb):
        sig.extend([1.0] * half)
        sig.extend([0.0] * (per - half))
    return make_time(nb), np.array(sig)


ENCODERS.append(("Clock", clock))

COLORS = [
    '#4fc3f7',
    '#ff8a65',
    '#9ccc65',
    '#ffd54f',
    '#ef5350',
    '#7e57c2',
    '#26a69a',
    '#90a4ae',
    '#ffffff',
]


class SignalEncoderApp(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        _title = getattr(master, 'title', None)
        if callable(_title):
            _title("Signal Encoders")
        try:
            style = ttk.Style()
            try:
                style.theme_use('clam')
            except Exception:
                pass
            style.configure('.', background=FRAME_BG, foreground=FG)
            style.configure('TFrame', background=FRAME_BG)
            style.configure('TLabel', background=FRAME_BG, foreground=FG)
            style.configure('TButton', background=WIDGET_BG, foreground=FG)
            style.map('TButton', background=[('active', ACCENT)])
            style.configure('TEntry', fieldbackground=WIDGET_BG, foreground=FG)
            _cfg = getattr(self.master, 'configure', None)
            if callable(_cfg):
                try:
                    _cfg(**{'bg': DARK_BG})
                except Exception:
                    pass
        except Exception:
            pass

        self.pack(fill='both', expand=True)
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(side='top', fill='x', padx=8, pady=8)

        ttk.Label(top, text='Mode:').pack(side='left')
        self.mode_var = tk.StringVar(value='Integer')
        self.mode_combo = ttk.Combobox(top, textvariable=self.mode_var, values=['Integer', 'Hex Bytes', 'Binary'], width=12, state='readonly')
        self.mode_combo.pack(side='left', padx=(4, 8))
        self.mode_combo.bind('<<ComboboxSelected>>', self._on_mode_change)

        ttk.Label(top, text='Value:').pack(side='left')
        self.entry = ttk.Entry(top, width=40)
        self.entry.pack(side='left', padx=6)
        self.entry.insert(0, '123')

        encode_btn = ttk.Button(top, text='Encode', command=self.on_encode)
        encode_btn.pack(side='left', padx=6)

        info_frame = ttk.Frame(self)
        info_frame.pack(side='top', fill='x', padx=8)
        self.hex_label = ttk.Label(info_frame, text='Hex: -')
        self.hex_label.pack(side='left')
        self.bin_label = ttk.Label(info_frame, text='Binary: -')
        self.bin_label.pack(side='left', padx=12)

        if HAS_PLOTTING:
            self.fig, self.axes = plt.subplots(len(ENCODERS), 1, figsize=(8, 2.0 * len(ENCODERS)), sharex=True)
            plt.subplots_adjust(hspace=0.6)
            for ax, (name, _) in zip(self.axes, ENCODERS):
                ax.set_ylabel(name)
                ax.set_ylim(-1.5, 1.5)
                ax.grid(True, which='both', axis='x', linestyle=':', alpha=0.5)
                try:
                    ax.set_axisbelow(False)
                except Exception:
                    pass
                ax.tick_params(colors=FG)
                for spine in ax.spines.values():
                    spine.set_color(FG)

            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            w = self.canvas.get_tk_widget()
            w.pack(side='top', fill='both', expand=True)
            try:
                w.config(bg=FRAME_BG)
            except Exception:
                pass
        else:
            ttk.Label(self, text='Plotting libraries (matplotlib, numpy) not found. Install requirements to see plots.').pack(padx=8, pady=8)

    def on_encode(self):
        txt = self.entry.get().strip()
        if not txt:
            messagebox.showerror('Error', 'Please enter an integer')
            return
        mode = self.mode_var.get() if hasattr(self, 'mode_var') else 'Integer'
        try:
            if mode == 'Integer':
                n = int(txt, 0)
                if n < 0:
                    raise ValueError('negative')
                b = int_to_bytes(n)
            elif mode == 'Hex Bytes':
                b = parse_bytes_input(txt)
            elif mode == 'Binary':
                b = parse_binary_input(txt)
            else:
                n = int(txt, 0)
                b = int_to_bytes(n)
        except ValueError:
            messagebox.showerror('Error', f'Invalid input for mode {mode}')
            return

        bits = bytes_to_bits(b)

        self.hex_label.config(text='Hex: ' + b.hex() + f'   ({len(b)} bytes)')
        binstr = ''.join(str(bit) for bit in bits)
        if len(binstr) > 128:
            binshow = binstr[:120] + '...(%d bits)' % len(binstr)
        else:
            binshow = binstr
        self.bin_label.config(text='Binary: ' + binshow)

        if not HAS_PLOTTING:
            messagebox.showinfo('Info', 'Plots are disabled because matplotlib/numpy are not installed.\nRun: pip install -r requirements.txt')
            return

        for ax in self.axes:
            ax.clear()

        for idx, ((name, func), ax) in enumerate(zip(ENCODERS, self.axes)):
            t, sig = func(bits)
            color = COLORS[idx % len(COLORS)]
            ax.plot(t, sig, drawstyle='steps-post', color=color, linewidth=1.5, zorder=1)
            ax.set_ylabel(name, color=color)
            ax.set_ylim(-1.5, 1.5)
            ax.set_yticks([-1, 0, 1])
            ax.grid(True, which='both', axis='x', linestyle=':', alpha=0.5)
            nbits = len(bits)
            for k in range(nbits + 1):
                try:
                    ax.axvline(k, color=GRID_COLOR, linewidth=0.6, alpha=0.6, zorder=10)
                except Exception:
                    ax.axvline(k, color='white', linewidth=0.6, alpha=0.6, zorder=10)

        self.axes[-1].set_xlabel('Bit index (time)')
        self.fig.tight_layout()
        self.canvas.draw()

    def _on_mode_change(self, event=None):
        mode = self.mode_var.get()
        if mode == 'Integer':
            sample = '305419896'
        elif mode == 'Hex Bytes':
            sample = '1a2b3c (hex bytes, spaces/0x allowed)'
        elif mode == 'Binary':
            sample = '01010110 (bits, spaces allowed)'
        else:
            sample = ''
        try:
            if not self.entry.get().strip():
                self.entry.delete(0, 'end')
                self.entry.insert(0, sample)
        except Exception:
            pass


def parse_bytes_input(txt):
    """Parse a string of hex bytes (e.g., '1a2b3c') into bytes."""
    try:
        cleaned = ''.join(ch for ch in txt if ch.isalnum())
        hexchars = ''.join(ch for ch in cleaned if ch in '0123456789abcdefABCDEF')
        if len(hexchars) == 0:
            raise ValueError('no hex')
        if len(hexchars) % 2 != 0:
            hexchars = '0' + hexchars
        return bytes.fromhex(hexchars)
    except Exception:
        raise ValueError('Invalid hex bytes')


def parse_binary_input(txt):
    """Parse a string of binary digits (e.g., '1101') into bytes."""
    try:
        bits = ''.join(ch for ch in txt if ch in '01')
        if len(bits) == 0:
            raise ValueError('no bits')
        bits = bits.rjust(((len(bits) + 7) // 8) * 8, '0')
        return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    except Exception:
        raise ValueError('Invalid binary string')


if __name__ == '__main__':
    root = tk.Tk()
    app = SignalEncoderApp(master=root)
    root.mainloop()
