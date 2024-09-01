from enum import Enum

class Region(Enum):
    VINNYTSIA = 'VINNYTSIA'
    VOLYN = 'VOLYN'
    DNIPRO = 'DNIPRO'
    DONETSK = 'DONETSK'
    IVANO_FRANKIVSK = 'IVANO-FRANKIVSK'
    KHERSON = 'KHERSON'
    KHMELNYTSKYI = 'KHMELNYTSKYI'
    KYIV = 'KYIV'
    KYIV_OBLAST = 'KYIV OBLAST'
    KIROVOHRAD = 'KIROVOHRAD'
    LUHANSK = 'LUHANSK'
    LVIV = 'LVIV'
    MYKOLAIV = 'MYKOLAIV'
    ODESA = 'ODESA'
    POLTAVA = 'POLTAVA'
    RIVNE = 'RIVNE'
    SUMY = 'SUMY'
    TERNOPIL = 'TERNOPIL'
    KHARKIV = 'KHARKIV'
    ZAPORIZHZHIA = 'ZAPORIZHZHIA'
    ZHYTOMYR = 'ZHYTOMYR'
    CHERKASY = 'CHERKASY'
    CHERNIVTSI = 'CHERNIVTSI'
    CHERNIHIV = 'CHERNIHIV'
    CRIMEA = 'CRIMEA'

    @classmethod
    def choices(cls):
        return [(index + 1, key.value) for index, key in enumerate(cls)]

