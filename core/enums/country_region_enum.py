from enum import Enum

class Region(Enum):
    VINNYTSIA = 'Vinnytsia'
    VOLYN = 'Volyn'
    DNIPRO = 'Dnipro'
    DONETSK = 'Donetsk'
    IVANO_FRANKIVSK = 'Ivano-Frankivsk'
    KHERSON = 'Kherson'
    KHMELNYTSKYI = 'Khmelnytskyi'
    KYIV = 'Kyiv'
    KYIV_OBLAST = 'Kyiv Oblast'
    KIROVOHRAD = 'Kirovohrad'
    LUHANSK = 'Luhansk'
    LVIV = 'Lviv'
    MYKOLAIV = 'Mykolaiv'
    ODESSA = 'Odesa'
    POLTAVA = 'Poltava'
    RIVNE = 'Rivne'
    SUMY = 'Sumy'
    TERNOPIL = 'Ternopil'
    KHARKIV = 'Kharkiv'
    KHOLYNY = 'Khmelnytskyi'
    ZAPORIZHZHIA = 'Zaporizhzhia'
    ZHYTOMYR = 'Zhytomyr'
    CHERKASY = 'Cherkasy'
    CHERNIVTSI = 'Chernivtsi'
    CHERNIHIV = 'Chernihiv'
    Crimea = 'Crimea'


    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
