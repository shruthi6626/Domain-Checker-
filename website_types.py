import os
import sys
import re

def is_content_parked(content):
    return any(re.findall(r'buy this domain|parked free|godaddy|is for sale'
                          r'|domain parking|renew now|this domain|namecheap|buy now for'
                          r'|hugedomains|is owned and listed by|sav.com|searchvity.com'
                          r'|domain for sale|register4less|aplus.net|related searches'
                          r'|related links|search ads|domain expert|united domains'
                          r'|domain name has been registered|this domain may be for sale'
                          r'|domain name is available for sale|premium domain'
                          r'|this domain name|this domain has expired|domainpage.io'
                          r'|sedoparking.com|parking-lander', content, re.IGNORECASE))

# 1 save html files in a dir - make more 
# 2 read all .html files from that dir
# 3 read the content of each file
# 4 check the type

def is_shopping_page(content):
    return any(re.findall(
        r'add to cart|buy now|shopping cart|checkout|product details|price:|free shipping|sale|discount'
        r'|customer reviews|in stock|out of stock|order now|shop now|payment options|return policy'
        r'|shipping information|related products|secure checkout|promo code|limited time offer',
        content, re.IGNORECASE))


def is_blog_page(content):
    return any(re.findall(
        r'posted on|written by|comments|leave a comment|tags|categories|archives|subscribe|read more'
        r'|recent posts|blog post|author|share this|follow us|related articles|newsletter'
        r'|guest post|editor’s pick|blog archive|comments powered by',
        content, re.IGNORECASE)) 


def is_entertainment_page(content):
    return any(re.findall(
        r'featured video|watch now|music video|live performance|trailer|concert|movie premiere'
        r'|celebrity news|exclusive interview|episode|streaming now|music charts|award show'
        r'|video gallery|photo gallery|upcoming events|entertainment news|tv show|game release'
        r'|backstage|fansite|pop culture|red carpet|behind the scenes|ticket sale|album release',
        content, re.IGNORECASE))

def is_education_page(content):
    return any(re.findall(
        r'course syllabus|lecture notes|assignments|exams|quizzes|online class|curriculum|academic calendar'
        r'|faculty|student portal|class schedule|study materials|educational resources|distance learning'
        r'|tutorial|certificate program|enrollment|course registration|learning management system|gradebook'
        r'|virtual classroom|campus map|research publications|academic program|department|workshop|seminar',
        content, re.IGNORECASE)) 


def is_gov_page(content):
    return any(re.findall(
        r'official website|government agency|public services|department of|tax information|social security'
        r'|legislation|policy|regulations|permits|licenses|voting information|public records|e-government'
        r'|city council|mayor’s office|court system|government forms|budget report|public safety|emergency services'
        r'|citizen services|government news|municipality|federal|state government|local government|public notice',
        content, re.IGNORECASE))

def is_nonprofit_page(content):
    return any(re.findall(
        r'donate now|volunteer|mission statement|annual report|charity event|fundraising|nonprofit organization'
        r'|support our cause|make a donation|community outreach|grant application|sponsor|board of directors'
        r'|impact report|get involved|partner with us|philanthropy|help us|causes we support|tax deductible'
        r'|non-governmental organization|ngo|volunteer opportunities|fundraising campaign|charitable giving',
        content, re.IGNORECASE)) 

def is_nonprofit_page(content):
    return any(re.findall(
        r'donate now|volunteer|our mission|support our cause|nonprofit organization|make a donation'
        r'|charitable giving|fundraising event|community outreach|annual report|board of directors'
        r'|get involved|impact report|partner with us|non-governmental organization|ngo|tax deductible'
        r'|help us|charity|our programs|become a sponsor|grant application|501\(c\)\(3\)',
        content, re.IGNORECASE))

def main():
    _ = is_content_parked("sdlkfnskldnfklsdf")
    if _:
        print("Pass")
    else:
        print("Nope")

if __name__ == '__main__':
    main()
