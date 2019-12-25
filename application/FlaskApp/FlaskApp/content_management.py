from .functions import RouteFunctions
from .models import Category, Message, Image, Thumbnail, Admin, Book

# This dictionary contains static information and functions that can be accessed by Jinja templates.
# The purpose of it is to condense as much information together to avoid an overwhelming amount of
# render template parameters.

def Content():
    CONTENT_DICT = {"About": [["Grant Kennedy", "Front-end-lead", "/about/grant"],
                              ["Mark Hammond", "Back-end-lead", "/about/mark"],
                              ["Piero Calenzani", "Project Lead", "/about/piero"],
                              ["Varun Sura", "Front-end-developer", "/about/varun"],
                              ["Zhuoxin Tan", "Back-end-developer", "/about/zhuoxin"],
                              ["Will Yang", "Github Master", "/about/will"]],
                    "piero": ["Piero Calenzani", "/static/resources/Piero.jpg", "I'm a Computer Science major at \
                                San Francisco State University. An the team lead for this project. I was born in \
                                Peru and am bilingual in English and Spanish. I am currently on my last semester \
                                before graduation at the end of this year."],
                    "varun": ["Varun Sura", "/static/resources/Varun.png", "I am a graduate student at San \
                                Francisco State University. I am the front end developer for the Project."],
                    "will": ["William Yang", "/static/resources/will.JPG", "One of an international student \
                                in SFSU. Email: williamsych@gmail.com"],
                    "zhuoxin": ["Zhuoxin Tan", "/static/resources/Tan.png", "I'm a Computer Science student at \
                                San Francisco State University."],
                    "mark": ["Mark Hammond", "/static/resources/mark.jpg", "Mark is a senior at San Francisco \
                                State University. He is a native of the Monterey Bay, moving to San Francisco in 2011"],
                    "grant": ["Grant Kennedy", "/static/resources/grant.jpg", "I'm a senior Computer Science \
                                student at San Francisco State University. I currently work as a Technician at \
                                the Exploratorium where I hope to become an exhibit developer!"],
                    "Courses": ["AAS", "ACCT", "ADM", "AFRS", "AIS", "AMST", "ANTH", "ARAB", "ART", "ASTR", "ATHL",
                                "BECA", "BIOL", "BUS", "CAD", "CEEL", "CHEM", "CHIN", "CINE", "CJ", "CLAR", "CLAS",
                                "CLS", "CMX", "COMM", "CWL", "CSC", "CST", "CW", "DANC", "DES", "DFM", "DS", "ESE",
                                "ESM", "ECON", "EDAD", "EDDL", "EDUC", "EED", "ENGR", "ENG", "ENVS", "ETHS", "ERTH",
                                "EXCO", "FCS", "FIN", "FR", "GEOG", "GER", "GRN", "GPS", "GRE", "HSS", "HED", "HEBR",
                                "HIST", "HH", "HTM", "HUM", "ISYS", "ITEC", "ISED", "ID", "IBUS", "IR", "ITAL", "JAPN",
                                "JS", "JOUR", "KIN", "LBR", "LTNS", "LATN", "LCA", "LS", "LIB", "MGMT", "MSCI", "MKTG",
                                "MATH", "MEIS", "MGS", "MLL", "MS", "MUS", "NURS", "NUTR", "PRSN", "PHIL", "PT", "PHYS",
                                "PLSI", "PSY", "PA", "RRS", "RPT", "RELS", "RUSS", "SNSK", "SCI", "SED", "SXS", "SW",
                                "SOC", "SPAN", "SPED", "SLHS", "THA", "USP", "WGS"],
                    "categories": Category.get_all_categories,
                    "authenticated": RouteFunctions.authenticate,
                    "admin": Admin.exists,
                    "sender": Message.get_sender,
                    "getimage": Image.get_image,
                    "getthumb": Thumbnail.get_thumb,
                    "isbook": Book.is_book,
                    }
    return CONTENT_DICT
