# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_cartesian:
#
# Cartesian plots
# ===============
#
# This section documents features used for modifying Cartesian *x* and *y*
# axis settings, including axis scales, tick locations, and tick label
# formatting. It also documents a handy "dual units" feature.


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_locators:
#
# Tick locations
# --------------
#
# Matplotlib `tick locators
# <https://matplotlib.org/stable/gallery/ticks_and_spines/tick-locators.html>`__
# select sensible tick locations based on the axis data limits. In ProPlot, you can
# change the tick locator using the `~proplot.axes.CartesianAxes.format` keyword
# arguments `xlocator`, `ylocator`, `xminorlocator`, and `yminorlocator` (or their
# aliases, `xticks`, `yticks`, `xminorticks`, and `yminorticks`). This is powered by
# the `~proplot.constructor.Locator` :ref:`constructor function <why_constructor>`.
#
# You can use these keyword arguments to apply built-in matplotlib
# `~matplotlib.ticker.Locator`\ s by their "registered" names
# (e.g., ``xlocator='log'``), to draw ticks every ``N`` data values with
# `~matplotlib.ticker.MultipleLocator` (e.g., ``xlocator=2``), or to tick the
# specific locations in a list using `~matplotlib.ticker.FixedLocator` (just
# like `~matplotlib.axes.Axes.set_xticks` and `~matplotlib.axes.Axes.set_yticks`).
# If you want to work directly with the locator classes, they are also imported
# into the top-level namespace (e.g., ``pplt.MultipleLocator(5)`` is allowed).
#
# To generate lists of tick locations, we recommend using ProPlot's
# `~proplot.utils.arange` function -- it’s basically an *endpoint-inclusive*
# version of `numpy.arange`, which is usually what you'll want in this context.

# %%
import proplot as pplt
import numpy as np
state = np.random.RandomState(51423)
pplt.rc.update(
    metawidth=1, fontsize=10,
    metacolor='dark blue', suptitlecolor='dark blue',
    titleloc='upper center', titlecolor='dark blue', titleborder=False,
    axesfacecolor=pplt.scale_luminance('powderblue', 1.15),
)
fig = pplt.figure(share=False, refwidth=5, refaspect=(8, 1))
fig.format(suptitle='Tick locators demo')

# Step size for tick locations
ax = fig.subplot(711)
ax.format(
    xlim=(0, 200), xminorlocator=10, xlocator=30,
    title='MultipleLocator'
)

# Specific list of locations
ax = fig.subplot(712)
ax.format(
    xlim=(0, 10), xminorlocator=0.1,
    xlocator=[0, 0.3, 0.8, 1.6, 4.4, 8, 8.8, 10],
    title='FixedLocator',
)

# Ticks at numpy.linspace(xmin, xmax, N)
ax = fig.subplot(713)
ax.format(
    xlim=(0, 10), xlocator=('linear', 21),
    title='LinearLocator',
)

# Logarithmic locator, used automatically for log scale plots
ax = fig.subplot(714)
ax.format(
    xlim=(1, 100), xlocator='log', xminorlocator='logminor',
    title='LogLocator',
)

# Maximum number of ticks, but at "nice" locations
ax = fig.subplot(715)
ax.format(
    xlim=(1, 7), xlocator=('maxn', 11),
    title='MaxNLocator',
)

# Hide all ticks
ax = fig.subplot(716)
ax.format(
    xlim=(-10, 10), xlocator='null',
    title='NullLocator',
)

# Tick locations that cleanly divide 60 minute/60 second intervals
ax = fig.subplot(717)
ax.format(
    xlim=(0, 2), xlocator='dms', xformatter='dms',
    title='Degree-Minute-Second Locator (requires cartopy)',
)

pplt.rc.reset()

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_formatters:
#
# Tick formatting
# ---------------
#
# Matplotlib `tick formatters
# <https://matplotlib.org/stable/gallery/ticks_and_spines/tick-formatters.html>`__
# convert floating point numbers to nicely-formatted tick labels. In ProPlot, you can
# change the tick formatter using the `~proplot.axes.CartesianAxes.format` keyword
# arguments `xformatter` and `yformatter` (or their aliases, `xticklabels` and
# `yticklabels`). This is powered by the `~proplot.constructor.Formatter`
# :ref:`constructor function <why_constructor>`.
#
# You can use these keyword arguments to apply built-in matplotlib
# `~matplotlib.ticker.Formatter`\ s by their "registered" names
# (e.g., ``xformatter='log'``), to apply a ``%``-style format directive with
# `~matplotlib.ticker.FormatStrFormatter` (e.g., ``xformatter='%.0f'``), or
# to apply custom tick labels with `~matplotlib.ticker.FixedFormatter` (just
# like `~matplotlib.axes.Axes.set_xticklabels`). You can also apply one of ProPlot's
# new tick formatters -- for example, ``xformatter='deglat'`` to label ticks
# as geographic latitude coordinates, ``xformatter='pi'`` to label ticks as
# fractions of :math:`\pi`, or ``xformatter='sci'`` to label ticks with
# scientific notation. If you want to work directly with the formatter classes,
# they are also imported into the top-level namespace
# (e.g., ``pplt.SciFormatter()`` is allowed).
#
# ProPlot also changes the default tick formatter to
# `~proplot.ticker.AutoFormatter`. This class trims trailing zeros by
# default, can be used to *omit tick labels* outside of some data range, and
# can add arbitrary prefixes and suffixes to each label. See
# `~proplot.ticker.AutoFormatter` for details. To disable the trailing
# zero-trimming feature, set :rcraw:`formatter.zerotrim` to ``False``.

# %%
import proplot as pplt
pplt.rc.fontsize = 11
pplt.rc.metawidth = 1.5
pplt.rc.gridwidth = 1

# Create the figure
fig, axs = pplt.subplots(ncols=2, nrows=2, refwidth=1.5, share=False)
axs.format(
    ytickloc='both', yticklabelloc='both',
    titlepad='0.5em', suptitle='Default formatters demo'
)

# Formatter comparison
locator = [0, 0.25, 0.5, 0.75, 1]
axs[0].format(xformatter='scalar', yformatter='scalar', title='Matplotlib formatter')
axs[1].format(title='ProPlot formatter')
axs[:2].format(xlocator=locator, ylocator=locator)

# Limiting the tick range
axs[2].format(
    title='Omitting tick labels', ticklen=5, xlim=(0, 5), ylim=(0, 5),
    xtickrange=(0, 2), ytickrange=(0, 2), xlocator=1, ylocator=1
)

# Setting the wrap range
axs[3].format(
    title='Wrapping the tick range', ticklen=5, xlim=(0, 7), ylim=(0, 6),
    xwraprange=(0, 5), ywraprange=(0, 3), xlocator=1, ylocator=1
)
pplt.rc.reset()


# %%
import proplot as pplt
import numpy as np
pplt.rc.update(
    metawidth=1.2, fontsize=10, axesfacecolor='gray0', figurefacecolor='gray2',
    metacolor='gray8', gridcolor='gray8', titlecolor='gray8', suptitlecolor='gray8',
    titleloc='upper center', titleborder=False,
)
fig = pplt.figure(refwidth=5, refaspect=(8, 1), share=False)

# Scientific notation
ax = fig.subplot(911)
ax.format(xlim=(0, 1e20), xformatter='sci', title='SciFormatter')

# N significant figures for ticks at specific values
ax = fig.subplot(912)
ax.format(
    xlim=(0, 20), xlocator=(0.0034, 3.233, 9.2, 15.2344, 7.2343, 19.58),
    xformatter=('sigfig', 2), title='SigFigFormatter',  # 2 significant digits
)

# Fraction formatters
ax = fig.subplot(913)
ax.format(
    xlim=(0, 3 * np.pi), xlocator=np.pi / 4, xformatter='pi', title='FracFormatter',
)
ax = fig.subplot(914)
ax.format(
    xlim=(0, 2 * np.e), xlocator=np.e / 2, xticklabels='e', title='FracFormatter',
)

# Geographic formatters
ax = fig.subplot(915)
ax.format(
    xlim=(-90, 90), xlocator=30, xformatter='deglat', title='Latitude Formatter'
)
ax = fig.subplot(916)
ax.format(
    xlim=(0, 360), xlocator=60, xformatter='deglon', title='Longitude Formatter'
)

# User input labels
ax = fig.subplot(917)
ax.format(
    xlim=(0, 5), xlocator=np.arange(5),
    xticklabels=['a', 'b', 'c', 'd', 'e'], title='FixedFormatter',
)

# Custom style labels
ax = fig.subplot(918)
ax.format(
    xlim=(0, 0.001), xlocator=0.0001, xformatter='%.E', title='FormatStrFormatter',
)
ax = fig.subplot(919)
ax.format(
    xlim=(0, 100), xtickminor=False, xlocator=20,
    xformatter='{x:.1f}', title='StrMethodFormatter',
)
fig.format(ylocator='null', suptitle='Tick formatters demo')
pplt.rc.reset()

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_datetime:
#
# Datetime ticks
# --------------
#
# ProPlot can also be used to customize the tick locations and tick label
# format of "datetime" axes. To draw ticks on some particular time unit, just use a
# unit string (e.g., ``xlocator='month'``). To draw ticks every ``N`` time units,
# just use a (unit, N) tuple (e.g., ``xlocator=('day', 5)``). For `% style formatting
# <https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior>`__
# of datetime tick labels, just use a string containing ``'%'`` (e.g.
# ``xformatter='%Y-%m-%d'``). By default, *x* axis datetime axis labels are
# rotated 90 degrees, like in `pandas`_. This can be disabled by passing
# ``xrotation=0`` to `~proplot.axes.CartesianAxes.format` or by setting
# :rcraw:`formatter.timerotation` to ``0``. See `~proplot.constructor.Locator`
# and `~proplot.constructor.Formatter` for details.

# %%
import proplot as pplt
import numpy as np
pplt.rc.update(
    metawidth=1.2, fontsize=10, ticklenratio=0.7,
    figurefacecolor='w', axesfacecolor='pastel blue',
    titleloc='upper center', titleborder=False,
)
fig, axs = pplt.subplots(nrows=5, refwidth=6, refaspect=(8, 1), share=False)

# Default date locator
# This is enabled if you plot datetime data or set datetime limits
ax = axs[0]
ax.format(
    xlim=(np.datetime64('2000-01-01'), np.datetime64('2001-01-02')),
    title='Auto date locator and formatter'
)

# Concise date formatter introduced in matplotlib 3.1
ax = axs[1]
ax.format(
    xlim=(np.datetime64('2000-01-01'), np.datetime64('2001-01-01')),
    xformatter='concise', title='Concise date formatter',
)

# Minor ticks every year, major every 10 years
ax = axs[2]
ax.format(
    xlim=(np.datetime64('2000-01-01'), np.datetime64('2050-01-01')),
    xlocator=('year', 10), xformatter='\'%y', title='Ticks every N units',
)

# Minor ticks every 10 minutes, major every 2 minutes
ax = axs[3]
ax.format(
    xlim=(np.datetime64('2000-01-01T00:00:00'), np.datetime64('2000-01-01T12:00:00')),
    xlocator=('hour', range(0, 24, 2)), xminorlocator=('minute', range(0, 60, 10)),
    xformatter='T%H:%M:%S', title='Ticks at specific intervals',
)

# Month and year labels, with default tick label rotation
ax = axs[4]
ax.format(
    xlim=(np.datetime64('2000-01-01'), np.datetime64('2008-01-01')),
    xlocator='year', xminorlocator='month',  # minor ticks every month
    xformatter='%b %Y', title='Ticks with default rotation',
)
axs[:4].format(xrotation=0)  # no rotation for the first four examples
fig.format(ylocator='null', suptitle='Datetime locators and formatters demo')
pplt.rc.reset()


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_scales:
#
# Axis scales
# -----------
#
# "Axis scales" like ``'linear'`` and ``'log'`` control the *x* and *y* axis
# coordinate system. To change the axis scale, pass e.g. ``xscale='log'`` or
# ``yscale='log'`` to `~proplot.axes.Axes.format`. This is powered by the
# `~proplot.constructor.Scale` :ref:`constructor function <why_constructor>`.
# ProPlot makes several changes to the axis scale API:
#
# * The `~proplot.ticker.AutoFormatter` formatter is now used for all axis scales
#   by default, including ``'log'`` and ``'symlog'``. Matplotlib's behavior can
#   be restored by passing e.g. ``xformatter='log'`` or ``yformatter='log'`` to
#   `~proplot.axes.CartesianAxes.format`.
# * To make its behavior consistent with `~proplot.constructor.Locator` and
#   `~proplot.constructor.Formatter`, the `~proplot.constructor.Scale`
#   constructor function returns instances of `~matplotlib.scale.ScaleBase`,
#   and `~matplotlib.axes.Axes.set_xscale` and
#   `~matplotlib.axes.Axes.set_yscale` now accept these class instances in
#   addition to "registered" names like ``'log'``.
# * While matplotlib axis scales must be instantiated with an
#   `~matplotlib.axis.Axis` instance (for backwards compatibility reasons),
#   ProPlot axis scales can be instantiated without the axis instance
#   (e.g., ``pplt.LogScale()`` instead of ``pplt.LogScale(ax.xaxis)``).
# * The default `subs` for the ``'symlog'`` axis scale is now ``np.arange(1, 10)``,
#   and the default `linthresh` is now ``1``. Also the ``'log'`` and ``'symlog'``
#   axis scales now accept the keywords `base`, `linthresh`, `linscale`, and
#   `subs` rather than keywords with trailing ``x`` or ``y``.
#
# ProPlot also includes a few new axis scales. The ``'cutoff'`` scale (see
# `~proplot.scale.CutoffScale`) is useful when the statistical distribution
# of your data is very unusual. The ``'sine'`` scale `~proplot.scale.SineLatitudeScale`
# scales the axis with a sine function (resulting in an area-weighted spherical latitude
# coordinate) and the ``'mercator'`` scale `~proplot.scale.MercatorLatitudeScale`
# scales the axis with the Mercator projection latitude coordinate. The
# ``'inverse'`` scale `~proplot.scale.InverseScale` can be useful when
# working with spectral data, especially with :ref:`"dual" unit axes <ug_dual>`.
# If you want to work with these axis scales directly, they are also imported
# into the top-level namespace (e.g., ``pplt.CutoffScale(...)`` is allowed).

# %%
import proplot as pplt
import numpy as np
N = 200
lw = 3
pplt.rc.update({'meta.width': 1, 'label.weight': 'bold', 'tick.labelweight': 'bold'})
fig = pplt.figure(refwidth=1.8, share=False)

# Linear and log scales
ax1 = fig.subplot(221)
ax1.format(yscale='linear', ylabel='linear scale')
ax2 = fig.subplot(222)
ax2.format(ylim=(1e-3, 1e3), yscale='log', ylabel='log scale')
for ax in (ax1, ax2):
    ax.plot(np.linspace(0, 1, N), np.linspace(0, 1000, N), lw=lw)

# Symlog scale
ax = fig.subplot(223)
ax.format(yscale='symlog', ylabel='symlog scale')
ax.plot(np.linspace(0, 1, N), np.linspace(-1000, 1000, N), lw=lw)

# Logit scale
ax = fig.subplot(224)
ax.format(yscale='logit', ylabel='logit scale')
ax.plot(np.linspace(0, 1, N), np.linspace(0.01, 0.99, N), lw=lw)

fig.format(suptitle='Axis scales demo', ytickminor=True)
pplt.rc.reset()


# %%
import proplot as pplt
import numpy as np
fig, axs = pplt.subplots(nrows=4, refaspect=(5, 1), figwidth=6, sharex=False)

# Sample data
x = np.linspace(0, 4 * np.pi, 100)
dy = np.linspace(-1, 1, 5)
y1 = np.sin(x)
y2 = np.cos(x)
state = np.random.RandomState(51423)
data = state.rand(len(dy) - 1, len(x) - 1)

# Loop through various cutoff scale options
titles = ('Zoom out of left', 'Zoom into left', 'Discrete jump', 'Fast jump')
args = (
    (np.pi, 3),  # speed up
    (3 * np.pi, 1 / 3),  # slow down
    (np.pi, np.inf, 3 * np.pi),  # discrete jump
    (np.pi, 5, 3 * np.pi)  # fast jump
)
locators = (
    np.pi / 3,
    np.pi / 3,
    np.pi * np.append(np.linspace(0, 1, 4), np.linspace(3, 4, 4)),
    np.pi * np.append(np.linspace(0, 1, 4), np.linspace(3, 4, 4)),
)
for ax, iargs, title, locator in zip(axs, args, titles, locators):
    ax.pcolormesh(x, dy, data, cmap='grays', cmap_kw={'right': 0.8})
    for y, color in zip((y1, y2), ('coral', 'sky blue')):
        ax.plot(x, y, lw=4, color=color)
    ax.format(
        xscale=('cutoff', *iargs), title=title,
        xlim=(0, 4 * np.pi), ylabel='wave amplitude',
        xformatter='pi', xlocator=locator,
        xtickminor=False, xgrid=True, ygrid=False, suptitle='Cutoff axis scales demo'
    )

# %%
import proplot as pplt
import numpy as np

# Create figure
pplt.rc.reset()
state = np.random.RandomState(51423)
colors = ('coral', 'sky blue')
fig, axs = pplt.subplots(nrows=2, ncols=3, refwidth=1.7, order='F', share=False)
axs.format(toplabels=('Geographic scales', 'Exponential scales', 'Power scales'))

# Geographic scales
n = 20
x = np.linspace(-180, 180, n)
y1 = np.linspace(-85, 85, n)
y2 = np.linspace(-85, 85, n)
data = state.rand(len(x) - 1, len(y2) - 1)
for ax, scale, color in zip(axs[:2], ('sine', 'mercator'), colors):
    title = scale.title() + ' y-axis'
    ax.plot(x, y1, '-', color=color, lw=4)
    ax.pcolormesh(x, y2, data, cmap='grays', cmap_kw={'right': 0.8})
    ax.format(
        title=title, yscale=scale, ytickloc='left',
        yformatter='deg', grid=False, ylocator=20,
        xscale='linear', xlim=None, ylim=(-85, 85)
    )

# Exp scales
x = np.linspace(0, 1, 50)
y = 10 * x
data = state.rand(len(y) - 1, len(x) - 1)
for ax, a, c, color in zip(axs[2:4], (np.e, 2), (0.5, 2), colors):
    title = f"${(a, 'e')[a == np.e]}^{{{(c, '')[c == 1]}x}}$"
    ax.pcolormesh(x, y, data, cmap='grays', cmap_kw={'right': 0.8})
    ax.plot(x, y, lw=4, color=color)
    ax.format(ylim=(0.1, 10), yscale=('exp', a, c), title=title)

# Power scales
for ax, power, color in zip(axs[4:], (2, 1 / 4), colors):
    ax.pcolormesh(x, y, data, cmap='grays', cmap_kw={'right': 0.8})
    ax.plot(x, y, lw=4, color=color)
    ax.format(ylim=(0.1, 10), yscale=('power', power), title=f'$x^{{{power}}}$')


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_dual:
#
# Dual units
# ----------
#
# The `~proplot.axes.CartesianAxes.dualx` and
# `~proplot.axes.CartesianAxes.dualy` methods can be used to draw duplicate
# *x* and *y* axes meant to represent *alternate units* in the same
# coordinate range as the "parent" axis. This feature is powered by the
# `~proplot.scale.FuncScale` class. `~proplot.axes.CartesianAxes.dualx`
# and `~proplot.axes.CartesianAxes.dualy` accept either...
#
# #. A single linear forward function.
# #. A pair of arbitrary forward and inverse functions.
# #. An :ref:`axis scale <ug_scales>` name or class instance.
#
# In the third case, the axis scale transforms are used for the forward and
# inverse functions, and the default axis scale locators and formatters are used
# for the default dual axis locators and formatters. In the below examples,
# we generate dual axes with each of these three methods. Note that the
# "parent" axis scale is arbitrary -- in the first example, we create
# a `~proplot.axes.CartesianAxes.dualx` axis for a `symlog-scaled
# <https://matplotlib.org/stable/gallery/scales/symlog_demo.html>`__ axis.

# %%
import proplot as pplt
pplt.rc.update({'grid.alpha': 0.4, 'meta.width': 1, 'grid.linewidth': 1})
c1 = pplt.scale_luminance('cerulean', 0.5)
c2 = pplt.scale_luminance('red', 0.5)
fig = pplt.figure(refaspect=2.2, refwidth=3, share=False)
axs = fig.subplots([[1, 1, 2, 2], [0, 3, 3, 0]])
axs.format(
    suptitle='Duplicate axes with simple transformations',
    ylocator=[], yformatter=[], xcolor=c1, gridcolor=c1,
)

# Meters and kilometers
ax = axs[0]
ax.format(xlim=(0, 5000), xlabel='meters')
ax.dualx(
    lambda x: x * 1e-3,
    label='kilometers', grid=True, color=c2, gridcolor=c2
)

# Kelvin and Celsius
ax = axs[1]
ax.format(xlim=(200, 300), xlabel='temperature (K)')
ax.dualx(
    lambda x: x - 273.15,
    label='temperature (\N{DEGREE SIGN}C)', grid=True, color=c2, gridcolor=c2
)

# With symlog parent
ax = axs[2]
ax.format(xlim=(-100, 100), xscale='symlog', xlabel='MegaJoules')
ax.dualx(
    lambda x: x * 1e6,
    label='Joules', formatter='log', grid=True, color=c2, gridcolor=c2
)
pplt.rc.reset()

# %%
import proplot as pplt
pplt.rc.update({'grid.alpha': 0.4, 'meta.width': 1, 'grid.linewidth': 1})
c1 = pplt.scale_luminance('cerulean', 0.5)
c2 = pplt.scale_luminance('red', 0.5)
fig = pplt.figure(share=False, refaspect=0.4, refwidth=1.8)
fig.format(suptitle='Duplicate axes with pressure and height')

# Pressure as the linear scale, height on opposite axis (scale height 7km)
ax = fig.subplot(121)
ax.format(
    xformatter='null', ylabel='pressure (hPa)',
    ylim=(1000, 10), xlocator=[], ycolor=c1, gridcolor=c1
)
ax.dualy(
    'height', label='height (km)', ticks=2.5, color=c2, gridcolor=c2, grid=True
)

# Height as the linear scale, pressure on opposite axis (scale height 7km)
ax = fig.subplot(122)
ax.format(
    xformatter='null', ylabel='height (km)', ylim=(0, 20), xlocator='null',
    grid=True, gridcolor=c2, ycolor=c2
)
ax.dualy(
    'pressure', label='pressure (hPa)', locator=100, color=c1, gridcolor=c1, grid=True,
)
pplt.rc.reset()

# %%
import proplot as pplt
import numpy as np
pplt.rc.margin = 0
c1 = pplt.scale_luminance('cerulean', 0.5)
c2 = pplt.scale_luminance('red', 0.5)
fig, ax = pplt.subplots(refaspect=(3, 1), figwidth=6)

# Sample data
cutoff = 1 / 5
x = np.linspace(0.01, 0.5, 1000)  # in wavenumber days
response = (np.tanh(-((x - cutoff) / 0.03)) + 1) / 2  # response func
ax.axvline(cutoff, lw=2, ls='-', color=c2)
ax.fill_between([cutoff - 0.03, cutoff + 0.03], 0, 1, color=c2, alpha=0.3)
ax.plot(x, response, color=c1, lw=2)

# Add inverse scale to top
ax.format(
    title='Imaginary response function',
    suptitle='Duplicate axes with wavenumber and period',
    xlabel='wavenumber (days$^{-1}$)', ylabel='response', grid=False,
)
ax = ax.dualx(
    'inverse', locator='log', locator_kw={'subs': (1, 2, 5)}, label='period (days)'
)
pplt.rc.reset()