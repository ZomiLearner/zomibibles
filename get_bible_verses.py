import sys
sys.path.append('/usr/local/lib/python3.13/dist-packages/bible') # Fixing for the broken package

import bible.data
books = bible.data.bible_data("NKJV") # 31103
# ('NIV', 'NASB', 'RSV', 'NRSV', 'NCV', 'ESV', 'LB'):

book_codes = [
    "GEN","EXO","LEV","NUM","DEU","JOS","JDG","RUT",
    "1SA","2SA","1KI","2KI","1CH","2CH","EZR","NEH",
    "EST","JOB","PSA","PRO","ECC","SNG","ISA","JER",
    "LAM","EZK","DAN","HOS","JOL","AMO","OBA","JON",
    "MIC","NAM","HAB","ZEP","HAG","ZEC","MAL","MAT",
    "MRK","LUK","JHN","ACT","ROM","1CO","2CO","GAL",
    "EPH","PHP","COL","1TH","2TH","1TI","2TI","TIT",
    "PHM","HEB","JAS","1PE","2PE","1JN","2JN","3JN",
    "JUD","REV"
]

verses = []

for code, book in zip(book_codes, books):
    omissions = book.get("omissions", [])

    for chapter_num, verse_count in enumerate(book["verse_counts"], start=1):

        omitted = set()
        if chapter_num <= len(omissions) and omissions[chapter_num - 1]:
            omitted = set(omissions[chapter_num - 1])

        for verse_num in range(1, verse_count + 1):
            if verse_num not in omitted:
                verse = f"{code}_{chapter_num}_{verse_num}"
                verses.append(verse)

print(len(verses))
