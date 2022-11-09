import warnings
from pandas.core.common import SettingWithCopyWarning

warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

from . import rate
from . import recommendations
from . import utils
