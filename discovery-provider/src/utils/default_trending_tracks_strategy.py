from datetime import datetime
from dateutil.parser import parse
from src.utils.trending_strategy import TrendingType, TrendingVersion

N = 1
a = max
M = pow
F = 50
O = 1
R = 0.25
i = 0.01
q = 40.0
T = {'day': 1, 'week':7, 'month':30, 'year':365, 'allTime': 100000}

def z(time, track):
    # pylint: disable=W,C,R
    E=track['listens']
    e=track['windowed_repost_count']
    t=track['repost_count']
    x=track['windowed_save_count']
    A=track['save_count']
    o=track['created_at']
    l=track['owner_follower_count']
    j=track['karma']
    if l<3:
        return{'score':0,**track}
    H=(N*E+F*e+O*x+R*t+i*A)*j
    L=T[time]
    K=datetime.datetime.now()
    w=parse(o)
    k=(K-w).days
    Q=1
    if k>L:
        Q=a((1.0/q),(M(q,(1-k/L))))
    return{'score':H*Q,**track}

class DefaultTrendingTracksStrategy:
    def __init__(self):
        self.trending_type = TrendingType.TRACKS
        self.version = TrendingVersion.DEFAULT

    def get_track_score(self, time, track):
        return z(time, track)
 