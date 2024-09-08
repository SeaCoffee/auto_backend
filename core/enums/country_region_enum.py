from enum import Enum

class Region(Enum):
    """
    Перечисление регионов, используемое для выбора конкретного региона.
    Каждый регион представлен как строка с его именем на латинице.
    """

    CRIMEA = 'CRIMEA'
    VINNYTSIA = 'VINNYTSIA'
    VOLYN = 'VOLYN'
    DNIPRO = 'DNIPRO'
    DONETSK = 'DONETSK'
    IVANO_FRANKIVSK = 'IVANO-FRANKIVSK'
    KHERSON = 'KHERSON'
    KHMELNYTSKYI = 'KHMELNYTSKYI'
    KYIV = 'KYIV'
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

    @classmethod
    def choices(cls):
        """
        Возвращает список кортежей с порядковым номером и значением региона для использования в полях с выбором.
        """
        return [(index + 1, key.value) for index, key in enumerate(cls)]