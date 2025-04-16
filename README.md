# PhishingEmailDetection

This is an algorithm that recognizes phishing emails (label 1) by detecting what kind of language is used in the subject and body text of said emails. Emails are separated into normal and phishing emails, with words being counted from either like so:

<word> <positive> <negative>

Where <word> is the word itself, <positive> is the number of times that word appeared in a phishing email, and <negative> is the number of times that word appeared in a normal email. These counts are used to give a 'score' to the word, depending on which type of email the word is more likely to appear in. Positive scores imply the word is found more often in phishing emails (and vice versa).

The algorithm also adds to the score if the email sender is suspicious. This is determined by key words, email domains, and the excessive use of dots and dashes.


## How to Run

The code uses the in-built libraries 're', 'time', and 'csv', along with 'nltk' (for importing stopwords) and 'krovetzstemmer' (a stemming library). They can be imported like so:

>> pip install nltk
>> pip install krovetzstemmer

Or, you can use requirements.txt. Enter the directory where requirements.txt is located, then run the following command:

>> pip install -r requirements.txt

main.py is the main file to be run. You can use an IDE (like Visual Studio Code) or the command terminal to access the project directory. From there, simply run the file main.py. Assuming you are running from the terminal and in the correct directory, the following command will work:

>> python.exe main.py
