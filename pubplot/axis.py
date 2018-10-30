#!/usr/bin/env python3
"""
Define various axis scales, locators, and formatters. Also define normalizers
generally used for colormap scaling. Below is rough overview of API.
General Notes:
  * Want to try to avoid **using the Formatter to scale/transform values, and
    passing the locator an array of scaled/transformed values**. Makes more sense
    to instead define separate **axis transforms**, then can use locators and
    formatters like normal, as they were intended to be used. This way, if e.g.
    matching frequency-axis with wavelength-axis, just conver the **axis limits**
    so they match, then you're good.
Scales:
  * These are complicated. See: https://matplotlib.org/_modules/matplotlib/scale.html#ScaleBase
    Use existing ones as inspiration -- e.g. InverseScale modeled after LogScale.
  * Way to think of these is that *every single value you see on an axes first
    gets secretly converted through some equation*, e.g. logarithm, and plotted
    linearly in that transformation space.
  * Methods include:
      - get_transform(), which should return an mtransforms.Transform instance
      - set_default_locators_and_formatters(), which should return
        default locators and formatters
      - limit_range_for_scale(), which can be used to raise errors/clip
        stuff not within that range. From Mercator example: unlike the
        autoscaling provided by the tick locators, this range limiting will
        always be adhered to, whether the axis range is set manually,
        determined automatically or changed through panning and zooming.
  * Also, have to be 'registered' unlike locators and formatters, which
    can be passed to the 'set' methods. Or maybe not?
Transforms:
  * These are complicted. See: https://matplotlib.org/_modules/matplotlib/transforms.html#Transform
  * Attributes:
      - input_dims, output_dims, is_separable, and has_inverse; the dims are because
        transforms can be N-D, but for *scales* are always 1, 1. Note is_separable is
        true if transform is separable in x/y dimensions.
  * Methods:
      - transform(): transforms N-D coordinates, given M x N array of values. Can also
        just declare transform_affine or transform_non_affine.
      - inverted(): if has_inverse True, performs inverse transform.
Locators:
  * These are complicated. See: https://matplotlib.org/_modules/matplotlib/ticker.html#Locator
  * Special:
      - __init__() not defined on base class but *must* be defined for subclass.
  * Methods include:
      - tick_values(), which accepts vmin/vmax and returns values of located ticks
      - __call__(), which can return data limits, view limits, or
        other stuff; not sure how this works or when it's invoked.
      - view_limits(), which changes the *view* limits from default vmin, vmax
        to prevent singularities (uses mtransforms.nonsingular method; for
        more info on this see: https://matplotlib.org/_modules/matplotlib/transforms.html#nonsingular)
  * Methods that usually can be left alone:
      - raise_if_exceeds(), which just tests if ticks exceed MAXTICKS number
      - autoscale(), which calls the internal locator 'view_limits' with
        result of axis.get_view_interval()
      - pan() and zoom() for interactive purposes
Formatters:
  * Easy to construct: just build with FuncFormatter a function that accepts
    the number and a 'position', which maybe is used for offset or something
    but almost always don't touch it, leave it default.
Normalizers:
  * Generally these are used for colormaps, easy to construct: require
    only an __init__ method and a __call__ method.
  * The init method takes vmin, vmax, and clip, and can define custom
    attributes. The call method just returns a *masked array* to handle NaNs,
    and call transforms data from physical units to *normalized* units
    from 0-1, representing position in colormap.
"""
#------------------------------------------------------------------------------#
# Imports
#------------------------------------------------------------------------------#
import re
from . import utils
from fractions import Fraction
from types import FunctionType
import numpy as np
import numpy.ma as ma
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
import matplotlib.scale as mscale
import matplotlib.transforms as mtransforms

#------------------------------------------------------------------------------#
# Tick scales
#------------------------------------------------------------------------------#
scales = ['linear','log','symlog','logit', # builtin
          'sine','mercator','inverse'] # custom
def Scale(scale, **kwargs):
    """
    Generate arbitrary scale object.
    """
    args = []
    if utils.isvector(scale):
        scale, args = scale[0], scale[1:]
    # print('scale', scale, args)
    if scale in scales and not args:
        pass # already registered
    elif scale=='cutoff':
        scale = CutoffScaleFactory(*args, **kwargs)
    else:
        raise ValueError(f'Unknown scale {scale}.')
    return scale

def CutoffScaleFactory(l, u, scale=np.inf, name='cutoff'):
    """
    Constructer for scale with custom cutoffs. Three options here:
      1. Put a 'cliff' between two numbers (default).
      2. Accelerate the scale gradient between two numbers (scale>1).
      3. Deccelerate the scale gradient between two numbers (scale<1). So
         scale is fast on edges but slow in middle.
    TODO:
      * Alongside this, create method for drawing those cutoff diagonal marks
        with white space between.
    See: https://stackoverflow.com/a/5669301/4970632 for multi-axis solution
    and for this class-based solution. Note the space between 1-9 in Paul's answer
    is because actual cutoffs were 0.1 away (and tick locs are 0.2 apart).
    """
    scale_name = name # have to copy to different name
    class CutoffScale(mscale.ScaleBase):
        # Declare name
        name = scale_name
        def __init__(self, axis, **kwargs):
            mscale.ScaleBase.__init__(self)
            self.name = scale_name

        def get_transform(self):
            return self.CutoffTransform()

        def set_default_locators_and_formatters(self, axis):
            pass # for now default can be same as for ScaleBase

        class CutoffTransform(mtransforms.Transform):
            # Create transform object
            input_dims = 1
            output_dims = 1
            is_separable = True
            lower = l
            upper = u
            def __init__(self):
                mtransforms.Transform.__init__(self)
            def transform(self, a):
                a = np.array(a) # very numpy array
                aa = a.copy()
                m1 = (a>self.lower)
                m2 = (a>self.upper)
                m3 = (a>self.lower) & (a<self.upper)
                if scale==np.inf:
                    aa[m1] = a[m1] - (self.upper - self.lower)
                    aa[m3] = self.lower
                else:
                    aa[m2] = a[m2] - (self.upper - self.lower)*(1 - 1/scale)
                    aa[m3] = a[m3] - (a[m3] - self.lower)*(1 - 1/scale)
                return aa
            def transform_non_affine(self, a):
                return self.transform(a)
            def inverted(self):
                return CutoffScale.InvertedCutoffTransform()

        class InvertedCutoffTransform(mtransforms.Transform):
            input_dims = 1
            output_dims = 1
            is_separable = True
            lower = l
            upper = u
            def __init__(self):
                mtransforms.Transform.__init__(self)
            def transform(self, a):
                a = np.array(a)
                aa = a.copy()
                n = (self.upper-self.lower)*(1 - 1/scale)
                m1 = (a>self.lower)
                m2 = (a>self.upper - n)
                m3 = (a>self.lower) & (a<(self.upper - n))
                if scale==np.inf:
                    aa[m1] = a[m1] + (self.upper - self.lower)
                else:
                    aa[m2] = a[m2] + n
                    aa[m3] = a[m3] + (a[m3] - self.lower)*(1 - 1/scale)
                return aa
            def transform_non_affine(self, a):
                return self.transform(a)
            def inverted(self):
                return CutoffScale.CutoffTransform()

    # Register and return
    mscale.register_scale(CutoffScale)
    print(f'Registered scale "{scale_name}".')
    return scale_name

class MercatorLatitudeScale(mscale.ScaleBase):
    """
    See: https://matplotlib.org/examples/api/custom_scale_example.html
    The scale function:
        ln(tan(y) + sec(y))
    The inverse scale function:
        atan(sinh(y))
    Applies user-defined threshold below +/-90 degrees above and below which nothing
    will be plotted. See: http://en.wikipedia.org/wiki/Mercator_projection
    Mercator can actually be useful in some scientific contexts; one of Libby's
    papers uses it I think.
    """
    name = 'mercator'
    def __init__(self, axis, *, thresh=85.0, **kwargs):
        # Initialize
        mscale.ScaleBase.__init__(self)
        if thresh >= 90.0:
            raise ValueError('Threshold "thresh" must be <=90.')
        self.thresh = thresh

    def get_transform(self):
        # Return special transform object
        return self.MercatorLatitudeTransform(self.thresh)

    def limit_range_for_scale(self, vmin, vmax, minpos):
        # *Hard* limit on axis boundaries
        return max(vmin, -self.thresh), min(vmax, self.thresh)

    def set_default_locators_and_formatters(self, axis):
        # Apply these
        axis.set_major_locator(Locator(20)) # every 10 degrees
        axis.set_major_formatter(Formatter('deg'))
        axis.set_minor_formatter(Formatter('null'))

    class MercatorLatitudeTransform(mtransforms.Transform):
        # Default attributes
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True
        def __init__(self, thresh):
            # Initialize, declare attribute
            mtransforms.Transform.__init__(self)
            self.thresh = thresh
        def transform_non_affine(self, array):
            # For M N-dimensional transform, transform MxN into result
            # So numbers stay the same, but data will then be linear in the
            # result of the math below.
            array = np.radians(array) # convert to radians
            masked = ma.masked_where((array < -self.thresh) | (array > self.thresh), array)
            if masked.mask.any():
                return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
            else:
                return np.log(np.abs(np.tan(array) + 1.0 / np.cos(array)))
        def inverted(self):
            # Just call inverse transform class
            return MercatorLatitudeScale.InvertedMercatorLatitudeTransform(self.thresh)

    class InvertedMercatorLatitudeTransform(mtransforms.Transform):
        # As above, but for the inverse transform
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True
        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh
        def transform_non_affine(self, a):
            return np.degrees(np.arctan(np.sinh(a)))
        def inverted(self):
            return MercatorLatitudeScale.MercatorLatitudeTransform(self.thresh)

class SineLatitudeScale(mscale.ScaleBase):
    """
    The scale function:
        sin(rad(y))
    The inverse scale function:
        deg(arcsin(y))
    """
    name = 'sine'
    def __init__(self, axis, **kwargs):
        # Initialize
        mscale.ScaleBase.__init__(self)

    def get_transform(self):
        # Return special transform object
        return self.SineLatitudeTransform()

    def limit_range_for_scale(self, vmin, vmax, minpos):
        # *Hard* limit on axis boundaries
        return max(vmin, -90), min(vmax, 90)

    def set_default_locators_and_formatters(self, axis):
        # Apply these
        ticks = np.arange(-80, 81, 20)
        axis.set_major_locator(mticker.FixedLocator(ticks))
        axis.set_major_formatter(CoordinateFormatter(cardinal=False, deg=True))
        axis.set_minor_formatter(mticker.NullFormatter())

    class SineLatitudeTransform(mtransforms.Transform):
        # Default attributes
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True
        def __init__(self):
            # Initialize, declare attribute
            mtransforms.Transform.__init__(self)
        def transform_non_affine(self, a):
            # Transformation
            with np.errstate(invalid='ignore'): # NaNs will always be False
                m = (a >= -90) & (a <= 90)
            if not m.all():
                aa = ma.masked_where(~m, a)
                return ma.sin(np.deg2rad(aa))
            else:
                return np.sin(np.deg2rad(a))
        def inverted(self):
            # Just call inverse transform class
            return SineLatitudeScale.InvertedSineLatitudeTransform()

    class InvertedSineLatitudeTransform(mtransforms.Transform):
        # As above, but for the inverse transform
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True
        def __init__(self):
            mtransforms.Transform.__init__(self)
        def transform_non_affine(self, a):
            # Clipping, instead of setting invalid, fixes weird issue where
            # ylim is inappropriately zoomed way in
            aa = a.copy()
            aa[a < -1] = -1
            aa[a >  1] = 1
            return np.rad2deg(ma.arcsin(aa))
        def inverted(self):
            return MercatorLatitudeScale.SineLatitudeTransform()

class InverseScale(mscale.ScaleBase):
    """
    Similar to LogScale, but this scales to be linear in *inverse* of x. Very
    useful e.g. to plot wavelengths on twin axis with wavenumbers.
    Important note: Unlike log-scale, we can't just warp the space between
    the axis limits -- have to actually change axis limits. This scale will
    invert and swap the limits you provide. Weird! But works great!
    """
    # Declare name
    name = 'inverse'
    def __init__(self, axis, minpos=1e-2, **kwargs):
        # Initialize (note thresh is always needed)
        mscale.ScaleBase.__init__(self)
        self.minpos = minpos

    def get_transform(self):
        # Return transform class
        return self.InverseTransform(self.minpos)

    def limit_range_for_scale(self, vmin, vmax, minpos):
        # *Hard* limit on axis boundaries
        # vmin = self.minpos if vmin<=0 else vmin
        # vmax = self.minpos if vmax<=0 else vmax
        # print(vmax, vmin)
        # return 1.0/vmax, 1.0/vmin # also *reverses* the axis direction, for some reason (not sure how, because we swap vmin/vmax here)
        # Above was dumb, see LogScale example; this should set the limits
        # in *scaled coordinates* (e.g. log uses -1000, meaning 10^(-1000))
        return vmin, vmax

    def set_default_locators_and_formatters(self, axis):
        # Consider changing this
        # TODO: fix minor locator issue
        axis.set_major_locator(mticker.LogLocator(base=10, subs=[1]))
        axis.set_major_formatter(mticker.LogFormatter())
        axis.set_minor_locator(mticker.LogLocator(base=10, subs='auto'))
        axis.set_minor_formatter(mticker.NullFormatter())

    class InverseTransform(mtransforms.Transform):
        # Create transform object
        input_dims = 1
        output_dims = 1
        is_separable = True
        def __init__(self, minpos):
            mtransforms.Transform.__init__(self)
            self.minpos = minpos
        def transform(self, a, eps=1e-2):
            a = np.array(a)
            aa = a.copy()
            aa[a<=0] = eps
            # aa[a<=0] = np.nan # minpos
            return 1.0/aa
        def transform_non_affine(self, a):
            return self.transform(a)
        def inverted(self):
            return InverseScale.InvertedInverseTransform(self.minpos)

    class InvertedInverseTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True
        def __init__(self, minpos):
            mtransforms.Transform.__init__(self)
            self.minpos = minpos
        def transform(self, a, eps=1e-2):
            a = np.array(a)
            aa = a.copy()
            aa[a<=0] = eps
            # aa[a<=0] = np.nan # messes up automatic ylim setting
            return 1.0/aa
        def transform_non_affine(self, a):
            return self.transform(a)
        def inverted(self):
            return InverseScale.InverseTransform(self.minpos)

# Register hard-coded scale names, so user can set_xscale and set_yscale with strings
mscale.register_scale(InverseScale)
mscale.register_scale(SineLatitudeScale)
mscale.register_scale(MercatorLatitudeScale)

#------------------------------------------------------------------------------#
# Helper functions for instantiating arbitrary Locator and Formatter classes
# When calling these functions, the format() method should automatically
# detect presence of date axis by testing if unit converter is on axis is
# DateConverter instance
# See: https://matplotlib.org/api/units_api.html
# And: https://matplotlib.org/api/dates_api.html
# Also see: https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/axis.py
# The axis_date() method just sets the converter to the date one
#------------------------------------------------------------------------------#
def Locator(locator, *args, minor=False, time=False, **kwargs):
    """
    Default locator. Can be instantiated with a bunch of
    different objects.
    Argument:
        Can be number (specify multiples along which ticks
        are drawn), list (tick these positions), or string for dictionary
        lookup of possible locators.
    Optional:
        time: whether we want 'datetime' locators
        kwargs: passed to locator when instantiated
    Note: Default Locator includes 'nbins' option to subsample
    the points passed so that no more than 'nbins' ticks are selected.
    """
    # Do nothing, and return None if locator is None
    if isinstance(locator, mticker.Locator):
        return locator
    # Decipher user input
    if locator is None:
        if time:
            locator = mticker.AutoDateLocator(*args, **kwargs)
        elif minor:
            locator = mticker.AutoMinorLocator(*args, **kwargs)
        else:
            locator = mticker.AutoLocator(*args, **kwargs)
    elif type(locator) is str: # dictionary lookup
        if locator=='logminor':
            locator = 'log'
            kwargs.update({'subs':np.arange(0,10)})
        elif locator not in locators:
            raise ValueError(f'Unknown locator "{locator}". Options are {", ".join(locators.keys())}.')
        locator = locators[locator](*args, **kwargs)
    elif utils.isscalar(locator): # scalar variable
        locator = mticker.MultipleLocator(locator, *args, **kwargs)
    else:
        locator = mticker.FixedLocator(np.sort(locator), *args, **kwargs) # not necessary
    return locator

def Formatter(formatter, *args, time=False, tickrange=None, **kwargs):
    """
    As above, auto-interpret user input.
    Includes option for %-formatting of numbers and dates, passing a list of strings
    for explicitly overwriting the text.
    Argument:
        can be number (specify max precision of output), list (set
        the strings on integers of axis), string (for .format() or percent
        formatting), string for dictionary lookup of possible
        formatters, Formatter instance, or function.
    Optional:
        time: whether we want 'datetime' formatters
        kwargs: passed to locator when instantiated
    """
    # Already have a formatter object
    if isinstance(formatter, mticker.Formatter): # formatter object
        return formatter
    # Interpret user input
    if formatter is None: # by default use my special super cool formatter, better than original
        if time:
            formatter = mdates.AutoDateFormatter(*args, **kwargs)
        else:
            formatter = CustomFormatter(*args, tickrange=tickrange, **kwargs)
    elif isinstance(formatter, FunctionType):
        formatter = mticker.FuncFormatter(formatter, *args, **kwargs)
    elif type(formatter) is str: # assumption is list of strings
        if '{x}' in formatter:
            formatter = mticker.StrMethodFormatter(formatter, *args, **kwargs) # new-style .format() formatter
        elif '%' in formatter:
            if time:
                formatter = mdates.DateFormatter(formatter, *args, **kwargs) # %-style, dates
            else:
                formatter = mticker.FormatStrFormatter(formatter, *args, **kwargs) # %-style, numbers
        else:
            if formatter not in formatters:
                raise ValueError(f'Unknown formatter "{formatter}". Options are {", ".join(formatters.keys())}.')
            if formatter in ['deg','deglon','deglat','lon','lat']:
                kwargs.update({'deg':('deg' in formatter)})
            formatter = formatters[formatter](*args, **kwargs)
    elif utils.isscalar(formatter): # interpret scalar number as *precision*
        formatter = CustomFormatter(formatter, *args, tickrange=tickrange, **kwargs)
    else:
        formatter = mticker.IndexFormatter(formatter) # list of strings on the integers
        # formatter = mticker.FixedFormatter(formatter) # list of strings on the major ticks, wherever they may be
    return formatter

#-------------------------------------------------------------------------------
# Formatting classes for mapping numbers (axis ticks) to formatted strings
# Create pseudo-class functions that actually return auto-generated formatting
# classes by passing function references to Funcformatter
#-------------------------------------------------------------------------------
# First the default formatter
def CustomFormatter(precision=2, tickrange=[-np.inf, np.inf]):
    """
    Format as a number, with N sigfigs, and trimming trailing zeros.
    Recall, must pass function in terms of n (number) and loc.
    Arguments:
        precision: max number of digits after decimal place (default 3)
        tickrange: range [min,max] in which we draw tick labels (allows removing
            tick labels but keeping ticks in certain region; default [-np.inf,np.inf])
    For minus sign scaling, see: https://tex.stackexchange.com/a/79158/73149
    """
    # Format definition
    if tickrange is None:
        tickrange = [-np.inf, np.inf]
    elif utils.isscalar(tickrange): # use e.g. -1 for no ticks
        tickrange = [-tickrange, tickrange]
    def f(value, location):
        # Exit if not in tickrange
        eps = abs(value)/1000
        if (value+eps)<tickrange[0] or (value-eps)>tickrange[1]:
            return '' # avoid some ticks
        # Return special string
        # * Note *cannot* use 'g' because 'g' precision operator specifies count of
        #   significant digits, not places after decimal place.
        # * There is no format that specifies digits after decimal place AND trims trailing zeros.
        string = f'{{{0}:.{precision:d}f}}'.format(value) # f-string compiled, then format run
        if '.' in string: # g-style trimming
            string = string.rstrip('0').rstrip('.')
        if string=='-0': # special case
            string = '0'
        if value>0 and string=='0':
            raise RuntimeError('Tried to round tick position label to zero. Add precision or use an exponential formatter.')
            # pass
        # Use unicode minus instead of ASCII hyphen (which is default)
        string = re.sub('-', '−', string) # pure unicode minus
        # string = re.sub('-', '${-}$', string) # latex version
        # string = re.sub('-', u'\u002d', string) # unicode hyphen minus, looks same as hyphen
        # string = re.sub('-', r'\scalebox{0.75}[1.0]{$-$}', string)
        return string
    # And create object
    return mticker.FuncFormatter(f)

#------------------------------------------------------------------------------#
# Formatting with prefixes
#------------------------------------------------------------------------------#
def PrefixSuffixFormatter(*args, prefix=None, suffix=None, **kwargs):
    """
    Arbitrary prefix and suffix in front of values.
    """
    prefix = prefix or ''
    suffix = suffix or ''
    def f(value, location):
        # Finally use default formatter
        func = CustomFormatter(*args, **kwargs)
        return prefix + func(value, location) + suffix
    # And create object
    return mticker.FuncFormatter(f)

def MoneyFormatter(*args, **kwargs):
    """
    Arbitrary prefix and suffix in front of values.
    """
    # And create object
    return PrefixSuffixFormatter(*args, prefix='$', **kwargs)

#------------------------------------------------------------------------------#
# Formatters for dealing with one axis in geographic coordinates
#------------------------------------------------------------------------------#
def CoordinateFormatter(*args, cardinal=None, deg=True, **kwargs):
    """
    Generalized function for making LatFormatter and LonFormatter.
    Requires only which string to use for points left/right of zero (e.g. W/E, S/N).
    """
    def f(value, location):
        # Optional degree symbol
        suffix = ''
        if deg:
            suffix = '\N{DEGREE SIGN}' # Unicode lookup by name
        # Apply suffix if not on equator/prime meridian
        if isinstance(cardinal,str):
            if value<0:
                value *= -1
                suffix += cardinal[0]
            elif value>0:
                suffix += cardinal[1]
        # Finally use default formatter
        func = CustomFormatter(*args, **kwargs)
        return func(value, location) + suffix
    # And create object
    return mticker.FuncFormatter(f)

def LatFormatter(*args, **kwargs):
    """
    Just calls CoordinateFormatter. Note the strings are only used if
    we set cardinal=True, otherwise just prints negative/positive degrees.
    """
    return CoordinateFormatter(*args, cardinal='SN', **kwargs)

def LonFormatter(*args, **kwargs):
    """
    Just calls CoordinateFormatter. Note the strings are only used if
    we set cardinal=True, otherwise just prints negative/positive degrees.
    """
    return CoordinateFormatter(*args, cardinal='WE', **kwargs)

#------------------------------------------------------------------------------#
# Formatters with fractions
#------------------------------------------------------------------------------#
def FracFormatter(number, symbol):
    """
    Format as fractions, multiples of some value, e.g. a physical constant.
    """
    def f(n, loc): # must accept location argument
        frac = Fraction(n/number).limit_denominator()
        if n==0: # zero
            string = '0'
        elif frac.denominator==1: # denominator is one
            if frac.numerator==1:
                string = f'${symbol}$'
            elif frac.numerator==-1:
                string = f'${{-}}{symbol:s}$'
            else:
                string = f'${frac.numerator:d}{symbol:s}$'
        elif frac.numerator==1: # numerator is +/-1
            string = f'${symbol:s}/{frac.denominator:d}$'
        elif frac.numerator==-1:
            string = f'${{-}}{symbol:s}/{frac.denominator:d}$'
        else: # and again make sure we use unicode minus!
            string = f'${frac.numerator:d}{symbol:s}/{frac.denominator:d}$'
        # string = re.sub('-', '−', string) # minus will be converted to unicode version since it's inside LaTeX math
        return string
    # And create FuncFormatter class
    return mticker.FuncFormatter(f)

def PiFormatter():
    """
    Return FracFormatter, where the number is np.pi and
    symbol is $\pi$.
    """
    return FracFormatter(np.pi, r'\pi')

def eFormatter():
    """
    Return FracFormatter, where the number is np.exp(1) and
    symbol is $e$.
    """
    return FracFormatter(np.exp(1), 'e')

# Declare dictionaries
# Includes some custom classes, so has to go at end
locators = {
    'none':        mticker.NullLocator,
    'null':        mticker.NullLocator,
    'log':         mticker.LogLocator,
    'maxn':        mticker.MaxNLocator,
    'linear':      mticker.LinearLocator,
    'log':         mticker.LogLocator,
    'multiple':    mticker.MultipleLocator,
    'fixed':       mticker.FixedLocator,
    'index':       mticker.IndexLocator,
    'symmetric':   mticker.SymmetricalLogLocator,
    'logit':       mticker.LogitLocator,
    'minor':       mticker.AutoMinorLocator,
    'microsecond': mdates.MicrosecondLocator,
    'second':      mdates.SecondLocator,
    'minute':      mdates.MinuteLocator,
    'hour':        mdates.HourLocator,
    'day':         mdates.DayLocator,
    'weekday':     mdates.WeekdayLocator,
    'month':       mdates.MonthLocator,
    'year':        mdates.YearLocator,
    }
formatters = { # note default LogFormatter uses ugly e+00 notation
    'none':      mticker.NullFormatter,
    'null':      mticker.NullFormatter,
    'strmethod': mticker.StrMethodFormatter,
    'formatstr': mticker.FormatStrFormatter,
    'scalar':    mticker.ScalarFormatter,
    'log':       mticker.LogFormatterSciNotation,
    'eng':       mticker.LogFormatterMathtext,
    'sci':       mticker.LogFormatterSciNotation,
    'logit':     mticker.LogitFormatter,
    'eng':       mticker.EngFormatter,
    'percent':   mticker.PercentFormatter,
    '$':         MoneyFormatter,
    'pi':        PiFormatter,
    'e':         eFormatter,
    'deg':       CoordinateFormatter,
    'lat':       LatFormatter,
    'lon':       LonFormatter,
    'deglat':    LatFormatter,
    'deglon':    LonFormatter,
    }
