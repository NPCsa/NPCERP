from num2words import num2words
import re
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def convert_number_to_words(self,number,lang):
        if lang == 'ar':
            return self.convert_number(number)
        elif lang == 'en':
            return num2words(number, lang='en')

    def convert_number(self, numbers):
        number = numbers
        mask = "{0:.2f}"
        s_number = mask.format(number)
        split = s_number.split('.')
        post_fix = ""
        d_num = int(split[1])
        if d_num > 0:
            if len(split[1]) == 1:
                post_fix = " من العشرة"
            else:
                post_fix = " من المائة"

        if d_num > 0:
            post_fix = " فاصل " + self.convert_long(d_num) + post_fix

        result = self.convert_long(split[0]) + post_fix

        # remove extra spaces!
        result = re.sub(r"^\\s+", "", result)
        result = re.sub(r"\\b\\s{2,}\\b", " ", result)
        return result.strip()

    def convert_long(self, number):
        # 0 to 999 999 999 999
        if number == 0:
            return "صفر"

        s_number = str(number)

        # pad with "0"
        s_number = s_number.zfill(12)

        # XXXnnnnnnnnn
        billions = int(s_number[0:3])
        # nnnXXXnnnnnn
        millions = int(s_number[3:6])
        # nnnnnnXXXnnn
        hundred_thousands = int(s_number[6:9])
        # nnnnnnnnnXXX
        thousands = int(s_number[9:12])

        trad_billions = ""
        if billions == 0:
            trad_billions = ""
        elif billions == 1:
            trad_billions = " مليار "
        elif billions == 2:
            trad_billions = " ملياران "
        elif billions >= 3 and billions <= 10:
            trad_billions = self.convert_less_than_onethousand(billions) + " مليارات "
        else:
            trad_billions = self.convert_less_than_onethousand(billions) + " مليار "

        result = trad_billions

        trad_millions = ""
        if millions == 0:
            trad_millions = ""
        elif millions == 1:
            trad_millions = " مليون "
        elif millions == 2:
            trad_millions = " مليونان "
        elif millions >= 3 and millions <= 10:
            trad_millions = self.convert_less_than_onethousand(millions) + " ملايين "
        else:
            trad_millions = self.convert_less_than_onethousand(millions) + " مليون "

        if result.strip() and trad_millions.strip():
            result = result + " و "

        result = result + trad_millions

        trad_hundred_thousands = ""
        if hundred_thousands == 0:
            trad_hundred_thousands = ""
        elif hundred_thousands == 1:
            trad_hundred_thousands = "ألف "
        elif hundred_thousands == 2:
            trad_hundred_thousands = "ألفان "
        elif hundred_thousands >= 3 and hundred_thousands <= 10:
            trad_hundred_thousands = self.convert_less_than_onethousand(hundred_thousands) + " آلاف "
        else:
            trad_hundred_thousands = self.convert_less_than_onethousand(hundred_thousands) + " ألف "

        if result.strip() and trad_hundred_thousands.strip():
            result = result + " و "
        result = result + trad_hundred_thousands

        trad_thousand = self.convert_less_than_onethousand(thousands)
        if result.strip() and trad_thousand.strip():
            result = result + " و "
        result = result + trad_thousand

        # remove extra spaces!
        result = re.sub(r"^\\s+", "", result)
        result = re.sub(r"\\b\\s{2,}\\b", " ", result)
        return result.strip()

    def convert_less_than_onethousand(self, number):
        so_far = ""

        num_names = [
            "",
            " واحد",
            # "ONE",
            " اثنان",
            # "TWO",
            " ثلاثة",
            # "THREE",
            " اربعة",
            # "FOUR",
            " خمسة",
            # "FIVE",
            " ستة",
            # "SIX",
            " سبعة",
            # "SEVEN",
            " ثمانية",
            # "EIGHT",
            " تسعة",
            # "NINE",
            # "TEN",
            " عشرة",
            # "ELEVEN"
            " إحدى عشر",
            # "TWELVE",
            " إثنى عشر",
            # "THIRTEEN",
            " ثلاثة عشر",
            # "FOURTEEN",
            " اربعة عشر",
            # "FIFTEEN",
            " خمسة عشر",
            # "SIXTEEN",
            " ستة عشر",
            # "SEVENTEEN",
            " سبعة عشر",
            # "EIGHTEEN",
            " ثمانية عشر",
            # "NINETEEN"
            " تسعة عشر"
        ]

        tens_names = [
            "",
            " عشرة",
            # "TEN",
            " عشرون",
            # "TWENTY",
            " ثلاثون",
            # "THIRTY",
            " اربعون",
            # "FORTY",
            " خمسون",
            # "FIFTY",
            " ستون",
            # "SIXTY",
            " سبعون",
            # "SEVENTY",
            " ثمانون",
            # "EIGHTY",
            " تسعون"
            # "NINETY",
        ]

        if (number % 100 < 20):
            so_far = num_names[int(number % 100)]
            number /= 100
        else:
            so_far = num_names[int(number % 10)]
            number /= 10

            if so_far.strip() and tens_names[int(number % 10)].strip():
                so_far = so_far + " و "
            so_far = so_far + tens_names[int(number % 10)]
            number /= 10
        result = ""
        if so_far.strip():
            result = " و " + so_far
        else:
            result = so_far
        number = int(number)
        if number == 0:
            return so_far
        elif number == 1:
            return "مائة" + result
        elif number == 2:
            return "مائتان" + result
        elif number == 8:
            return num_names[int(number)][:-4] + "مائة" + result
        else:
            return num_names[int(number)][:-1] + "مائة" + result
