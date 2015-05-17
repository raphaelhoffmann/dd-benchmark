#! /usr/bin/env python3

import ddext
from ddext import SD

def init():
    #ddext.import_lib('re')
    ddext.input('doc_id', 'text')
    ddext.input('words', 'text')

    ddext.returns('id', 'bigint')
    ddext.returns('doc_id', 'text')
    ddext.returns('is_true', 'boolean')
    ddext.returns('features', 'text[]')


def run(doc_id, words):
    #import os
    #plpy.info(os.getcwd())

    if 'stopwords' in SD:
        stopwords = SD['stopwords']
    else:
        stopwords = [line.strip() for line in open('/lfs/local/1/raphaelh/stanford-memex/dicts/common_words.tsv')]
        SD['stopwords'] = stopwords

    import sys
    import os

    import collections

    Mention = collections.namedtuple('Mention', ['id', 'doc_id', 'is_true', 'features'])

    if 'inout_set' in SD:
        inout_set = SD['inout_set']
    else:
        #inout_set = [line.strip() for line in open('/lfs/local/1/raphaelh/stanford-memex/dicts/common_words.tsv')]
        # removed: discreet, beautiful asian, hot, pamper, sexy, lovely
        inout_set = frozenset(['i have', 'i offer you', 'i will', 'i \'m', 'my', 'blowjob', 'thugs', 'pics', 'lol', 'gentlemen', 'blonde', 'seduce', 'totally', 'exotic', 'ass', 'boobs', 'fetish', 'kissing', 'passionate', 'sex', 'mature', 'hotness', 'beauty', 'erotic', 'roses', 'babe', 'ebony', 'gents', 'anal', 'fantasies', 'fetishes', 'pimps', 'petite', 'girl', 'lover', 'feminine', 'discretion', 'amazing body', 'text me', 'booty', 'tits', 'plz', 'xoxo', 'boobs', 'bbw', 'my name is', 'gentleman', 'play time boys', 'i date', 'best night', '100% me', 'my southern charm', 'i will give', 'i will be', 'nasty', 'gratifying experience', 'to being your', 'my desire is', 'hourglass figure', 'voluptuous', 'hey boys', 'private condo', 'sense of humour', 'leave wanting more', 'mes photos', 'experience to remember', 'breast', 'i want you', 'real photos', 'see your beautiful', 'call someone else', 'what you see', 'long legs', 'my legs', 'i am completely', 'be shy', 'not shy', 'open-minded', 'open minded', 'up all night', 'overnights', 'open to new', 'pictures are real', 'call me anytime', 'i am new', 'titties', 'i am waiting', 'waiting for you', 'love to have fun', 'men only', 'over nights', '100% real', 'deepthoat', 'real fun', 'no hood areas', 'no black men', 'want me', 'discrete', 'call me', 'no law inforcement', 'no law enforcement', 'time with me', 'good clean fun', 'nude', 'take my time', 'me again', 'young sweet girls', 'care of your needs', 'weiter kosten mchtest', 'thick thighs', 'extremely sweet', 'i am a white', 'let me show', 'ultimate female', 'pure ecstasy', 'come lay up', 'i adore', 'beyond your imagination', 'i love what i', 'trust me', 'taste is sweet', 'play with me', 'time spent with me', 'seduction', 'help put a smile', 'i love to please', 'princess', 'donations', 'vulgar', 'your day the best', 'busty', 'you completely satisfied', 'for your enjoyment', 'available day & night', 'session with me', 'freshly showered', 'heavenly delight', 'cute', 'natural breasts', 'my moves', 'i am sweet', 'dirty sluts', 'intimate', 'hello i am', 'beautiful woman', 'caramel skin', 'pretty face', 'can come to you', 'interested in meeting someone', 'you will love my', 'like to have fun', 'ihr bekommt mich', 'not fake', 'no fakeness', 'enjoy what i do', 'i \'ll treat', 'sweety', 'mutual oral', 'exquisite lady', 'how good it feels', 'be yours tonight', 'want to be yours', '80qk', 'my service is', 'xxx', 'private location', 'to please you', 'luv what I do', 'my body', 'every move is right', 'for a night', 'live your dreams', 'explosion', 'any man that knows', 'i love sensuous touch', 'take care of my', 'passion', 'my contagious', 'i provide', 'ich fessel', 'best girls', 'want to see what', 'willing to be your', 'those of you who', 'i can do', 'in pleasure', 'relaxing night', 'ultimate pleasure', 'with me', 'easy going personality', 'i love', 'pure women', 'i promise you', 'descrete', 'duo or 1-on-1', 'day for you', 'pampering', 'secret adventure', 'have you ever', 'asian pretty girls', 'available all night', 'no drama', 'stop wasting your time', 'let me become', 'let me', 'addiction', 'i know just what', 'i promise', 'you just have to', 'make love', 'clean and professional', 'hook up', 'i offer a service', 'i can treat you', 'might be love', 'come play', 'no law enforcemnet', 'misstress', 'bust', 'forward to being your', 'pretty hair', 'my warm way', 'no explicit questions', 'will not be disappointed', 'allow me', 'even better in person', 'like to have fun', 'i have', 'call girls', 'drama free', 'schmusen', 'ready to please', 'geil', 'you like me to', 'i prefer', 'kiss', 'no drama', 'all kinds of fun', 'hear from you', 'i am very', 'amaze you with', '1000% real', 'have a great time', 'time to have fun', 'i am here to', 'you must see', 'you will have fun', 'princessa', 'Lesb**spiele', 'i am available', 'no time for bs', 'no bb', 'i really do', 'my place', 'beautiful face', 'call sandy at', 'xoxoxoxo', 'treat yourself to', 'no explicit talk', 'no explicit text', 'time for the best', 'come see', 'licking balls', 'ready to meet', 'what are you waiting', 'not waste your time', 'i am', 'asian glow', 'give me a call', 'baby', 'double fun', 'serious men', 'friendly girls', 'do this for fun', 'contact me at', 'hi boys', 'hello boys', 'love to please', '100% all real', 'hottest', 'my name is', '36ddenhanced', 'real pics', 'let \'s play', '100% real', 'long hair', 'what u want', 'cater to your needs', 'flirty', 'please you', 'gorgeous full figured', 'pictures are 100% real', 'for 1 night only', 'curvy latina', 'hottest', 'snowbunny', 'we have five gurls', 'intimos', '34dd', '36dd', 'no low ballers', 'rose donation', 'mature lady', 'playful', 'playfully', 'affectionate', 'complex young woman', 'px are real', 'la nuit', 'clean and classy'])
        SD['inout_set'] = inout_set

    if 'labour_set' in SD:
        labour_set = SD['labour_set']
    else:
        labour_set = frozenset(['consultants', 'resume', 'this position', 'qualifications', 'degree', 'paperwork', 'industrys', 'industry', 'systems', 'cpm', 'diploma', 'hazmat', 'lifting', 'driver', 'organisation', 'manager', 'license', 'merchandise', 'employer', 'competencies', 'department', 'driving', 'managing', 'engineers', 'engineer', 'businesses', 'nationwide', 'application process', 'revenue', 'management', 'work with us', 'our mission', 'work environment', 'make more money', 'financial rewards', 'customer service', 'attics', 'retail', 'career', 'free training', 'transmission', 'transmissions', 'health and safety', 'self development',  'unternehmen', 'mathematical', 'laboratory', 'current openings', 'ad agency', 'automobiles', 'per month', 'usa truck', 'leadership experience', 'cisco', 'clean restroom', 'latest technology', 'team atmosphere', 'working environment', 'clear and professional', 'coordinator', 'startup opportunities', 'conformance', 'account leads', 'competitive media', 'propensity to travel',  'compensation', 'water lawns', 'processing company', 'ability to communicate', 'your own schedule', 'wireless company', 'relocate', 'trailer', 'productively', 'representative', 'unbefristeter', 'unbefristet', 'patientinnen', 'clinic', 'underwriters', 'experience with web services', 'payment solutions', 'sales person', '401k', 'team member', 'company description', 'permanent pay', 'full-time', 'staffing agency', 'representative', 'assistant', 'healthcare', 'associate', 'employment', 'pt position', 'clerk', 'billion', 'customer service', 'excellent salary', 'accounting', 'clinical', 'fastest growing', 'fast growing', 'licensed', 'physicians' , 'arbeiten', 'fachkenntnisse', 'software', 'corporation', 'responsibilities', 'organization', 'executive', 'complete an application', 'maintenance associate', 'repairs', 'system', 'documentation', 'monthly bonuses', 'a new position', 'rehabilitation research', 'implementation', 'complete the application', 'one year hospital', 'experience required', 'strong commitment', 'earning up to', 'pathologist', 'communication skills', 'pharmaceutical', 'job location', 'nurses', 'developer', 'rehabilitation', 'we are looking for', 'company profile', 'we are seeking an', 'laborer', 'dental', 'associates', 'architects', 'medical', 'career', 'nursing care', 'sales training', 'excelentes habilidades interpessoal','rehab', 'sales associates', 'firm', 'consulting opportunity', 'job location', 'we are seeking a', 'job overview', 'teamwork', 'assistant', 'supplier', 'business unit', 'salary', 'practical nurse', 'cashiers', 'job number', 'nurse needed', 'leading global', 'tax professional', 'rn', 'hospital'])
        SD['labour_set'] = labour_set

    if 'massageparlor_set' in SD:
        massageparlor_set = SD['massageparlor_set']
    else:
        massageparlor_set = frozenset(['walk-ins', 'opening hours', 'walkins', 'jacuzzi', 'therapist', 'therapists', 'therapies', 'deep tissue', 'shiatsu massage', 'sauna', 'spa', 'spa packages', 'therapuetic massage', 'therapeutic', 'accupressure', 'private rooms', 'our services', 'staff', 'masseuses', 'open daily', 'free parking', '7days', 'home spa', 'vip spa', 'now open', 'hamstrings', 'lower back', 'injuries', 'grand opening', 'tableshower', 'sauna', 'credit cards', 'attendants', 'book an appointment', 'chambres vip', 'jacuzzi', 'aroma massage 12921', 'blvd', 'cards accepted', 'facilities'])
        SD['massageparlor_set'] = massageparlor_set

    #TODO: open hours extractor
    #TODO: address extractor
    escort_set = frozenset(['escorts'])

    hard_pos_words = frozenset(['fern st', 'spa rooms', 'private rooms'])
    hard_neg_words = frozenset(['incall', 'outcall', 'in-call', 'out-call', 'in-calls', 'out-calls', 'incalls', 'outcalls', 'your resume', 'employment', 'job description', 'seeking a qualified', 'intensive care rn', 'nurse', 'air force', 'pune independent female escort'])

    pos_words = massageparlor_set
    neg_words = inout_set | escort_set # labour_set | inout_set

    def featurize(words, m):
        # all words, but not stop words?
        features = []
        for w in words:
            if not w in stopwords:
                features.append(w)
        return m._replace(features=features)

    def overlaps(set1, set2):
        for w in set1:
            if w in set2:
                #plpy.info(w) 
                return True
        return False


    def supervise(words, m):
        ws = set(words)
        for i in range(2,5):
            for s in range(0, len(words)-i):
                ws.add(' '.join(words[s:s+i]))
        overlaps_pos = overlaps(pos_words, ws)
        overlaps_neg = overlaps(neg_words, ws)
        is_true = None
        if overlaps_pos and not(overlaps_neg):
            is_true = True
        if not(overlaps_pos) and overlaps_neg:
            is_true = False
        if overlaps(labour_set, ws):
            is_true = False
        if overlaps(hard_pos_words, ws):
            is_true = True
        if overlaps(hard_neg_words, ws):
            is_true = False
        return m._replace(is_true=is_true)

    words_arr = [w.lower() for w in words.split(' ')]
    m = Mention(id=None,doc_id=doc_id,is_true=None,features=[])
    m = featurize(words_arr, m)
    m = supervise(words_arr, m)
    yield [m.id, m.doc_id, m.is_true,m.features]

