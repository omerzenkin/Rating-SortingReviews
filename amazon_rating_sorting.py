import pandas as pd
import math
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df = pd.read_csv("data/amazon_review.csv")
df.head()
df.shape


###Görev 1: Average Rating’i güncel yorumlara göre hesaplayınız ve var olan average rating ile kıyaslayınız####

#Adım 1: Ürünün ortalama puanını hesaplayınız.
df["overall"].mean()


#Adım 2: Tarihe göre ağırlıklı puan ortalamasını hesaplayınız
df.info()
df.head()
df["reviewTime"] = pd.to_datetime(df["reviewTime"])
df["reviewTime"].max()
current_date = pd.to_datetime('2014-12-07 00:00:00')
df["days"] = (current_date - df["reviewTime"]).dt.days

# df["days"].describe().T
# df["days"].quantile(0.25)
# df["days"].describe([0.03, 0.05, 0.01, 0.25, 0.75, 0.90, 0.95, 0.99])

df['reviewTime'] = pd.to_datetime(df['reviewTime'], dayfirst=True)
current_date = pd.to_datetime(str(df['reviewTime'].max()))
df["day_diff2"] = (current_date - df['reviewTime']).dt.days
df.head()

df.loc[df["days"] <= df["days"].quantile(0.25), "overall"].mean()  #4.6957928802588995
df.loc[(df["days"] > df["days"].quantile(0.25)) & (df["days"] <= df["days"].quantile(0.50)), "overall"].mean() #4.636140637775961
df.loc[(df["days"] > df["days"].quantile(0.50)) & (df["days"] <= df["days"].quantile(0.75)), "overall"].mean() #4.571661237785016
df.loc[(df["days"] > df["days"].quantile(0.75)), "overall"].mean() #4.4462540716612375

def time_based_weighted_average(df, w1=28, w2=26, w3=24, w4=22):
    return df.loc[df["days"] <= df["days"].quantile(0.25), "overall"].mean() * w1 / 100 + \
           df.loc[(df["days"] > df["days"].quantile(0.25)) & (df["days"] <= df["days"].quantile(0.50)), "overall"].mean() * w2 / 100 + \
           df.loc[(df["days"] > df["days"].quantile(0.50)) & (df["days"] <= df["days"].quantile(0.75)), "overall"].mean() * w3 / 100 + \
           df.loc[(df["days"] > df["days"].quantile(0.75)), "overall"].mean() * w4 / 100

time_based_weighted_average(df, 30, 26, 22, 22)
df.head()

#Adım 3: Ağırlıklandırılmış puanlamada her bir zaman diliminin ortalamasını karşılaştırıp yorumlayınız
df.loc[df["days"] <= df["days"].quantile(0.25), "overall"].mean()
df.loc[df["days"] <= df["days"].quantile(0.75), "overall"].mean()
###Görev 2: Ürün için ürün detay sayfasında görüntülenecek  review’i belirleyiniz.

#Adım 1: helpful_no değişkenini üretiniz

df["helpful_no"] = df["total_vote"] - df["helpful_yes"]
df.head()

#Adım 2: score_pos_neg_diff, score_average_rating ve wilson_lower_bound skorlarını hesaplayıp veriye ekleyiniz.

########################3score_pos_neg_diff#########################

def score_up_down_diff(helpful_yes, helpful_no):
    return helpful_yes - helpful_no

df["score_pos_neg_diff"] = df.apply(lambda x: score_up_down_diff(x["helpful_yes"],
                                                                 x["helpful_no"]), axis=1)
df.sort_values("score_pos_neg_diff", ascending=False).head(10)

######################score_average_rating#############################3

def score_average_rating(helpful_yes, helpful_no):
    if helpful_yes+ helpful_no == 0:
        return 0
    return helpful_yes / (helpful_yes + helpful_no)

df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"], x["helpful_no"]), axis=1)

df.sort_values("score_average_rating", ascending=False).head()
df.head(20)
df[df["score_average_rating"] != 0]
##################wilson_lower_bound####################################

def wilson_lower_bound(helpful_yes, helpful_no, confidence=0.95):
    """
    Wilson Lower Bound Score hesapla

    - Bernoulli parametresi p için hesaplanacak güven aralığının alt sınırı WLB skoru olarak kabul edilir.
    - Hesaplanacak skor ürün sıralaması için kullanılır.
    - Not:
    Eğer skorlar 1-5 arasıdaysa 1-3 negatif, 4-5 pozitif olarak işaretlenir ve bernoulli'ye uygun hale getirilebilir.
    Bu beraberinde bazı problemleri de getirir. Bu sebeple bayesian average rating yapmak gerekir.

    Parameters
    ----------
    up: int
        up count
    down: int
        down count
    confidence: float
        confidence

    Returns
    -------
    wilson score: float

    """
    n = helpful_yes + helpful_no
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * helpful_yes / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)

df.sort_values("wilson_lower_bound", ascending=False).head(20)





















