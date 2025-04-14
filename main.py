#Phishing Email Detection -- main.py

#imports go here
import krovetzstemmer
import re
import time
import csv

#global values
csv.field_size_limit(500000)
FOLD_COUNT = 10



def clean(doc_text):
    '''
    Detects markup language in text, removing words and values associated with it. ALL phrases in between markup tags are deleted.
    This includes #lt; and #bt; (brackets), any tag with # and ; (general markup), and words ending in = or starting with _.
    Punctuation is also removed, but - and ' will stay if not found at the beginning/end of a word.
    
    Words not useful for document ranking (large strings) are removed.
    '''
    doc_text = re.sub(r"#lt;.{0,100}#gt;|#[^\s]*;|<.{0,100}>|<|>", ' ', doc_text)
    doc_text = re.sub(r" [^\s]*= | _[^\s]* |[^\w\s\'-]+| ['\-_]{1,}|['\-_]{1,} | {2,}", ' ', doc_text)
    doc_text = re.sub(r"\n| [^\s]{15,} ", ' ', doc_text)
    
    return doc_text



def clean_tests():
    '''
    Optional test function. Used to manually check if the clean() function operates as intended, by giving dummy inputs.
    '''
    test_lines = [  "URL//none This is a normal sentence.",
                    "URL//both I have #lt;br#gt; two friends.",
                    "URL//l_only Three #lt; Five is true.",
                    "URL//l_connect Two#lt;Four is also true.",
                    "URL//r_only But three #gt; five is NOT true.",
                    "URL//r_connect and nor is two#gt;Four, it also is NOT also true.",
                    "URL//both Both tags#lt;#gt;should disappear",
                    "URL//both the same#lt;Bad!#gt;will happen here",
                    "URL//both before opening tag #lt;Bad!#gt;is a space.",
                    "URL//both after closing tag#lt;Bad!#gt; is a space",
                    "URL//gen we have a generic#amp;tag and that's a-okay.",
                    "URL//equal this = and this= are different, and so is 4==3; none should stay",
                    "URL//underline __this this gets removed. We don't__ want it, we don't love __Bad!__ it",
                    "URL//punctuation This?>#%@cannot stay, but apostrophe's and-dashes like these can; 'but -not'' these-- ",
                ] 
                
    for doc in test_lines:
        doc = clean(doc)
        token_doc = list(x for x in doc.split()[1:])
        print(token_doc)
    print("_________________\n")



def word_counting(stemmer, word_bank, text, label):
    '''
    Reads text (subject line + email) filled with words, adding them to the word bank as is appropriate.
    Words found in normal emails will increment the negative count, and words found in phishing emails increment the positive count.
    '''
    for token in text:
        if token == "" or token == " " or "Â" in token or (token.isascii() == False):
            continue
        token = stemmer.stem(token)
        if token not in word_bank:           #first global appearance; initialize
            word_bank[token] = {"positive": 0, "negative": 0}
            
        if label == "1":
            word_bank[token]["positive"] += 1
        else:
            word_bank[token]["negative"] += 1

    return word_bank



def text_scoring(word_bank, text):
    '''
    Reads text (subject line + email) filled with words, scoring it based on the word bank counts.
    Words found more often in normal emails will add negative values to the score.
    Words found more often in phishing emails will add positive values to the score.
    A label is returned based on the cumulative score.
    '''
    score = 0

    for token in text:
        if token not in word_bank:           #unseen word; +0 score
            continue
        
        pos_count = word_bank[token]["positive"]
        neg_count = word_bank[token]["negative"]
        local_multiplier = 1     
        if (neg_count > pos_count):
            local_multiplier = -1
        score += (local_multiplier * max(neg_count, pos_count)) / (neg_count + pos_count)

    if score > 0:
        return 1        #label as phishing email
    return 0            #label as normal email



def phishing_email_detection():
    '''
    Main program. Reads a dataset of emails to find which words correspond with normal/phishing emails (labels: 0/1).
    Will divide itself into ten folds (90% training, 10% test), with test emails being used to determine model accuracy.
    Each fold will be tested one by one, producing an accuracy score for each; these are used to get an average accuracy score.
    Test emails with negative scores = normal emails, and test emails with positive scores = phishing emails.
    '''
    #initialize needed variables 
    dataset = list()
    folds = list()
    accuracy_list = list()
    stemmer = krovetzstemmer.Stemmer()
    t0 = time.time()
   
    file = open("CEAS_08.csv", 'r', encoding='ISO-8859-1')                      #sender,receiver,date,subject,body,label,urls
    csvfile = csv.reader(file, delimiter = ",")
    for index, lines in enumerate(csvfile):
        if index == 0:                                                          #only contains headers, do not include
            continue
        
        dataset.append([lines[0], lines[3], lines[4], lines[5], lines[6]])      #sender, subject, body, label, urls
    
    instance_count = (len(dataset))


    #Split corpus instances into 10 folds (for 90% training, 10% test)
    r = instance_count % FOLD_COUNT                                             #remainder instances
    fold_num = int( (instance_count) // FOLD_COUNT)
    last_fold_num = int(fold_num + r)           
    
    #give an equal number of instances to all folds
    for m in range(FOLD_COUNT - 1):
        folds.append([])        
        for i in range(fold_num):
            instance_index = (fold_num * m) + (i)
            instance_values = dataset[instance_index]
            folds[m].append(instance_values)
    
    #last fold; give remaining instances
    folds.append([])                            
    for i in range(last_fold_num):
        instance_index = (fold_num * (FOLD_COUNT - 1)) + (i)
        instance_values = dataset[instance_index]
        folds[FOLD_COUNT - 1].append(instance_values)
    

    #-----LOOP FOR TRAIN/TEST-----
    for m in range(FOLD_COUNT):
        word_bank = dict()
        true_labels = list()
        pred_labels = list()
        correct_matches = 0
        
        #train
        for i in range(FOLD_COUNT):
            if i == m:
                continue
            for data in folds[i]:
                text = clean(data[1] + " " + data[2]).split(" ")
                #print(text)
                word_bank = word_counting(stemmer, word_bank, text, label=data[3])

        #test
        for data in folds[m]:
            true_labels.append(int(data[3]))
            text = clean(data[1] + " " + data[2]).split(" ")
            pred_labels.append(text_scoring(word_bank, text))

        #fold accuracy
        for i in range(len(true_labels)):
            if pred_labels[i] == true_labels[i]:
                correct_matches += 1
        acc = correct_matches / len(true_labels) * 100
        accuracy_list.append(acc)
        print(f"Accuracy for fold {m+1}: {round(acc, 1)} %")
    

    #Get average accuracy
    avg_acc = 0
    for acc in accuracy_list:
        avg_acc += acc
    avg_acc /= FOLD_COUNT
    print(f"Average accuracy: {round(avg_acc, 1)} %")

    return 0



if __name__ == "__main__":
    phishing_email_detection()
    