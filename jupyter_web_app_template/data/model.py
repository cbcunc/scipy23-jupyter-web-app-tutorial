# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/data.model.ipynb.

# %% auto 0
__all__ = ['DataModel']

# %% ../../nbs/data.model.ipynb 2
from traitlets import HasTraits, TraitError, Unicode, Int, Float, validate, observe
import pandas as pd
import ipywidgets as widgets
from scipy.signal import savgol_filter
import statsmodels.api as sm
import json

# %% ../../nbs/data.model.ipynb 3
class DataModel(HasTraits):
    
    path = Unicode()
    from_year = Int()
    to_year = Int()
    ema_span = Int(default_value = 2)
    frac = Float(default_value = .05)
    it = Int(default_value = 3)
    window_size = Int(default_value = 5)
    poly_order = Int(default_value = 3)
    min = Int()
    max = Int()
    
    def __init__(self, path='../data/land-ocean-temp-index.csv'):
        self.path = path
        self.df = self.upload_df_from_path()
        self.selected = self.df
        self.min = min(self.df['Year'])
        self.max = max(self.df['Year'])
        self.to_year = self.max
        self.from_year = self.min
        
    @observe('from_year')
    def _observe_to_year(self, change):
        self.selected = self.df[(self.df['Year'] >= int(change['new'])) & (self.df['Year'] <= int(self.to_year))]
        self.len = len(self.df.index)
        
    @observe('to_year')
    def _observe_to_year(self, change):
        self.selected = self.df[(self.df['Year'] >= int(self.from_year)) & (self.df['Year'] <= int(change['new']))]
        self.len = len(self.df.index)
        
    @observe('ema_span')
    def _observe_ema_span(self, change):
        self._update_EMA_column(change['new'])
        
    @observe('frac')
    def _observe_frac(self, change):
        self._update_LOWESS_column(change['new'], self.it)
        
    @observe('it')
    def _observe_it(self, change):
        self._update_LOWESS_column(self.frac, change['new'])
        
    @observe('window_size')
    def _observe_window_size(self, change):
        self._update_savgol_column(change['new'], self.poly_order)

    @observe('poly_order')
    def _observe_window_size(self, change):
        self._update_savgol_column(self.window_size, change['new'])
        
    def _update_EMA_column(ema_span):
        df['EMA'] = df['Temperature'].ewm(span=ema_span, adjust=False).mean()
        
    def _update_LOWESS_column(frac, it):
        # Apply LOESS smoothing to the Temperature column
        loess_smooth = sm.nonparametric.lowess(df['Temperature'], df['Year'], frac=frac)
        df['LOWESS'] = loess_smooth[:, 1]
        
    def _update_savgol_column(window_size, poly_order):
        # Apply Savitzky-Golay smoothing to the Temperature column
        df['Savitzky-Golay'] = savgol_filter(df['Temperature'], window_size, poly_order)

    @validate('ema_span')
    def _valid_ema_span(self, change):
        if proposal['value'] < 1:
            raise TraitError('ema_span must be greater or equal to one')
            
    @validate('frac')
    def _valid_frac(self, change):
        if proposal['value'] < 0 or proposal['value'] > 1:
            raise TraitError('frac must be in the range of 0 to 1')
            
    @validate('it')
    def _valid_frac(self, change):
        if proposal['value'] < 1 or proposal['value'] > 10:
            raise TraitError('frac must be in the range of 1 to 10')
            
    @validate('window_size')
    def _valid_frac(self, change):
        if proposal['value'] < 0 or proposal['value'] > self.len:
            raise TraitError('window_size must be less than or equal to the size of df')
            
    @validate('poly_order')
    def _valid_frac(self, change):
        if proposal['value'] < 0 or proposal['value'] > self.window_size:
            raise TraitError('poly_order must be less than window_length')
        
    @validate('from_year')
    def _valid_from_year(self, proposal):
        if proposal['value'] > self.to_year:
            raise TraitError('from_year must be less than or equal to to_year')
        if proposal['value'] < self.min:
            raise TraitError('from_year out of temperature data range')
        return proposal['value']
    
    @validate('to_year')
    def _valid_to_year(self, proposal):
        if proposal['value'] < self.from_year:
            raise TraitError('to_year must be greater than or equal to from_year')
        if proposal['value'] > self.max:
            raise TraitError('to_year out of temperature data range')
        return proposal['value']
    
    def upload_df_from_path(self):
        return pd.read_csv(self.path, escapechar='#')
        
    def __repr__(self):
        return json.dumps(self.trait_values(), indent=2)
