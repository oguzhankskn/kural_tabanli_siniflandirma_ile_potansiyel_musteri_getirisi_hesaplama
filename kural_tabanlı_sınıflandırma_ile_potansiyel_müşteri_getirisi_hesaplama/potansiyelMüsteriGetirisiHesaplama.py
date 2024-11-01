#KURAL TABANLI SINIFLANDIRMA İLE POTANSİYEL MÜŞSTERİ GETİRİSİ HESAPLAMA



################################################################################
#İŞ PROBLEMİ
################################################################################
#Bir oyun şirketinin müşterilerinin bazı özelliklerini kullanarak seviye tabanlı (level based) yeni müşteri tanımları
#oluşturmak ve bu yeni müşteri tanımlarına göre segmentler oluşturup bu segmentlere göre yeni gelebilecek müşterilerin
#şirkete ortalama ne kadar kazandırabileceğini tahmin etmek istemektedir.

#Örnek: Türkiye'den IOS kullanıcısı olan 25 yaşındaki bir erkek kullanıcının ortalama ne kadar kazandırabileceği belirlenmek isteniyor


################################################################################
#Persona.csv veri seti uluslararası bir oyun şirketinin sattığı ürünlerin fiyatlarını ve bu ürünleri satın alan kullanıcıların bazı
#demografik bilgilerini barındırmaktadır. Veri seti her satış işleminde oluşan kayıtlardan meydana gelmektedir. Bunun anlamı tablo
#tekilleştirilmemiştir. Diğer bir ifade ile belirli demografik özelliklere sahip bir kullanıcı briden fazla alışveriş yapmış olabilir.


#PRICE: müşterinin harcama tutarı
#SOURCE : müşterinin bağlandığı cihaz türü
#SEX: müşterinin cinsiyeti
#COUNTRY: müşterinin ülkesi
#AGE: müşterinin yaşı

##############################################   UYGULAMA ÖNCESİ TABLO  ################################################
#          PRICE     SOURCE   SEX   COUNTRY   AGE
# 0         39       android  male     bra     17
# 1         39       android  male     bra     17
# 2         49       android  male     bra     17
# 3         29       android  male     tur     17
# 4         49       android  male     tur     17


#######################################   UYGULAMA SONRASI ELDE EDİLEN TABLO  ##########################################
#           customer_level_based          PRICE       SEGMENT
# 0         BRA_ANDROID_FEMALE_0_18     1139.800000       A
# 1         BRA_ANDROOD_FEMALE_19_23    1070.600000       A
# 2         BRA_ANDROOD_FEMALE_24_30     508.142857       A
# 3         BRA_ANDROOD_FEMALE_31_40     233.166667       C
# 4         BRA_ANDROOD_FEMALE_41_70     236.666667       C

import pandas as pd


df = pd.read_csv("persona.csv")

#VERİYE GENEL BAKIŞ
def check_func(dataframe, head=5):
    ####################    SHAPE    #######################
    print("SHAPE")
    print(df.shape)
    print("------------------------------------------------")
    ####################    HEAD    ########################
    print("HEAD")
    print(df.head(head))
    print("------------------------------------------------")
    ####################     TAİL    #######################
    print("TAİL")
    print(df.tail(head))
    print("------------------------------------------------")
    ####################    NUNIQUE    #####################
    print("NUNIQUE")
    print(df.nunique())
    print("------------------------------------------------")
    ####################    DTYPE    #######################
    print("DTYPES")
    print(df.dtypes)
    print("------------------------------------------------")
    ################    VALUE COUNTS    ####################
    print("VALUE_COUNTS")
    print(df["COUNTRY"].value_counts())
    print("------------------------------------------------")
    ####################    DESCRİBE    ####################
    print("DESCRİBE")
    print(df.describe().T)

check_func(df)




#kaç unique SOURCE değer var, frekansları neler
df["SOURCE"].nunique()
df["SOURCE"].value_counts()

#kaç unique PRICE vardır
df["PRICE"].nunique()

#hangi PRICE'dan kaç satış gerçekleşmiş
df["PRICE"].value_counts()

#hangi ülkeden kaçar tane satış olmuş
df["COUNTRY"].value_counts()

#ülklere göre satışlardan toplam ne kadar kazanılmış
df.groupby("COUNTRY")["PRICE"].sum()

#SOURCE türlerine göre satış sayıları nedir
df["SOURCE"].value_counts()

#ülkelere göre PRICE ortalamaları nedir
df.groupby("COUNTRY")["PRICE"].mean()

#SOURCE'lere göre PRICE ortalaması nedir
df.groupby("SOURCE")["PRICE"].mean()

#COUNTRY-SOURCE kırılımında PRICE ortalamaları nedir
df.groupby(["COUNTRY", "SOURCE"]).agg({"PRICE": "mean" })




#COUNTRY, SOURCE, SEX, AGE kırılımında ortalama kazançlar nedir
agg_df = df.groupby(["COUNTRY", "SOURCE", "SEX", "AGE"]).agg({"PRICE" : "mean"}).sort_values("PRICE" , ascending=False) #sort_values ile sıralama işlemi


#indekste yer alan isimleri değişken ismine çevrilmesi
agg_df = agg_df.reset_index()



#age değişkenini kategorik değişkene çevirme, aralıkları ikna edici şekilde oluşturuldu
bins = [0, 18, 23, 30, 40, agg_df["AGE"].max()]
labels = ["0_18", "19_23", "24_30", "31_40", "41_70"]

agg_df["AGE_CAT"] = pd.cut(agg_df["AGE"], bins, labels=labels)
agg_df.head()


#Yeni seviye tabanlı müşteriler tanımlandı
agg_df["customers_level_based"] = agg_df[["COUNTRY", "SOURCE", "SEX", "AGE_CAT"]].agg(lambda x: "_".join(x).upper(), axis=1)

#agg_df["customers_level_based"] = [ "_".join(i).upper for i in agg_df.drop(["AGE","PRICE"], axis=1).values]            #2. yöntem

#[row[0].upper() + "_" + row[1].upper() + "_" + row[2].upper() + "_" + row[5].upper() for row in agg_df.values]         #3. yöntem


#gereksiz değerleri çıkarma işlemi
agg_df = agg_df[["customers_level_based", "PRICE"]]
agg_df.head()

#for i in agg_df["customers_level_based"].values:
#    print(i.split("_"))

#Burada ufak bir problem var. Birçok aynı segment olacak
#Örneğin USA_ANDROID_MALE_0_18 segmentinden birçok sayıda olacak
#kontrol edelim
agg_df["customers_level_based"].value_counts()

#bu sebeple segmentlere göre groupby yaptıktan sonra price ortalamalarını almalı ve segmentleri tekilleştirmelisiniz
agg_df = agg_df.groupby("customers_level_based").agg({"PRICE" : "mean"})

agg_df = agg_df.reset_index()



#Yeni müşterileri segmentlere ayrılma işlemi
agg_df["SEGMENT"] = pd.qcut(agg_df["PRICE"], 4, labels=["D","C","B","A"])

agg_df.groupby(("SEGMENT"), observed=False)["PRICE"].mean()                                                                    #segment ortalamları hesaplandı


#Yeni gelen müşterileri sınıflandırıp, ne kadar gelir getirebileceklerini tahmin ediniz
print("---------------------------------------------------------")
print("EKLENEN YENİ DEĞERLER TAHMİNİ")
print("---------------------------------------------------------")

new_user = ("TUR_ANDROID_FEMALE_31_40")                                                                                 #"TUR_ANDROID_FEMALE_31_40" müşteri oluşturuldu
print(agg_df[agg_df["customers_level_based"] == new_user])                                                              #değer tahmini tabloya yansıdı

new_user2 = ("FRA_IOS_FEMALE_31_40")                                                                                    #"FRA_IOS_FEMALE_31_40" müşteri oluşturuldu
print(agg_df[agg_df["customers_level_based"] == new_user2])                                                             #değer tahmini tabloya yansıdı